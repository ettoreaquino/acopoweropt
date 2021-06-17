# main.py
import pandas as pd
import random

from acopoweropt import colony, system

PSystem = system.PowerSystem(name='s15')
Colony = colony.PowerColony(n_ants=5,
                            pheromone_evp_rate={'worst': 0.75, 'mean': 0.25, 'best': 0.05},
                            power_system=PSystem)

n_iter = 10

for i in range(n_iter):
    # Getting last taken paths
    paths = Colony.paths.query("iteration == {i}".format(i=i))

    # Evaporate Pheromone
    Colony.evaporate_pheromone(paths=paths, power_system=PSystem)

    print(i)
    print(Colony.pheromone)

    # Selecting Ants (80/20) to follow or not the pheromone paths
    taken_paths = []
    for ant in range(1, Colony.n_ants + 1):
        decision = random.random()
        if decision <= 0.8:
            # ANT Follows Path
            operative_zones = Colony.choose_path()
            existing_path = paths.query("path == '{}'".format(",".join([str(n) for n in operative_zones])))

            # Check if chosen path was already calculated:
            if existing_path.values.size != 0:
                solution = existing_path.reset_index().loc[0]
                solution['ant'] = ant
                solution['iteration'] = i + 1
                solution = solution.to_frame().T.set_index('ant')
                taken_paths.append(solution)
            else:
                operation = PSystem.get_operation(operative_zones=operative_zones)
                solution = pd.DataFrame(
                    [colony.seek_food(ant=ant, iteration=i + 1, operation=operation, power_system=PSystem)]
                ).set_index('ant')
                taken_paths.append(solution)

        else:
            # ANT Sets to new path
            operation = PSystem.sample_operation()
            solution = pd.DataFrame(
                [colony.seek_food(ant=ant, iteration=i + 1, operation=operation, power_system=PSystem)]
            ).set_index('ant')
            taken_paths.append(solution)

    # Updating Paths
    new_paths = pd.concat(taken_paths).sort_index()
    Colony.paths = Colony.paths.append(new_paths)

    # Updating Best and Worst Paths
    Colony.update_best_and_worst(paths=new_paths)

    # Updating Pheromone
    Colony.update_pheromone(paths=new_paths, iteration=i + 1)