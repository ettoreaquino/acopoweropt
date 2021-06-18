"""
Module to handle classes and methods related to the Ant Colony Optimizer
"""
import os
import imageio
import numpy as np
import pandas as pd
import random
import time

from acopoweropt import system

import matplotlib.pyplot as plt


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
        self.__init_best_and_worst(power_system=power_system)

        # Initial pheromone update in init
        self.update_best_and_worst(
            paths=self.paths.query("iteration == {i}".format(i=0))
        )
        self.pheromone = self.update_pheromone(
            paths=self.paths.query("iteration == {i}".format(i=0)), iteration=0
        )

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
                seek_food(
                    ant=ant, iteration=0, operation=operation, power_system=power_system
                )
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
        self.pheromone_history = {0: df}

    def __init_best_and_worst(self, power_system: system.PowerSystem):
        sample_path = ",".join(["1"] * power_system.operative_zones.shape[0])

        self.best_and_worst = pd.DataFrame(
            [
                {
                    "ant": "best",
                    "iteration": 0,
                    "path": sample_path,
                    "status": "",
                    "distance": np.inf,
                },
                {
                    "ant": "worst",
                    "iteration": 0,
                    "path": sample_path,
                    "status": "",
                    "distance": -np.inf,
                },
            ]
        ).set_index("ant")

    def update_pheromone(self, paths: pd.DataFrame, iteration: int):
        """Updates the PowerColony.pheromone in place

        Parameters
        ----------
        paths : pandas.Dataframe
            The Dataframe representing the paths taken by the ants
        iteration : int
            The iteration when the update happened

        Returns
        -------
        pandas.DataFrame
            DataFrame of the updated pheromone matrix

        """
        pheromone_df = self.pheromone.copy()

        for ant in paths.itertuples():
            distance = ant.distance

            for i, opz in enumerate(ant.path.split(",")):
                tgu = i + 1
                opz = int(opz)
                pheromone = 1000 / distance

                pheromone_df.at[opz, tgu] = pheromone_df.at[opz, tgu] + pheromone

        self.pheromone_history.update({iteration: self.pheromone})
        return pheromone_df

    def evaporate_pheromone(
        self, paths: pd.DataFrame, power_system: system.PowerSystem
    ):
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

        best_path = self.best_and_worst.loc["best"].path.split(",")
        worst_path = self.best_and_worst.loc["worst"].path.split(",")
        pheromone_df = self.pheromone.copy()

        for ant in paths.itertuples():
            for i, opz in enumerate(ant.path.split(",")):
                tgu = i + 1  # TGUs are indexed from 1
                opz = int(opz)

                if power_system.operative_zones[tgu] == 1:
                    evaporation = 1 - self.pheromone_evp_rate["best"]
                else:
                    if opz == best_path[i]:
                        evaporation = 1 - self.pheromone_evp_rate["best"]
                    elif opz == worst_path[i]:
                        evaporation = 1 - self.pheromone_evp_rate["worst"]
                    else:
                        evaporation = 1 - self.pheromone_evp_rate["mean"]

                pheromone_df.at[opz, tgu] = pheromone_df.at[opz, tgu] * evaporation

        return pheromone_df

    def update_best_and_worst(self, paths: pd.DataFrame):

        best = paths[paths.distance == paths.distance.min()]
        worst = paths[paths.distance == paths.distance.max()]

        best_value = best.distance.iloc[0]
        best_path = best.path.iloc[0]
        best_status = best.status.iloc[0]
        best_iter = best.iteration.iloc[0]

        worst_value = worst.distance.iloc[0]
        worst_path = worst.path.iloc[0]
        worst_status = worst.status.iloc[0]
        worst_iter = worst.iteration.iloc[0]

        if best_value <= self.best_and_worst.loc["best"].distance:
            self.best_and_worst.at["best", "iteration"] = best_iter
            self.best_and_worst.at["best", "path"] = best_path
            self.best_and_worst.at["best", "status"] = best_status
            self.best_and_worst.at["best", "distance"] = best_value

        if worst_value >= self.best_and_worst.loc["worst"].distance:
            self.best_and_worst.at["worst", "iteration"] = worst_iter
            self.best_and_worst.at["worst", "path"] = worst_path
            self.best_and_worst.at["worst", "status"] = worst_status
            self.best_and_worst.at["worst", "distance"] = worst_value

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
            self.pheromone.sample(
                n=1,
                weights=[
                    i[1] / self.pheromone[tgu].sum()
                    for i in self.pheromone[tgu].iteritems()
                ],
                axis=0,
            ).index[0]
            for tgu in self.pheromone.columns
        ]

    def seek(
        self,
        max_iter: int,
        power_system: system.PowerSystem,
        show_progress: bool = False,
    ):

        start = time.time()
        print("Initializing seek...")

        for i in range(max_iter):
            # Getting last taken paths
            paths = self.paths.query("iteration == {i}".format(i=i))

            # Evaporate Pheromone
            self.pheromone = self.evaporate_pheromone(
                paths=paths, power_system=power_system
            )

            # Selecting Ants (80/20) to follow or not the pheromone paths
            taken_paths = []
            for ant in range(1, self.n_ants + 1):
                decision = random.random()
                if decision <= 0.8:
                    # ANT Follows Path
                    operative_zones = self.choose_path()
                    existing_path = paths.query(
                        "path == '{}'".format(
                            ",".join([str(n) for n in operative_zones])
                        )
                    )

                    # Check if chosen path was already calculated:
                    if existing_path.values.size != 0:
                        solution = existing_path.reset_index().loc[0]
                        solution["ant"] = ant
                        solution["iteration"] = i + 1
                        solution = solution.to_frame().T.set_index("ant")
                        taken_paths.append(solution)
                    else:
                        operation = power_system.get_operation(
                            operative_zones=operative_zones
                        )
                        solution = pd.DataFrame(
                            [
                                seek_food(
                                    ant=ant,
                                    iteration=i + 1,
                                    operation=operation,
                                    power_system=power_system,
                                )
                            ]
                        ).set_index("ant")
                        taken_paths.append(solution)

                else:
                    # ANT Sets to new path
                    operation = power_system.sample_operation()
                    solution = pd.DataFrame(
                        [
                            seek_food(
                                ant=ant,
                                iteration=i + 1,
                                operation=operation,
                                power_system=power_system,
                            )
                        ]
                    ).set_index("ant")
                    taken_paths.append(solution)

            # Updating Paths
            new_paths = pd.concat(taken_paths).sort_index()
            self.paths = self.paths.append(new_paths)

            # Updating Best and Worst Paths
            self.update_best_and_worst(paths=new_paths)

            # Updating Pheromone
            self.pheromone = self.update_pheromone(paths=new_paths, iteration=i + 1)

            # Plot evolution
            if show_progress:
                print(
                    "iter: {}, MinValue found: {}".format(
                        i + 1, new_paths.distance.min()
                    )
                )
                # df = self.pheromone.T
                # df['tgu'] = df.index
                # df.plot.bar(x='tgu', y=self.pheromone.index, rot=0)
        end = time.time()
        print(
            "========================\nSeek finished in {}s:\n".format(
                round(end - start, 2)
            )
        )

    def create_pheromone_movie(self, duration: float):

        directory = "images"
        plt.title("Pheromone Intensity")
        plt.xlabel("Thermal Generation Unit")
        plt.ioff()

        if not os.path.exists(directory):
            os.mkdir(directory)
            print("Directory {} Created".format(directory))
        else:
            raise Exception("Directory {} already exists".format(directory))

        for iteration in self.pheromone_history:
            df = self.pheromone_history[iteration]
            ax = df.T.plot(kind="bar")
            fig = ax.get_figure()
            plt.close(fig)
            fig.savefig("images/phr_{}.png".format(iteration))

        images = []
        for filename in os.listdir(directory):
            images.append(imageio.imread(os.path.join(directory, filename)))
        imageio.mimsave("pheromone.gif", images, duration=duration)
