from eppy.modeleditor import IDF
import argparse
import os


def fmu_generate():

    parser = argparse.ArgumentParser(description="co-zybench for evaluating thermal comfort provision systems")
    parser.add_argument('ep_idd', type=str, help='path to Energy+.idd file, usually in the root path of EnergyPlus')
    parser.add_argument('model_path', type=str, help='path to EnergyPlus model')

    args = parser.parse_args()

    # configure IDD from EnergyPlus
    # idd_path = r"D:\Programming\EnergyPlus\EnergyPlusV23.1\Energy+.idd"
    idd_path = args.ep_idd
    IDF.setiddname(idd_path)

    # read IDF
    idf = IDF(args.model_path)

    thermal_zones = idf.idfobjects["ZONE"]

    idf.newidfobject(
        "ExternalInterface", Name_of_External_Interface="FunctionalMockupUnitExport"
    )
    for zone in thermal_zones:
        idf.newidfobject(
            "ExternalInterface:FunctionalMockupUnitExport:From:Variable",
            OutputVariable_Index_Key_Name=zone.Name,
            OutputVariable_Name="Zone Air Temperature",
            FMU_Variable_Name="temp_" + zone.Name,
        )

    idf.newidfobject(
        "ExternalInterface:FunctionalMockupUnitExport:From:Variable",
        OutputVariable_Index_Key_Name="COIL HEATING ELECTRIC 1",
        OutputVariable_Name="Heating Coil Electricity Energy",
        FMU_Variable_Name="heat_energy",
    )
    idf.newidfobject(
        "ExternalInterface:FunctionalMockupUnitExport:From:Variable",
        OutputVariable_Index_Key_Name="COIL COOLING DX TWO SPEED 1",
        OutputVariable_Name="Cooling Coil Electricity Energy",
        FMU_Variable_Name="cool_energy",
    )
    idf.newidfobject(
        "ExternalInterface:FunctionalMockupUnitExport:From:Variable",
        OutputVariable_Index_Key_Name="Environment",
        OutputVariable_Name="Site Outdoor Air Drybulb Temperature",
        FMU_Variable_Name="temp_out",
    )

    thermostat = idf.idfobjects["ThermoStatSetpoint:DualSetpoint"]
    for num in range(len(thermostat)):
        thermostat[num].Cooling_Setpoint_Temperature_Schedule_Name = "sch_clg_" + str(num + 1)
        thermostat[num].Heating_Setpoint_Temperature_Schedule_Name = "sch_htg_" + str(num + 1)

        idf.newidfobject(
            "ExternalInterface:FunctionalMockupUnitExport:To:Schedule",
            Schedule_Name="sch_clg_" + str(num + 1),
            FMU_Variable_Name="sch_clg_" + str(num + 1),
            Initial_Value="50",
        )
        idf.newidfobject(
            "ExternalInterface:FunctionalMockupUnitExport:To:Schedule",
            Schedule_Name="sch_htg_" + str(num + 1),
            FMU_Variable_Name="sch_htg_" + str(num + 1),
            Initial_Value="-10",
        )
        
    directory, filename = os.path.split(args.model_path)
    file_base, file_extension = os.path.splitext(filename)
    new_filename = f"{file_base}_out{file_extension}"
    new_path = os.path.join(directory, new_filename)

    idf.saveas(new_path)
    print("idf saved.")

    # # Path to the VsDevCmd.bat file
    # vs_dev_cmd = r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\VsDevCmd.bat"
    #
    # # result = subprocess.run(vs_dev_cmd, shell=True)
    # # Your command
    # your_command = r"cd /d D:\Programming\Projects\H2H\H2H-main\H2H-main\internship\code\sim_model && python ./EnergyPlusToFMU/Scripts/EnergyPlusToFMU.py -i D:\\Programming\\EnergyPlus\\EnergyPlusV23.1\\Energy+.idd -w ./weather_file/paris.epw -a 1 ./test_out.idf"
    # # Full command to run
    # full_command = f'"{vs_dev_cmd}" && {your_command}'
    # result = subprocess.run(
    #     full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    # )
    #
    # # batch_file = r"./sim_model/ttt.bat"
    # #
    # # # Run the batch file
    # # result = subprocess.run(
    # #     batch_file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    # # )
    # print("Output:", result.stdout)
    # print("Error:", result.stderr)
    # print("ok")


if __name__ == "__main__":
    # main(sys.argv[1:])
    # main(['NYC', "const", 0, 0])
    fmu_generate()