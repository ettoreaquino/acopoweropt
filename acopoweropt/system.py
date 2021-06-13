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
import numpy as np
import random

from cvxopt import matrix, solvers


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
    demand : float
        The power demand being requested to the system.
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
        
    def solve(self, operation: pd.DataFrame):
        """Returns a solution to a specific operation configuration.

        Given a specific configuration to be solved, this function uses cvxopt
        quadratic programing to solve the system.

        One possible source of configuration data can be obtained by using the
        provided `PowerSystem.sample_operation()` method, which randomly creates
        a possible configuration for the system to be operated.

        Parameters
        ----------
        operation : pd.DataFrame
            DataFrame representing the operation of the system.

        Returns
        -------
        dict
            A dictionary containing all of the solution results

        """
    
        demand = np.array([self.demand], dtype="double")
        
        # Equation parameters cP^2 + bP + a
        a = operation.a.sum()
        b = operation.b.to_numpy(dtype="double")
        c = operation.c.to_numpy(dtype="double")
        
        # CVXOPT needs a system of equations:
        Pmin = operation.Pmin.to_numpy(dtype="double")
        Pmax = operation.Pmax.to_numpy(dtype="double")

        P = matrix(2 * (c[..., None] * np.eye(operation.shape[0])))
        q = matrix(b)

        G_min = -1 * np.eye(operation.shape[0])
        G_max = np.eye(operation.shape[0])
        G = matrix(np.concatenate((G_min,G_max)))
        h = matrix(np.concatenate((-1 * Pmin,Pmax)))

        A = matrix(np.ones(operation.shape[0]), (1, c.shape[0]))
        b = matrix(demand)
        
        return solvers.qp(P, q, G, h, A, b)