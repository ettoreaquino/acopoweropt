'''
Singleton classes to load a Power System configuration
'''

import json
import pandas as pd

class PowerSystem:
    '''
    Singleton Class to load a power system data
    '''


    def __init__(self, name: str):
        # Loading selected system
        self.__load(name=name)

        # Defining key attributes
        self.tgus = self.data.tgu.unique() # n of Thermal Generation Units
        self.opzs = self.data.tgu.value_counts().sort_index().to_frame(name='total') # Operative Zones by each 


    def __load(self, name:str):
        try:
            with open('systems.json') as f:
                data = json.loads(f.read())

                df = pd.DataFrame(data[name]['data'])
                df = df.rename(columns=df.iloc[0]).drop([0])

                self.name = name
                self.load = data[name]['load']
                self.data = df

        except Exception as e:
            print("Error reading system {} from systems.json".format(system))