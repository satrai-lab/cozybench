import os.path
import random
from datetime import datetime
from strategies import get_next_loss
from comfort_collector import knn_train
import pandas as pd


class Participant:
    """
    Note:   p_id starts from 1,
            space_num starts from 1
    """
    num = 0
    location = {}  # -1 means not inside
    itc_loss = {}
    loss = {}
    occ_profile = {}

    def __init__(self, space_num, occ_config, history_data, pattern, path_trajectory, collection_strategy):
        """

        :param occ_config: configuration file of the occupants
        :param history_data: history data of the occupants, for training the comfort collector
        :param pattern: scenario_pattern, decides the voting sys
        :param path_trajectory: path to the trajectory folder
        """

        self.collection_strategy = collection_strategy
        self.path_trajectory = path_trajectory
        self.space_num = space_num
        self.history_data = history_data
        if str(occ_config).isdigit():
            self.has_profile = False
            self.config_occ_profile(occ_config)
        else:
            self.has_profile = True
            self.config_occ_profile(occ_config)

        if pattern is not None:
            self.all_params = ['ta', 'activity_20', 'age', 'gender', 'weight_level', "preference"]
            self.pattern_system = int(pattern[1])
            self.pattern_mode = int(pattern.split("_")[1])
            if self.pattern_system == 2 and self.pattern_mode != 100:
                if self.pattern_mode == 75:
                    self.knn_params = self.all_params[0:4]
                elif self.pattern_mode == 50:
                    self.knn_params = self.all_params[0:3]
                elif self.pattern_mode == 25:
                    self.knn_params = self.all_params[0:2]
            else:
                self.knn_params = self.all_params[0:5]
            self.knn_model = knn_train(self.knn_params)
            self.knn_model_all_params = knn_train(self.all_params[0:5])

        else:
            self.pattern_system = 0
            self.pattern_mode = 0

    def config_occ_profile(self, config_file):
        if self.has_profile:
            f_config = open(config_file, "r")
            line = f_config.readline()
            params = line.strip().split(",")
            line = f_config.readline()

            occ_id = 1
            while line:
                data = line.strip().split(",")
                person = {}
                for i in range(len(params)):
                    person[params[i]] = data[i]
                self.occ_profile[occ_id] = person

                self.itc_loss[occ_id] = 0
                self.loss[occ_id] = 0
                self.location[occ_id] = -1

                occ_id += 1
                line = f_config.readline()
            f_config.close()
            self.num = occ_id
        else:
            occ_id = 1
            # now config_file is the number of people, history_data is distribution like [30, 40, 30]
            cold_preferred = self.history_data[0]
            neutral_preferred = self.history_data[1]
            warm_preferred = self.history_data[2]
            for i in range(config_file):
                random_number = random.uniform(0, 100)
                if random_number < cold_preferred:
                    self.occ_profile[occ_id] = 0
                elif random_number < cold_preferred+neutral_preferred:
                    self.occ_profile[occ_id] = 1
                else:
                    self.occ_profile[occ_id] = 2
                self.itc_loss[occ_id] = 0
                self.loss[occ_id] = 0
                self.location[occ_id] = -1
                occ_id += 1
            self.num = occ_id

    def clean(self):
        """
        Clean participants' losses and locations.
        Used before changing to another algo while remaining participants' configuration.
        """
        for person_id in self.loss.keys():
            self.loss[person_id] = 0
            self.location[person_id] = -1

    def _locate(self, time: datetime):
        """
        Update people's current location
        :param time: datetime, simulation time
        """

        # clean the old location to be -1
        for p_id in range(self.num):
            self.location[p_id + 1] = -1
        f_p = open(os.path.join(self.path_trajectory, str(1) + ".txt"))
        # f_p = open(self.path_trajectory + str(time.month) + ".txt")
        line = f_p.readline()
        while line:
            data = line.strip().split(";")
            if data[1][4:] == str(time)[4:]:
                people = data[-1].split(",")[:-1]
                for p_id in people:
                    if int(data[0]) >120:
                        self.location[int(p_id)] = random.randint(1, 120)
                    else:
                        self.location[int(p_id)] = int(data[0])
                    # self.location[int(p_id)] = 1
            line = f_p.readline()

    def vote(self, time: datetime, temp: dict):
        """
        Votes generation by the temperature
        :param time: datetime, used to locate people
        :param temp: dictionary, indoor temperature of each space
        :return: dictionary, a dictionary of people's votes
        """

        self._locate(time)
        random_activity = random.randint(1, 2)
        # ["historical_based", "prior_knowledge"]

        # real_votes = {}
        # for s in range(1, self.space_num + 1):
        #     real_votes[s] = {}
        # for index in range(1, self.num + 1):
        #     if self.location[index] > -1:
        #         knn_data = {}
        #         for p in self.all_params[0:5]:
        #             if p == "activity_20":
        #                 knn_data[p] = [random_activity]
        #             elif p == "ta":
        #                 knn_data[p] = [temp[self.location[index]]]
        #             else:
        #                 knn_data[p] = [self.occ_profile[index][p]]
        #
        #         knn_data = pd.DataFrame(knn_data)  # Replace with your own data
        #
        #         predicted_comfort = self.knn_model_all_params.predict(knn_data)
        #
        #         real_votes[self.location[index]][index] = predicted_comfort[0].round()

        if self.collection_strategy == "historical_based":
            votes = {}
            for s in range(1, self.space_num + 1):
                votes[s] = {}
            # collect votes based on indoor temperature where people locate
            for index in range(1, self.num + 1):
                if self.location[index] > -1:
                    if self.pattern_system == 1:
                        random_number = random.randint(1, 100)
                        if random_number > self.pattern_mode:
                            continue

                    knn_data = {}
                    for p in self.knn_params:
                        if p == "activity_20":
                            knn_data[p] = [random.randint(1, 2)]
                        elif p == "ta":
                            knn_data[p] = [temp[self.location[index]]]
                        else:
                            knn_data[p] = [self.occ_profile[index][p]]

                    knn_data = pd.DataFrame(knn_data)  # Replace with your own data

                    predicted_comfort = self.knn_model.predict(knn_data)

                    votes[self.location[index]][index] = predicted_comfort[0].round()

                    if votes[self.location[index]][index] < -3:
                        votes[self.location[index]][index] = -3
                    if votes[self.location[index]][index] > 3:
                        votes[self.location[index]][index] = 3

        elif self.collection_strategy == "prior_knowledge":
            vote_sheet = {
                0: {
                    16: -3, 17: -3, 18: -3, 19: -3, 20: -2, 21: -2, 22: -1, 23: -1, 24: 0, 25: 0, 26: 0, 27: 1, 28: 1, 29: 2, 30: 2
                },
                1: {
                    16: -3, 17: -3, 18: -2, 19: -2, 20: -1, 21: -1, 22: 0, 23: 0, 24: 0, 25: 0, 26: 1, 27: 1, 28: 2, 29: 2, 30: 3
                },
                2: {
                    16: -3, 17: -2, 18: -2, 19: -1, 20: -1, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 1, 27: 2, 28: 3, 29: 3, 30: 3
                }
            }
            votes = {}
            for s in range(1, self.space_num + 1):
                votes[s] = {}

            for index in range(1, self.num + 1):
                # if person index is in the building
                if self.location[index] > 0:
                    temperature = round(temp[self.location[index]])
                    if temperature <= 16:
                        comfort = -3
                    elif temperature > 30:
                        comfort = 3
                    else:
                        comfort = vote_sheet[self.occ_profile[index]][temperature]
                    votes[self.location[index]][index] = comfort
        else:
            raise Exception("no thermal comfort collection??")
        return votes, votes

    def update_loss(self, votes: dict, atc: dict):
        """

        :param votes: dict, votes of everyone
        :param atc: dict, atc of every space
        :return:
        """
        new_loss = {}
        for room_id, value in atc.items():
            if value == 4:
                continue
            next_loss = get_next_loss(votes[room_id], self.loss, atc[room_id])
            for p_id, loss in next_loss.items():
                if p_id not in new_loss.items():
                    new_loss[p_id] = loss

        for p_id, loss in new_loss.items():
            self.loss[p_id] = loss

        for room_id in votes.keys():
            for p_id, vote in votes[room_id].items():
                self.itc_loss[p_id] += abs(vote - atc[room_id])
