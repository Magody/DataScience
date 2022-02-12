from models.Neat import *
import random
from models.evolution.Genome import Genome

epochs = 50
input_size = 10

max_population = 100


output_size = 1
neat:Neat = Neat(input_size,output_size,max_population)

inp:list = [0 for _ in range(input_size)]
for i in range(len(inp)):
    inp[i] = random.random()


print("EVOLVING PHASE")
for i in range(epochs):
    for j in range(len(neat.genomes.data)):
        genome:Genome = neat.genomes.data[j]
        score:float = genome.forward(inp)[0]
        genome.score = score
        
    neat.evolve()


    neat.printSpecies()
