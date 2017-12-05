"""
"""
import os
import csv
import numpy as np

def calc_sigm_load_profile_yh(load_profiles, curr_yr):
    """Calculate sigmoid diffusion
    """
    pass

def temporal_disaggregation(curr_yr, et_demand_y, load_profiles, region_names):
    """Disaggregat temporally from y to yh
    """
    et_demand_yh = {}

    # --------------------------------------------------------------------
    # Calculate current year profile with base year and profile from 2015
    # --------------------------------------------------------------------
    #TODO: Write sigmoid diffusion and calculate cy profile
    #profile_yh = calc_sigm_load_profile_yh(load_profiles, curr_yr)
    for load_profile in load_profiles:
        if load_profile.name == 'av_lp_2015.csv':
            profile_yh = load_profile.shape_yh

    # ------------
    # Disaggregate
    # ------------
    for region in region_names:
        reg_profile_yh = et_demand_y[region] * profile_yh
        et_demand_yh[region] = reg_profile_yh

    return et_demand_yh

def get_load_profiles(path):
    """
    """
    all_load_profiles = []

    # Name of load profiles to load
    names = ['av_lp_2015.csv', 'av_lp_2050.csv']

    for name in names:

        path_to_csv = os.path.join(path, name)
        lp_dh = read_load_shape(path_to_csv)

        # -------------------------------
        # Shape for every hour in a year
        # -------------------------------
        shape_yd = np.full((365), 1/365) #Every day the same

        # -------------------------------
        # Shape for every hour in a year
        # -------------------------------
        shape_yh = shape_yd[:, np.newaxis]  * lp_dh#Assign same profile to every day

        # --------------------
        # Create load profile
        # --------------------
        lp = LoadProfile(
            name=name,
            year=name[-8:-4],
            shape_yd=shape_yd,
            shape_yh=shape_yh)

        all_load_profiles.append(lp)

    return all_load_profiles

def read_load_shape(path_to_csv):
    """This function reads in load profile from
    a csv file

    Arguments
    ----------
    path_to_csv : str
        Path to csv file
    """
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        for row in read_lines:
            dh_shape = np.zeros((24), dtype=float)
            for cnt, row_entry in enumerate(row):
                dh_shape[int(_headings[cnt])] = float(row_entry)

    return dh_shape

class LoadProfile(object):
    """L

    Arguments
    ----------
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
