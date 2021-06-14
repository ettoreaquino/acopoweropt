import pandas as pd
from unittest import TestCase

from acopoweropt import colony


class TestColony(TestCase):
    def test_Colony_should_receive_ants(self):
        with self.subTest():
            Colony = colony.Colony(n_ants=5, phr_evp_rate=0.25, power_system_name="s10")

            self.assertEqual(Colony.n_ants, 5)
            self.assertEqual(Colony.phr_evp_rate, 0.25)
            self.assertEqual(Colony.power_system_name, "s10")

    def test_Colony_should_initialize_paths(self):
        with self.subTest():
            Colony = colony.Colony(n_ants=5, phr_evp_rate=0.25, power_system_name="s10")

            Colony.initialize()

            self.assertTrue(type(Colony.initial_paths) == pd.DataFrame)
