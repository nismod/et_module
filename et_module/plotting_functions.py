"""Plotting functions
"""
import matplotlib.pyplot as plt

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
