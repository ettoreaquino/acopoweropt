"""
Module to handle classes and methods related to the Ant Colony Optimizer
"""

from os import initgroups
import numpy as np
import pandas as pd

from acopoweropt import system


class PowerColony:
    """Singleton Class to load a PowerColony.

    A 'Power Colony' is an Ant Colony with knowledge of Power Systems.

    Parameters
    ----------
    n_ants : int
        Number of ants in the colony
    phr_evp_rate : float
        Pheromone evaporation rate
    power_system_name str
        Power System to serve as environment for the Ant Colony to seek solutions

    Attributes
    ----------
    n_ants : int
        Number of ants in the colony
    pheromone_evap_rate : float
        Pheromone evaporation rate
    initial_paths : pandas.DataFrame
        Dataframe showing the initial paths taken by the ants
    pheromone : pandas.DataFrame
        Dataframe showing the map of pheromone
    """

    def __init__(
        self, n_ants: int, pheromone_evap_rate: float, PowerSystem: system.PowerSystem
    ):

        self.n_ants = n_ants
        self.phr_evp_rate = pheromone_evap_rate
        self.__initialize(PowerSystem=PowerSystem)
        self.__init_phr(PowerSystem=PowerSystem)

    def __initialize(self, PowerSystem: system.PowerSystem):
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

        df = pd.DataFrame(
            [
                self.__seek_food(ant=ant, PowerSystem=PowerSystem)
                for ant in range(1, self.n_ants + 1)
            ]
        ).set_index("ant")

        self.initial_paths = df

    def __seek_food(self, ant: int, PowerSystem: system.PowerSystem) -> dict:

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

    def __init_phr(self, PowerSystem: system.PowerSystem) -> pd.DataFrame:

        df = pd.DataFrame(
            np.zeros((PowerSystem.opzs.index.max(), PowerSystem.opzs.max()))
        )
        df.index = df.index + 1
        df.columns = df.columns + 1
        df = df.rename_axis("tgu")

        for ant in self.initial_paths.itertuples():
            distance = ant.distance
            for i, opz in enumerate(ant.path.split(",")):
                tgu = i + 1
                opz = int(opz)
                pheromone = 1000 / distance

                df.at[tgu, opz] = df.at[tgu, opz] + pheromone

        self.pheromone = df
        self.__calc_pheromone_probabilities()

    def __calc_pheromone_probabilities(self):
        opzs = self.pheromone.columns.tolist()
        n_opzs = len(opzs)

        for opz in self.pheromone.columns:
            p_opz = "p{}".format(opz)
            self.pheromone[p_opz] = (
                100 * self.pheromone[opz] / self.pheromone.iloc[:, :n_opzs].sum(axis=1)
            )

            self.pheromone[p_opz] = self.pheromone[p_opz].round().astype(int)
