"""The sector model wrapper for smif to run the energy demand model
"""
import os
import logging
import configparser
import numpy as np
from datetime import date
from collections import defaultdict
from smif.model.sector_model import SectorModel
from pkg_resources import Requirement, resource_filename
from pyproj import Proj, transform
from et_module import main_functions

REGION_SET_NAME = 'lad_uk_2016'

class ETWrapper(SectorModel):
    """Energy Demand Wrapper
    """
    def __init__(self, name):
        super().__init__(name)

        self.user_data = {}

    def array_to_dict(self, input_array):
        """Convert array to dict

        Arguments
        ---------
        input_array : numpy.ndarray
            timesteps, regions, interval

        Returns
        -------
        output_dict : dict
            timesteps, region, interval

        """
        output_dict = defaultdict(dict)
        for r_idx, region in enumerate(self.get_region_names(REGION_SET_NAME)):
            output_dict[region] = input_array[r_idx, 0]

        return dict(output_dict)

    def before_model_run(self, data=None):
        """Implement this method to conduct pre-model run tasks

        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
            Access parameter values (before any model is run, no dependency
            input data or state is guaranteed to be available)

        Info
        -----
        `self.user_data` allows to pass data from before_model_run to main model
        """
        pass

    def initialise(self, initial_conditions):
        """
        """
        pass

    def simulate(self, data_handle):
        """Runs the Energy Demand model for one `timestep`

        Arguments
        ---------
        data_handle : dict
            A dictionary containing all parameters and model inputs defined in
            the smif configuration by name

        Returns
        =======
        et_module_out : dict
            Outputs of et_module
        """
        logging.info("... start et_module")

        # ---------------------
        # Load input variables
        # ---------------------

        # Define base year
        base_yr = 2015

        # Scenario parameters from narrative YAML file
        yr_until_changed = data_handle.get_parameter('yr_until_changed_lp')                 # Year until regime would be fully realised
        load_profile_scenario = data_handle.get_parameter('load_profile_charging_regime')   # Sheduled or unsheduled

        # Regions
        logging.info("... loading regions")
        regions = self.get_region_names(REGION_SET_NAME)

        # Current year of simulation
        logging.info("... loading base and simulation year")
        simulation_yr = data_handle.current_timestep

        # Hourly transport demand of simulation year (electrictiy)
        logging.info("... loading transport input")
        elec_array_data = data_handle.get_base_timestep_data('electricity')
        et_demand_elec_input = self.array_to_dict(elec_array_data)

        # Paths where csv profile are stored
        logging.info("... loading paths")
        main_path = os.path.dirname(os.path.abspath(__file__))
        csv_path_lp = os.path.join(main_path, '_config_data')

        # ------------------------------------
        # Load EV charging load profiles
        # ------------------------------------
        load_profiles = main_functions.get_load_profiles(
            csv_path_lp)
        logging.info("... load load profiles")

        # ------------------
        # Temporal disaggregation of load profile
        # ------------------
        logging.info("changing load profile")
        reg_et_demand_yh = main_functions.load_curve_assignement(
            curr_yr=simulation_yr,
            base_yr=base_yr,
            yr_until_changed=yr_until_changed,
            et_service_demand_yh=et_demand_elec_input,
            load_profiles=load_profiles,
            regions=regions,
            charging_scenario=load_profile_scenario,
            diffusion='sigmoid')

        et_module_out = {}
        et_module_out['electricity'] = reg_et_demand_yh

        # -------
        # Testing
        # -------
        assert round(np.sum(et_module_out['electricity']), 2) == round(sum(et_demand_elec_input.values()), 2)

        print("... Finished running et_module")
        return et_module_out

    def extract_obj(self, results):
        return 0
