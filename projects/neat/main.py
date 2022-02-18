from models.Neat import *
import random
from models.evolution.Genome import Genome
from tqdm import tqdm



def run_experiment(seed,verbose_level=0):

    # replicate experiment
    random.seed(seed)

    epochs = 200 # 100 in paper
    global input_size, output_size
    input_size = 2 + 1 # + 1 bias

    max_population = 400 # 150 in paper
    output_size = 1

    neat:Neat = Neat(
        input_size,output_size,max_population
    )

    global current_input
    current_input = [1,0,0]

    

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


    def scoreOR(genome:Genome)->float:
        # The resulting number was squared to give proportionally more fitness the closer a network was to a solution.
                
        # fitness function: XOR
        global input_size, output_size

        fitness:float = 0

        for i in range(2):
            for j in range(2):

                inp:list = [1,i,j]

                output:list = genome.forward(inp)

                if inp[1] == 1 or inp[2] == 1:
                    # 1
                    fitness += output[0]
                else:
                    # 0
                    fitness += (1 - output[0])

        # maximum can get: 4
        final_fitness = fitness * fitness
        final_fitness_with_penalization = final_fitness
        return final_fitness_with_penalization # square for sparse more the fitness and do better selections


    def scoreXOR(genome:Genome)->float:
        # The resulting number was squared to give proportionally more fitness the closer a network was to a solution.
                
        # fitness function: XOR
        global input_size, output_size

        fitness:float = 0

        for i in range(2):
            for j in range(2):

                inp:list = [1,i,j]

                output:list = genome.forward(inp)

                if inp[1] == inp[2]:
                    # Expected: 0
                    fitness += (1 - output[0])
                else:
                    # Expected: 1
                    fitness += output[0]


        # maximum can get: 4
        return fitness * fitness # square for sparse more the fitness and do better selections


    debug_step = epochs//10 # epochs//10 
    for i in tqdm(range(epochs)):
        # we can collect scores by frame, in this case we can directly collect from functions
        for j in range(len(neat.genomes)):
            genome:Genome = neat.genomes[j]
            genome.score = scoreXOR(genome)
        
        neat.evolve(verbose_level=verbose_level-1,debug_step=debug_step)
            

    best_genome = neat.getBestGenome()

    operator = "&"
    
    
    if verbose_level > 0:
        print(f"BEST SCORE {best_genome.score}")
        print("CONNECTIONS: ", len(best_genome.connections))
        print(best_genome)
        print(f"0 {operator} 0 =", round(best_genome.forward([1,0,0])[0],2))
        print(f"0 {operator} 1 =", round(best_genome.forward([1,0,1])[0],2))
        print(f"1 {operator} 0 =", round(best_genome.forward([1,1,0])[0],2))
        print(f"1 {operator} 1 =", round(best_genome.forward([1,1,1])[0],2))
        print("Mutation rates:")
        print(best_genome.mutation_rates)

    global genome_draw
    genome_draw = best_genome

    #for specie in neat.species.data:
    #    print(f"Specie {specie.id} sample: {specie.representative}")
    return best_genome.score

temp = -math.inf
temp2 = -1

worst_score = math.inf
worst_seed = -1

bad_seeds = []

begin = 0
end = 10
verbose_level = 0

for s in range(begin,end+1):
    ff = run_experiment(s,verbose_level)
    if ff <= 9:
        bad_seeds.append(s)
        print(f"Bad score {s}", ff)
    if ff > temp:
        temp = ff
        temp2 = s
    if ff < worst_score:
        worst_score = ff
        worst_seed = s

    
print("best")
print(temp)
print(temp2)

print("worst seed")
print(worst_score)
print(worst_seed)
print("BAD seeds", bad_seeds)