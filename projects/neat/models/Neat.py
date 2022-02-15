import random
from .data_structures.RandomHashSet import RandomHashSet
from .data_structures.RandomSelector import RandomSelector
from .evolution.Genome import Genome
from .network.Neuron import *
from .evolution.Specie import Specie
from .network.Activation import ActivationFunction


class Neat:

     

    all_connections:dict = dict() # type hashmap<ConnectionGene, ConnectionGene>

    map_neuron_innovation_number:dict = dict() # type <innovation_number:int, sample_x_y:int[2]>. Example: m[2] = (0.1,0.212121)
    
    genomes:RandomHashSet = None # type Genome
    species:RandomHashSet = None # type Specie


    def __init__(self, input_size:int, output_size:int, population:int):


        self.all_connections = dict()
        self.map_neuron_innovation_number = dict()
        self.genomes = RandomHashSet()
        self.species = RandomHashSet()

        self.activationFunctionHidden = ActivationFunction.relu
        self.activationFunctionOutput = ActivationFunction.sigmoid_bounded

        self.reset(input_size, output_size, population)


    def reset(self, input_size:int, output_size:int, population:int)->None:
        # print("d:NEAT:reset")
        self.input_size = input_size
        self.output_size = output_size
        self.POPULATION = population

        self.all_connections.clear()
        self.map_neuron_innovation_number.clear()
        self.genomes.clear()

        # creates base input neurons and save them as reference
        for i in range(input_size):
            y = (i+1)/float(input_size+1)
            innovation_number:int = i+1
            self.getNeuronNew(0.1,y,innovation_number,self.activationFunctionHidden)

        # creates base output neurons and save them as reference
        for i in range(output_size):
            y = (i+1)/float(output_size+1)
            innovation_number:int = input_size + (i+1)
            self.getNeuronNew(0.9,y,innovation_number,self.activationFunctionOutput)

        # creates dynamic genomes list
        for i in range(self.POPULATION):
            genome:Genome = self.empty_genome(connect_input_output=True)
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

        if x == 0.9:
            return self.getNeuronNew(x,y,innovation_number,self.activationFunctionOutput,exist)
        else:
            return self.getNeuronNew(x,y,innovation_number,self.activationFunctionHidden,exist)

    
    def empty_genome(self, prefill:bool=True, connect_input_output:bool=True) -> Genome:

        input_neurons:list = []
        output_neurons:list = []

        if prefill:

            for innovation_number in range(1, self.input_size+1):
                input_neurons.append(self.getNeuron(innovation_number))

            for innovation_number in range(self.input_size+1,self.input_size+self.output_size+1):
                output_neurons.append(self.getNeuron(innovation_number))

        genome = Genome(input_neurons,[],output_neurons)
        if connect_input_output:
            # initial connection
            for input_neuron in genome.input_neurons:
                for output_neuron in genome.output_neurons:
                    genome.insertConnection(self.getConnection(input_neuron,output_neuron))

        return genome
        

    def evolve(self)->None:

        self.speciate()
        self.removeSpeciesWeak()
        self.reducePopulation(0.5)
        self.removeExtinctSpecies() # delete all species with one or less genomes (only representative or none)
        self.scoreSpecies()
        # self.removeStaleSpecies() # remove genomes that has no top scores, respect to its specie
        # self.scoreSpecies()
        # REFILL POPULATION
        respeciate = self.reproduce()
        # if respeciate:
        #    self.speciate()
        # in crossover there exist a 75% of crossover and 25% of just copy
        # todo: champion selection where species has more than 5 individuals
        self.mutate()
        self.scoreSpecies()

        for specie in self.species.data:
            specie.increaseGeneration()


        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            genome.orderNetwork()

        
    def printSpecies(self)->None:
        print("##########################################")
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            print(s)
        print("##########################################")
        
    def reproduce(self)->bool:

        respeciate:bool = False

        species_available:list = []
        for specie in self.species.data:
            if specie.can_reproduce:
                species_available.append(specie)

        len_species_available = len(species_available)
        if len_species_available > 0:
        
            # todo: optimize function
            to_remove = []
            to_add = []

            for i in range(len(self.genomes.data)):
                genome:Genome = self.genomes.data[i]
                # if the specie is dead select a random
                if genome.id_specie == -1:
                    specie:Specie = species_available[random.randint(0,len_species_available-1)]
                    # break new genome
                    # todo: check that genome_new is the same included in storage of neurons in empty_genome?
                    genome_new:Genome = self.empty_genome(prefill=True,connect_input_output=False)
                    genome_new:Genome = specie.breed(genome_new)

                    to_add.append(genome_new)
                    to_remove.append(genome)
                    # force this genome
                    specie.forcePut(genome_new)

            # needed not to change array while iterating
            for genome_new in to_add:
                self.genomes.add(genome_new)
            for genome in to_remove:
                self.genomes.remove(genome)

        else:
            # specie stagnated, generate new specimens
            respeciate = True
            # todo: optimize function
            to_remove = []
            to_add = []
            for i in range(len(self.genomes.data)):
                genome:Genome = self.genomes.data[i]
                # if the specie is dead select a random
                if genome.id_specie == -1:
                    
                    genome_new:Genome = self.empty_genome(prefill=True)

                    to_add.append(genome_new)
                    to_remove.append(genome)

            # needed not to change array while iterating
            for genome_new in to_add:
                self.genomes.add(genome_new)
            for genome in to_remove:
                self.genomes.remove(genome)

        return respeciate

    def mutate(self)->None:

        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]


            # alter the rate for every mutation 
            for mutation,rate in genome.mutation_rates.items():
                if random.random() < 0.5:
                    genome.mutation_rates[mutation] = 0.95 * rate
                else:
                    genome.mutation_rates[mutation] = 1.05 * rate
                

            # mutate weights
            p1:float = random.random()
            if p1 < genome.mutation_rates["connection_weight"]:
                # if mutate, exist a probability of become weights random or just do a step
                genome.mutateConnectionWeights()

            # mutate link
            p2:float = random.random()
            if p2 < genome.mutation_rates["link"]:
                self.mutateGenomeLink(genome)

            if len(genome.hidden_neurons) < genome.MAX_HIDDEN_NEURONS:
                p3:float = random.random()
                if p3 < genome.mutation_rates["node"]:
                    self.mutateGenomeNode(genome)

            p4:float = random.random()
            if p4 < genome.mutation_rates["enable"]:
                genome.mutateRandomLinkToggle(toggle_to_enabled=True)

            p5:float = random.random()
            if p5 < genome.mutation_rates["disable"]:
                genome.mutateRandomLinkToggle(toggle_to_enabled=False)
                

    def mutateGenomeLink(self, genome:Genome)->bool:
        # todo: improve search selection. important!
        added:bool = False
        for _ in range(100):
            a, b = genome.getRandomGenePair()

            con:Connection = None
            if a.x < b.x:
                connection_type:int = b.getNeuronType()
                con = Connection(a,b)
            else:
                connection_type:int = a.getNeuronType()
                con = Connection(b,a)


            con = self.getConnection(con.neuronFrom, con.neuronTo)

            if genome.existConnection(con.innovation_number):
                # if exists or is not set to False, return
                continue

            con.weight = Connection.getRandomWeight(multiplier_range=0.5)

            
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
        

        from_neuron:Neuron = con.neuronFrom
        to_neuron:Neuron = con.neuronTo

        # always split the link into two nodes
        replace_index, key = self.getReplaceIndex(from_neuron,to_neuron)

        middle:Neuron = None

        create_new_node:bool = True

        if replace_index > 0:
            # already exist a node in the connection
            if not genome.existNeuronInnovationNumber(replace_index):
                # If already exist a neuron in general, but not in genome, create a copy
                middle = self.getNeuron(replace_index)
                create_new_node = False
        
        if create_new_node:
            # if no previous neuron was created between this connection
            x = (from_neuron.x + to_neuron.x)/2
            y = (from_neuron.y + to_neuron.y)/2 + (random.random() * 0.1 - 0.05)
            innovation_number:int = len(self.map_neuron_innovation_number)+1
            middle:Neuron = self.getNeuronNew(x,y,innovation_number,self.activationFunctionHidden)
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
        # genome.removeConnection(con) If we remove, then in a mutation will create it again... a loop forever
        con.enabled = False
        # the middle is a brand new or existing in general storage mapping
        genome.insertNeuron(middle)

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

    def getSumSpeciesScore(self):
        s:float = 0

        for specie in self.species.data:
            s += specie.score
        
        return s


    def removeSpeciesWeak(self)->None:
        # remove species that not aport in the total average sum
        total_sum:float = self.getSumSpeciesScore()

        i:int = self.species.size()-1
        while i >= 0:
            contribution:float = math.floor((self.species.get(i).score/total_sum) * self.POPULATION)
            if contribution < 1:
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

        self.scoreSpecies()

        

    def scoreSpecies(self):
        # evaluate scores for each specie
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            s.evaluateScore()
    
    def reducePopulation(self, SURVIVORS:float = 0.5)->None:
        # kill X% of population
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            s.reducePopulation(1-SURVIVORS)



