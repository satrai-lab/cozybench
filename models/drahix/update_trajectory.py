import random

mapping_table = {
    1: 15, 2: 13, 3: 14, 4: 12, 5: 10, 6: 11, 7: 8, 8: 9, 9: 1, 10: 3,
    11: 5, 12: 7, 13: 2, 14: 4, 15: 6, 16: 7, 17: 16, 18: 17, 19: 20,
    20: 20, 21: 29, 22: 22, 23: 18, 24: 19, 25: 21, 26: 23, 27: 25,
    28: 27, 29: 30, 30: 31, 31: 26, 32: 28
}

for month in range(12):
    with open("./trajectories_old/" + str(month+1) + ".txt", "r") as read_file:
        write_file = open("./trajectories/" + str(month+1) + ".txt", "w")

        line = read_file.readline()
        # write_file.write(line)
        while line:
            space_num_in_smart_spec = line.split(";")[0]
            data = line.split(";")
            if int(space_num_in_smart_spec) == 0:
                line = read_file.readline()
                continue
            if space_num_in_smart_spec[1] == "1":
                space_number = random.randint(32, 54)
            else:
                space_number = mapping_table[int(space_num_in_smart_spec[-2:])]
            people = data[-1].split(",")
            if len(people) <= 30:
                if random.randint(0, 100) < 100:
                    add_num = random.randint(0, 20)
                    if len(people) < 5:
                        add_num *= 2
                        if add_num > 30:
                            add_num = 30
                    for i in range(add_num):
                        added_p_id = random.randint(1, 160)
                        while str(added_p_id) in people:
                            added_p_id = random.randint(1, 159)
                        people.insert(0, str(added_p_id))
                people = ",".join(people)
                data[-1] = people

            numbers = data[-1].split(",")
            seen = set()
            number_result = []
            for num in numbers:
                if num and num not in seen:
                    number_result.append(num)
                    seen.add(num)

            data[-1] = ",".join(number_result)

            data[0] = str(space_number)

            new_line = ';'.join(data)
            write_file.write(new_line)

            line = read_file.readline()
