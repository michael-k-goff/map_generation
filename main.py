# Main

from population import Population
from generator import Generator

# Uncomment the following to run the full genetic algorithm.
# Warning: might take a while.
pop = Population()
pop.evolve()
pop.draw_map("map.png")

# Uncomment the following to draw a random map
gen = Generator(None, "Random")
gen.draw_map("random.png")
