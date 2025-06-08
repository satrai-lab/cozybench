import subprocess
import datetime
import argparse
from datetime import datetime, timedelta
from time import sleep

from colorama import Fore, Back, Style, init
from tqdm import tqdm

from occupants import Participant
from result_collector import Result
from sim_ep import CoSimulation
from eppy.modeleditor import IDF

from strategies import SensationAggregator, generate_set_point


def main():
    # parser = argparse.ArgumentParser(description="co-zybench for evaluating thermal comfort provision systems")
    # parser.add_argument('-s', '--system', required=False, help='name of the thermal comfort system to be evaluated', default="majority")
    # parser.add_argument('-b', '--building', required=False, help='path to the building energyplus model', default="building")
    # parser.add_argument('-o', '--occupant', required=False, help='path to the occupant trajectories', default="models/drahix/trajectories")
    # parser.add_argument('-p', '--profile', required=False, help='path to the occupant profile file', default="models/drahix/occ_config.txt")
    #
    # args = parser.parse_args()
    #
    # algorithms = []
    # if args.system[0] == "[":
    #     algorithms = args.system[1:-1].split(",")
    #     print(algorithms)
    # else:
    #     algorithms.append(args.system)

    # path_ep_model = args.building
    # path_trajectories = args.occupant
    # path_profile = args.profile

    # path_ep_model = "models/office/CZ4/in.idf"
    # path_trajectories = "models/office/trajectories"
    # path_profile = "./models/office/occ_config.txt"

    path_ep_model = "models/synthetic_large/10floors_V2.idf"
    path_trajectories = "models/synthetic_large/trajectories"
    path_profile = 1200

    repeat_time = 1
    # TODO
    scenario_system = [0]
    percentage = [100]
    # distribution_scenarios = {"MW80": [20, 0, 80], "MW70": [30, 0, 70], "NM": [40, 20, 40], "MC70": [70, 0, 30], "MC80": [80, 0, 20]}
    # sensation_collector = ["historical_based", "prior_knowledge"]
    # hvac_controller = ["fixed_rule", "preference_estimation"]
    hvac_controller = ["preference_estimation"]
    algorithms = ["majority", "fair", "drift"]
    cities = ["paris"]
    weather_file_mapping = {"mumbai": "models/weathers/mumbai", "la": "models/weathers/la",
                            "paris": "models/weathers/paris", "scranton": "models/weathers/scranton"}

    # scenario_system = [1]
    # percentage = [100]
    # view for required processing time

    total_simulation_iteration = len(algorithms) * repeat_time * len(hvac_controller) * len(cities)
    current_simulation_iteration = 0
    start_time = datetime.now()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    for r_time in range(repeat_time):
        for city in cities:
            for algo in algorithms:
                for hvac_control_strategy in hvac_controller:
                    model_path = path_ep_model

                    epw_file_path = weather_file_mapping[city] + ".epw"

                    # total number of how many times all the people got involved in the system
                    total_num = 0

                    idd_file = r"D:\Programming\EnergyPlus\EnergyPlusV22-2-0\Energy+.idd"
                    IDF.setiddname(idd_file)
                    idf_origin = IDF(model_path)

                    ddy_file_path = weather_file_mapping[city]+".ddy"
                    ddy_idf = IDF(ddy_file_path)

                    design_day_classes = ['SizingPeriod:DesignDay']
                    for cls in design_day_classes:
                        idf_origin.removeallidfobjects(cls)

                    design_days = ddy_idf.idfobjects["SizingPeriod:DesignDay".upper()]
                    design_days = design_days[0]

                    idf_origin.copyidfobject(design_days)

                    idf_origin.save("models/temp/temp.idf")

                    idf = IDF("models/temp/temp.idf")

                    thermal_zones = []
                    for zone in idf.idfobjects['ZONEHVAC:EQUIPMENTCONNECTIONS']:
                        thermal_zones.append(zone.Zone_Name)
                    space_num = len(thermal_zones)

                    # occupants = Participant(space_num, path_profile, "knn/ashrae_comfort_data.csv", "s1_100", path_trajectories, "historical_based")
                    occupants = Participant(space_num, path_profile, [30, 40, 30], "s1_100",
                                            path_trajectories, "prior_knowledge")

                    occupants.clean()

                    result = Result(occupants, city)

                    input_param = {}
                    output_param = {}
                    for index, zone in enumerate(thermal_zones):
                        input_param['sch_clg_'+str(index+1)] = ["Zone Temperature Control", "Cooling Setpoint", zone, 50]
                        input_param['sch_htg_'+str(index+1)] = ["Zone Temperature Control", "Heating Setpoint", zone, 0]
                        output_param['temp'+str(index+1)] = ["Zone Air Temperature", zone]

                    # handles for energy consumption:
                    for index, zone in enumerate(thermal_zones):
                        output_param["ec_clg_tz" + str(index + 1)] = ["Zone Air System Sensible Cooling Energy", zone]
                        output_param["ec_htg_tz" + str(index + 1)] = ["Zone Air System Sensible Heating Energy", zone]
                    output_param.update({'ec_clg_coil': ["Cooling Coil Electricity Energy", "COIL COOLING DX TWO SPEED 1"],
                                    'ec_htg_coil': ["Heating Coil Electricity Energy", "1 SPD DX HTG COIL"],
                                    'temp_out': ["Site Outdoor Air Drybulb Temperature", "Environment"]})

                    idf_fans = idf.idfobjects["Fan:OnOff"]
                    for fan in idf_fans:
                        output_param["ec_fan_" + fan.Name] = ["Fan Electricity Energy", fan.Name]

                    start_date = datetime.strptime("2010-01-01", "%Y-%m-%d")
                    end_date = datetime.strptime("2010-12-30", "%Y-%m-%d")

                    # TODO: run PyEP
                    # TODO: configure sensation collector, sensation aggregator and hvac controller

                    if algo == "const":
                        turn_off_when_empty = False
                    else:
                        turn_off_when_empty = True

                    co_sim = CoSimulation("models/temp/temp.idf", start_date, end_date, input_param, output_param, occupants.vote,
                                          SensationAggregator(algo, occupants), generate_set_point, result,
                                          occupants.update_loss, epw_file_path, turn_off_when_empty, weather_file_mapping[city]+".epw", hvac_control_strategy)
                    co_sim.run()



                    result.save_result(start_time.strftime("%Y%m%d%H%M%S"), city+"_"+algo+"_"+str(hvac_control_strategy)+"_"+str(repeat_time), co_sim.total_people_count)

                    end_time = datetime.now()
                    used_time = end_time-start_time
                    current_simulation_iteration += 1
                    avg_time = used_time/current_simulation_iteration
                    total_time = avg_time * total_simulation_iteration
                    required_time = total_time - used_time
                    sleep(1)
                    print(Fore.CYAN + Back.MAGENTA + "total time" + str(total_time) + Style.RESET_ALL)
                    print(Fore.CYAN + Back.MAGENTA + "used time" + str(used_time) + Style.RESET_ALL)
                    print(Fore.CYAN + Back.MAGENTA + "require time" + str(required_time) + Style.RESET_ALL)

                    print("Done:" + city+"_"+algo+"_"+str(hvac_control_strategy) + "\n\n\n")

                    # is_finished = True
                    # while is_finished:
                    #     sim_time = datetime(2010, 1, 1) + timedelta(seconds=co_sim.time)


if __name__ == "__main__":
    main()
