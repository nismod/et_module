from et_module.main import main
import numpy as np


class TestMainRunner:

    def test_main_runner(self):

        regions = ['A', 'B', 'C']
        timestep = 2010
        trips = np.array([[0, 10, 0], [5, 0, 5], [2, 2, 0]])
        elec = np.array([[0, 10, 0], [5, 0, 5], [2, 2, 0]])

        actual = main(regions, timestep, trips, elec)
        expected = np.array([150.,  75.,  30.])

        np.testing.assert_allclose(actual, expected)