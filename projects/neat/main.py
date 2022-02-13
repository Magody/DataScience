from models.Neat import *
import random
from models.evolution.Genome import Genome
from tqdm import tqdm


epochs = 30
global input_size, output_size
input_size = 2 # + 1 bias?

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
    if (i+1)%10 == 0:
        neat.printSpecies()

best_genome = neat.getBestGenomeInSpecies()
    
print(f"BEST SCORE {best_genome.score}")
print(round(best_genome.forward([0,0])[0],2))
print(round(best_genome.forward([0,1])[0],2))
print(round(best_genome.forward([1,0])[0],2))
print(round(best_genome.forward([1,1])[0],2))