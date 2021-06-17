import pandas as pd
import numpy as np
import random

from acopoweropt import colony, system

PSystem = system.PowerSystem(name='s15')
Colony = colony.PowerColony(n_ants=5,
                            pheromone_evap_rate=0.25,
                            PowerSystem=PSystem)

print("Iteracao: {} - MinValue: {}".format(0, Colony.paths[0].distance.min()))

n_iter = 20

for i in range(n_iter):
    # Getting last taken paths
    paths = Colony.paths[i].copy()
    
    # Evaporate Pheromone
    Colony.pheromone = (1 - Colony.pheromone_evap_rate) * Colony.pheromone
   
    # Selecting Ants (80/20) to follow or not the pheromone paths
    l = []
    for ant in range(1, Colony.n_ants + 1):
        decision = random.random()
        if decision <= 0.8:
            ## ANT Follows Path
            operative_zones = Colony.choose_path()
            chosen_path = ",".join([str(int) for int in operative_zones])
            existing_path = paths.query("path == '{}'".format(chosen_path)) 

            ## Check if chosen path was already calculated:
            if existing_path.values.size != 0:
                l.append(existing_path)
            else:
                operation = PSystem.get_operation(operative_zones=operative_zones)
                solution = pd.DataFrame([Colony.seek_food(ant=ant, operation=operation, PowerSystem=PSystem)]).set_index('ant')
                l.append(solution)
                
        else:
        ## ANT Sets to new path
            operation = PSystem.sample_operation()
            solution = pd.DataFrame([Colony.seek_food(ant=ant, operation=operation, PowerSystem=PSystem)]).set_index('ant')
            l.append(solution)

    new_paths = pd.concat(l).sort_index()
    Colony.paths.update({i+1: new_paths})
    
    # Updating Pheromone
    new_pheromone = Colony.update_pheromone(paths=new_paths)
    Colony.pheromone_history.update({i+1: new_pheromone})
    
    print("Iteracao: {} - MinValue: {}".format(i+1, paths.distance.min()))