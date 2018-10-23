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

        nr_of_regions = len(regions)

        simulation_yr = data_handle.current_timestep
        print("SIULATION YR " + str(simulation_yr))

        # Read number of EV trips starting in regions (np.array(regions, 24h))
        reg_trips_ev_24h = data_handle.get_base_timestep_data('trips')

        # Get hourly demand data for day for every region (np.array(regions, 24h)) (kWh)
        reg_elec_24h = data_handle.get_base_timestep_data('electricity')

        # --------------------------------------
        # Assumptions
        # --------------------------------------
        assumption_nr_ev_per_trip = 1               # [-] Number of EVs per trip
        assumption_ev_p_with_v2g_capability = 1.0   # [%] Percentage of EVs not used for v2g and G2V
        assumption_av_charging_state = 0.5          # [%] Assumed average charging state of EVs before peak trip hour
        assumption_av_usable_battery_capacity = 30  # [kwh] Average (storage) capacity of EV Source: https://en.wikipedia.org/wiki/Electric_vehicle_battery
        assumption_safety_margin = 0.1              # [%] Assumed safety margin (minimum capacity SOC)

        # --------------------------------------
        # 1. Find peak demand hour for EVs
        # --------------------------------------
        # Hour of electricity peak demand in day
        reg_peak_position_h_elec = np.argmax(reg_elec_24h, axis=1)

        # Total electricity demand of all trips of all vehicles
        reg_peak_demand_h_elec = np.max(reg_elec_24h, axis=1)

        # --------------------------------------
        # 2. Get number of EVs in peak hour with
        # help of trip number
        # --------------------------------------
        reg_max_nr_ev = np.zeros((nr_of_regions))
        for region_nr, peak_hour_nr in enumerate(reg_peak_position_h_elec):
            reg_max_nr_ev[region_nr] = reg_trips_ev_24h[region_nr][peak_hour_nr] * assumption_nr_ev_per_trip

        # --------------------------------------
        # 3. Calculate total EV battery capacity
        # of all vehicles which can do V2G
        # --------------------------------------

        # Number of EVs with V2G capability
        reg_nr_v2g_ev = reg_max_nr_ev * assumption_ev_p_with_v2g_capability

        # Demand in peak hour of all EVs with V2G capabilityies
        average_demand_vehicle = reg_peak_demand_h_elec / reg_max_nr_ev
        average_demand_vehicle[np.isnan(average_demand_vehicle)] = 0 #replace nan with 0
        average_demand_vehicle[np.isinf(average_demand_vehicle)] = 0 #replace inf with 0

        # Calculate peak demand of all vehicles with V2G capability
        reg_peak_demand_h_elec_v2g_ev = average_demand_vehicle * reg_nr_v2g_ev

        # Calculate overall maximum capacity of all EVs with V2G capabilities
        reg_max_capacity_v2g_ev = reg_nr_v2g_ev * assumption_av_usable_battery_capacity

        # --------------------------------------
        # 4. Calculate flexible "EV battery" used for G2V and v2g
        # -------------------------------------
        # Calculated capacity of safety margin (blue area)
        capacity_safety_margin = reg_max_capacity_v2g_ev * assumption_safety_margin

        # Calculate maximum possible V2G capacity
        acutal_v2g_capacity = np.zeros((nr_of_regions))

        # Itereage regions and check whether the actual
        # consumption including safety margin is larger
        # than the demand based on the average soc assumption
        for region_nr, reg_peak_h_capacity in enumerate(reg_max_capacity_v2g_ev):

            # Actual used capacity of all vehicles with V2G capabilities and minimum charging state
            used_capacity_incl_margin = reg_peak_demand_h_elec_v2g_ev[region_nr] + capacity_safety_margin[region_nr]

            # Cannot be higher than maximum storage capacity
            if (used_capacity_incl_margin > reg_peak_demand_h_elec_v2g_ev[region_nr]):
                used_capacity = reg_peak_demand_h_elec_v2g_ev[region_nr]
            else:
                pass

            # Capacity necessary for assumed average SOC of region
            average_soc_capacity = assumption_av_charging_state * reg_peak_h_capacity

            # If average state of charging smaller than actual used capacity
            # the V2G capacity gets reduced
            if used_capacity > average_soc_capacity:

                # More is use than minimum SOC
                acutal_v2g_capacity[region_nr] = reg_peak_h_capacity - used_capacity

                if (reg_peak_h_capacity - used_capacity) < 0:
                    acutal_v2g_capacity[region_nr] = 0

                # Test that not minus capacity
                #assert (reg_peak_h_capacity - used_capacity) >= 0
            else:
                # Less is use than minimum SOC
                acutal_v2g_capacity[region_nr] = reg_peak_h_capacity - average_soc_capacity

                if (reg_peak_h_capacity - average_soc_capacity) < 0:
                    acutal_v2g_capacity[region_nr] = 0

                # Test that not minus capacity
                #assert (reg_peak_h_capacity - average_soc_capacity) >= 0

        return acutal_v2g_capacity

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
