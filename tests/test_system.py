from unittest import TestCase

from acopoweropt import system


class TestSystem(TestCase):
    def test_System_should_load_powersystem(self):
        with self.subTest():
            System = system.PowerSystem(name="s10")

            self.assertEqual(System.demand, 2700)

    def test_System_should_break_when_name_does_not_exist(self):
        with self.subTest():
            with self.assertRaises(Exception):
                System = system.PowerSystem(name="s35")
