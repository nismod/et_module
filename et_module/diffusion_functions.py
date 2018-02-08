
def linear_diff(base_yr, curr_yr, value_start, value_end, yr_until_changed):
    """Calculate a linear diffusion for a current year. If
    the current year is identical to the base year, the
    start value is returned

    Arguments
    ----------
    base_yr : int
        The year of the current simulation
    curr_yr : int
        The year of the current simulation
    value_start : float
        Fraction of population served with fuel_enduse_switch in base year
    value_end : float
        Fraction of population served with fuel_enduse_switch in end year
    yr_until_changed : str
        Year until changed is fully implemented

    Returns
    -------
    fract_cy : float
        The fraction in the simulation year
    """
    # Total number of simulated years
    sim_years = yr_until_changed - base_yr  + 1

    if curr_yr == base_yr or sim_years == 0 or value_end == value_start:
        fract_cy = value_start
    else:
        #-1 because in base year no change
        fract_cy = ((value_end - value_start) / (sim_years - 1)) * (curr_yr - base_yr) + value_start

    return fract_cy
