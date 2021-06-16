from unittest import TestCase

from acopoweropt import colony
from acopoweropt import system


class TestColony(TestCase):
    def test_PowerColony_should_correctly_initialize(self):
        with self.subTest():
            System = system.PowerSystem(name="s15")
            Colony = colony.PowerColony(
                n_ants=5, pheromone_evap_rate=0.25, PowerSystem=System
            )

            self.assertEqual(Colony.n_ants, 5)
            self.assertEqual(Colony.phr_evp_rate, 0.25)
