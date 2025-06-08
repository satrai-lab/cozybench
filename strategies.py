import math
from collections import Counter

import numpy as np
import pandas as pd


class SensationAggregator:
    def __init__(self, strategy, occupants):
        self.strategy = strategy
        self.occupant = occupants
        self.mode = None

    def get_atc(self, thermal_sensation: dict, sim_output: dict):

        if self.mode is None:
            raise Exception("not clear what is the season!")

        if len(thermal_sensation) == 0:
            return 4
        if self.strategy == "const":
            return 0
        elif self.strategy == "majority":
            return majority(thermal_sensation)
        elif self.strategy == "drift":
            return drift(thermal_sensation, self.mode)
        elif self.strategy == "fair":
            return fairness(thermal_sensation, self.occupant.loss)


def majority(thermal_sensation: dict):
    """
    Aggregate the thermal_sensation with Majority Approach
    :param thermal_sensation: dict, thermal_sensation of each person in one space
    :return: int, the aggregated vote which is from -3 to 3
    """

    counter = Counter(list(thermal_sensation.values()))
    return counter.most_common(1)[0][0]


# def thermal_comfort_provision_system(occupants: list, building, space):
#     """
#     A Thermal Comfort Provision System that takes the status of occupants and building as inputs to generate an actual
#     HVAC control action for the space.
#     :param occupants: A list of Occupant objects representing the current state of occupants in the current space
#     :param building: A Building object with the current state of the building
#     :param space: A Space object includes the environment of the space for HVAC controlling
#     :return: A float value for the set point of the HVAC system for the current space.
#     """
#
#     # Sensation Collector that estimates thermal sensations (from -3 to 3) of occupants
#     for occ in occupants:
#         occ.thermal_sensation = generate_random_sensation(occ)
#
#     # Sensation Aggregator that aggregate sensations for HVAC control
#     # accumulate all thermal sensations of occupants as the "group thermal sensation"
#     counter = sum(list(occ.thermal_sensation for occ in occupants))
#
#     # HVAC control that translate "group thermal sensation" to HVAC control actions
#     # if "group thermal sensation" is larger than 0, people feel hot. Reduce the set point by 2 degrees
#     if counter > 0:
#         return space.temperature - 2
#     else:
#         return space.temperature + 2



def drift(thermal_sensation: dict, mode):
    """
    Aggregate the thermal_sensation with Drift Approach
    :param thermal_sensation: dict, thermal_sensation of each person in one space
    :param mode: str, "clg" or "htg"
    :return: int, the aggregated vote which is from -3 to 3
    """

    flag = True if mode == "htg" else False

    avg = round(sum(thermal_sensation.values()) / len(thermal_sensation))
    # Drift -- subtract 1 (feel cold) from avg for saving cooling energy, vice versa
    avg = avg - 1 if flag else avg + 1
    return max(-3, min(avg, 3))


def fairness(thermal_sensation: dict, loss: dict):
    """
    Aggregate the thermal_sensation with Fairness Approach
    -- Select the vote that decrease the total Loss and the greatest Loss
    :param thermal_sensation: dict, thermal_sensation of each person in one space
    :param loss: dict, loss of Participant (everyone?)
    :return: int, the aggregated vote which is from -3 to 3
    """

    max_loss_pid = None
    max_loss = -float('inf')

    for p_id in thermal_sensation.keys():
        if loss[p_id] > max_loss:
            max_loss = loss[p_id]
            max_loss_pid = p_id

    # add the vote of the person with max loss +- 1 in the list
    atc_list = [n for n in [thermal_sensation[max_loss_pid], thermal_sensation[max_loss_pid] - 1,
                            thermal_sensation[max_loss_pid] + 1] if -3 <= n <= 3]

    # pick one from the list that makes the max loss and the total loss decrease
    min_gross_abs_loss = float('inf')
    selected_atc = 0
    # selected_loss = get_next_loss(thermal_sensation, loss, selected_atc)

    for atc in atc_list:
        next_loss = get_next_loss(thermal_sensation, loss, atc)
        gross_abs_loss = _get_gross_abs_loss(next_loss)
        if next_loss[max_loss_pid] < max_loss and gross_abs_loss < min_gross_abs_loss:
            min_gross_abs_loss = gross_abs_loss
            selected_atc = atc
            # selected_loss = next_loss

    return selected_atc


def mpc_model(thermal_sensation: dict, atc, loss, outdoor_temp, current_temp):
    itc = 0
    tce = 0

    for p_id, v in thermal_sensation.items():
        itc += abs(v - atc)

    new_loss = get_next_loss(thermal_sensation, loss, atc)
    for p_id in thermal_sensation.keys():
        tce += abs(new_loss[p_id])

    ec_grade = outdoor_temp - generate_set_point(current_temp, atc)

    return itc, tce, ec_grade


def hybrid(thermal_sensation, loss: dict, outdoor_temp, current_temp):
    """
    Aggregate the thermal_sensation with Hybrid Approach
    :param current_temp:
    :param thermal_sensation: DICT, thermal_sensation of each person in one space
    :param loss: dict, loss of Participant (everyone?)
    :param outdoor_temp: double,
    :return: INT, the aggregated vote which is from -3 to 3
    """

    all_results = {}
    all_results_itc = []
    all_results_tce = []
    all_results_ecg = []

    for pid, l in loss.items():
        if l > 30 and pid in thermal_sensation.keys():
            return fairness(thermal_sensation, loss)

    for atc in range(-3, 4):
        itc, tce, ecg = mpc_model(thermal_sensation, atc, loss, outdoor_temp, current_temp)
        all_results[atc] = (itc, tce, ecg)
        all_results_itc.append(itc)
        all_results_tce.append(tce)
        all_results_ecg.append(ecg)

    atc_maj = majority(thermal_sensation)
    atc_drift = drift(thermal_sensation, True)
    atc_fairness = fairness(thermal_sensation, loss)

    # calculate scores
    min_score = float('inf')
    atc_min_score = 0
    # for atc in range(min(atc_maj, min(atc_fairness, atc_drift)), max(atc_maj, max(atc_fairness, atc_drift)) + 1):
    for atc in [atc_maj, atc_drift, atc_fairness]:
        z_itc = calculate_z_score(all_results[atc][0],
                                  all_results_itc)
        z_tce = calculate_z_score(all_results[atc][1],
                                  all_results_tce)
        z_ecg = calculate_z_score(all_results[atc][2],
                                  all_results_ecg)
        z_score = 1.5 * z_itc + 2 * z_tce + z_ecg
        if z_score < min_score:
            min_score = z_score
            atc_min_score = atc

    return atc_min_score


def get_next_loss(thermal_sensation, loss: dict, atc):
    """
    Calculate loss of all the persons if take this input atc
    Note: the thermal_sensation may include a part of people
    :param thermal_sensation: dict, thermal_sensation
    :param loss: dict, current loss
    :param atc: int, the aggregated thermal comfort to be taken
    :return: dict, extra loss of all persons
    """
    loss_new = loss
    avg_loss = 0

    if len(thermal_sensation) == 0:
        return loss_new

    # calculate the average loss
    for v in thermal_sensation.values():
        avg_loss += abs(atc - v)
    avg_loss /= len(thermal_sensation)

    # each add extra loss
    for key, value in thermal_sensation.items():
        # loss
        a = abs(atc - value)
        # extra loss
        b = a - avg_loss
        loss_new[key] = loss[key] + b

    return loss_new


def _get_gross_abs_loss(loss):
    gross_value = 0
    for value in loss.values():
        gross_value += abs(value)
    return gross_value


def calculate_z_score(double_value, data):
    """
    calculate the z-score of the double_value based on the data
    :param double_value:
    :param data:
    :return:
    """
    mean = sum(data) / len(data)
    std = (sum((x - mean) ** 2 for x in data) / len(data)) ** 0.5
    if std == 0:
        return abs(data[0] - double_value)
    z_score = (double_value - mean) / std
    return z_score


def generate_set_point(temp_current, atc_to_space, hvac_controller_strategy):
    # ["fixed_rule", "preference_estimation"]
    if hvac_controller_strategy =="fixed_rule":
        atc_abs = abs(atc_to_space)
        sign = atc_to_space / atc_abs if atc_to_space != 0 else 0

        if atc_abs == 0:
            return temp_current
        elif atc_abs == 1:
            return temp_current - (1 * sign)
        elif atc_abs == 2:
            return temp_current - (2 * sign)
        elif atc_abs == 3:
            return temp_current - (3 * sign)
        else:
            raise Exception("problem here in generate_set_point")
    elif hvac_controller_strategy == "preference_estimation":
        df = pd.read_csv('knn/ashrae_comfort_data.csv',  low_memory=False)
        df = df.dropna(subset=['ta', 'thermal_sensation', 'season'])
        return calculate_target_temperature(df, temp_current, atc_to_space)
    else:
        raise Exception("no such HVAC controller??")


def calculate_target_temperature(df, T_current, C_current):
    # Step 1: Extract comfort levels within the temperature range of T_current ± 1°C
    if C_current == 0:
        return T_current

    temp_range_df = df[(df['ta'] >= T_current - 0.5) & (df['ta'] <= T_current + 0.5)]

    if temp_range_df.empty:
        if C_current > 0:
            return T_current-2
        else:
            return T_current+2

    comfort_levels = temp_range_df['thermal_sensation']

    # Step 2: Calculate mean (μ) and standard deviation (σ) of the comfort levels
    mu = comfort_levels.mean()
    sigma = comfort_levels.std()

    if sigma == 0:
        if C_current > 0:
            return T_current - 2
        else:
            return T_current + 2

    # Step 3: Determine the position y in the Gaussian distribution for the current comfort level
    y = (C_current - mu) / sigma * -1

    # Step 4: Find the subset of data where users reported being comfortable (e.g., -0.5 ≤ sensation ≤ 0.5)
    comfortable_df = df[(df['thermal_sensation'] >= -0.5) & (df['thermal_sensation'] <= 0.5)]
    temp_deviation = abs(C_current)
    if C_current > 0:
        comfortable_df = comfortable_df[comfortable_df['ta'] < T_current]
    else:
        comfortable_df = comfortable_df[comfortable_df['ta'] > T_current]

    if comfortable_df.empty:
        raise ValueError("No comfortable data available in the dataset.")

    # Map the y value to a position within the comfortable_df
    comfortable_temperatures = comfortable_df['ta'].values
    comfortable_comfort_levels = comfortable_df['thermal_sensation'].values

    # Normalize the comfortable comfort levels to find the target position
    normalized_comfort_levels = (comfortable_comfort_levels - comfortable_comfort_levels.mean()) / comfortable_comfort_levels.std()

    # Find the temperature that corresponds to the y position
    # We use interpolation to map the y value to the corresponding temperature
    target_temperature = np.interp(y, normalized_comfort_levels, comfortable_temperatures)
    y_normalized = (y + 3) / 6
    # print(y)
    target_temperature = np.percentile(comfortable_temperatures, y_normalized * 100)

    return target_temperature


# if __name__ == '__main__':
#     print(generate_set_point(20, -2, 22, "preference_estimation"))