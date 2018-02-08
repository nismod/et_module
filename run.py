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
from et_module import main

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
        """
        print("... start et_module")

        # Paths where csv profile are stored
        main_path = resource_filename(Requirement.parse("et_module"), "")
        path_lp_csv = os.path.join(main_path, '_config_data')

        # ------------------
        # Load charging load profiles
        # ------------------
        load_profiles = main.get_load_profiles(path_lp_csv)

        simulation_yr = data_handle.current_timestep
        #data['sim_param']['curr_yr'] = data_handle.current_timestep
        # ------------------
        # Temporally disaggregate load profile
        # ------------------
        # Hourly demand of simulation year
        elec_array_data = data_handle.get_base_timestep_data('electricity')
        et_demand_y_electricity = self.array_to_dict(elec_array_data)

        # Regions
        region_names = self.get_region_names(REGION_SET_NAME)

        reg_et_demand_yh = main.temporal_disaggregation(
            simulation_yr=simulation_yr,
            et_demand_y=et_demand_y_electricity,
            load_profiles=load_profiles,
            region_names=region_names)

        et_module_out = {}
        et_module_out['electricity'] = reg_et_demand_yh

        print("... Finished running et_module")
        return et_module_out

    def extract_obj(self, results):
        return 0
