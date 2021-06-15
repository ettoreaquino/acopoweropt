"""
Module to handle classes and methods related to the Ant Colony Optimizer
"""

import pandas as pd
import random

from acopoweropt import system


class Colony:
    """Singleton Class to load an Ant Colony.

    Parameters
    ----------
    n_ants : int
        Number of ants in the colony
    phr_evp_rate : float
        Pheromone evaporation rate

    Attributes
    ----------
    n_ants : int
        Number of ants in the colony
    phr_evp_rate : float
        Pheromone evaporation rate
    """

    def __init__(self, n_ants: int, phr_evp_rate: float):

        self.n_ants = n_ants
        self.phr_evp_rate = phr_evp_rate

    def seek_food(self, ant: int, PowerSystem: system.PowerSystem) -> dict:
        
        option = PowerSystem.sample_operation()
        result = PowerSystem.solve(operation=option)
        distance = result.get("Ft")
        status = result.get("status")

        return {
            "ant": ant,
            "path": ",".join([str(int) for int in option.opz.to_list()]),
            "status": status,
            "distance": distance,
            "tau": 1 / distance,
        }

    def initialize(self, power_system_name: str):
        """Initialize colony

        Initializes colony by seting the ants towards random paths. Although not ideal
        each random path will make use of PowerSystem.sample_operation() and the path
        distance will be calculated using PowerSystem.solve(operation).

        Later improvements should aim to decouple the PowerSystem from within the colony
        initialization method.

        Parameters
        ----------

        Returns
        -------
        pd.DataFrame
            A dataframe showing the informations regarding the initial paths taken by the ants
        """

        PSystem = system.PowerSystem(name=power_system_name)

        df = pd.DataFrame(
            [
                self.seek_food(ant=ant, PowerSystem=PSystem)
                for ant in range(1, self.n_ants + 1)
            ]
        ).set_index("ant")

        self.initial_paths = df