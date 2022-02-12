from sys import intern
from models.Neat import *
import random
from models.evolution.Genome import Genome
from tqdm import tqdm

epochs = 10
global input_size, output_size
input_size = 2

max_population = 100
output_size = 1

neat:Neat = Neat(input_size,output_size,max_population)


def score(genome:Genome)->float:
    # fitness function: XOR
    global input_size, output_size

    fitness:float = 0

    for i in range(2):
        for j in range(2):

            inp:list = [i,j]

            output:list = genome.forward(inp)

            if inp[0] == inp[1]:
                # 0 XOR 0 = 0, 1 XOR 1 = 0
                fitness += (1 - output[0])
            else:
                # 1 XOR 0 = 1, 0 XOR 1 = 1
                fitness += (output[0] - 0)

    return fitness/4


print("EVOLVING PHASE")
for i in tqdm(range(epochs)):
    for j in range(len(neat.genomes.data)):
        genome:Genome = neat.genomes.data[j]
        genome.score = score(genome)
        
    neat.evolve()
    neat.printSpecies()
    print()

best_score:float = -math.inf
best_genome:Genome = None

for i in range(neat.species.size()):
    specie:Specie = neat.species.get(i)
    if specie.score > best_score:
        best_score = specie.score

        internal_score:float = -math.inf
        for j in range(specie.genomes.size()):
            g:Genome = specie.genomes.get(j)

            if g.score > internal_score:
                internal_score = g.score
                best_genome = g
    
print(f"BEST SCORE {best_genome.score} {best_score}")
print(round(best_genome.forward([0,0])[0]))
print(round(best_genome.forward([0,1])[0]))
print(round(best_genome.forward([1,0])[0]))
print(round(best_genome.forward([1,1])[0]))