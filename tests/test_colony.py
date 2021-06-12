from unittest import TestCase

from acopoweropt import colony


class TestColony(TestCase):
    def test_colony_should_receive_ants(self):
        with self.subTest():
            Colony = colony.Colony(n_ants=5, phr_evp_rate=0.25)

            self.assertEqual(Colony.n_ants, 5)
            self.assertEqual(Colony.phr_evp_rate, 0.25)
