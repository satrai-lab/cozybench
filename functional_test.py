import run
from datetime import datetime

"""
Functional testing using the Majority Approach in a Paris office building scenario.
With the parameters:
      "in.fmu" is the EnergyPlus FMI co-simulation model
      "maj" refers to the Majority approach
      "s1_75" means Sys_1 with 75%. (75% would share their data or provide their sensation)
      "occ_config.txt" defines the occupant profiles
      "trajectory" is the folder that contains occupant movement trajectories
      "ashae_comfort_data.csv" is the historic data of occupants' thermal comfort. 
      "datetime" is used to generate new result folder.  
"""

run.main(['./models/office/Paris/in.fmu', 'maj', 's1_75', './models/office/occ_config.txt',
          './models/office/trajectories', 'knn/ashae_comfort_data.csv', datetime.now().strftime("%Y%m%d%H%M%S")])
