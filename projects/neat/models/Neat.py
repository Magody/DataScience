import random
from .data_structures.RandomHashSet import RandomHashSet
from .evolution.Genome import Genome
from .network.Neuron import *
from .evolution.Specie import Specie
from .network.Activation import ActivationFunction
from .network.Connection import *


class Neat:

    species:RandomHashSet = None # type Specie
    genomes:list = [] # type Genome


    def __init__(self, input_size:int, output_size:int, population:int):

        self.genomes = []
        self.species = RandomHashSet()
        # The stagnation number varies with probability of genomes and total number of epochs
        self.STAGNATED_MAXIMUM = 50 # todo: remove the stagnat variable in Specie class

        self.reset(input_size, output_size, population)


    def reset(self, input_size:int, output_size:int, population:int)->None:
        # print("d:NEAT:reset")

        self.generation = 0

        self.input_size = input_size
        self.output_size = output_size
        self.POPULATION = population
        Connection.ALL_CONNECTIONS.clear()
        Neuron.map_neuron_innovation_number.clear()
        self.genomes.clear()

        # creates base input neurons and save them as reference
        for i in range(input_size):
            y = (i+1)/float(input_size+1)
            innovation_number:int = i+1
            Neuron.getNeuronNew(0.1,y,innovation_number,ActivationFunction.relu)

        # creates base output neurons and save them as reference
        for i in range(output_size):
            y = (i+1)/float(output_size+1)
            innovation_number:int = input_size + (i+1)
            Neuron.getNeuronNew(0.9,y,innovation_number,ActivationFunction.sigmoid_bounded)

        # creates dynamic genomes list
        for i in range(self.POPULATION):
            genome:Genome = Genome.empty_genome(input_size, output_size, connect_input_output=True)
            self.addGenomeAndApplySpecie(genome)

    def addGenomeAndApplySpecie(self, genome:Genome):
        self.genomes.append(genome)
        self.addToSpecie(genome)

    def sortSpeciesByScore(self):
        for i in range(len(self.species.data)):
            specie:Specie = self.species.data[i]
            # sort ascending ascending. Todo: improve to always get sorted
            specie.genomes.data.sort(key=lambda genome: genome.score)
               
    def evolve(self,verbose_level=1,debug_step=5)->None:
        
        self.scoreSpecies()
        self.sortSpeciesByScore()
        self.reducePopulation(SURVIVORS=0.5)
        self.scoreSpecies()

        # Restore best genomes is the most important part to keep good scores in future!
        genomes_champions = []
        self.generation += 1

        for specie in self.species.data:
            specie.increaseGeneration()
            if len(specie.genomes.data) >= 5:
                # add the champion ofeach specie
                # not add directly because the array will increase in run time and can loop forever
                # copy unchanged
                # TOP COUPLE: elitist method. todo: parametize it
                genome_champion1:Genome = Genome.copy(specie.genomes.data[-1], copy_specie=False)
                genome_champion2:Genome = Genome.copy(specie.genomes.data[-2], copy_specie=False)
                
                genomes_champions.append(genome_champion1)
                genomes_champions.append(genome_champion2)
        
        
         # After get the best of stagnant specie, remove it
        self.removeSpeciesWeak()
        self.removeStaleSpecies() # not needed in this implementation of XOR, but can be useful in other
        self.reducePopulation(SURVIVORS=0.2)  # sort by genome.score ascending in all species
        
        # even if specie dissapear, we preserve the best of that dissapeared specie
        # add champions at final after final reduction
        for champion in genomes_champions:
            # todo: improve this performance
            self.addGenomeAndApplySpecie(champion) # already sorted, so, the best is last
        

        self.populate(reservation_space=0) # mutate here, len(genomes_champions)
        
       
        
        
       
    
        if verbose_level > 0 and (self.generation == 1 or self.generation % debug_step == 0): 
            self.printSpecies()
            print(end="")

        for i in range(len(self.genomes)):
            genome:Genome = self.genomes[i]
            genome.orderNetwork()

        
    def populate(self, reservation_space=0)->None:

        
        
        """
        species_available:list = []
        for specie in self.species.data:
            if specie.can_reproduce:
                species_available.append(specie)
        """

       
        while len(self.genomes) < (self.POPULATION-reservation_space):
            # species_available[random.randint(0, len(species_available)-1)]
            # self.species.data[random.randint(0, len(self.species.data)-1)]
            specie:Specie = self.species.data[random.randint(0, len(self.species.data)-1)] # 
            
            if specie.can_reproduce:
                # stagnant species
                specie.genomes.data[random.randint(0, len(specie.genomes.data)-1)].mutate()
            
            child:Genome = specie.breed()
            child.mutate()
            child.id_specie = -1
            self.genomes.append(child)
            self.addToSpecie(child) # add to the same or new specie if mutate was meaningful

    
    def removeExtinctSpecies(self)->None:
        i:int = self.species.size()-1
        while i >= 0:

            # if only representative is left...
            if self.species.get(i).size() <= 1:
                self.removeSpecie(i)

            i -= 1


    def removeSpeciesWeak(self)->None:
        # remove species that not aport in the total average sum
        total_sum:float = 0
        for specie in self.species.data:
            total_sum += specie.score


        i:int = self.species.size()-1
        while i >= 0:
            contribution:float = math.floor((self.species.get(i).score/total_sum) * self.POPULATION)
            if contribution < 1:
                self.removeSpecie(i)
            i -= 1

    def removeStaleSpecies(self)->None:
        # remove species that not aport in the total average sum
       
        i:int = self.species.size()-1
        while i >= 0:
            if self.species.get(i).generations_from_last_improve > self.STAGNATED_MAXIMUM:
                self.removeSpecie(i)
            i -= 1

    def removeSpecie(self, index:int):
        # todo, improve maybe using dynamic allocating as the beginning
        
        genome_hope:Genome = None
        if len(self.species.data) == 1:
            specie:Specie = self.species.data[0]
            print(f"END WORLD with best score {specie.best_score} actual {specie.score}")
            genome_hope:Genome = Genome.copy(self.species.get(index).genomes.data[-1], copy_specie=False)
            #print(f"Specie {specie.id} sample: {specie.representative}")
            # for i in range(5):
            #    print(f"Other: {specie.genomes.get(i)}")
            # print()
            

        for genome in self.species.get(index).genomes.data:
            # remove the references of genomes
            self.genomes.remove(genome)
        self.species.removeByIndex(index)

        if not genome_hope is None:
            # copy of the best:
            self.addGenomeAndApplySpecie(genome_hope)

            for i in range(self.POPULATION//10):
                self.addGenomeAndApplySpecie(Genome.empty_genome(self.input_size,self.output_size,connect_input_output=False))







    def addToSpecie(self,genome:Genome)->None:
        # reset all except representative
            
        if genome.id_specie != -1:
            raise Exception("already has specie")

        found:bool = False
        for j in range(len(self.species.data)):
            s:Specie = self.species.data[j]
            if s.put(genome):
                found = True
                break
        
        if not found:
            # create a new specie and the representative will be this new client
            self.species.add(Specie(genome))

    def scoreSpecies(self):
        # evaluate scores for each specie
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            s.evaluateScore()
    
    def reducePopulation(self, SURVIVORS:float = 0.5)->None:
        # kill X% of population
        for i in range(len(self.species.data)):
            specie:Specie = self.species.data[i]
            percentage = 1-SURVIVORS
            # kill clients with low score
            amount:float = math.floor(percentage * specie.genomes.size())

            i:int = 0
            while i < amount:
                genome:Genome = specie.genomes.get(0)
                genome.id_specie = -1
                genome.score = 0
                specie.genomes.removeByIndex(0)
                self.genomes.remove(genome)
                i += 1


    def getBestGenome(self)->Genome:

        best_score = -math.inf
        best_genome = None
        for genome in self.genomes:
            if genome.score > best_score:
                best_score = genome.score
                best_genome = genome
        return best_genome

    def printSpecies(self)->None:
        print("##########################################")
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            print(s)
        print("##########################################")
