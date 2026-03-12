import argparse
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from eppy.modeleditor import IDF

from occupants import Participant
from result_collector import Result
from sim_ep import CoSimulation
from strategies import SensationAggregator, generate_set_point


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_ENERGYPLUS_DIR = Path(r"D:\Programming\EnergyPlus\EnergyPlusV22-2-0")
DEFAULT_IDD_FILE = DEFAULT_ENERGYPLUS_DIR / "Energy+.idd"
DEFAULT_CITY = "paris"
WEATHER_FILE_MAPPING = {
    "mumbai": REPO_ROOT / "models" / "weathers" / "mumbai",
    "la": REPO_ROOT / "models" / "weathers" / "la",
    "paris": REPO_ROOT / "models" / "weathers" / "paris",
    "scranton": REPO_ROOT / "models" / "weathers" / "scranton",
}
SUPPORTED_CONTROL_MONTHS = {1, 2, 6, 7, 8, 12}


def parse_args():
    parser = argparse.ArgumentParser(description="Run a short EnergyPlus functional test for Co-zyBench.")
    parser.add_argument("--energyplus-dir", default=str(DEFAULT_ENERGYPLUS_DIR), help="Path to the EnergyPlus installation directory.")
    parser.add_argument("--idd-file", default=str(DEFAULT_IDD_FILE), help="Path to the EnergyPlus IDD file.")
    parser.add_argument("--city", default=DEFAULT_CITY, choices=sorted(WEATHER_FILE_MAPPING.keys()), help="City weather file to use.")
    parser.add_argument("--start-date", default="2010-01-01", help="Simulation start date in YYYY-MM-DD format.")
    parser.add_argument("--days", type=int, default=1, help="Number of days to simulate.")
    return parser.parse_args()


def ensure_path_exists(path: Path, label: str):
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")


def prepare_test_model(base_model_path: Path, idd_file: Path, ddy_file_path: Path, output_model_path: Path, start_date: datetime, end_date: datetime):
    IDF.setiddname(str(idd_file))
    idf_origin = IDF(str(base_model_path))
    ddy_idf = IDF(str(ddy_file_path))

    for cls in ["SizingPeriod:DesignDay"]:
        idf_origin.removeallidfobjects(cls)

    design_days = ddy_idf.idfobjects["SizingPeriod:DesignDay".upper()]
    if design_days:
        idf_origin.copyidfobject(design_days[0])

    for run_period in idf_origin.idfobjects["RUNPERIOD"]:
        run_period.Begin_Month = start_date.month
        run_period.Begin_Day_of_Month = start_date.day
        run_period.End_Month = end_date.month
        run_period.End_Day_of_Month = end_date.day

    simulation_control = idf_origin.idfobjects["SIMULATIONCONTROL"]
    if simulation_control:
        simulation_control[0].Run_Simulation_for_Sizing_Periods = "No"
        simulation_control[0].Run_Simulation_for_Weather_File_Run_Periods = "Yes"

    time_steps = idf_origin.idfobjects["TIMESTEP"]
    if time_steps:
        time_steps[0].Number_of_Timesteps_per_Hour = 1

    output_model_path.parent.mkdir(parents=True, exist_ok=True)
    idf_origin.save(str(output_model_path))
    return IDF(str(output_model_path))


def build_parameters(idf):
    thermal_zones = [zone.Zone_Name for zone in idf.idfobjects["ZONEHVAC:EQUIPMENTCONNECTIONS"]]
    input_param = {}
    output_param = {}

    for index, zone in enumerate(thermal_zones, start=1):
        input_param[f"sch_clg_{index}"] = ["Zone Temperature Control", "Cooling Setpoint", zone, 50]
        input_param[f"sch_htg_{index}"] = ["Zone Temperature Control", "Heating Setpoint", zone, 0]
        output_param[f"temp{index}"] = ["Zone Air Temperature", zone]

    output_param.update(
        {
            "ec_clg_coil": ["Cooling Coil Electricity Energy", "Coil Cooling DX Two Speed 1"],
            "ec_htg_coil": ["Heating Coil Electricity Energy", "1 Spd DX Htg Coil"],
            "temp_out": ["Site Outdoor Air Drybulb Temperature", "Environment"],
        }
    )

    for fan in idf.idfobjects["FAN:ONOFF"]:
        output_param[f"ec_fan_{fan.Name}"] = ["Fan Electricity Energy", fan.Name]

    return thermal_zones, input_param, output_param


class FunctionalTestCoSimulation(CoSimulation):
    def run(self):
        state = self.api.state_manager.new_state()
        temp_run_dir = Path(self.e.get_temp_run_dir())
        try:
            self.api.runtime.callback_begin_zone_timestep_after_init_heat_balance(state, self.callback_function)
            self.api.runtime.run_energyplus(state, [
                '-w', self.weather_path,
                '-d', str(temp_run_dir),
                self.model_path,
            ])
        finally:
            self.api.state_manager.delete_state(state)
            shutil.rmtree(temp_run_dir, ignore_errors=True)


def main():
    args = parse_args()
    os.chdir(REPO_ROOT)

    energyplus_dir = Path(args.energyplus_dir)
    idd_file = Path(args.idd_file)
    base_model_path = REPO_ROOT / "models" / "office" / "CZ4" / "in.idf"
    trajectory_path = REPO_ROOT / "models" / "office" / "trajectories"
    profile_path = REPO_ROOT / "models" / "office" / "occ_config.txt"
    weather_base_path = WEATHER_FILE_MAPPING[args.city]
    ddy_file_path = Path(str(weather_base_path) + ".ddy")
    weather_file_path = Path(str(weather_base_path) + ".epw")
    runtime_temp_root = REPO_ROOT / ".functional_test_runtime"
    output_model_path = runtime_temp_root / "functional_test.idf"

    ensure_path_exists(energyplus_dir, "EnergyPlus directory")
    ensure_path_exists(idd_file, "IDD file")
    ensure_path_exists(base_model_path, "Functional test model")
    ensure_path_exists(trajectory_path / "1.txt", "Functional test trajectory file")
    ensure_path_exists(profile_path, "Functional test profile file")
    ensure_path_exists(ddy_file_path, "Design day file")
    ensure_path_exists(weather_file_path, "Weather file")

    if args.days < 1:
        raise ValueError("--days must be at least 1.")

    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    if start_date.month not in SUPPORTED_CONTROL_MONTHS:
        supported_months = ", ".join(str(month) for month in sorted(SUPPORTED_CONTROL_MONTHS))
        raise ValueError(
            "--start-date month must be one of "
            f"{supported_months} so the control loop in sim_ep.py is exercised during the functional test."
        )

    end_date = start_date + timedelta(days=args.days - 1)

    old_temp = os.environ.get("TEMP")
    old_tmp = os.environ.get("TMP")
    runtime_temp_root.mkdir(exist_ok=True)
    os.environ["TEMP"] = str(runtime_temp_root.resolve())
    os.environ["TMP"] = str(runtime_temp_root.resolve())

    try:
        idf = prepare_test_model(base_model_path, idd_file, ddy_file_path, output_model_path, start_date, end_date)
        thermal_zones, input_param, output_param = build_parameters(idf)

        occupants = Participant(
            len(thermal_zones),
            str(profile_path),
            None,
            None,
            str(trajectory_path),
            "prior_knowledge",
        )
        occupants.clean()

        result = Result(occupants, args.city)
        CoSimulation.ep_path = energyplus_dir
        co_sim = FunctionalTestCoSimulation(
            str(output_model_path),
            start_date,
            end_date,
            input_param,
            output_param,
            occupants.vote,
            SensationAggregator("majority", occupants),
            generate_set_point,
            result,
            occupants.update_loss,
            str(weather_file_path),
            True,
            str(weather_file_path),
            "fixed_rule",
        )
        co_sim.run()

        if co_sim.total_people_count <= 0:
            raise RuntimeError("Functional test completed without collecting any occupant interactions.")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        identify = "functional_test_majority_fixed_rule_1"
        result.save_result(timestamp, identify, co_sim.total_people_count)

        result_dir = REPO_ROOT / "results" / f"result_{timestamp}"
        result_file = result_dir / f"result-{identify}.txt"
        if not result_file.exists():
            raise FileNotFoundError(f"Functional test did not produce the expected result file: {result_file}")

        print("Functional test completed successfully.")
        print(f"Model: {base_model_path}")
        print(f"Weather: {weather_file_path}")
        print(f"Result file: {result_file}")
        print(f"Occupant interactions recorded: {co_sim.total_people_count}")
    finally:
        if old_temp is None:
            os.environ.pop("TEMP", None)
        else:
            os.environ["TEMP"] = old_temp
        if old_tmp is None:
            os.environ.pop("TMP", None)
        else:
            os.environ["TMP"] = old_tmp
        shutil.rmtree(runtime_temp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
