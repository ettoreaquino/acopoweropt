from unittest import TestCase

from acopoweropt import colony
from acopoweropt import system


class TestColony(TestCase):
    def test_PowerColony_should_correctly_initialize(self):
        with self.subTest():
            System = system.PowerSystem(name="s10")
            n_ants = 5
            pheromone_evap_rate = 0.25
            Colony = colony.PowerColony(
                n_ants=n_ants,
                pheromone_evap_rate=pheromone_evap_rate,
                PowerSystem=System,
            )

            self.assertEqual(Colony.n_ants, n_ants)
            self.assertEqual(Colony.pheromone_evap_rate, pheromone_evap_rate)

            # Initial paths should have the same n of rows as the number of ants
            self.assertTrue(len(Colony.paths[0].index) == n_ants)

            # Pheromone matrix should have a shape of max(OPZs) x TGUs
            self.assertTrue(
                Colony.pheromone.shape == (System.opzs.max(), System.opzs.index.max())
            )
