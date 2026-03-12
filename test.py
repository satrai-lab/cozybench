# from eppy import modeleditor
# from eppy.modeleditor import IDF
#
# # Set the EnergyPlus installation path and IDD file path
# iddfile = r"D:\Programming\EnergyPlus\EnergyPlusV22-2-0\Energy+.idd"
# IDF.setiddname(iddfile)
#
# # Read the IDF file
# idf_file = "./models/office/in.idf"
# idf = IDF(idf_file)




# def look_for_all_coils():
#     """
#     Find all coils. This may be useful later.
#     :return:
#     """
#     coil_types = [
#         'COIL:COOLING:DX:SINGLESPEED',
#         'COIL:COOLING:DX:TWOSPEED',
#         'COIL:COOLING:DX:VARIABLESPEED',
#         'COIL:COOLING:WATER',
#         'COIL:COOLING:WATER:DETAILEDGEOMETRY',
#         'COIL:COOLING:WATER:HEATPUMP',
#         'COIL:HEATING:ELECTRIC',
#         'COIL:HEATING:FUEL',
#         'COIL:HEATING:DESUPERHEATER',
#         'COIL:HEATING:STEAM',
#         'COIL:HEATING:WATER',
#         'COIL:HEATING:WATER:DETAILEDGEOMETRY',
#         'COIL:HEATING:DX:SINGLESPEED',
#         'COIL:HEATING:DX:VARIABLESPEED',
#     ]
#
#     # Print the name of each Coil
#     for coil_type in coil_types:
#         coils = idf.idfobjects.get(coil_type, [])
#         for coil in coils:
#             print(f"{coil_type} Name: {coil.Name}")

# output_variables = idf.idfobjects['OUTPUT:VARIABLE']
#
# # Print each Output:Variable name and its corresponding component
# for output_variable in output_variables:
#     variable_name = output_variable.Variable_Name
#     key_value = output_variable.Key_Value
#     print(f"Output Variable: {variable_name}, Corresponding Component: {key_value}")


# def function_a() -> str:
#     return "Function A was called"
#
# def function_b() -> str:
#     return "Function B was called"
#
# def call_func(func: callable):
#     return func()
#
# print(call_func(function_b))

# import pytz
# from datetime import datetime
#
# local_datetime = datetime(2023, 5, 1, 8, 0, 0)
# local_time_zone = pytz.timezone('Europe/Berlin')
# local_dt = local_time_zone.localize(local_datetime)
# utc_dt = local_dt.astimezone(pytz.utc)
# print(utc_dt)


from colorama import Fore, Back, Style, init

# Initialize colorama
init()

# Print using different colors
print(Fore.RED + "This is red text" + Style.RESET_ALL)
print(Fore.GREEN + "This is green text" + Style.RESET_ALL)
print(Fore.BLUE + "This is blue text" + Style.RESET_ALL)
print(Back.YELLOW + "This text has a yellow background" + Style.RESET_ALL)
print(Fore.CYAN + Back.MAGENTA + "This is cyan text with a magenta background" + Style.RESET_ALL)
print(Style.BRIGHT + "This is bright text" + Style.RESET_ALL)
print(Style.DIM + "This is dim text" + Style.RESET_ALL)
print(Style.NORMAL + "This is normal text" + Style.RESET_ALL)

# If you want to keep a specific color active
persistent_content = Fore.BLUE + "This content stays visible" + Style.RESET_ALL
print(persistent_content)

