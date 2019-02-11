"""The sector model wrapper for smif to run the energy demand model
"""
import numpy as np

def main(regions, timestep, reg_trips_ev_24h, reg_elec_24h):
    """Runs the electric vehicle model for one `timestep`

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
    assumption_nr_ev_per_trip = 1               # [-] Number of EVs per trip
    assumption_ev_p_with_v2g_capability = 1.0   # [%] Percentage of EVs not used for v2g and G2V
    assumption_av_charging_state = 0.5          # [%] Assumed average charging state of EVs before peak trip hour
    assumption_av_usable_battery_capacity = 30.0  # [kwh] Average (storage) capacity of EV Source: https://en.wikipedia.org/wiki/Electric_vehicle_battery
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
    actual_v2g_capacity = np.zeros((nr_of_regions))

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
            actual_v2g_capacity[region_nr] = reg_peak_h_capacity - used_capacity

            if (reg_peak_h_capacity - used_capacity) < 0:
                actual_v2g_capacity[region_nr] = 0

            # Test that not minus capacity
            #assert (reg_peak_h_capacity - used_capacity) >= 0
        else:
            # Less is use than minimum SOC
            actual_v2g_capacity[region_nr] = reg_peak_h_capacity - average_soc_capacity

            if (reg_peak_h_capacity - average_soc_capacity) < 0:
                actual_v2g_capacity[region_nr] = 0

            # Test that not minus capacity
            #assert (reg_peak_h_capacity - average_soc_capacity) >= 0

    return actual_v2g_capacity


if __name__ == '__main__':

    main()