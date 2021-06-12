from unittest import TestCase

from acopoweropt import system


class TestSystem(TestCase):
    def test_System_should_load_powersystem(self):
        with self.subTest():
            System = system.PowerSystem(name="s10")

            self.assertEqual(System.load, 2700)

    def test_System_should_break_when_name_does_not_exist(self):
        with self.subTest():
            with self.assertRaises(Exception):
                System = system.PowerSystem(name="s35")

    def test_System_should_return_array_of_thermal_generation_unit_ids(self):
        with self.subTest():
            System = system.PowerSystem(name="s10")

            self.assertEqual(
                System.tgus.tolist(), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            )

    def test_System_should_return_df_of_tgu_and_number_of_operative_zones(self):
        with self.subTest():
            System = system.PowerSystem(name="s15")

            self.assertEqual(
                System.opzs.options.to_list(),
                [1, 4, 1, 1, 4, 4, 1, 1, 1, 1, 1, 3, 1, 1, 1],
            )

    def test_System_should_correctly_randomize_a_combination_of_tgus(self):
        with self.subTest():
            PSystem = system.PowerSystem(name="s10")

            opt = PSystem.rand_opt_zones()

            self.assertEqual(len(opt), len(PSystem.tgus))
            self.assertTrue(opt[0] <= PSystem.opzs.iloc[0].options)
