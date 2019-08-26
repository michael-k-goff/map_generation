# Dependencies
import random
import os
import sys
from sda import *
from map import *

# Project hyperparameters

debug_mode = 1 # Set if you want to see progress displayed while running the evolutionary algorithm

# Hyperparameters related to the learning algorithms
mnm = 1 # Maximum number of mutations
sda_size = 12 # Number of nodes in each SDA
population_size = 32 # Number of SDAs kept in a population
tournament_size = 7 # Number of SDAs chosen for mating, of which the two best are crossed over.
generations = 5 # Number of updatings to do

# Some functions that are necessary for running the genetic algorithm

# Create random SDAs for starting the algorithm
def random_sda():
    labels = [["1","1","0","0","00","11","01","10"][random.randint(0,7)] for i in range(sda_size)]
    transitions = [[random.randint(0,sda_size-1),random.randint(0,sda_size-1)] for i in range(sda_size)]
    return SDA(labels,transitions)

def mutate(s):
    # Introduce random mutations to s
    num_mutations = random.randint(1,mnm)
    for i in range(num_mutations):
        random_node = random.randint(0,sda_size-1)
        if random.randint(0,1):
            s.emit[random_node] = ["1","1","0","0","00","11","01","10"][random.randint(0,7)]
        else:
            s.next_state[random_node][random.randint(0,1)] = random.randint(0,sda_size-1)

# Crossover function. As per the paper, we are using two-point crossover.
def crossover(s1,s2):
    # Find crossover points
    point1 = random.randint(0,sda_size-1)
    point2 = (point1+random.randint(1,sda_size-1))%sda_size
    if point1 > point2:
        point1, point2 = point2, point1

    # Perform the crossover
    emit3 = s1.emit[:point1]+s2.emit[point1:point2]+s1.emit[point2:]
    emit4 = s2.emit[:point1]+s1.emit[point1:point2]+s2.emit[point2:]
    # The following is a bit clunky because we need to deepcopy these arrays
    next_state3 = [0]*sda_size
    next_state4 = [0]*sda_size
    for i in range(point1):
        next_state3[i] = [s1.next_state[i][0], s1.next_state[i][1]]
        next_state4[i] = [s2.next_state[i][0], s2.next_state[i][1]]
    for i in range(point1, point2):
        next_state3[i] = [s2.next_state[i][0], s2.next_state[i][1]]
        next_state4[i] = [s1.next_state[i][0], s1.next_state[i][1]]
    for i in range(point2, sda_size):
        next_state3[i] = [s1.next_state[i][0], s1.next_state[i][1]]
        next_state4[i] = [s2.next_state[i][0], s2.next_state[i][1]]

    # Build new SDAs
    s3 = SDA(emit3, next_state3)
    s4 = SDA(emit4, next_state4)

    # Mutation
    mutate(s3)
    mutate(s4)

    return s3,s4

class Population:
    def __init__(self):
        self.pop = [random_sda() for i in range(population_size)]
        self.scores = [evaluate_sda(self.pop[i]) for i in range(population_size)]
    def update(self):
        selection = random.sample(range(population_size),tournament_size)

        # Find the best two and worst two
        best = selection[0]
        second_best = selection[1]
        worst = selection[0]
        second_worst = selection[1]
        if self.scores[best] < self.scores[second_best]:
            best,second_best = second_best,best
        if self.scores[worst] > self.scores[second_worst]:
            worst,second_worst = second_worst,worst
        for i in range(2,tournament_size):
            if self.scores[selection[i]] >= self.scores[best]:
                best,second_best = selection[i],best
            elif self.scores[selection[i]] >= self.scores[second_best]:
                second_best = selection[i]
            if self.scores[selection[i]] <= self.scores[worst]:
                worst,second_worst = selection[i],worst
            elif self.scores[selection[i]] <= self.scores[second_worst]:
                second_worst = selection[i]

        # Mate them and replace the worst ones
        new1, new2 = crossover(self.pop[best], self.pop[second_best])
        self.pop[worst] = new1
        self.pop[second_worst] = new2
        self.scores[worst] = evaluate_sda(new1)
        self.scores[second_worst] = evaluate_sda(new2)

    def evolve(self):
        if debug_mode:
            print( "Initial Population: Max score is " + str(max(self.scores)) )
        for i in range(generations):
            if debug_mode and i%100 == 0:
                print( "Generation " + str(i) + ": Max score is " + str(max(self.scores)) )
            self.update()

    def get_best(self):
        best = 0
        for i in range(population_size):
            if self.scores[i] > self.scores[best]:
                best = i
        return self.pop[best]

# Draw map from an SDA
def draw_from_sda(s,filename):
    map_ = generate_map(s,"SDA")
    map_.draw_map(filename)

# Testing
pop = Population()
pop.evolve()
best = pop.get_best()
draw_from_sda(best,"asdf.png")
