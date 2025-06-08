import pandas as pd
from datetime import datetime
import pytz
import numpy as np
import os


def _get_itc_increment(votes: dict, atc):
    itc = 0
    for p_id, v in votes.items():
        itc += abs(v - atc)
    return itc


class Result:

    his_ec = {}
    pointer_ec = 0
    his_itc = {}
    pointer_itc = 0
    his_tce = {}
    pointer_tce = 0

    carbon_file_mapping = {"mumbai": "models/carbon_intensity/IN-WE_2023_hourly.csv",
                           "la": "models/carbon_intensity/US-CAL-CISO_2023_hourly.csv",
                           "paris": "models/carbon_intensity/FR_2023_hourly.csv",
                           "scranton": "models/carbon_intensity/US-MIDA-PJM_2023_hourly.csv"}

    time_zone = {"mumbai": "Asia/Kolkata",
                           "la": "America/Los_Angeles",
                           "paris": "Europe/Paris",
                           "scranton": "America/New_York"}

    def __init__(self, occupants, city):
        # TODO user define region from input
        self.ec_clg = 0
        self.ec_htg = 0
        self.ec_fan = 0
        self.itc = 0
        self.tce = 0
        self.carbon_emission = 0
        self.occupants = occupants

        self.local_time_zone = pytz.timezone(self.time_zone[city])
        self.path_intensity_file = self.carbon_file_mapping[city]

        self.carbon_intensity = pd.read_csv(self.path_intensity_file)
        self.carbon_intensity['Datetime (UTC)'] = pd.to_datetime(self.carbon_intensity['Datetime (UTC)'])

    def add_consumption(self, consumption_clg, consumption_htg, consumption_fan, demand):
        if demand == "clg":
            self.ec_clg += consumption_clg
        else:
            self.ec_htg += consumption_htg
        self.ec_fan += consumption_fan

    def update_itc(self, votes: dict, atc: dict):
        for space_id, votes_space in votes.items():
            if atc[space_id] == 4 or len(votes_space) == 0:
                continue
            self.itc += _get_itc_increment(votes_space, atc[space_id])

    def update_co2_emission(self, energy_consumption, date):
        local_dt = self.local_time_zone.localize(date)
        utc_dt = local_dt.astimezone(pytz.utc)
        utc_dt = np.datetime64(utc_dt)
        row = self.carbon_intensity.loc[self.carbon_intensity['Datetime (UTC)'] == utc_dt]
        if not row.empty:
            self.carbon_emission += row['Carbon Intensity gCO₂eq/kWh (direct)'].values[0] * energy_consumption
        else:
            data_sorted = self.carbon_intensity.sort_values(by='Datetime (UTC)')
            # find the nearest one before
            nearest_before = data_sorted[data_sorted['Datetime (UTC)'] <= utc_dt]
            nearest_before = nearest_before.iloc[-1] if not nearest_before.empty else None

            # find the nearest one after
            nearest_after = data_sorted[data_sorted['Datetime (UTC)'] > utc_dt]
            nearest_after = nearest_after.iloc[0] if not nearest_after.empty else None

            if nearest_before is not None and nearest_after is not None:

                avg_intensity = (nearest_before['Carbon Intensity gCO₂eq/kWh (direct)'] + nearest_after[
                    'Carbon Intensity gCO₂eq/kWh (direct)']) / 2
                self.carbon_emission += avg_intensity * energy_consumption
            elif nearest_before is not None:

                self.carbon_emission += nearest_before['Carbon Intensity gCO₂eq/kWh (direct)'] * energy_consumption
            elif nearest_after is not None:

                self.carbon_emission += nearest_after['Carbon Intensity gCO₂eq/kWh (direct)'] * energy_consumption
            else:
                raise Exception("Cannot find carbon intensity data")

    def reset(self):
        self.ec_clg = 0
        self.itc = 0

    def save_result(self, timestamp, identify, total_itc_count):
        current_time = datetime.now()
        # timestamp_str = current_time.strftime("%Y%m%d%H%M%S")
        result_path = "./results/" + f"result_{timestamp}"
        if not os.path.exists(result_path):
            try:
                os.mkdir(result_path)
                print(f"Result Directory '{result_path}' created successfully.")
            except OSError as error:
                print(f"Error creating directory: {error}")

        with open(result_path+"./result-"+identify+".txt", "a") as file:
            file.write("energy cooling (kwh): \n")
            file.write(str(self.ec_clg / 3600000) + "\n")
            file.write("energy heating (kwh): \n")
            file.write(str(self.ec_htg / 3600000) + "\n")
            file.write("energy fan (kwh): \n")
            file.write(str(self.ec_fan / 3600000) + "\n")
            file.write("energy total (kwh): \n")
            file.write(str((self.ec_clg+self.ec_htg+self.ec_fan) / 3600000) + "\n")
            file.write("co2:\n")
            file.write(str(self.carbon_emission) + "\n")
            file.write("itc: \n")
            file.write(str(self.itc) + "\n")
            file.write("avg itc: \n")
            file.write(str(self.itc/total_itc_count) + "\n")
            file.write("tce:\n")
            for loss in self.occupants.loss.values():
                file.write(str(loss) + "\n")
            file.write("std tce: \n")
            file.write(str(np.std(list(self.occupants.loss.values()))) + "\n")



