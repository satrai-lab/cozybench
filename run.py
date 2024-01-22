import os
import subprocess
import time
import sys
import json
from datetime import datetime, timedelta
from participant import Participant
from fmu import CoSimulation
from strategies import get_atc, generate_set_point
from result import Result


def main(argv):
    """

    :param argv: include [path_fmu, strategy, scenario_pattern, path_profile, path_trajectory, history_data]
        scenario pattern is like e.g. S1_25 which means 25% system 1
        Sys1 is people voting, 25% means 25% people would love to vote
        Sys2 is device sensing, 25% means 25% parameters (age, gender, weight, activity) are used
    :return:
    """

    result = Result()
    space = 6
    # total number of how many times all the people got involved in the system
    total_num = 0

    model_path = argv[0]
    algo = argv[1]
    pattern = argv[2]
    occ_config = argv[3]
    trajectory = argv[4]
    history_data = argv[5]
    timestamp = argv[6]

    # define participant
    participant = Participant(space, occ_config, history_data, pattern, trajectory)
    participant.clean()

    # run simulation
    output_param = ['temp_1', 'temp_2', 'temp_3', 'temp_4', 'temp_5', 'temp_6',
                    'ec_cooling_coil', 'ec_heating_coil', 'temp_out']

    start_date = datetime.strptime("2010-01-01", "%Y-%m-%d")
    end_date = datetime.strptime("2010-12-30", "%Y-%m-%d")

    co_sim = CoSimulation(model_path, start_date, end_date)

    result_dict = {}

    is_finish = True
    while is_finish:

        sim_time = datetime(2010, 1, 1) + timedelta(seconds=co_sim.fmu_model.time)

        season = None
        if sim_time.month in [6, 7, 8]:
            season = "clg"
        elif sim_time.month in [1, 2, 12]:
            season = "htg"

        input_param = {}
        # do simulation between 8 and 19h
        if season is not None and 8 <= sim_time.hour <= 19:

            # get temperature of each space
            indoor_temp = {}
            for i in range(1, space + 1):
                indoor_temp[i] = co_sim.output['temp_' + str(i)][0]

            print("indoor temperature:\t" + str(indoor_temp[1])[:4])

            votes_by_room, real_votes_by_room = participant.vote(sim_time, indoor_temp)
            for values in real_votes_by_room.values():
                total_num += len(values)

            # occupancy:
            for i in range(1, space + 1):
                # input_param['sch_occ_' + str(i)] = len(real_votes_by_room[i]) / 18
                input_param['sch_occ_' + str(i)] = 0

            # aggregate votes of each space and generate new set point
            atc = {}

            if season == "clg":
                for i in range(1, space + 1):
                    input_param['sch_htg_' + str(i)] = 0
                input_param['sch_deck_htg'] = 0
            else:
                for i in range(1, space + 1):
                    input_param['sch_clg_' + str(i)] = 50
                input_param['sch_deck_clg'] = 50

            if algo == "const":
                for i in range(1, space + 1):
                    param = {"indoor_temp": co_sim.output['temp_' + str(i)][0],
                             "outdoor_temp": co_sim.output['temp_out'][0],
                             "ec_cooling_coil": co_sim.output["ec_cooling_coil"][0],
                             "ec_heating_coil": co_sim.output["ec_heating_coil"][0]}
                    atc[i] = get_atc(algo, votes_by_room[i], participant.loss, param)
                    input_param['sch_'+season+'_' + str(i)] = 23
                if season == "clg":
                    input_param['sch_deck_clg'] = 23
                else:
                    input_param['sch_deck_htg'] = 23

            else:
                # calculate new set points for cooling:
                if season == "clg":
                    min_set_point = 56
                    for i in range(1, space + 1):
                        param = {"indoor_temp": co_sim.output['temp_' + str(i)][0],
                                 "outdoor_temp": co_sim.output['temp_out'][0],
                                 "ec_cooling_coil": co_sim.output["ec_cooling_coil"][0],
                                 "ec_heating_coil": co_sim.output["ec_heating_coil"][0]}
                        atc[i] = get_atc(algo, votes_by_room[i], participant.loss, param)
                        if atc[i] == 4:
                            input_param['sch_clg_' + str(i)] = 50
                            continue
                        new_sp = generate_set_point(co_sim.output['temp_' + str(i)][0], atc[i])
                        input_param['sch_clg_' + str(i)] = new_sp
                        min_set_point = min(min_set_point, new_sp)

                        input_param['sch_htg_' + str(i)] = 0

                    input_param['sch_deck_clg'] = min_set_point - 6
                    input_param['sch_deck_htg'] = 0
                # for heating
                else:
                    max_set_point = -6
                    for i in range(1, space + 1):
                        param = {"indoor_temp": co_sim.output['temp_' + str(i)][0],
                                 "outdoor_temp": co_sim.output['temp_out'][0],
                                 "ec_cooling_coil": co_sim.output["ec_cooling_coil"][0],
                                 "ec_heating_coil": co_sim.output["ec_heating_coil"][0]}
                        atc[i] = get_atc(algo, votes_by_room[i], participant.loss, param)
                        if atc[i] == 4:
                            input_param['sch_htg_' + str(i)] = 0
                            continue
                        new_sp = generate_set_point(co_sim.output['temp_' + str(i)][0], atc[i])
                        input_param['sch_htg_' + str(i)] = min(new_sp, 45)
                        max_set_point = max(max_set_point, new_sp)

                        input_param['sch_clg_' + str(i)] = 50

                    input_param['sch_deck_htg'] = max_set_point + 6
                    input_param['sch_deck_clg'] = 50

            participant.update_loss(real_votes_by_room, atc)
            result.update_itc(real_votes_by_room, atc)
            result.add_consumption(co_sim.output['ec_cooling_coil'][0], co_sim.output['ec_heating_coil'][0], season)



        else:
            input_param['sch_deck_clg'] = 50
            for i in range(1, space + 1):
                input_param['sch_clg_' + str(i)] = 50
            input_param['sch_deck_htg'] = 0
            for i in range(1, space + 1):
                input_param['sch_htg_' + str(i)] = 0

            if sim_time.hour == 23:
                result_dict[str(sim_time.strftime("%Y-%m-%d"))] = {}
                result_dict[str(sim_time.strftime("%Y-%m-%d"))]["cooling_consumption"] = result.ec_clg
                result_dict[str(sim_time.strftime("%Y-%m-%d"))]["heating_consumption"] = result.ec_htg

                result_itc = {}
                for pid, itc in participant.itc_loss.items():
                    result_itc[pid] = itc
                result_dict[str(sim_time.strftime("%Y-%m-%d"))]["itc"] = result_itc
                result_dict[str(sim_time.strftime("%Y-%m-%d"))]["total_itc"] = result.itc


                result_loss = {}
                for pid, loss in participant.loss.items():
                    result_loss[pid] = loss

                result_dict[str(sim_time.strftime("%Y-%m-%d"))]["equality"] = result_loss
        is_finish = co_sim.simulate(input_param, output_param)

    # print("finished ........................................................")
    # program_end_time = datetime.now()
    # print((program_end_time-program_start_time).seconds)
    # input()

    # result_dict = {}
    # result_dict["cooling_consumption"] = result.ec_clg
    # result_dict["heating_consumption"] = result.ec_htg
    # result_dict["itc"] = result.itc

    # result_loss = {}
    # for pid, loss in participant.loss.items():
    #     result_loss[pid] = loss
    #
    # result_dict["equality"] = result_loss

    result_path = "./result/" + "result_" + timestamp + "/"
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    with open(result_path + algo + str(argv[2]) + ".json", "w") as json_file:
        json.dump(result_dict, json_file, indent=4)


    # f = open("./result/" + city + "/" + algo + str(argv[2]) + ".txt", 'w')
    # f.write("consumption cooling \n")
    # f.write(str(result.ec_clg) + '\n')
    # f.write("consumption heating \n")
    # f.write(str(result.ec_htg) + '\n')
    # f.write("itc\n")
    # f.write(str(result.itc) + "\n")
    # f.write("equality \n")
    # for loss in participant.loss.values():
    #     f.write(str(loss) + "\n")

    # for key, value in result.items():
    #     print(key + ":  " + str(value.ec))
    # f.close()
    print(algo + " finished ")

    print(total_num)


if __name__ == "__main__":
    main(sys.argv[1:])
    # main(['./models/office/Paris/in.fmu', "const", "s1_25", "./models/office/occ_config.txt", "./models/office/trajectories", "knn/ashrae_comfort_data.csv"])
    # main(['./models/office/Paris/in.fmu', 'maj', 's1_75', './models/office/occ_config.txt', './models/office/trajectories', 'knn/ashae_comfort_data.csv'])
