import random
from .data_structures.RandomHashSet import RandomHashSet
from .data_structures.RandomSelector import RandomSelector
from .evolution.Genome import Genome
from .network.Neuron import *
from .evolution.Specie import Specie
from .network.Activation import ActivationFunction

class NeatConfig:

    def __init__(
        self, 
        SURVIVORS:float=0.8,
        WEIGHT_SHIFT_STRENGTH:float=0.8,
        WEIGHT_RANDOM_STRENGTH:float=0.8,
        PROBABILITY_MUTATE:float = 0.8,
        MAX_NEURONS:int = 10
    ):
        self.SURVIVORS:float = SURVIVORS
        self.WEIGHT_SHIFT_STRENGTH:float = WEIGHT_SHIFT_STRENGTH
        self.WEIGHT_RANDOM_STRENGTH:float = WEIGHT_RANDOM_STRENGTH # for normal initialization too
        self.PROBABILITY_MUTATE:float = PROBABILITY_MUTATE
        self.MAX_NEURONS:int = MAX_NEURONS


class Neat:

     

    all_connections:dict = dict() # type hashmap<ConnectionGene, ConnectionGene>

    map_neuron_innovation_number:dict = dict() # type <innovation_number:int, sample_x_y:int[2]>. Example: m[2] = (0.1,0.212121)
    
    genomes:RandomHashSet = None # type Genome
    species:RandomHashSet = None # type Specie


    def __init__(self, config:NeatConfig, input_size:int, output_size:int, clients:int):

        self.config = config

        self.all_connections = dict()
        self.map_neuron_innovation_number = dict()
        self.genomes = RandomHashSet()
        self.species = RandomHashSet()        

        self.reset(input_size, output_size, clients)


    def reset(self, input_size:int, output_size:int, clients:int)->None:
        # print("d:NEAT:reset")
        self.input_size = input_size
        self.output_size = output_size
        self.max_clients = clients

        self.all_connections.clear()
        self.map_neuron_innovation_number.clear()
        self.genomes.clear()

        # creates base input neurons and save them as reference
        for i in range(input_size):
            y = (i+1)/float(input_size+1)
            innovation_number:int = i+1
            self.getNeuronNew(0.1,y,innovation_number,ActivationFunction.sigmoid)

        # creates base output neurons and save them as reference
        for i in range(output_size):
            y = (i+1)/float(output_size+1)
            innovation_number:int = input_size + (i+1)
            self.getNeuronNew(0.9,y,innovation_number,ActivationFunction.sigmoid)

        # creates dynamic genomes list
        for i in range(self.max_clients):
            genome:Genome = self.empty_genome()
            genome.orderNetwork() # may be not necessary
            self.genomes.add(genome)
    
    def getBestGenomeInSpecies(self)->Genome:
        best_score:float = -math.inf
        best_genome:Genome = None

        for i in range(self.species.size()):
            specie:Specie = self.species.get(i)
            if specie.score > best_score:
                best_score = specie.score

                internal_score:float = -math.inf
                for j in range(specie.genomes.size()):
                    g:Genome = specie.genomes.get(j)

                    if g.score > internal_score:
                        internal_score = g.score
                        best_genome = g
        return best_genome
                        
    def getConnection(self, node1:Neuron, node2:Neuron)->Connection:

        # have to be a new object with same existing innovation number or new one
        connectionGene:Connection = Connection(node1,node2)

        key = connectionGene.hashCode()
        if key in self.all_connections:
            # just copy the innovation_number
            connectionGene.innovation_number = self.all_connections[key].innovation_number
        else:
            connectionGene.innovation_number = len(self.all_connections) + 1
            self.all_connections[key] = connectionGene
        
        return connectionGene

    def setReplaceIndex(self, node1:Neuron, node2:Neuron, index:int)->None:
        connectionGene:Connection = Connection(node1,node2)
        key = connectionGene.hashCode()
        self.all_connections[key].replace_index = index


    def getReplaceIndex(self, node1:Neuron, node2:Neuron)->int:
        connectionGene:Connection = Connection(node1,node2)
        key = connectionGene.hashCode()
        data:Connection = self.all_connections.get(key, None)

        if data is None:
            return 0, key
        return data.replace_index, key

    def getNeuronNew(self,x:float,y:float,innovation_number:int,activation_function,exist:bool=False)->Neuron:
        n:Neuron = Neuron(x,y,innovation_number,activation_function)
        if not exist:
            # no exist, so add it to storage
            self.map_neuron_innovation_number[innovation_number] = (n.x,n.y)
        return n

    def getNeuron(self,innovation_number_expected:int,x:float=-1,y:float=-1)->Neuron:
        # singleton for x and y for unique innovation_number        

        len_neurons_created:int = len(self.map_neuron_innovation_number)

        exist:bool = False

        innovation_number:int = len_neurons_created + 1
        if innovation_number_expected <= len_neurons_created:
            # in the history this gene was already created
            innovation_number = innovation_number_expected
            sample = self.map_neuron_innovation_number[innovation_number]
            x = sample[0]
            y = sample[1]
            exist = True       

        return self.getNeuronNew(x,y,innovation_number,ActivationFunction.sigmoid,exist)

    
    def empty_genome(self, prefill:bool=True) -> Genome:

        input_neurons:list = []
        output_neurons:list = []

        if prefill:

            for innovation_number in range(1, self.input_size+1):
                input_neurons.append(self.getNeuron(innovation_number))

            for innovation_number in range(self.input_size+1,self.input_size+self.output_size+1):
                output_neurons.append(self.getNeuron(innovation_number))

        return Genome(input_neurons,[],output_neurons)


    def selectBestGenomes(self,amount=2,method="elitist"):
        # todo: improve performance
        best_individuals_values:list = [-math.inf for _ in range(amount)]
        best_individuals_index:list = [-1 for _ in range(amount)]

        best_individuals:list = []

        if method == "elitist":

            for i in range(len(self.genomes)):
                genome:Genome = self.genomes[i]

                individual_fitness = genome.score

                first_min_value:int = math.inf
                first_min_index:int = -1
                for j,val1 in enumerate(best_individuals_values):
                    if val1 < first_min_value:
                        first_min_value = val1
                        first_min_index = j


                if individual_fitness > first_min_value:
                    best_individuals_values[first_min_index] = individual_fitness
                    best_individuals_index[first_min_index] = i

        else:
            raise Exception("method not allowed for selection")

        best_individuals_index:list = [-1 for _ in range(amount)]

        best_individuals:list = []

        for index in best_individuals_index:
            best_individuals.append(self.genomes[index])

        return best_individuals

    def selectBestGenomesFromSpecie(self,specie:Specie,amount=2,method="elitist"):
        # todo: improve performance
        best_individuals_values:list = [-math.inf for _ in range(amount)]
        best_individuals_index:list = [-1 for _ in range(amount)]

        best_individuals:list = []


        if method == "elitist":

            for i in range(specie.genomes.size()):
                genome:Genome = specie.genomes.get(i)

                individual_fitness = genome.score

                first_min_value:int = math.inf
                first_min_index:int = -1
                for j,val1 in enumerate(best_individuals_values):
                    if val1 < first_min_value:
                        first_min_value = val1
                        first_min_index = j


                if individual_fitness > first_min_value:
                    best_individuals_values[first_min_index] = individual_fitness
                    best_individuals_index[first_min_index] = i

        else:
            raise Exception("method not allowed for selection")

        best_individuals:list = []

        for index in best_individuals_index:
            best_individuals.append(specie.genomes.get(index))


        return best_individuals


    
    # We need the reference control, so this method can't be in Specie
    def breedFromSpecie(self, specieFrom:Specie)->Genome:
        # return Genome
        best_genomes:list = self.selectBestGenomesFromSpecie(specieFrom)
        genome1:Genome = best_genomes[0]
        genome2:Genome = best_genomes[1]


        # no nodes nor connections
        genome_base:Genome = self.empty_genome(prefill=True)
        
        if genome1.score > genome2.score:
            genome_base = Genome.crossover(genome1,genome2,genome_base)
        else:
            genome_base = Genome.crossover(genome2,genome1,genome_base)

        #if len(genome_base.input_neurons) == 0:
        #    return self.empty_genome(prefill=True)
        return genome_base


    def evolve(self)->None:


        self.speciate()
        self.reducePopulation() # reduce poblation a percentaje for each specie, selecting the best
        self.removeExtinctSpecies() # delete all species with one or less genomes (only representative or none)
        self.reproduce()
        self.mutate()


        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            genome.orderNetwork()

        
    def printSpecies(self)->None:
        print("##########################################")
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            print(f"Specie: {s} {s.score} {s.size()}")
        print("##########################################")
        
    def reproduce(self)->None:

        selector:RandomSelector = RandomSelector() # type Species

        # Get species with their score
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            selector.add(s,s.score)
        
        # todo: optimize function
        to_remove = []
        to_add = []

        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            # if the specie is dead select a random
            if genome.id_specie == -1:
                s:Specie = selector.random()
                # break new genome
                genome_new:Genome = self.breedFromSpecie(s) # B

                
                to_add.append(genome_new)
                to_remove.append(genome)
                # force this client into the specie
                s.forcePut(genome_new)

        # needed not to change array while iterating
        for genome_new in to_add:
            self.genomes.add(genome_new)
        for genome in to_remove:
            self.genomes.remove(genome)

                

    def mutate(self)->None:

        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]

            p:float = random.random()

            if p < self.config.PROBABILITY_MUTATE:
                # mutate
                mutate_methods:list = [0,1,2,3]

                mutate_method:int = mutate_methods[random.randint(0,len(mutate_methods)-1)]

                if mutate_method == 0:
                    if not self.mutateGenomeLink(genome):
                        genome.mutateWeightShift(self.config.WEIGHT_SHIFT_STRENGTH)
                elif mutate_method == 1:
                    if len(genome.hidden_neurons) < self.config.MAX_NEURONS:
                        self.mutateGenomeNode(genome)
                    else:
                        genome.mutateWeightShift(self.config.WEIGHT_SHIFT_STRENGTH)
                elif mutate_method == 2:
                    genome.mutateWeightShift(self.config.WEIGHT_SHIFT_STRENGTH)
                elif mutate_method == 3:
                    genome.mutateLinkToggle()
                # elif mutate_method == 4:
                #    genome.mutateWeightRandom(self.WEIGHT_RANDOM_STRENGTH)

                

    def mutateGenomeLink(self, genome:Genome)->bool:
        # todo: improve search selection. important!
        added:bool = False
        for _ in range(100):
            a, b = genome.getRandomGenePair()

            con:Connection = None
            if a.x < b.x:
                con = Connection(a,b)
            else:
                con = Connection(b,a)


            con = self.getConnection(con.from_neuron, con.to_neuron)

            if genome.existConnection(con.innovation_number):
                # if exists or is not set to False, return
                continue

            con.weight = (random.random() * 2 - 1) * self.config.WEIGHT_RANDOM_STRENGTH

            
            genome.insertConnection(con)
            added = True
            break
        return added

    def mutateGenomeNode(self, genome:Genome):
        # add hidden node in EXISTING connection
        con:Connection = genome.getRandomConnection()
        
        if con is None:
            # there is no connections yet
            return
        

        from_neuron:Neuron = con.from_neuron
        to_neuron:Neuron = con.to_neuron

        # always split the link into two nodes
        replace_index, key = self.getReplaceIndex(from_neuron,to_neuron)

        middle:Neuron = None

        create_new_node:bool = True

        if replace_index > 0:
            if not genome.existGene(replace_index):
                # If already exist a neuron, create a copy
                middle = self.getNeuron(replace_index)
                create_new_node = False
        
        if create_new_node:
            # if no previous neuron was created between this connection
            x = (from_neuron.x + to_neuron.x)/2
            y = (from_neuron.y + to_neuron.y)/2 + (random.random() * 0.1 - 0.05)
            innovation_number:int = len(self.map_neuron_innovation_number)+1
            middle:Neuron = self.getNeuronNew(x,y,innovation_number,ActivationFunction.sigmoid)
            self.setReplaceIndex(from_neuron,to_neuron,middle.innovation_number)
        

        con1:Connection = self.getConnection(from_neuron,middle)
        con2:Connection = self.getConnection(middle,to_neuron)

        # before link: set weight to 1
        con1.weight = 1
        # next link: restore the properties of original long connection
        con2.weight = con.weight
        con2.enabled = con.enabled

        # if input [1,2,3] and output [4]
        # adding hidden node is hidden [5]
        # originally 1->4, and we want to put the node 5 in middle
        # now 1->5->4. the original connection 1->4 have to be removed
        genome.removeConnection(con)
        # the middle is a brand new or existing in general storage mapping
        genome.insertGene(middle)

        # now we add the segmented connection
        genome.insertConnection(con1)
        genome.insertConnection(con2)

    def removeExtinctSpecies(self)->None:
        i:int = self.species.size()-1
        while i >= 0:

            # if only representative is left...
            if self.species.get(i).size() <= 1:
                self.species.get(i).goExtinct()
                self.species.removeByIndex(i)

            i -= 1

    def speciate(self)->None:
        # reset all except representative
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            s.reset()

        # iterate and add client to corresponding specie
        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            
            if genome.id_specie != -1:
                continue


            found:bool = False
            for j in range(len(self.species.data)):
                s:Specie = self.species.data[j]
                if s.put(genome):
                    found = True
                    break
            
            if not found:
                # create a new specie and the representative will be this new client
                self.species.add(Specie(genome))

        # evaluate scores for each specie
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            s.evaluateScore()
    
    def reducePopulation(self)->None:
        # kill X% of population
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            s.reducePopulation(1-self.config.SURVIVORS)



