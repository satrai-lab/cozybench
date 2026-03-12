from energyplus_api_helpers.import_helper import EPlusAPIHelper
from pathlib import Path
import csv

# Initialize the API
ep_path = Path(r'D:\Programming\EnergyPlus\EnergyPlusV23-2-0')
e = EPlusAPIHelper(ep_path)
api = e.get_api_instance()
handles = {}
log_data = []  # Used to store output data
previous_co2 = None

def co_simulation_callback(state):
    global previous_co2

    timestep = api.exchange.current_time(state)

    # Get the current temperature and CO2 concentration
    temp = api.exchange.get_variable_value(state, handles["temp"])
    co2_ppm = api.exchange.get_variable_value(state, handles["co2"])

    # Compute the schedule value to simulate device CO2 absorption intensity
    print("value:")
    schedule_value = float(input())

    # Set the schedule actuator value
    api.exchange.set_actuator_value(state, handles["sink_schedule"], schedule_value)

    # Compute delta CO2
    if previous_co2 is None:
        delta_co2 = 0.0
    else:
        delta_co2 = co2_ppm - previous_co2
    previous_co2 = co2_ppm

    # Record data
    log_data.append({
        "Time (hr)": round(timestep, 2),
        "Temp (°C)": round(temp, 2),
        "CO2 (ppm)": round(co2_ppm, 2),
        "Schedule": round(schedule_value, 2),
        "ΔCO2 (ppm)": round(delta_co2, 2)
    })

    print(f"Time={timestep:.2f}h | Temp={temp:.2f}°C | CO2={co2_ppm:.1f}ppm | Schedule={schedule_value:.2f} | ΔCO2={delta_co2:.1f}")

def simulation_main():
    def on_ready(state):
        # Get variable handles
        handles["temp"] = api.exchange.get_variable_handle(state, "Zone Mean Air Temperature", "Thermal Zone 1")
        handles["co2"] = api.exchange.get_variable_handle(state, "Zone Air CO2 Concentration", "Thermal Zone 1")

        # Get the schedule actuator handle that controls CO2 sink intensity
        handles["sink_schedule"] = api.exchange.get_actuator_handle(
            state,
            "Schedule:Constant",
            "Schedule Value",
            "MyCO2SinkSchedule"
        )

    # Register callback functions
    api.runtime.callback_begin_system_timestep_before_predictor(sim_state, co_simulation_callback)
    api.runtime.callback_begin_zone_timestep_after_init_heat_balance(sim_state, on_ready)

    # Run the simulation
    api.runtime.run_energyplus(sim_state, ["-r", "-w", weather_path, "-d", "output", idf_path])

    # Save results to CSV after the simulation completes
    output_path = Path("CO2_absorption_test/co2_absorption_log.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Time (hr)", "Temp (°C)", "CO2 (ppm)", "Schedule", "ΔCO2 (ppm)"])
        writer.writeheader()
        writer.writerows(log_data)
    print(f"\n✅ Results saved to: {output_path.resolve()}")

# Start the simulation
idf_path = "CO2_absorption_test/in.idf"
weather_file_mapping = {
    "mumbai": "models/weathers/mumbai",
    "la": "models/weathers/la",
    "paris": "models/weathers/paris",
    "scranton": "models/weathers/scranton"
}
weather_path = weather_file_mapping["paris"] + ".epw"
sim_state = api.state_manager.new_state()

simulation_main()
