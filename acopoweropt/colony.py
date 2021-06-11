'''
Singleton classes to initialize an Ant Colony
'''

class Colony:
    '''
    Singleton Class to load a power system data
    '''


    def __init__(self, n_ants: int, pher_evap_rate: float):

        self.n_ants = n_ants
        self.pher_evap_rate = pher_evap_rate
        