def aggregate(list_cities: list, list_algorithms: list, scenarios_system: list, percentage: list, repeat_time: int):
    file_itc = open("./result/result/itc.csv", 'w')
    file_tce = open("./result/result/tce.csv", 'w')
    file_ec = open("./result/result/ec.csv", 'w')
    for city in list_cities:
        for sys in scenarios_system:
            for percent in percentage:
                for algo in list_algorithms:
                    list_itc = []
                    list_tce = []
                    list_ec_cooling = []
                    list_ec_heating = []
                    for r_time in range(repeat_time):
                        f = open("./result/" + city + "/" + algo + "s" + str(sys) + "_" + str(percent) + ".txt", 'r')
                        data = f.readline()
                        current_metrics = None
                        while data:
                            if "consumption" in data and "cooling" in data:
                                current_metrics = list_ec_cooling
                            elif "consumption" in data and "heating" in data:
                                current_metrics = list_ec_heating
                            elif "itc" in data:
                                current_metrics = list_itc
                            elif "equality" in data:
                                current_metrics = list_tce
                            elif current_metrics is not None:
                                current_metrics.append(float(data.strip()))
                            data = f.readline()
                    file_ec.write(city + "," + algo + "," + "s" + str(sys) + "_" + str(percent) + ",")
                    file_ec.write(str(sum(list_ec_cooling)/repeat_time * 2.77778e-7) + ",")
                    file_ec.write(str(sum(list_ec_heating) / repeat_time * 2.77778e-7) + "\n")

                    file_itc.write(city + "," + algo + "," + "s" + str(sys) + "_" + str(percent) + ",")
                    file_itc.write(str(sum(list_itc) / repeat_time) + "\n")

                    file_tce.write(city + "," + algo + "," + "s" + str(sys) + "_" + str(percent) + ",")
                    for tce in list_tce:
                        file_tce.write(str(tce) + ",")
                    file_tce.write("\n")


if __name__ == "__main__":
    algorithms = ["fair", "drift", "maj", "const"]

    cities = ["Mumbai", "Cairo", "LA", "Paris"]
    # cities = ["NYC"]
    scenario_system = [1, 2]
    percentage = [25, 50, 75, 100]

    aggregate(cities, algorithms, scenario_system, percentage, 5)
