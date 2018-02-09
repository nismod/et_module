import numpy as np
from et_module import main_functions

def test_load_curve_assignement():
    """
    """
    et_service_demand_yh = {
        'regA': np.ones((365, 24)),
        'regB': np.ones((365, 24))}

    regions = ['regA', 'regB']
    charging_scenario = 'sheduled'

    flat_profile_yd = np.full((365), 1/365)
    flat_profile_yh = np.full((365, 24), 1/8760)

    load_profiles = [
        main_functions.LoadProfile(
            name='av_lp_2015.csv',
            year=2015,
            shape_yd=flat_profile_yd,
            shape_yh=flat_profile_yh),
        main_functions.LoadProfile(
            name='av_lp_2050.csv',
            year=2050,
            shape_yd=flat_profile_yd,
            shape_yh=flat_profile_yh)
        ]

    #Sheduled
    '''result = main_functions.load_curve_assignement(
        curr_yr=2015,
        base_yr=2015,
        yr_until_changed=2050,
        et_service_demand_yh=et_service_demand_yh,
        load_profiles=load_profiles,
        regions=regions,
        charging_scenario='sheduled',
        diffusion='linear')

    reg_array_nr = range(len(regions))[0]
    year_hour_nr = 0

    assert result[reg_array_nr][year_hour_nr] == 1

    #Unsheduled
    result = main_functions.load_curve_assignement(
        curr_yr=2015,
        base_yr=2015,
        yr_until_changed=2050,
        et_service_demand_yh=et_service_demand_yh,
        load_profiles=load_profiles,
        regions=regions,
        charging_scenario='unsheduled',
        diffusion='linear')

    assert result[reg_array_nr][year_hour_nr] == 1
    '''

    # ---
    not_flat_profile_yh = np.full((365, 24), 1/8760)

    tot_daily_percentages_year = sum(list(range(24))) * 365

    for day in range(365):
        hours_in_day = list(range(24))
        for h in hours_in_day:
            not_flat_profile_yh[day][h] = h / tot_daily_percentages_year

    load_profiles = [
        main_functions.LoadProfile(
            name='av_lp_2015.csv',
            year=2015,
            shape_yd=flat_profile_yd,
            shape_yh=flat_profile_yh),
        main_functions.LoadProfile(
            name='av_lp_2050.csv',
            year=2050,
            shape_yd=flat_profile_yd,
            shape_yh=not_flat_profile_yh)
        ]

    result = main_functions.load_curve_assignement(
        curr_yr=2050,
        base_yr=2015,
        yr_until_changed=2050,
        et_service_demand_yh=et_service_demand_yh,
        load_profiles=load_profiles,
        regions=regions,
        charging_scenario='sheduled',
        diffusion='linear')

    reg_array_nr = range(len(regions))[0]
    year_hour_nr = 5

    expected = not_flat_profile_yh[0][year_hour_nr] * 8760

    assert result[reg_array_nr][year_hour_nr] == expected

    # ---
    result = main_functions.load_curve_assignement(
        curr_yr=2025,
        base_yr=2000,
        yr_until_changed=2050,
        et_service_demand_yh=et_service_demand_yh,
        load_profiles=load_profiles,
        regions=regions,
        charging_scenario='sheduled',
        diffusion='linear')

    reg_array_nr = range(len(regions))[0]
    year_hour_nr = 5

    half_between_cy_and_ey = 0.5 #difference between 0 and 0.5 for first hour

    by = flat_profile_yh[0][year_hour_nr]
    ey = not_flat_profile_yh[0][year_hour_nr]
    expected = (by + ((ey - by) * half_between_cy_and_ey)) * 8760

    assert result[reg_array_nr][year_hour_nr] == expected
