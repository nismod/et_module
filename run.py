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
        """Runs prior to any ``simulate()`` step

        Writes scenario data out into the scenario files

        Saves useful data into the ``self.user_data`` dictionary for access
        in the ``simulate()`` method

        Data is accessed using the `get_scenario_data()` method is provided
        as a numpy array with the dimensions timesteps-by-regions-by-intervals.

        Info
        -----
        `self.user_data` allows to pass data from before_model_run to main model
        """
        pass

    def initialise(self, initial_conditions):
        """
        """
        pass

    def simulate(self, timestep, data=None):
        """Runs the Energy Demand model for one `timestep`

        Arguments
        ---------
        timestep : int
            The name of the current timestep
        data : dict
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

        # ------------------
        # Temporally disaggregate load profile
        # ------------------
        # Annual demand of simulation year
        et_demand_y = self.array_to_dict(data['et_demand'])

        # Regions
        region_names = self.get_region_names(REGION_SET_NAME)

        reg_et_demand_yh = main.temporal_disaggregation(
            curr_yr=timestep,
            et_demand_y=et_demand_y,
            load_profiles=load_profiles,
            region_names=region_names)

        et_module_out = reg_et_demand_yh
        print(":.. Finished running et_module")
        return {'model_name': et_module_out}

    def extract_obj(self, results):
        """Implement this method to return a scalar value objective function

        This method should take the results from the output of the `simulate`
        method, process the results, and return a scalar value which can be
        used as the objective function

        Arguments
        =========
        results : :class:`dict`
            The results from the `simulate` method

        Returns
        =======
        float
            A scalar component generated from the simulation model results
        """
        pass

