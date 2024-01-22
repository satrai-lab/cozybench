from pyfmi import load_fmu
from datetime import datetime, timedelta


class CoSimulation:
    input = {}
    output = {}

    def __init__(self, model_path, start_date: datetime, end_date: datetime):
        """

        :param model_path: str, path to the the fmu model
        :param start_date: datetime, start date
        :param end_date: datetime, end date
        """
        ep_time_step = 2
        # num_step = (end_date - start_date).days * 24 * ep_time_step

        beginning_date = datetime(start_date.year, 1, 1)

        self.current_second = (start_date - beginning_date).days * 24*60*60
        self.finish_second = (end_date - beginning_date).days * 24*60*60

        self.second_per_step = (60/ep_time_step) * 60
        self.fmu_model = load_fmu(model_path)
        self.fmu_model.initialize(self.current_second, self.finish_second, stop_time_defined=True)

    def simulate(self, inputs: dict, outputs: list):
        """

        :param inputs: dict, input parameters and values
        :param outputs: list, output parameter names
        :return: bool, success or not (is co-sim finished)
        """
        if self.current_second > self.finish_second:
            self.fmu_model.reset()
            return False

        # # TODO: Occupancy
        # for i in range(6):
        #     inputs["sch_occ_"+str(i+1)] = 0

        # print(inputs)

        for key, value in inputs.items():
            self.fmu_model.set(key, float(value))
        res = self.fmu_model.do_step(current_t=self.current_second, step_size=self.second_per_step, new_step=True)

        for param in outputs:
            self.output[param] = self.fmu_model.get(param)

        self.current_second += self.second_per_step

        return True
