from pathlib import Path
from energyplus_api_helpers.import_helper import EPlusAPIHelper
from datetime import datetime, timedelta
import re

from result_collector import Result


class CoSimulation:
    ep_path = Path(r'D:\Programming\EnergyPlus\EnergyPlusV22-2-0')

    def __init__(self, model_path, start_date: datetime, end_date: datetime, input_param: dict, output_param: dict,
                 sensation_collector: callable, sensation_aggregator: callable, hvac_controller: callable,
                 result: Result,
                 update_loss, epw_file_path, turn_off_when_empty, weather_path, hvac_control_strategy):
        """

        :param model_path: str, path to the energyplus model
        :param start_date: datetime, start date
        :param end_date: datetime, end date
        :param input_param: dict, input actuators, e.g., {sp1: [Zone Temperature Control, Cooling Setpoint, TZ1]}
        :param output_param: dict, output variables, e.g., {temp1: [Zone Air Temperature, Thermal Zone 1]}
        :param sensation_collector: callable function, generate sensation from occupants.
        """

        self.total_people_count = 0

        self.model_path = model_path
        self.start_date = start_date
        self.end_date = end_date
        # self.ep_input_param_variable = {}
        # self.ep_input_param_actuator = {}
        self.ep_input_param = input_param
        self.ep_output_param = output_param
        self.sensation_collector = sensation_collector
        self.sensation_aggregator = sensation_aggregator
        self.get_atc = sensation_aggregator.get_atc
        self.hvac_controller = hvac_controller
        self.evaluation_results = result
        self.update_loss = update_loss

        self.ep_output_value = {key: None for key in output_param.keys()}

        self.e = EPlusAPIHelper(self.ep_path)
        self.api = self.e.get_api_instance()
        self.got_handles = False
        self.handle_variables = {}
        self.handle_actuators = {}
        self.sim_time = start_date

        self.epw_file_path = epw_file_path
        self.turn_off_when_empty = turn_off_when_empty
        self.weather_path = weather_path
        self.hvac_control_strategy = hvac_control_strategy

    def run(self):
        state = self.api.state_manager.new_state()
        self.api.runtime.callback_begin_zone_timestep_after_init_heat_balance(state, self.callback_function)
        self.api.runtime.run_energyplus(state, [
            '-a',
            '-w', self.weather_path,
            '-d', self.e.get_temp_run_dir(),
            self.model_path
        ])

    def callback_function(self, state):
        # If handles haven't been set
        if not self.got_handles:
            if not self.api.exchange.api_data_fully_ready(state):
                return
            for key, value in self.ep_input_param.items():
                self.handle_actuators[key] = self.api.exchange.get_actuator_handle(state, value[0], value[1], value[2])
            for key, value in self.ep_output_param.items():
                self.handle_variables[key] = self.api.exchange.get_variable_handle(state, value[0], value[1])

            # if got handles successfully
            flag_invalid_handle = False
            key_to_remove = []
            for key, handle in self.handle_variables.items():
                if handle == -1:
                    if "ec" in key:
                        key_to_remove.append(key)
                    else:
                        print("***Invalid handles " + key + ", check spelling and sensor/actuator availability")
                        flag_invalid_handle = True
            for key in key_to_remove:
                del self.handle_variables[key]
            for key, handle in self.handle_actuators.items():
                if handle == -1:
                    print("***Invalid handles " + key + ", check spelling and sensor/actuator availability")
                    flag_invalid_handle = True

            if flag_invalid_handle:
                raise Exception("invalid handles detected")

            self.got_handles = True

        if self.api.exchange.warmup_flag(state):
            return

        # update sim_time
        month = self.api.exchange.month(state)
        day = self.api.exchange.day_of_month(state)
        hour = self.api.exchange.hour(state)
        minute = self.api.exchange.minutes(state)
        if 20 <= minute <= 40:
            minute = 30
        else:
            minute = 0
        self.sim_time = self.sim_time.replace(month=month, day=day, hour=hour, minute=minute)

        # print(self.sim_time)

        season = None
        if self.api.exchange.month(state) in [6, 7, 8]:
            season = "clg"
            self.sensation_aggregator.mode = "clg"
        elif self.api.exchange.month(state) in [1, 2, 12]:
            season = "htg"
            self.sensation_aggregator.mode = "htg"

        if season is not None and 8 <= self.api.exchange.hour(state) <= 19:

            # get values of variables
            indoor_temp = {}
            for variable, handle in self.handle_variables.items():
                variable_value = self.api.exchange.get_variable_value(state, handle)
                self.ep_output_value[variable] = variable_value
                if "temp" in variable:
                    if variable.lstrip("temp").isdigit():
                        indoor_temp[int(variable.lstrip("temp"))] = variable_value

            # get indoor temperature
            estimated_sensation, real_sensation = self.sensation_collector(self.sim_time, indoor_temp)

            for key, value in real_sensation.items():
                self.total_people_count += len(value)

            group_thermal_sensation = {}
            new_set_point = {}
            for key, value in estimated_sensation.items():
                group_thermal_sensation[key] = self.get_atc(value, self.ep_output_value)

            # self.api.exchange.set_actuator_value(state, self.handle_actuators['sch_htg_1'], 20)

            for actuator, handle in self.handle_actuators.items():
                if season in ['htg', 'clg']:
                    if season in actuator:
                        num_space = int(re.search(r'\d.*', actuator).group(0))
                        if self.turn_off_when_empty:
                            if group_thermal_sensation[num_space] == 4:
                                if season == 'htg':
                                    setpoint_when_empty = 19
                                else:
                                    setpoint_when_empty = 28
                                self.api.exchange.set_actuator_value(state, handle, setpoint_when_empty)
                            elif group_thermal_sensation[num_space]:
                                set_point = self.hvac_controller(indoor_temp[num_space], group_thermal_sensation[num_space], self.hvac_control_strategy)
                                if set_point > 30:
                                    set_point = 30
                                elif set_point < 17:
                                    set_point = 17
                                self.api.exchange.set_actuator_value(state, handle, set_point)

                        else:
                            self.api.exchange.set_actuator_value(state, handle, 23)
                else:
                    if "clg" in actuator:
                        self.api.exchange.set_actuator_value(state, handle, 40)
                    elif "htg" in actuator:
                        self.api.exchange.set_actuator_value(state, handle, 0)

            self.update_loss(estimated_sensation, group_thermal_sensation)

            # Update results
            self.evaluation_results.update_itc(real_sensation, group_thermal_sensation)

            energy_cooling = 0
            energy_heating = 0
            energy_fan = 0
            for key, value in self.ep_output_value.items():
                if value is None:
                    continue
                if "ec" in key:
                    if "clg" in key:
                        energy_cooling += value
                    elif "htg" in key:
                        energy_heating += value
                    elif "fan" in key:
                        energy_fan += value
            self.evaluation_results.add_consumption(energy_cooling,
                                                    energy_heating, energy_fan, season)

            if season == "clg":
                self.evaluation_results.update_co2_emission(energy_cooling, self.sim_time)
            # elif season is "htg":
            #     self.evaluation_results.update_co2_emission(energy_heating + energy_fan, self.sim_time)

        else:
            for actuator, handle in self.handle_actuators.items():
                if "clg" in actuator:
                    self.api.exchange.set_actuator_value(state, handle, 40)
                elif "htg" in actuator:
                    self.api.exchange.set_actuator_value(state, handle, 0)

    # def is_date_between(self, year: int, month: int, day: int):
    #     """
    #     check if current date is between two datetime
    #
    #     :param year:
    #     :param month:
    #     :param day:
    #     :return: A Boolean value
    #     """
    #     given_date = datetime(year, month, day)
    #     return self.start_date <= given_date <= self.end_date
