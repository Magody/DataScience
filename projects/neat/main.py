from models.Neat import *
import random
from models.evolution.Genome import Genome
from models.nodes.NodeGene import ConnectionGene

epochs = 20
input_size = 10


output_size = 1
neat:Neat = Neat(input_size,output_size,20)

inp:list = [0 for _ in range(input_size)]
for i in range(len(inp)):
    inp[i] = random.random()

print("EVOLVING PHASE")
for i in range(epochs):
    for j in range(len(neat.genomes.data)):
        genome:Genome = neat.genomes.data[j]
        score:float = genome.calculate(inp)[0]
        genome.score = score
        
    neat.evolve()
    print(f"END: epoch {i}")
    neat.printSpecies()

print("INNOVATION READ")
for i in range(len(neat.genomes.data)):
    genome:Genome = neat.genomes.data[i]

    for j in range(len(genome.connections.data)):
        g:ConnectionGene = genome.connections.data[j]
        # print(g.innovation_number,end=" ")
    # print()