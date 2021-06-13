"""
Module to handle classes and methods related to a selected Power System.

This module should follow a systems.json file:
{ 
    "{name}": {
        "load": float,
        "data": list<list>
    },
    {...},
    "{name}": {
        "load": float,
        "data": list<list>
    }
}

Where {name} should be changed to whatever name you may choose to your system.
For example, 's10'. 
"""


import json
import pandas as pd
import random


class PowerSystem:
    """Singleton Class to load a power system data.

    Parameters
    ----------
    name : str
        Name of the Power System chosen. This should be exactly as used in
        systems.json file

    Attributes
    ----------
    name : str
        Name of the Power System chosen. This should be exactly as used in
        systems.json file
    data : pandas.DataFrame
        A pandas DataFrame containing all the provided data regarding each
        TGU
    load : float
        The power load being requested to the system.
    tgus : list
        A list of Termal Generation Units as presented in system.json file.
    opzs : pandas.DataFrame
        A pandas DataFrame containing the the operative zone options of each
        TGU.
    """

    def __init__(self, name: str):
        self.__read_config(name=name)

    def __read_config(self, name: str):
        # This special method initializes the power system using the config file
        # systems.json. If the name is not present in the file, __initialize
        # raises an exception.
        try:
            with open("systems.json") as f:
                content = json.loads(f.read())
                psystem = content[name]
        except:
            print("Error reading system '{}' from systems.json".format(name))

        df = pd.DataFrame(psystem["data"])
        df = df.rename(columns=df.iloc[0]).drop([0])

        self.name = name
        self.data = df.set_index('tgu')
        self.demand = psystem["demand"]

    def sample_operation(self) -> pd.DataFrame:
        """Returns a random sample of a possible operation of the system.

        Parameters
        ----------

        Returns
        -------
        pandas.DataFrame
            DataFrame of a possible operation of the system.

        """
        psystem_data = self.data
        l = []
        for tgu in psystem_data.index.unique():
            possible_operations = psystem_data.loc[tgu]

            if type(possible_operations) == pd.DataFrame:
                # Randomly sample one option if more than one is available
                l.append(possible_operations.sample())
            else:
                # Restructure the operations back to a dataframe to be composed
                l.append(possible_operations.to_frame()
                                            .transpose()
                                            .rename_axis('tgu'))
                
        return pd.concat(l)
