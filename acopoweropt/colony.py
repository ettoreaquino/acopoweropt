"""
Module to handle classes and methods related to the Ant Colony Optimizer
"""
import numpy as np
import pandas as pd

from acopoweropt import system


def seek_food(
    ant: int, iteration: int, operation: pd.DataFrame, power_system: system.PowerSystem
) -> dict:
    """Gets the result of a food seeking

    Parameters
    ----------
    ant : int
        The id indicating the ant
    iteration : int
        The id of which iteration the seek occurred
    operation : pd.DataFrame
        The operation data to be used
    power_system : system.PowerSystem
        The PowerSystem instance which will serve as an environment for the ants to seek food

    Returns
    -------
    pandas.DataFrame
        DataFrame of the updated pheromone matrix

    """
    result = power_system.solve(operation=operation)
    distance = result.get("Ft")
    status = result.get("status")

    return {
        "ant": ant,
        "iteration": iteration,
        "path": ",".join([str(n) for n in operation.opz.to_list()]),
        "status": status,
        "distance": distance,
        "tau": 1 / distance,
    }


class PowerColony:
    """Singleton Class to load a PowerColony.

    A 'Power Colony' is an Ant Colony with knowledge of Power Systems.

    Parameters
    ----------
    n_ants : int
        Number of ants in the colony
    pheromone_evp_rate : dict
        Pheromone evaporation rate
    power_system_name str
        Power System to serve as environment for the Ant Colony to seek solutions

    Attributes
    ----------
    n_ants : int
        Number of ants in the colony
    pheromone_evp_rate : dict
        Pheromone evaporation rate
    paths : dict
        A dictionary of DataFrames showing the paths taken by the ants on each iteration
    pheromone : pandas.DataFrame
        Dataframe showing the map of pheromone
    """

    def __init__(
        self, n_ants: int, pheromone_evp_rate: dict, power_system: system.PowerSystem
    ):

        self.n_ants = n_ants
        self.pheromone_evp_rate = pheromone_evp_rate

        # Initialize colony
        self.__initialize(power_system=power_system)
        self.__init_phr(power_system=power_system)

        # Initial pheromone update in init
        self.update_pheromone(paths=self.paths.query("iteration == {i}".format(i=0)))
        self.pheromone_history = {0: self.pheromone}

    def __initialize(self, power_system: system.PowerSystem):
        # Initialize colony

        # Initializes colony by setting the ants towards random paths. Although not ideal
        # each random path will make use of PowerSystem.sample_operation() and the path
        # distance will be calculated using PowerSystem.solve(operation).

        # Later improvements should aim to decouple the PowerSystem from within the colony
        # initialization method.

        paths = []
        for ant in range(1, self.n_ants + 1):
            operation = power_system.sample_operation()
            paths.append(
                seek_food(ant=ant, iteration=0, operation=operation, power_system=power_system)
            )

        df = pd.DataFrame(paths).set_index("ant")
        self.paths = df

    def __init_phr(self, power_system: system.PowerSystem):
        df = pd.DataFrame(
            np.zeros(
                (
                    power_system.operative_zones.max(),
                    power_system.operative_zones.index.max(),
                )
            )
        )
        df.index = df.index + 1
        df.columns = df.columns + 1
        df = df.rename_axis("opz")

        self.pheromone = df

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

            for i, opz in enumerate(ant.path.split(',')):
                tgu = i + 1
                opz = int(opz)
                pheromone = round(1000 / distance, 4)

                self.pheromone.at[opz, tgu] = self.pheromone.at[opz, tgu] + pheromone

        return self.pheromone

    def evaporate_pheromone(self, paths: pd.DataFrame, power_system: system.PowerSystem):
        """Updates the PowerColony.pheromone in place

        Parameters
        ----------
        paths : pandas.Dataframe
            The Dataframe representing the paths taken by the ants
        power_system : system.PowerSystem
            The Power System class which serves as the environment for the colony

        Returns
        -------
        pandas.DataFrame
            DataFrame of the updated pheromone matrix

        """

        best_path = paths[paths.distance == paths.distance.min()].iloc[0].path.split(',')
        worst_path = paths[paths.distance == paths.distance.max()].iloc[0].path.split(',')

        for ant in paths.itertuples():
            for i, opz in enumerate(ant.path.split(',')):
                tgu = i + 1  # TGUs are indexed from 1
                opz = int(opz)

                if power_system.operative_zones[tgu] == 1:
                    evaporation = (1 - self.pheromone_evp_rate['best'])
                else:
                    if opz == best_path[i]:
                        evaporation = (1 - self.pheromone_evp_rate['best'])
                    elif opz == worst_path[i]:
                        evaporation = (1 - self.pheromone_evp_rate['worst'])
                    else:
                        evaporation = (1 - self.pheromone_evp_rate['mean'])

                self.pheromone.at[opz, tgu] = evaporation * self.pheromone.at[opz, tgu]

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
