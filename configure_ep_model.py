from eppy import modeleditor
from eppy.modeleditor import IDF

# Set the EnergyPlus IDD file path
idd_file = r"D:\Programming\EnergyPlus\EnergyPlusV22-2-0\Energy+.idd"

# Set the path of the IDF file to modify
idf_path = "./models/drahix/drahix.idf"

# Load the IDD file with Eppy
IDF.setiddname(idd_file)

# Open the IDF file
idf = IDF(idf_path)


# for i, people in enumerate(idf.idfobjects["PEOPLE"]):
#     schedule_name = "People_Schedule_" + str(i)
#
#     # Create a new Schedule:Compact object
#     schedule = idf.newidfobject("SCHEDULE:COMPACT",
#                                 Name=schedule_name,
#                                 Schedule_Type_Limits_Name="Fraction",
#                                 Field_1="Through: 12/31",
#                                 Field_2="For: AllDays",
#                                 Field_3="Until: 24:00",
#                                 Field_4="0.0")
#
#     # Assign the generated schedule name to the current People object
#     people.Number_of_People_Schedule_Name = schedule_name
#     people.Number_of_People_Calculation_Method = "People"
#     people.Number_of_People = 100


# for space in idf.idfobjects["SPACE"]:
#     # Create a new ThermalZone object
#     thermal_zone_name = f"ThermalZone_{space.Name}"
#     thermal_zone = idf.newidfobject("ZONE",
#                                     Name=thermal_zone_name)
#
#     # Assign the newly created thermal zone to the Space object
#     space.Zone_Name = thermal_zone_name
#
#
# # Save the modified IDF file
# idf.save("./models/configured/output_withzones.idf")

print(len(idf.idfobjects["SPACE"]))
