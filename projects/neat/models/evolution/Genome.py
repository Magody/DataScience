import random
from ..data_structures.RandomHashSet import RandomHashSet
from ..network.Neuron import *



class Genome:

    score:float = 0

    id_specie: int = -1

    def __init__(self,input_neurons:list,hidden_neurons:list,output_neurons:list,C1=1,C2=1,C3=1,CP=4):

        self.id_specie = -1
        self.score:float = 0

        self.C1:float = C1
        self.C2:float = C2
        self.C3:float = C3
        self.CP:float = CP

        self.input_neurons:list = input_neurons # type: Neuron
        self.hidden_neurons:list = hidden_neurons # type: Neuron
        self.output_neurons:list = output_neurons # type: Neuron

        self.connections_hash:dict = dict()

        # Input just for hashing. type: hashmap<to_neuron.innovation_number:int,list[Connection]> 
        self.input_connections:dict = {neuron.innovation_number:[] for neuron in self.input_neurons}
        # type: hashmap<to_neuron.innovation_number:int,list[Connection]> 
        self.hidden_connections:dict = {neuron.innovation_number:[] for neuron in self.hidden_neurons}
        # type: hashmap<to_neuron.innovation_number:int,list[Connection]> 
        self.output_connections:dict = {neuron.innovation_number:[] for neuron in self.output_neurons} # type: hashmap<to_neuron.innovation_number:int,list[Connection]>

        # redundancy, more RAM for faster proccessing
        self.connections:list = []
        self.neurons:list = []
        self.neurons.extend(input_neurons)
        self.neurons.extend(hidden_neurons)
        self.neurons.extend(output_neurons)


    def existGene(self, innovation_number:int):

        return innovation_number in self.input_connections or innovation_number in self.hidden_connections or innovation_number in self.output_connections
        

    
    def orderNetwork(self):
        # 0.1(input) -> 0.1<x<0.9 (hidden) -> 0.9(output)
        # todo: can be improved maybe
        self.hidden_neurons.sort(key=lambda neuron: neuron.x) # , reverse=True
        # self.connections.sort(key=lambda con: con.innovation_number)

    def insertGene(self,gene:Neuron)->None:
        
        neuron_type:int = gene.getNeuronType()

        if gene.innovation_number in self.input_connections:
            # sanity control
            return
        if gene.innovation_number in self.output_connections:
            # sanity control
            return
        if gene.innovation_number in self.hidden_connections:
            # sanity control
            return

        self.neurons.append(gene)

        if neuron_type == EnumConnectionTypes.TYPE_INPUT:
            self.input_neurons.append(gene)
        elif neuron_type == EnumConnectionTypes.TYPE_HIDDEN:
            self.hidden_neurons.append(gene)     
        elif neuron_type == EnumConnectionTypes.TYPE_OUTPUT:
            self.output_neurons.append(gene)            
        else:
            raise Exception(f"Not supported connection type: {gene.x}")


    def insertConnection(self,connection:Connection)->None:
       
        connection_type:int = Connection.getConnectionType(connection)


        # todo: all this function can be improved ordering in insertion

        if self.connections_hash.get(connection.innovation_number,False):
            # if exists or is not set to False, return
            raise Exception("Connection already inserted")

        self.connections_hash[connection.innovation_number] = True

        len_connections = len(self.connections)
        if len_connections == 0:
            self.connections.append(connection)
        else:
            inserted:bool = False
            for i in range(len_connections):
                innovation_number:int = self.connections[i].innovation_number
                if connection.innovation_number <= innovation_number:
                    self.connections.insert(i, connection)
                    inserted = True
                    break
            if not inserted:
                self.connections.append(connection)

        if connection_type == EnumConnectionTypes.TYPE_HIDDEN:
            if not connection.to_neuron.innovation_number in self.hidden_connections:
                self.hidden_connections[connection.to_neuron.innovation_number] = []   
            self.hidden_connections[connection.to_neuron.innovation_number].append(connection)
            
        elif connection_type == EnumConnectionTypes.TYPE_OUTPUT:
            if not connection.to_neuron.innovation_number in self.output_connections:
                self.output_connections[connection.to_neuron.innovation_number] = []   

            self.output_connections[connection.to_neuron.innovation_number].append(connection)
            
        else:
            raise Exception(f"Not supported connection type: {connection.to_neuron.x}")

        

        

    def removeConnection(self,connection:Connection)->None:
       
        connection_type:int = Connection.getConnectionType(connection)




        self.connections_hash[connection.innovation_number] = False

        if connection_type == EnumConnectionTypes.TYPE_HIDDEN:
            self.hidden_connections[connection.to_neuron.innovation_number].remove(connection)
        elif connection_type == EnumConnectionTypes.TYPE_OUTPUT:
            self.output_connections[connection.to_neuron.innovation_number].remove(connection)
        else:
            raise Exception(f"Not supported connection type: {connection.to_neuron.x}")

        
        self.connections.remove(connection)





    def getRandomGene(self):

        len_neurons:int = len(self.neurons)

        if len_neurons == 0:
            return None

        selected:int = random.randint(0,len_neurons-1)
        return self.neurons[selected]

    def getRandomGenePair(self):
        families:list = [0,1,2]
        a:Neuron = self.getRandomGene()
        b:Neuron = None

        family:int = -1
        if a.x == 0.1:
            family = 0
        elif a.x == 0.9:
            family = 2
        else:
            family = 1

        families.remove(family)
        other_family = families[random.randint(0,len(families)-1)]

        if other_family == 1:
            len_hidden = len(self.hidden_neurons)
            if len_hidden == 0:
                families.remove(other_family)
                other_family = families[random.randint(0,len(families)-1)]
            else:
                b = self.hidden_neurons[random.randint(0,len(self.hidden_neurons)-1)]

        if other_family == 0:
            b = self.input_neurons[random.randint(0,len(self.input_neurons)-1)]
        
        if other_family == 2:
            b = self.output_neurons[random.randint(0,len(self.output_neurons)-1)]

        
        return a,b


        

    def getRandomConnection(self):

        len_connections:int = len(self.connections)

        if len_connections == 0:
            return None

        selected_connection:int = random.randint(0,len_connections-1)
        return self.connections[selected_connection]

        

    def forward(self,input:list)->list:
        # input double
        len_input_neurons = len(self.input_neurons)
        len_hidden_neurons = len(self.hidden_neurons)
        len_output_neurons = len(self.output_neurons)

        if len(input) != len_input_neurons:
            raise Exception("Data doesn't fit")
        
        # Forward input (feed)
        for i in range(len_input_neurons):
            self.input_neurons[i].output = input[i]

        # forward hidden in order by x
        for i in range(len_hidden_neurons):
            hidden_neuron:Neuron = self.hidden_neurons[i]
            hidden_neuron_connections:list = self.hidden_connections[hidden_neuron.innovation_number]
            
            hidden_neuron_output:float = 0
            for j in range(len(hidden_neuron_connections)):
                c:Connection = hidden_neuron_connections[j]
                if c.enabled:
                    hidden_neuron_output += c.weight * c.from_neuron.output
            
            hidden_neuron.output = hidden_neuron.activationFunction(hidden_neuron_output)

        # forward output layer
        output:list = [0 for _ in range(len(self.output_neurons))]

        for i in range(len_output_neurons):
            output_neuron:Neuron = self.output_neurons[i]
            output_neuron_connections:list = self.output_connections[output_neuron.innovation_number]
            
            output_neuron_output:float = 0
            for j in range(len(output_neuron_connections)):
                c:Connection = output_neuron_connections[j]
                if c.enabled:
                    output_neuron_output += c.weight * c.from_neuron.output
            
            output_neuron.output = output_neuron.activationFunction(output_neuron_output)
            Genome.TEST_SCORE += output_neuron_output
            Genome.TEST_SCORE_COUNT += 1
            output[i] = output_neuron.output

        return output


    TEST_SCORE = 0
    TEST_SCORE_COUNT = 0
    """
    calculated the distance between this genome g1 and a second genome g2
        - g1 must have the highest innovation number!
    """
    def distance(self, g2)->float:
        # todo: check this function with the paper
        # g2 -> Genome
        g1 = self

        len_connections_g1:int = len(g1.connections)
        len_connections_g2:int = len(g2.connections)

        highest_innovation_gene1 = 0
        if len_connections_g1 != 0:
            highest_innovation_gene1 = g1.connections[len_connections_g1-1].innovation_number

        highest_innovation_gene2 = 0
        if len_connections_g2 != 0:
            highest_innovation_gene2 = g2.connections[len_connections_g2-1].innovation_number

        if highest_innovation_gene1 < highest_innovation_gene2:
            g = g1
            g1 = g2
            g2 = g
            # recalculate lens
            len_connections_g1:int = len(g1.connections)
            len_connections_g2:int = len(g2.connections)

        index_g1:int = 0
        index_g2:int = 0
        disjoint:int = 0
        excess:int = 0
        weight_diff:float = 0
        similar:int = 0

        while index_g1 < len_connections_g1 and index_g2 < len_connections_g2:
            gene1:Connection = g1.connections[index_g1]
            gene2:Connection = g2.connections[index_g2]

            in1:int = gene1.innovation_number
            in2:int = gene2.innovation_number

            if in1 == in2:
                # similar gene
                similar += 1
                weight_diff += abs(gene1.weight-gene2.weight)
                index_g1 += 1
                index_g2 += 1
            elif in1 > in2:
                # disjoint gene of b
                disjoint += 1
                index_g2 += 1
            else:
                # disjoint gene of a
                disjoint += 1
                index_g1 += 1

        weight_diff /= max(1,similar)
        excess = len_connections_g1 - index_g1

        N = max(len_connections_g1,len_connections_g2)
        if N < 20:
            N = 1

        return ((self.C1 * disjoint)/N) + ((self.C2 * excess) / N) + (self.C3 * weight_diff)


    def mutateWeightShift(self, WEIGHT_SHIFT_STRENGTH): 
        con:Connection = self.getRandomConnection()
        if not con is None:
            con.weight = con.weight + ((random.random()*2-1) * WEIGHT_SHIFT_STRENGTH)
        
    def mutateWeightRandom(self, WEIGHT_RANDOM_STRENGTH): 
        con:Connection = self.getRandomConnection()
        if not con is None:
            con.weight = ((random.random()*2-1) * WEIGHT_RANDOM_STRENGTH)
        
    def mutateLinkToggle(self):
        con:Connection = self.getRandomConnection()
        if not con is None:
            con.enabled = not con.enabled


    
    """
    * creates a new genome.
     * g1 should have the higher score
     *  - take all the genes of a
     *  - if there is a genome in a that is also in b, choose randomly
     *  - do not take disjoint genes of b
     *  - take excess genes of a if they exist
     return Genome
    """
    @staticmethod
    def crossover(g1, g2, genome):
        """ 
        g1 has to be the genome with highest score.
        """

        # genome is a "empty" base genome with existing or no nodes

        index_g1 = 0
        index_g2 = 0

        # Connections have to be sorted for this alignment
        while index_g1 < len(g1.connections) and index_g2 < len(g2.connections):

            connection1:Connection = g1.connections[index_g1]
            connection2:Connection = g2.connections[index_g2]

            in1:int = connection1.innovation_number
            in2:int = connection2.innovation_number



            



            if in1 == in2:
                # similar gene
                if random.random() > 0.5:
                    genome.insertConnection(connection1)
                else:
                    genome.insertConnection(connection2)
                index_g1 += 1
                index_g2 += 1
            elif in1 > in2:
                # disjoint gene of b
                # g1 has better score, so g2 is discarded
                index_g2 += 1
            else:
                # disjoint gene of a
                # g1 has better score, so preserve the gene
                genome.insertConnection(connection1)
                index_g1 += 1

        before = [index_g1,len(genome.connections)]

        if before[1] == 0 and len(g1.connections) == 2:
            print()

        while index_g1 < len(g1.connections):
            # todo: check if this is useful
            connection1:Connection = g1.connections[index_g1]
            genome.insertConnection(connection1)
            index_g1 += 1

        for i in range(len(genome.connections)):
            c:Connection = genome.connections[i]
            genome.insertGene(c.from_neuron)
            genome.insertGene(c.to_neuron)

        #cons1 = [cons_b for cons_a in genome.hidden_connections.values() for cons_b in cons_a]
        #cons2 = [cons_b for cons_a in genome.output_connections.values() for cons_b in cons_a]
        #if len(cons1) + len(cons2) != len(genome.connections):
        #    print()


        return genome
        

    
