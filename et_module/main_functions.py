"""
"""
import os
import csv
import numpy as np
from et_module import diffusion_functions
from et_module.plotting_functions import plot_lp_dh

def calc_sigm_load_profile_yh(load_profiles, simulation_yr):
    """Calculate sigmoid diffusion
    """
    pass

def load_curve_assignement(
        curr_yr,
        base_yr,
        yr_until_changed,
        et_service_demand_yh,
        load_profiles,
        regions,
        diffusion='linear'
    ):
    """Assign input electrictiy demand (given as "tranport service"
    for every hour in a year) to an hourly energy demand load profile
    depending (see documentation for more information).

    Arguments
    =========
    curr_yr : int
        Current simulation year
    base_yr : int
        Base year of simulation
    yr_until_changed : int
        Year until changed is fully implemented
    et_service_demand_yh : dict
        Transport energy demand for every region (hourly demand)
    load_profiles : list
        Load profile objects
    regions : list
        All region names
    diffusion : str
        Type of diffusion between base year and end year load profile
            'linear':   Linear change over time towards future load profile
            'sigmoid':  Sigmoid change over time towards future load profile #TODO IMPLENET

    Returns
    =========
    et_demand_yh : array
        Houlry demand, np.array(reg_array_nr, 8760 timesteps)
    """
    et_demand_yh = np.zeros((len(regions), 365 * 24), dtype=float)

    # -------------------
    # Calculate diffusion
    # -------------------
    if diffusion == 'linear':
        simulation_year_p = diffusion_functions.linear_diff(
            base_yr=base_yr,
            curr_yr=curr_yr,
            value_start=0,
            value_end=1,
            yr_until_changed=yr_until_changed)

    if diffusion == 'sigmoid':
        # Default sigmoid parameters
        simulation_year_p = diffusion_functions.sigmoid_diffusion(
            base_yr=base_yr,
            curr_yr=curr_yr,
            end_yr=yr_until_changed,
            sig_midpoint=0,
            sig_steeppness=1)

    # --------------------------------------------------------------------
    # Calculate current year profile with base year and profile from 2015
    # --------------------------------------------------------------------

    # Get base year load profile
    for load_profile in load_profiles:
        if load_profile.name == 'av_lp_2015.csv':
            profile_yh_by = load_profile.shape_yh
            print(" -- A " + str(np.sum(profile_yh_by)))

    # Get future year load profile
    for load_profile in load_profiles:
        if load_profile.name == 'av_lp_2050.csv':
            profile_yh_ey = load_profile.shape_yh
            print(" -- B " + str(np.sum(profile_yh_ey)))
            print(" -- B " + str(profile_yh_ey.shape))

    if base_yr == curr_yr:
        profile_yh_cy = profile_yh_by
    elif curr_yr == yr_until_changed or curr_yr > yr_until_changed:
        profile_yh_cy = profile_yh_ey
    else:

        # Calculate difference between by and ey
        diff_profile = profile_yh_ey - profile_yh_by

        # Calculate difference up to cy
        diff_profile_cy = diff_profile * simulation_year_p


        # Add difference to by
        profile_yh_cy = profile_yh_by + diff_profile_cy


    # Plotting
    plot_lp_dh(profile_yh_cy[0])

    # ------------------------------------
    # Disaggregate for every region
    # ------------------------------------
    for region_array_nr, region in enumerate(regions):

        # Sum total service demand to annual demand
        et_service_demand_y = np.sum(et_service_demand_yh[region])

        # Multiply the annual total service demand with yh load profile
        reg_profile_yh = et_service_demand_y * profile_yh_cy

        # Reshape (365 days, 24hours) into 8760 timesteps
        et_demand_yh[region_array_nr] = reg_profile_yh.reshape(8760)

    return et_demand_yh

def get_load_profiles(path):
    """Read in all load profiles from csv files and store in
    `LoadProfile`.

    Arguments
    =========
    path : str
        Path where load profiles are stored

    Returns
    =======
    load_profiles : list
        All load profiles objects
    """
    load_profiles = []

    # Name of load profiles to load
    names = [
        'av_lp_2015.csv',
        'av_lp_2050.csv']

    for name in names:

        # Create path to csv file
        path_to_csv = os.path.join(path, name)

        # Read in csv load profile
        lp_dh = read_load_shape(path_to_csv)

        lp_dh_p = lp_dh / 100 # convert percentage to fraction

        # Shape for every hour in a year (Assign same profile to every day)
        shape_yd = np.full((365), 1/365) 

        # Shape for every hour in a year (365) * (24)
        shape_yh = shape_yd[:, np.newaxis]  * lp_dh_p 

        # Create load profile
        load_profile = LoadProfile(
            name=name,
            year=name[-8:-4],
            shape_yd=shape_yd,
            shape_yh=shape_yh)

        load_profiles.append(load_profile)

    return load_profiles

def read_load_shape(path_to_csv):
    """This function reads in a load profile from
    a csv file of a single day.

    Arguments
    =========
    path_to_csv : str
        Path to csv file

    Returns
    =======
    shape_dh : array (24)
        Load profile
    """
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        for row in read_lines:
            shape_dh = np.zeros((24), dtype=float)
            for cnt, row_entry in enumerate(row):
                shape_dh[int(_headings[cnt])] = float(row_entry)

    return shape_dh

class LoadProfile(object):
    """Class to store load profiles

    Arguments
    ----------
    name : str
        Name of load profile
    year : int
        Year of load profile
    shape_yd : array
        Yearly load profile
    shape yh : array
        Daily load profile

    Note
    ====
    -   `Yearly load profile (yd)` can be used to derive the energy demand
        of all days in year. This is achieved by multiplying total
        annual demand with this _yd array with the array shape (365)

    -   `Daily load profile (yh)` can be used to derive the energy demand
        of all hours in a year. This is achieved by multiplying total
        annual demand with the this _yh array with the array shape (365, 24).
    """
    def __init__(
            self,
            name,
            year,
            shape_yd,
            shape_yh
        ):
        """Constructor
        """
        self.name = name
        self.year = year
        self.shape_yd = shape_yd
        self.shape_yh = shape_yh
