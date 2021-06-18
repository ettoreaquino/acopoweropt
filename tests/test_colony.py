from unittest import TestCase

from acopoweropt import colony
from acopoweropt import system


class TestColony(TestCase):
    def test_PowerColony_should_correctly_initialize(self):
        with self.subTest():
            PowerSystem = system.PowerSystem(name="s10")
            n_ants = 5
            pheromone_evp_rate = {"worst": 0.4, "mean": 0.25, "best": 0.05}
            Colony = colony.PowerColony(
                n_ants=n_ants,
                pheromone_evp_rate=pheromone_evp_rate,
                power_system=PowerSystem,
            )

            self.assertEqual(Colony.n_ants, n_ants)
            self.assertEqual(Colony.pheromone_evp_rate, pheromone_evp_rate)

            # Initial paths should have the same n of rows as the number of ants
            self.assertTrue(len(Colony.paths.index.unique()) == n_ants)

            # Pheromone matrix should have a shape of max(OPZs) x TGUs
            self.assertTrue(
                Colony.pheromone.shape
                == (
                    PowerSystem.operative_zones.max(),
                    PowerSystem.operative_zones.index.max(),
                )
            )
