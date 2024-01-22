import subprocess
import datetime
import argparse


def main():
    parser = argparse.ArgumentParser(description="co-zybench for evaluating thermal comfort provision systems")
    parser.add_argument('-s', '--system', required=True, help='name of the thermal comfort system to be evaluated')
    parser.add_argument('-b', '--building', required=False, help='path to the building FMU model')
    parser.add_argument('-o', '--occupant', required=False, help='path to the occupant trajectories')
    parser.add_argument('-p', '--profile', required=False, help='path to the occupant profile file')

    args = parser.parse_args()


    # algorithms = argv[0]
    # if algorithms[0] == "[":
    #     algorithms = algorithms[1:-1].split(",")
    #
    # building = ""
    # occupant = ""
    # flag_model = False
    # if len(argv) > 1:
    #     flag_model = True
    #     building = argv[1]
    #     if not building.isdigit():
    #         occupant = argv[2]
    algorithms = []
    if args.system[0] == "[":
        algorithms = args.system[1:-1].split(",")
        print(algorithms)
    else:
        algorithms.append(args.system)

    path_fmu_model = args.building
    path_trajectories = args.occupant
    path_profile = args.profile

    # cities = ["Paris"]
    # ratios = [0, 1, 2, 3, 4]
    repeat_time = 1
    scenario_system = [1, 2]
    percentage = [25, 50, 75, 100]

    # time view
    total_simulation = len(algorithms) * repeat_time * len(scenario_system) * len(percentage)
    current_simulation = 0
    start_time = datetime.datetime.now()

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    for r_time in range(repeat_time):
        for algo in algorithms:
            for sce_sys in scenario_system:
                for sce_model in percentage:
                    arguments = [path_fmu_model, algo.strip(), "s" + str(sce_sys)+"_"+str(sce_model), path_profile, path_trajectories, "knn/ashrae_comfort_data.csv", timestamp]
                    # if flag_model:
                    #     arguments.append([building, occupant])

                    path = "run.py"
                    print("running ", arguments)

                    ret = subprocess.run(["python", path] + arguments, shell=True, capture_output=True)

                    current_simulation += 1
                    current_time = datetime.datetime.now()
                    used_second = (current_time - start_time).seconds
                    print("used time:\t", used_second/60)
                    print("estimate time:\t", (used_second/current_simulation) * (total_simulation-current_simulation)/60)

    print("finish")


if __name__ == "__main__":
    main()
