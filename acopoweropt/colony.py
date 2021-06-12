"""
Module to handle classes and methods related to the Ant Colony Optimizer
"""

import pandas as pd
import random


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
