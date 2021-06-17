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
    pheromone_evap_rate : float
        Pheromone evaporation rate
    power_system_name str
        Power System to serve as environment for the Ant Colony to seek solutions

    Attributes
    ----------
    n_ants : int
        Number of ants in the colony
    pheromone_evap_rate : float
        Pheromone evaporation rate
    paths : dict
        A dictionary of DataFrames showing the paths taken by the ants on each iteraction
    pheromone : pandas.DataFrame
        Dataframe showing the map of pheromone
    """

    def __init__(
        self, n_ants: int, pheromone_evap_rate: float, PowerSystem: system.PowerSystem
    ):

        self.n_ants = n_ants
        self.pheromone_evap_rate = pheromone_evap_rate
        
        # Initialize colony 
        self.__initialize(PowerSystem=PowerSystem)
        self.__init_phr(PowerSystem=PowerSystem)

        # Initial pheromone update in init
        self.update_pheromone(paths=self.paths[0])
        self.pheromone_history = {0: self.pheromone}

    def __initialize(self, PowerSystem: system.PowerSystem):
        #Initialize colony

        #Initializes colony by seting the ants towards random paths. Although not ideal
        #each random path will make use of PowerSystem.sample_operation() and the path
        #distance will be calculated using PowerSystem.solve(operation).

        #Later improvements should aim to decouple the PowerSystem from within the colony
        #initialization method.
    
        df = pd.DataFrame(
            [
                self.__initial_seek(ant=ant, PowerSystem=PowerSystem)
                for ant in range(1, self.n_ants + 1)
            ]
        ).set_index("ant")

        self.paths = {0:df}

    def __initial_seek(self, ant: int, PowerSystem: system.PowerSystem) -> dict:
        
        operation = PowerSystem.sample_operation()

        return self.seek_food(ant=ant, operation=operation, PowerSystem=PowerSystem)

    def __init_phr(self, PowerSystem: system.PowerSystem) -> pd.DataFrame:
        df = pd.DataFrame(
            np.zeros((PowerSystem.opzs.max(), PowerSystem.opzs.index.max()))
        )
        df.index = df.index + 1
        df.columns = df.columns + 1
        df = df.rename_axis("opz")

        self.pheromone = df

    def seek_food(self, ant: int, operation: pd.DataFrame, PowerSystem: system.PowerSystem) -> dict:
        """Gets the result of a food seeking

        Parameters
        ----------
        paths : pandas.Dataframe
            The Dataframe representing the paths taken by the ants

        Returns
        -------
        pandas.DataFrame
            DataFrame of the updated pheromone matrix

        """
        result = PowerSystem.solve(operation=operation)
        distance = result.get("Ft")
        status = result.get("status")

        return {
            "ant": ant,
            "path": ",".join([str(int) for int in operation.opz.to_list()]),
            "status": status,
            "distance": distance,
            "tau": 1 / distance,
        }

    def update_pheromone(self, paths: pd.DataFrame) -> pd.DataFrame:
        """Updates the PowerColony.pheromone in place

        Parameters
        ----------
        paths : pandas.Dataframe
            The Dataframe representing the paths taken by the ants

        Returns
        -------
        pandas.DataFrame
            DataFrame of the updated pheromone matrix

        """
        for ant in paths.itertuples():
            distance = ant.distance

            for i, opz in enumerate(ant.path.split(",")):
                tgu = i + 1
                opz = int(opz)
                pheromone = round(1000 / distance, 4)

                self.pheromone.at[opz, tgu] = self.pheromone.at[opz, tgu] + pheromone

        return self.pheromone

    def choose_path(self) -> list:
        """Returns a possible path to be taken based on the pheromone matrix

        Parameters
        ----------

        Returns
        -------
        list
            A sequence of operative zones.
        """
        return [
            self.pheromone.sample(n=1, weights=self.pheromone[tgu], axis=0).index[0]
            for tgu in self.pheromone.columns
        ]
