
"""To run et_module locally for debugging purposes

"""
import os
from et_module import main

main_path = os.path.abspath(r'C:\users\cenv0553\nismod\models\et_module')

path_lp_csv = os.path.join(main_path, '_config_data')

# Load load profiles
load_profiles = main.get_load_profiles(path_lp_csv)

