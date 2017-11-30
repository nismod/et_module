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

from et_module.main import dummy_function

class ETWrapper(SectorModel):
    """Energy Demand Wrapper
    """
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

        print(data)
        test_input = "ET_INTPUT"
        output = dummy_function(test_input)
        print(output)
        print(":.. Finished running et_module")
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

        return

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
