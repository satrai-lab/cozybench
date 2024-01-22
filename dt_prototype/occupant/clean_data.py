def clean_data(file_add):
    f_read = open(file_add, "r")
    f_write = open("data_clean.csv", "w")
    line = f_read.readline()
    f_write.write("id," + line)
    i = 0
    line = f_read.readline()
    while line:
        # line = f_read.readline()
        data_write = line.split(",")
        while line and line.split(",")[0] == data_write[0] and line.split(",")[2] == data_write[2]:
            end_date = line.split(",")[-1]
            line = f_read.readline()

        i = i+1
        data_write[-1] = end_date
        data_write.pop(1)
        f_write.write(str(i) + "," + ",".join(data_write))