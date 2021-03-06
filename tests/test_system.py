import pandas as pd
from unittest import TestCase

from acopoweropt import system


class TestSystem(TestCase):
    def test_System_should_correctly_load_powersystem(self):
        with self.subTest():
            System = system.PowerSystem(name="s10")

            # Demand
            self.assertEqual(System.demand, 2700)

            # Data
            self.assertTrue(type(System.data) == pd.DataFrame)
            self.assertTrue(System.data.index.name == "tgu")
            self.assertTrue(
                System.data.columns.to_list() == ["opz", "a", "b", "c", "Pmin", "Pmax"]
            )

    def test_System_should_raise_exception_when_name_does_not_exist(self):
        with self.subTest():
            with self.assertRaises(Exception):
                System = system.PowerSystem(name="s35")

    def test_System_sample_operation_should_be_a_valid_sample(self):
        with self.subTest():
            System = system.PowerSystem(name="s15")

            sample_operation = System.sample_operation()

            self.assertTrue(type(sample_operation) == pd.DataFrame)
            self.assertTrue(
                System.data.index.unique().to_list() == sample_operation.index.to_list()
            )

    def test_System_get_operation_should_raise_if_operative_zones_are_invalid(self):
        with self.subTest():
            with self.assertRaises(Exception):
                System = system.PowerSystem(name="s10")

                opzs = [2, 3, 1, 2, 1, 1, 3, 1]
                operation = System.get_operation(operative_zones=opzs)

    def test_System_get_operation_should_return_a_valid_operation(self):
        with self.subTest():
            System = system.PowerSystem(name="s15")

            opzs = [1, 2, 1, 1, 1, 4, 1, 1, 1, 1, 1, 2, 1, 1, 1]
            operation = System.get_operation(operative_zones=opzs)

            self.assertTrue(type(operation) == pd.DataFrame)
            self.assertTrue(
                System.data.index.unique().to_list() == operation.index.to_list()
            )
            self.assertTrue(
                operation.columns.to_list() == ["opz", "a", "b", "c", "Pmin", "Pmax"]
            )

    def test_System_should_solve_operation(self):
        with self.subTest():
            System = system.PowerSystem(name="s15")

            operation = System.sample_operation()
            solution = System.solve(operation=operation)

            self.assertTrue(type(solution.get("status")) == str)
            self.assertTrue(type(solution.get("Ft")) == float)
            self.assertTrue(type(solution.get("operation")) == pd.DataFrame)
