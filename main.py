# main.py
from acopoweropt import colony, system

# Um sistema de de usinas termicas pode ser instanciado via system.PowerSystem:
PSystem = system.PowerSystem(name='s15')

# Em seguida, a colonia pode ser initializada passando como parametro o sistema instanciado
# que servira de 'ambiente' para a busca de alimento pelas formigas
Colony = colony.PowerColony(n_ants=100,
                            pheromone_evp_rate={'worst': 0.75, 'mean': 0.25, 'best': 0.05},
                            power_system=PSystem)

# A busca por alimento pode ser realizada atraves do metodo 'seek':
# OBS: a variavel opcional 'show_progress' permite observar as iteracoes.

Colony.seek(max_iter=20, power_system=PSystem, show_progress=True)

# Apos a obtencao de resultados eh possivel avaliar o comportamento da solucao
# de forma visual
ax = Colony.paths.groupby('iteration').distance.min().plot(y='distance')

# Uma animacao pode ser produzida para observar o comportamento do feromonio
# uma pasta eh criada para conter a evolucao do feromonio em cada iteracao
# e um gif eh produzido na raiz do projeto.
Colony.create_pheromone_movie(duration=0.25)