import os
import sys
from prod.Colors import TextStyles
from prod.repository.ConfigRepository import ConfigRepository

print("Hello World!")
print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "../config.ini"
abs_file_path = os.path.join(script_dir, rel_path)

configRepo = ConfigRepository()
configExist = configRepo.does_config_file_exist()
is_config_file_valid = configRepo.is_config_file_valid()
print("Is config valid: " + str(is_config_file_valid))



stockTicker = input("What Stock would you like to track? >> ")
print("You entered " + stockTicker)

print(TextStyles.OKGREEN + "Warning: No active frommets remain. Continue?" + TextStyles.ENDC)
print(f"{TextStyles.WARNING}Warning: No active frommets remain. Continue?{TextStyles.ENDC}")