import random
from .data_structures.RandomHashSet import RandomHashSet
from .data_structures.RandomSelector import RandomSelector
from .evolution.Genome import Genome
from .network.Neuron import *
from .evolution.Specie import Specie
from .network.Activation import ActivationFunction

class Neat:


    SURVIVORS:float = 0.8

    WEIGHT_SHIFT_STRENGTH:float = 0.3
    WEIGHT_RANDOM_STRENGTH:float = 1

    PROBABILITY_MUTATE_LINK:float = 0.01
    PROBABILITY_MUTATE_NODE:float = 0.05
    PROBABILITY_MUTATE_WEIGHT_SHIFT:float = 0.02
    PROBABILITY_MUTATE_WEIGHT_RANDOM:float = 0.02
    PROBABILITY_MUTATE_TOGGLE_LINK:float = 0
    

    all_connections = dict() # type hashmap<ConnectionGene, ConnectionGene>

    all_nodes:RandomHashSet = None # type NodeGene
    genomes:RandomHashSet = None # type Genome
    species:RandomHashSet = None # type Specie

    max_clients:int = 0
    output_size:int = 0
    input_size:int = 0



    def __init__(self,input_size:int, output_size:int, clients:int):
        

        

        self.SURVIVORS:float = 0.8

        
        self.all_connections = dict()
        self.all_nodes = RandomHashSet()
        self.genomes = RandomHashSet()
        self.species = RandomHashSet()


        self.WEIGHT_SHIFT_STRENGTH:float = 0.3
        self.WEIGHT_RANDOM_STRENGTH:float = 1
        self.PROBABILITY_MUTATE_LINK:float = 0.01
        self.PROBABILITY_MUTATE_NODE:float = 0.1
        self.PROBABILITY_MUTATE_WEIGHT_SHIFT:float = 0.02
        self.PROBABILITY_MUTATE_WEIGHT_RANDOM:float = 0.02
        self.PROBABILITY_MUTATE_TOGGLE_LINK:float = 0.01

        self.reset(input_size, output_size, clients)


    def reset(self, input_size:int, output_size:int, clients:int)->None:
        # print("d:NEAT:reset")
        self.input_size = input_size
        self.output_size = output_size
        self.max_clients = clients

        self.all_connections.clear()
        self.all_nodes.clear()
        self.genomes.clear()

        for i in range(input_size):
            y = (i+1)/float(input_size+1)
            n:Neuron = self.getNeuronNew(0.1,y,ActivationFunction.sigmoid)

        for i in range(output_size):
            y = (i+1)/float(output_size+1)
            n:Neuron = self.getNeuronNew(0.9,y,ActivationFunction.sigmoid)

        for i in range(self.max_clients):
            genome:Genome = self.empty_genome()
            genome.reconnectNodes()
            self.genomes.add(genome)
    

    def getConnection(self, node1:Neuron, node2:Neuron)->Connection:

        connectionGene:Connection = Connection(node1,node2)

        key = connectionGene.hashCode()
        if key in self.all_connections:
            # todo: check that hashcode is the key
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
            return 0
        return data.replace_index

    def getNeuronNew(self,x:float,y:float,activation_function)->Neuron:
        n:Neuron = Neuron(x,y,self.all_nodes.size()+1,activation_function)
        self.all_nodes.add(n)
        return n

    def getNeuron(self,id:int,x:float=-1,y:float=-1)->Neuron:
        # singleton
        if id <= self.all_nodes.size():
            return self.all_nodes.get(id-1)
        return self.getNeuronNew(x,y,ActivationFunction.sigmoid)

    
    def empty_genome(self) -> Genome:

        nodes:RandomHashSet = RandomHashSet()
        for i in range(self.input_size+self.output_size):
            nodes.add(self.getNeuron(i+1))

        # todo: ensure is passed by reference
        g:Genome = Genome(nodes)

        return g

    
    # We need the reference control, so this method can't be in Specie
    def breedFromSpecie(self, specieFrom:Specie)->Genome:
        # return Genome
        genome1:Genome = specieFrom.genomes.randomElement()
        genome2:Genome = specieFrom.genomes.randomElement()


        genome_base:Genome = self.empty_genome()
        
        if genome1.score > genome2.score:
            return Genome.crossover(genome1,genome2,genome_base)
        
        return Genome.crossover(genome2,genome1,genome_base)


    def evolve(self)->None:


        self.genSpecies()
        self.kill() # reduce poblation a percentaje for each specie, selecting the best
        self.removeExtinctSpecies() # delete all species with one or less genomes (only representative or none)
        self.reproduce()
        self.mutate()


        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            genome.reconnectNodes()

        


    def printSpecies(self)->None:
        print("##########################################")
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            print(f"{s} {s.score} {s.size()}")
        
    def reproduce(self)->None:

        selector:RandomSelector = RandomSelector() # type Species

        # Get species with their score
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            selector.add(s,s.score)
        
        
        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]
            # if the specie is dead select a random
            if genome.id_specie == -1:
                s:Specie = selector.random()
                # break new genome
                genome_new:Genome = self.breedFromSpecie(s) # B
                genome_new.input_nodes = genome.input_nodes
                genome_new.hidden_nodes = genome.hidden_nodes
                genome_new.output_nodes = genome.output_nodes

                self.genomes.data[i] = genome_new
                # force this client into the specie
                s.forcePut(genome_new)
                

    def mutate(self)->None:

        for i in range(len(self.genomes.data)):
            genome:Genome = self.genomes.data[i]

            p_mutate_link:float = random.random()
            p_mutate_node:float = random.random()
            p_mutate_weight_shift:float = random.random()
            p_mutate_weight_random:float = random.random()
            p_mutate_link_toggle:float = random.random()

            if p_mutate_link < self.PROBABILITY_MUTATE_LINK:
                self.mutateGenomeLink(genome)
            if p_mutate_node < self.PROBABILITY_MUTATE_NODE:
                self.mutateGenomeNode(genome)
            if p_mutate_weight_shift < self.PROBABILITY_MUTATE_WEIGHT_SHIFT:
                genome.mutateWeightShift(self.WEIGHT_SHIFT_STRENGTH)
            if p_mutate_weight_random < self.PROBABILITY_MUTATE_WEIGHT_RANDOM:
                genome.mutateWeightRandom(self.WEIGHT_RANDOM_STRENGTH)
            if p_mutate_link_toggle < self.PROBABILITY_MUTATE_TOGGLE_LINK:
                genome.mutateLinkToggle()

    def mutateGenomeLink(self, genome:Genome, trysearch=100):

        for i in range(trysearch):
            a:Neuron = genome.neurons.randomElement()
            b:Neuron = genome.neurons.randomElement()

            if a is None or b is None:
                continue

            if a.x == b.x:
                continue


            con:Connection = None
            if a.x < b.x:
                con = Connection(a,b)
            else:
                con = Connection(b,a)

            if genome.connections.contains(con):
                continue

            con = self.getConnection(con.from_neuron, con.to_neuron)
            con.weight = (random.random() * 2 - 1) * self.WEIGHT_RANDOM_STRENGTH

            genome.connections.addSorted(con) # check if is connections from genome or neat
            return

    def mutateGenomeNode(self, genome:Genome):
        con:Connection = genome.connections.randomElement()
        if con is None:
            return

        from_neuron:Neuron = con.from_neuron
        to_neuron:Neuron = con.to_neuron

        replace_index:int = self.getReplaceIndex(from_neuron,to_neuron)

        middle:Neuron = None

        if replace_index == 0:
            x = (from_neuron.x + to_neuron.x)/2
            y = (from_neuron.y + to_neuron.y)/2 + (random.random() * 0.1 - 0.05)

            middle:Neuron = self.getNeuronNew(x,y,ActivationFunction.sigmoid)
            self.setReplaceIndex(from_neuron,to_neuron,middle.innovation_number)
        else:
            middle = self.getNeuron(replace_index)

        

        con1:Connection = self.getConnection(from_neuron,middle)
        con2:Connection = self.getConnection(middle,to_neuron)

        con1.weight = 1
        con2.weight = con.weight
        con2.enabled = con.enabled

        genome.connections.remove(con)
        genome.connections.add(con1)
        genome.connections.add(con2)

        genome.neurons.add(middle)

    def removeExtinctSpecies(self)->None:
        i:int = self.species.size()-1
        while i >= 0:

            # if only representative is left...
            if self.species.get(i).size() <= 1:
                self.species.get(i).goExtinct()
                self.species.removeByIndex(i)

            i -= 1

    def genSpecies(self)->None:
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
    
    def kill(self)->None:
        # kill X% of population
        for i in range(len(self.species.data)):
            s:Specie = self.species.data[i]
            s.kill(1-self.SURVIVORS)



