from models.Neat import *
import random
from models.evolution.Genome import Genome
from tqdm import tqdm

epochs = 100 # 100 in paper
global input_size, output_size
input_size = 2 + 1 # + 1 bias

max_population = 1000 # 150 in paper
output_size = 1

neat:Neat = Neat(
    input_size,output_size,max_population
)

global current_input
current_input = [1,0,0]

def run_experiment():
    

    def scoreAND(genome:Genome)->float:
        # The resulting number was squared to give proportionally more fitness the closer a network was to a solution.
                
        # fitness function: XOR
        global input_size, output_size

        fitness:float = 0

        for i in range(2):
            for j in range(2):

                inp:list = [1,i,j]

                output:list = genome.forward(inp)

                if inp[1] == 1 and inp[2] == 1:
                    # 1
                    fitness += output[0]
                else:
                    # 0
                    fitness += (1 - output[0])

        # maximum can get: 4
        return fitness * fitness # square for sparse more the fitness and do better selections


    print("EVOLVING PHASE")
    for i in tqdm(range(epochs)):
        # we can collect scores by frame, in this case we can directly collect from functions
        for j in range(len(neat.genomes.data)):
            genome:Genome = neat.genomes.data[j]
            genome.score = scoreAND(genome)
        
        neat.evolve()
        if (i+1) % epochs//5 == 0:
            neat.printSpecies()

    best_genome = neat.getBestGenomeInSpecies()

    operator = "&"
    print(f"BEST SCORE {best_genome.score}")
    print(best_genome)
    print(f"0 {operator} 0 =", round(best_genome.forward([1,0,0])[0],2))
    print(f"0 {operator} 1 =", round(best_genome.forward([1,0,1])[0],2))
    print(f"1 {operator} 0 =", round(best_genome.forward([1,1,0])[0],2))
    print(f"1 {operator} 1 =", round(best_genome.forward([1,1,1])[0],2))

    global genome_draw
    genome_draw = best_genome


run_experiment()