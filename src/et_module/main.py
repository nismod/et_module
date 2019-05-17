"""The sector model wrapper for smif to run the energy demand model
"""
import numpy as np

def main(regions, timestep, reg_trips_ev_24h, reg_elec_24h):
    """Runs the electric vehicle model for one `timestep`

    Calculation steps:
    - Calculates based on number of trips the number of EV per region
    - Calculates based on number of EV per region and average storage capacity of EV total EV capacity per region

    Arguments
    ---------
    regions : list
        A list of region names
    timestep : int
        The current model year
    reg_trips_ev_24h : numpy.ndarray
        Array of shape regions-by-intervals containing the number of trips
        started in each region in each interval
    reg_elec_24h : numpy.ndarray
        Array of shape regions-by-intervals containing hourly demand data
        for every region in (kWh)

    Returns
    -------
    et_module_out : dict
        Outputs of et_module
    """
    nr_of_regions = len(regions)

    # --------------------------------------
    # Assumptions
    # --------------------------------------
    assumption_nr_ev_per_trip = 1                   # [-] Number of EVs per trip
    #assumption_ev_p_with_v2g_capability = 0.5       # [%] Percentage of EVs used for V2G and G2V
    #assumption_av_charging_state = 0.5              # [%] Assumed average state-of-charge of EVs before peak trip hour
    assumption_av_usable_battery_capacity = 30.0    # [kwh] Average (storage) capacity of EV Source: https://en.wikipedia.org/wiki/Electric_vehicle_battery
    #assumption_safety_margin = 0.1                  # [%] Assumed safety margin (minimum capacity SOC)

    # --------------------------------------
    # 1. Find peak demand hour for EVs
    # --------------------------------------
    # Hour of electricity peak demand in day per region
    reg_peak_position_h_elec = np.argmax(reg_elec_24h, axis=1)

    # Maximum electricity demand of all trips of all vehicles per region
    reg_peak_demand_h_elec = np.max(reg_elec_24h, axis=1)

    # --------------------------------------
    # 2. Calculate number of EVs in peak hour with help of trip number
    # --------------------------------------
    reg_max_nr_ev = np.zeros((nr_of_regions))
    for region_nr, peak_hour_nr in enumerate(reg_peak_position_h_elec):
        reg_max_nr_ev[region_nr] = reg_trips_ev_24h[region_nr][peak_hour_nr] * assumption_nr_ev_per_trip

    # --------------------------------------
    # 3. Calculate total vehicle battery capacity
    # --------------------------------------
    total_battery_capacity = np.zeros((nr_of_regions))
    for region_nr, reg_nr_EVs in enumerate(reg_max_nr_ev):

        reg_tot_battery_capacity = reg_nr_EVs * assumption_av_usable_battery_capacity

        total_battery_capacity[region_nr] = reg_tot_battery_capacity

    return total_battery_capacity
    '''
    # --------------------------------------
    # 3. Calculate total EV battery capacity of all vehicles which can do V2G
    # --------------------------------------
    # Calculate number of EVs with V2G capability
    reg_nr_v2g_ev = reg_max_nr_ev * assumption_ev_p_with_v2g_capability

    # Calculate demand in peak hour of all EVs with V2G capabilityies
    average_demand_vehicle = reg_peak_demand_h_elec / reg_max_nr_ev
    average_demand_vehicle[np.isnan(average_demand_vehicle)] = 0 #replace nan with 0
    average_demand_vehicle[np.isinf(average_demand_vehicle)] = 0 #replace inf with 0

    # Calculate peak demand of all vehicles with V2G capability
    reg_peak_demand_h_elec_v2g_ev = average_demand_vehicle * reg_nr_v2g_ev

    # Calculate overall maximum capacity of all EVs with V2G capabilities (C_max)
    reg_max_capacity_v2g_ev = reg_nr_v2g_ev * assumption_av_usable_battery_capacity

    # --------------------------------------
    # 4. Calculate flexible "EV battery capacity" used for G2V and v2g
    # -------------------------------------

    # V2G capacity
    actual_v2g_capacity = np.zeros((nr_of_regions))

    # Calculated capacity of safety margin (C_min blue area)
    capacity_safety_margin = reg_max_capacity_v2g_ev * assumption_safety_margin

    # Itereage regions and check whether the actual consumption considering the safety margin is larger
    # than the demand based on the average state-of-charge assumption
    for region_nr, reg_peak_h_capacity in enumerate(reg_max_capacity_v2g_ev):

        # Actual used capacity of all vehicles with V2G capabilities and minimum charging state
        used_capacity_incl_margin = reg_peak_demand_h_elec_v2g_ev[region_nr] + capacity_safety_margin[region_nr]

        # Cannot be higher than maximum storage capacity
        #if (used_capacity_incl_margin > reg_peak_demand_h_elec_v2g_ev[region_nr]):
        #    used_capacity = reg_peak_demand_h_elec_v2g_ev[region_nr]
        #else:
        #    pass
        #used_capacity = reg_peak_demand_h_elec_v2g_ev[region_nr]
        used_capacity = used_capacity_incl_margin

        # Capacity necessary for assumed average SOC of region (SOC_av)
        average_soc_capacity = assumption_av_charging_state * reg_peak_h_capacity

        # If average state of charging smaller than actual used capacity the V2G capacity gets reduced
        if used_capacity > average_soc_capacity:
            v2g_capacity = reg_peak_h_capacity - used_capacity

            if v2g_capacity < 0:
                actual_v2g_capacity[region_nr] = 0
            else:
                # More is use than minimum SOC
                actual_v2g_capacity[region_nr] = v2g_capacity
        else:
            v2g_capacity = reg_peak_h_capacity - average_soc_capacity

            if v2g_capacity < 0:
                actual_v2g_capacity[region_nr] = 0
            else:
                # Less is use than minimum SOC
                actual_v2g_capacity[region_nr] = v2g_capacity

    return actual_v2g_capacity'''
