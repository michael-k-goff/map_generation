# Map Generation

This project implements a random dungeon generator, based on [a paper](https://arxiv.org/pdf/1905.09618.pdf) by Daniel Ashlock and  Christoph Salge.

## Objective

The main goal of this project is to demonstrate the generation of randomized dungeons by self-driving automata that are evolved from a genetic algorithm.

## Project Structure

The project includes the following files.

- map_generation.ipynb: Jupyter notebook that implements the full map generation algorithm. It is annotated with explanation of the algorithm and suggestions for experimentation.
- main.py: Main file for the (non-Jupyter) python code.
- population.py: Implements the `Population` class and the core of the genetic algorithm.
- generator.py: Implements the `Generator` class, which defines how maps are created from self-driving automata.
- map.py: Implements the Map and Room classes and the rendering of maps to PNG files.
- sda.py: Implements self-driving automata.
- map[0-9].png: Maps generated from 10 runs of the genetic algorithm.
- random.png: A map generated from a random string of 0s and 1s instead of a self-driving automaton.
- sprawl.png: A map generated from the genetic algorithm, but with the optimization function changed to favor spread out maps over compact maps.
