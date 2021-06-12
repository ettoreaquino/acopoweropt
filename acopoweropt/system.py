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

        self.tgus = self.data.tgu.unique()
        self.opzs = (
            self.data.tgu.value_counts().sort_index().to_frame(name="options")
        )

    def __read_config(self, name: str):
        # This special method initializes the power system using the config file
        # systems.json. If the name is not present in the file, __initialize
        # raises an exception.
        try:
            with open("systems.json") as f:
                self.name = name
                psystem = json.loads(f.read())

                df = pd.DataFrame(psystem[name]["data"])
                df = df.rename(columns=df.iloc[0]).drop([0])

                self.data = df
                self.load = psystem[name]["load"]

        except Exception as e:
            print("Error reading system {} from systems.json".format(name))

    def rand_opt_zones(self):
        """Returns a random combination of possible operative zones of each TGU.

        Parameters
        ----------

        Returns
        -------
        list
            List representing which operative zone was randomized for each TGU.

        """
        return [random.randint(1, j) for i, j in self.opzs.itertuples()]
