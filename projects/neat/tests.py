from models.evolution.Genome import Genome
from models.Neat import Neat
from tqdm import tqdm
import random
import math
from models.evolution.Specie import SpecieConfig
from models.evolution.Genome import GenomeConfig

class TestLogicGates:
        

    def scoreAND(self,genome:Genome)->float:
        # The resulting number was squared to give proportionally more fitness the closer a network was to a solution.
                

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


    def scoreOR(self,genome:Genome)->float:
        # The resulting number was squared to give proportionally more fitness the closer a network was to a solution.
                

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


    def scoreXOR(self,genome:Genome)->float:
        # The resulting number was squared to give proportionally more fitness the closer a network was to a solution.
                
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

    def printSummary(self,genome:Genome):
        print(f"BEST SCORE {genome.score}")
        print("CONNECTIONS: ", genome.connections.size())
        print(genome)
        print(f"0 - 0 =", round(genome.forward([1,0,0])[0],2))
        print(f"0 - 1 =", round(genome.forward([1,0,1])[0],2))
        print(f"1 - 0 =", round(genome.forward([1,1,0])[0],2))
        print(f"1 - 1 =", round(genome.forward([1,1,1])[0],2))
        print("Mutation rates:")
        print(genome.mutation_rates)

    def run_experiment(self,neat:Neat,seed, gate:str="xor",verbose_level=0)->Genome:

        # replicate experiment
        random.seed(seed)

        epochs = neat.epochs

        debug_step = epochs//10 # epochs//10 
        for i in tqdm(range(epochs)):
            # we can collect scores by frame, in this case we can directly collect from functions
            for j in range(len(neat.genomes)):
                genome:Genome = neat.genomes[j]
                # set score and key to sort by
                if gate.lower() == "xor":
                    genome.setScore(self.scoreXOR(genome))
                elif gate.lower() == "or":
                    genome.setScore(self.scoreOR(genome))
                elif gate.lower() == "and":
                    genome.setScore(self.scoreAND(genome))
                else:
                    raise Exception(f"Unknown gate '{gate}'")
            
            neat.evolve(verbose_level=verbose_level-1,debug_step=debug_step)
            # best_genome = neat.getBestGenome()
            # self.printSummary(best_genome)
            # print()
                
        # sanity score: check
        # evaluate final genomes
        for j in range(len(neat.genomes)):
            genome:Genome = neat.genomes[j]
            # set score and key to sort by
            if gate.lower() == "xor":
                genome.setScore(self.scoreXOR(genome))
            elif gate.lower() == "or":
                genome.setScore(self.scoreOR(genome))
            elif gate.lower() == "and":
                genome.setScore(self.scoreAND(genome))
            else:
                raise Exception(f"Unknown gate '{gate}'")

        best_genome = neat.getBestGenome()

        
        if verbose_level > 0:
            self.printSummary(best_genome)
        return best_genome

    def executeSanityCheck(self,begin=1,end=10,verbose_level = 0):
        input_size = 2 + 1 # + 1 bias
        output_size = 1
        max_population = 400 # 200
        epochs = 200

        configGenome:GenomeConfig = GenomeConfig(
            probability_mutate_connections_weight = 0.8,
            probability_perturb = 0.9,
            probability_mutate_link = 0.1,
            probability_mutate_node = 0.05,
            probability_mutate_enable = 0.05,
            probability_mutate_disable = 0.02,
            std_weight_initialization = 1,
            weight_step = 0.02,
            MAX_HIDDEN_NEURONS = 10
        )

        configSpecie:SpecieConfig = SpecieConfig(
            STAGNATED_MAXIMUM = 40,
            probability_crossover = 0.8,
            C1=1,
            C2=1,
            C3=3,
            specie_threshold=3
        )


        # best, worst
        scores = [-math.inf, math.inf] 
        seeds = [-1, -1]
        bad_seeds = []

        

        for s in range(begin,end+1):
            neat:Neat = Neat(
                input_size,output_size,max_population,epochs,configGenome,configSpecie,elitist_save=3
            )

            result = self.run_experiment(neat,seed=s,gate="xor",verbose_level=verbose_level).score

            if result <= 9:
                bad_seeds.append(s)
                print(f"Bad score {s}", result)
            if result > scores[0]:
                scores[0] = result
                seeds[0] = s

            if result < scores[1]:
                scores[1] = result
                seeds[1] = s

            
        print("best,worst")
        print(scores)
        print(seeds)
        print("BAD seeds", bad_seeds)