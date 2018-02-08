import os
import sys
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
from energy_demand.plotting import plotting_program
from energy_demand.basic import basic_functions, conversions
from matplotlib.patches import Rectangle
from scipy import stats

# INFO
# https://stackoverflow.com/questions/35099130/change-spacing-of-dashes-in-dashed-line-in-matplotlib
# https://www.packtpub.com/mapt/book/big_data_and_business_intelligence/9781849513265/4/ch04lvl1sec56/using-a-logarithmic-scale
# Setting x labels: https://matplotlib.org/examples/pylab_examples/major_minor_demo1.html

def plot_lp_dh(data_dh_modelled):
    """Plot load curve of a day
    """
    x_values = range(24)

    plt.plot(
        x_values,
        list(data_dh_modelled),
        color='red',
        label='modelled')

    plt.tight_layout()

    plt.margins(x=0)

    plt.show()

