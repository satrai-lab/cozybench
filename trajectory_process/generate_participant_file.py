import datetime
from clean_data import clean_data

# room_space = {1: [2, 3, 4], 2: [5], 3: [6], 4: [8], 5: [10, 11, 12], 6: [13]}

clean_data("./data_synthetic_large.csv")

f_trajectory = open("./data_clean.csv", "r")

f_participants = []
for i in range(12):
    f_participants.append(open("./synthetic_large_traj/" + str(i + 1) + ".txt", "w"))

# list_space = [{}, {}, {}, {}, {}, {}]
current_date = datetime.datetime(2020, 1, 1, 0, 0, 0)

data_extracted = {}

line = f_trajectory.readline()
line = f_trajectory.readline()


# def add_occupant(space, time, person):
#     room = -1
#     for key, value in room_space.items():
#         if space in value:
#             room = key
#     if room == -1:
#         return
#     if time in list_space[room - 1]:
#         list_space[room - 1][time].append(person)
#     else:
#         list_space[room - 1][time] = [person]


while line:
    trajectory_data = line.split(",")
    time_start = datetime.datetime.strptime(trajectory_data[3], '%Y/%m/%d %H:%M')
    time_end = datetime.datetime.strptime(trajectory_data[4].strip(), '%Y/%m/%d %H:%M')
    person_id = trajectory_data[1]
    space_id = trajectory_data[2]

    if time_start.hour >= 6 and time_end.hour <= 21:
        # time that used to store in the dataset
        if 0 < time_start.minute <= 30:
            store_time = datetime.datetime(time_start.year, time_start.month, time_start.day,
                                           time_start.hour, 30, 0)
        else:
            store_time = datetime.datetime(time_start.year, time_start.month, time_start.day,
                                           time_start.hour+1, 0, 0)
        if store_time.month not in data_extracted:
            data_extracted[store_time.month] = {}
        if space_id not in data_extracted[store_time.month]:
            data_extracted[store_time.month][space_id] = {}
        if store_time not in data_extracted[store_time.month][space_id]:
            data_extracted[store_time.month][space_id][store_time] = []
        data_extracted[store_time.month][space_id][store_time].append(person_id)

    line = f_trajectory.readline()

    # # doing this because I want to save data separately by month
    # if current_date.month == time_start.month:
    #     if time_start.hour >= 7 and time_end.hour <= 19 and time_start.day == time_end.day:
    #         # if the time range is the same 1 hour
    #         if time_start.hour == time_end.hour:
    #             time = datetime.datetime(time_start.year, time_start.month, time_start.day, time_start.hour, 30, 0)
    #             add_occupant(int(trajectory_data[2]), str(time), trajectory_data[1])
    #             # if str(time) in list_space[int(trajectory_data[2])-1]:
    #             #     list_space[int(trajectory_data[2])-1][str(time)].append(trajectory_data[1])
    #             # else:
    #             #     list_space[int(trajectory_data[2])-1][str(time)] = []
    #             #     list_space[int(trajectory_data[2])-1][str(time)].append(trajectory_data[1])
    #             print(str(time))
    #         elif time_start.hour < time_end.hour:
    #             if time_start.minute < 30:
    #                 time = datetime.datetime(time_start.year, time_start.month, time_start.day, time_start.hour, 30, 0)
    #                 add_occupant(int(trajectory_data[2]), str(time), trajectory_data[1])
    #             for add_hour in range(time_end.hour - time_start.hour):
    #                 time = datetime.datetime(time_start.year, time_start.month, time_start.day,
    #                                          time_start.hour + add_hour + 1, 0, 0)
    #                 add_occupant(int(trajectory_data[2]), str(time), trajectory_data[1])
    #                 if add_hour != (time_end.hour - time_start.hour - 1):
    #                     time = datetime.datetime(time_start.year, time_start.month, time_start.day,
    #                                              time_start.hour + add_hour + 1, 30, 0)
    #                     add_occupant(int(trajectory_data[2]), str(time), trajectory_data[1])
    #                 elif time_end.minute > 30:
    #                     time = datetime.datetime(time_start.year, time_start.month, time_start.day,
    #                                              time_start.hour + add_hour + 1, 30, 0)
    #                     add_occupant(int(trajectory_data[2]), str(time), trajectory_data[1])
    #     line = f_trajectory.readline()
    # # it is the next month
    # else:
    #     # save the data of the last month
    #     # i is the number of the space
    #     for i in range(len(list_space)):
    #         dict_occupant = list_space[i]
    #         for key_date, value_occupants in dict_occupant.items():
    #             f_participants[current_date.month - 1].write(str(i + 1) + ";" + key_date + ";")
    #             for occupant in value_occupants:
    #                 f_participants[current_date.month - 1].write(occupant + ",")
    #             f_participants[current_date.month - 1].write("\n")
    #     # clear all the previous data
    #     list_space = [{}, {}, {}, {}, {}, {}]
    #
    #     # if the current month is 12, indicates the whole year is finished
    #     if current_date.month != 12:
    #         current_date = datetime.datetime(2020, current_date.month + 1, 1, 0, 0, 0)
    #     else:
    #         break

# data = {month: {space: {date: [person]}}}
for month, value1 in data_extracted.items():
    for space, value2 in value1.items():
        for date, list_person in value2.items():
            f_participants[month - 1].write(str(space) + ";" + str(date) + ";")
            for p in list_person:
                f_participants[month - 1].write(str(p) + ",")
            f_participants[month - 1].write("\n")

print("done")