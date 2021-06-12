'''
Singleton classes to initialize an Ant Colony
'''

import pandas as pd
import random

class Colony:
    '''
    Singleton Class to load a Colony.
    
    Attributes:
        n_ants: Number of ants in the colony
        food_srcs: Dataframe of possible food sources
        phr_evp_rate: Pheromone evaporation rate
    '''

    def __init__(self, n_ants: int, phr_evp_rate: float):

        self.n_ants = n_ants
        self.phr_evp_rate = phr_evp_rate
        