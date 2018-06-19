
"""To run et_module locally for debugging purposes

"""
import os
from et_module import main_functions

main_path = os.path.abspath('C:/users/cenv0553/ed/et_module')

path_lp_csv = os.path.join(main_path, '_config_data')

# Load load profiles
load_profiles = main_functions.get_load_profiles(path_lp_csv)
