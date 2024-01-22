import os.path
import random
from datetime import datetime
from strategies import get_next_loss
from knn import knn_train
import pandas as pd

from sklearn.impute import SimpleImputer


class Participant:
    """
    Note:   p_id starts from 1,
            space_num starts from 1
    """
    num = 0
    location = {}  # -1 means not inside
    # thermal_profile = {}  # from 0 to 2
    itc_loss = {}
    loss = {}
    occ_profile = {}

    def __init__(self, space_num, occ_config, history_data, pattern, path_trajectory):
        """

        :param occ_config: configuration file of the occupants
        :param history data of the occupants, for training KNN model
        :param pattern: scenario_pattern, decides the voting sys
        :param path_trajectory: path to the trajectory folder
        """

        self.path_trajectory = path_trajectory
        self.space_num = space_num
        self.config_occ_profile(occ_config)
        self.history_data = history_data

        self.all_params = ['ta', 'activity_20', 'age', 'gender', 'weight_level']
        self.pattern_system = int(pattern[1])
        self.pattern_mode = int(pattern.split("_")[1])
        # if pattern_system == 1 or pattern_mode == 100:
        #     self.knn_model = knn_train(params)
        if self.pattern_system == 2 and self.pattern_mode != 100:
            if self.pattern_mode == 75:
                self.knn_params = self.all_params[0:4]
            elif self.pattern_mode == 50:
                self.knn_params = self.all_params[0:3]
            elif self.pattern_mode == 25:
                self.knn_params = self.all_params[0:2]
        else:
            self.knn_params = self.all_params
        self.knn_model = knn_train(self.knn_params)
        self.knn_model_all_params = knn_train(self.all_params)

        # self.space_num = 0
        # person_id = 1
        # for room in occ.keys():
        #     for i in range(occ[room]):
        #         rand = random.randint(0, 99)
        #         if rand < dis[0]:
        #             preference = 0
        #         elif rand < dis[0] + dis[1]:
        #             preference = 1
        #         else:
        #             preference = 2
        #
        #         self.thermal_profile[person_id] = preference
        #         dis[preference] += 1
        #         self.loss[person_id] = 0
        #         person_id += 1
        #         self.location[person_id] = -1
        # self.num = person_id

    # def train_KNN(self, params):

    def config_occ_profile(self, config_file):
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
        f_p = open(os.path.join(self.path_trajectory, str(time.month) + ".txt"))
        # f_p = open(self.path_trajectory + str(time.month) + ".txt")
        line = f_p.readline()
        while line:
            data = line.strip().split(";")
            if data[1][4:] == str(time)[4:]:
                people = data[-1].split(",")[:-1]
                for p_id in people:
                    self.location[int(p_id)] = int(data[0])
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

        # real sensation
        real_votes = {}
        for s in range(1, self.space_num + 1):
            real_votes[s] = {}
        for index in range(1, self.num + 1):
            if self.location[index] > -1:
                knn_data = {}
                for p in self.all_params:
                    if p == "activity_20":
                        knn_data[p] = [random_activity]
                    elif p == "ta":
                        knn_data[p] = [temp[self.location[index]]]
                    else:
                        knn_data[p] = [self.occ_profile[index][p]]

                knn_data = pd.DataFrame(knn_data)  # Replace with your own data

                predicted_comfort = self.knn_model_all_params.predict(knn_data)

                real_votes[self.location[index]][index] = predicted_comfort[0].round()

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

                # imputer = SimpleImputer(strategy='mean')
                knn_data = pd.DataFrame(knn_data)  # Replace with your own data
                # knn_data[self.knn_params] = imputer.transform(knn_data[self.knn_params])

                predicted_comfort = self.knn_model.predict(knn_data)

                votes[self.location[index]][index] = predicted_comfort[0].round()

                # print(f"Predicted Thermal Comfort: {predicted_comfort[0]:.2f}")

                # if temp[self.location[index]] < 18:
                #     votes[self.location[index]][index] = -3
                # elif temp[self.location[index]] > 31:
                #     votes[self.location[index]][index] = 3
                # else:
                #     votes[self.location[index]][index] = voteSheet[round(temp[self.location[index]])][
                #         self.thermal_profile[index]]
                #
                # # add randomness
                # rand = random.randint(0, 99)
                # if rand < 15:
                #     votes[self.location[index]][index] += 1
                # elif rand < 30:
                #     votes[self.location[index]][index] -= 1
                # elif rand < 40:
                #     votes[self.location[index]][index] += 2
                # elif rand < 50:
                #     votes[self.location[index]][index] -= 2

                if votes[self.location[index]][index] < -3:
                    votes[self.location[index]][index] = -3
                if votes[self.location[index]][index] > 3:
                    votes[self.location[index]][index] = 3

        return votes, real_votes

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
