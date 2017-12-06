"""
"""
import os
import csv
import numpy as np

def calc_sigm_load_profile_yh(load_profiles, simulation_yr):
    """Calculate sigmoid diffusion
    """
    pass

def temporal_disaggregation(simulation_yr, et_demand_y, load_profiles, region_names):
    """Disaggregat temporally from y to yh

    Arguments
    =========
    simulation_yr : float
        Simulation year
    et_demand_y : dict
        Transport annual energy demand for every region
    load_profiles : list
        Load profile objects
    region_names : list
        All region names
    """
    et_demand_yh = {}

    # --------------------------------------------------------------------
    # Calculate current year profile with base year and profile from 2015
    # --------------------------------------------------------------------
    #TODO: Write sigmoid diffusion and calculate cy profile
    #profile_yh = calc_sigm_load_profile_yh(load_profiles, simulation_yr)
    for load_profile in load_profiles:
        if load_profile.name == 'av_lp_2015.csv':
            profile_yh = load_profile.shape_yh

    # ------------------------------------
    # Disaggregate for every region
    # ------------------------------------
    for region in region_names:
        reg_profile_yh = et_demand_y[region] * profile_yh
        et_demand_yh[region] = reg_profile_yh

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
    names = ['av_lp_2015.csv', 'av_lp_2050.csv']

    for name in names:

        # Create path to csv file
        path_to_csv = os.path.join(path, name)

        # Read in csv load profile
        lp_dh = read_load_shape(path_to_csv)

        # Shape for every hour in a year (Assign same profile to every day)
        shape_yd = np.full((365), 1/365) 

        # Shape for every hour in a year (365) * (24)
        shape_yh = shape_yd[:, np.newaxis]  * lp_dh 

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
