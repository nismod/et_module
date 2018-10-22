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
from energy_demand.read_write import read_data

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

    def before_model_run(self, data_handle=None):
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

        # ------------------------
        # Capacity based appraoch
        # ------------------------

        # ------------------------
        # Load data
        # ------------------------
        main_path = os.path.dirname(os.path.abspath(__file__))
        path_input_data = os.path.join(main_path, 'data', 'scenarios')

        regions = data_handle.get_region_names(REGION_SET_NAME)
        simulation_yr = data_handle.current_timestep

        # Read number of EV trips starting in regions (np.array(regions, 24h))
        nr_trips_ev_24h = data_handle.get_base_timestep_data('trips')

        # Get hourly demand data for day for every region (np.array(regions, 24h)) (kWh)
        reg_elec_24h = data_handle.get_base_timestep_data('electricity')

        # --------------------------------------
        # Assumptions
        # --------------------------------------
        assumption_nr_ev_per_trip = 1               # [] Number of EVs per trip
        assumption_nr_unreached_EVs = 1.0           # [%] Percentage of EVs not used for V2G and G2V
        assumption_av_charging_state = 0.5          # [%] Assumed average charging state of EVs before peak trip hour
        assumption_av_usable_battery_capacity = 30  # [kwh] Average (storage) capacity of EV Source: https://en.wikipedia.org/wiki/Electric_vehicle_battery

        # --------------------------------------
        # 1. Find peak demand hour for EVs
        # --------------------------------------

        # Number of reachable EVs in peak hour
        peak_h_reg_elec = np.argmax(reg_elec_24h, axis=1)
        peak_demand_h_reg_elec = np.max(reg_elec_24h, axis=1)

        # --------------------------------------
        # 2. Get number of EVs with help of trip number
        # --------------------------------------
        # Calculate number of EVs based on trips
        max_nr_ev_reg = nr_trips_ev_24h * assumption_nr_ev_per_trip
        #print("max_nr_ev_reg")
        #print(max_nr_ev_reg[0])

        # --------------------------------------
        # 3. Calculate total EV battery capacity
        # --------------------------------------
        # Number of reachable EVs
        nr_ev_reg = max_nr_ev_reg * assumption_nr_unreached_EVs
        #print("nr_ev_reg")
        #print(nr_ev_reg[0])

        # Calculate overall maximum capacity of all EVs for every hour
        total_max_capacity_regs = nr_ev_reg * assumption_av_usable_battery_capacity
        #print("total_max_capacity_regs")
        #print(total_max_capacity_regs[0])

        # Overall maximum capacity for peak hour
        peak_h_max_capacity = np.zeros((total_max_capacity_regs.shape[0]))

        for region_nr, peak_h_nr in enumerate(peak_h_reg_elec):
            peak_h_max_capacity[region_nr] = total_max_capacity_regs[region_nr][peak_h_nr]

        #print("peak_h_max_capacity")
        #print(peak_h_max_capacity[0])
        # --------------------------------------
        # 4. Calculate flexible "EV battery" used for G2V and V2G
        # --------------------------------------
        # Calculate maximum possible flexible battery size 
        max_potential_V2G_capacity = peak_h_max_capacity - peak_demand_h_reg_elec
        #print("max_potential_V2G_capacity")
        #print(max_potential_V2G_capacity[0])
        #print("peak_demand_h_reg_elec")
        #print(peak_demand_h_reg_elec[0])

        # Include safety marging
        assumption_safety_margin = 0.1 # [%]
        
        # Calculated capacity of safety margin
        capacity_safety_margin = peak_h_max_capacity * assumption_safety_margin
        #print("capacity_safety_margin")
        #print(capacity_safety_margin[0])

        # Calculate actual V2G_capacity
        acutal_V2G_capacity = max_potential_V2G_capacity - capacity_safety_margin
        #print("acutal_V2G_capacity")
        #print(acutal_V2G_capacity[0])

        # If below zero, set to zero
        acutal_V2G_capacity[acutal_V2G_capacity < 0] = 0
        #print("acutal_V2G_capacity")
        #print(acutal_V2G_capacity[0])

        return acutal_V2G_capacity

        '''# ---------------------
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
        return et_module_out'''

    def extract_obj(self, results):
        return 0
    
    #simulate("gg", data_handle={})

#ETWrapper(name="test")
