import math
import random
from.Neuron import *

class Network:
    input_neurons:list = []
    hidden_neurons:list = []
    output_neurons:list = []

    def __init__(
        self,
        input_neurons:list,
        hidden_neurons:list,
        output_neurons:list
    ):
        self.input_neurons:list = input_neurons # type: Neuron
        self.hidden_neurons:list = hidden_neurons # type: Neuron
        self.output_neurons:list = output_neurons # type: Neuron

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


    def existNeuron(self, innovation_number:int):

        # todo: improve brute force
        for neuron in self.input_neurons:
            if neuron.innovation_number == innovation_number:
                return True
        for neuron in self.hidden_neurons:
            if neuron.innovation_number == innovation_number:
                return True
        for neuron in self.output_neurons:
            if neuron.innovation_number == innovation_number:
                return True

        return False

    def existConnection(self, innovation_number:int):

        # todo: improve brute force
        for con in self.connections:
            if con.innovation_number == innovation_number:
                return True

        return False
        

    
    def orderNetwork(self):
        # 0.1(input) -> 0.1<x<0.9 (hidden) -> 0.9(output)
        # todo: can be improved maybe
        self.hidden_neurons.sort(key=lambda neuron: neuron.x) # , reverse=True
        # self.connections.sort(key=lambda con: con.innovation_number)

    

    def insertNeuron(self,gene:Neuron)->None:
        neuron_type:int = gene.getNeuronType()

        if self.existNeuron(gene.innovation_number):
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

        connections_expected = self.getConnectionsFromHiddenAndOutput()
        connections_expected.sort(key=lambda con: con.innovation_number)
        self.connections.sort(key=lambda con: con.innovation_number)


        if connection_type == EnumConnectionTypes.TYPE_HIDDEN:
            index = -1
            for i in range(len(self.hidden_connections[connection.to_neuron.innovation_number])):
                con:Connection = self.hidden_connections[connection.to_neuron.innovation_number][i]
                if connection.innovation_number == con.innovation_number:
                    index = i
                    break
            self.hidden_connections[connection.to_neuron.innovation_number].pop(index)
        elif connection_type == EnumConnectionTypes.TYPE_OUTPUT:
            index = -1
            for i in range(len(self.output_connections[connection.to_neuron.innovation_number])):
                con:Connection = self.output_connections[connection.to_neuron.innovation_number][i]
                if connection.innovation_number == con.innovation_number:
                    index = i
                    break
            self.output_connections[connection.to_neuron.innovation_number].pop(index)
        else:
            raise Exception(f"Not supported connection type: {connection.to_neuron.x}")

        index = -1
        for i in range(len(self.connections)):
            con:Connection = self.connections[i]
            if connection.innovation_number == con.innovation_number:
                index = i
                break
        self.connections.pop(index)

        connections_expected = self.getConnectionsFromHiddenAndOutput()
        connections_expected.sort(key=lambda con: con.innovation_number)
        self.connections.sort(key=lambda con: con.innovation_number)

        


    def countConnections(self):
        cons1 = [cons_b for cons_a in self.hidden_connections.values() for cons_b in cons_a]
        cons2 = [cons_b for cons_a in self.output_connections.values() for cons_b in cons_a]
        
        return [len(cons1), len(cons2)]

    
    def getConnectionsFromHiddenAndOutput(self):
    
        cons1 = [cons_b for cons_a in self.hidden_connections.values() for cons_b in cons_a]
        cons2 = [cons_b for cons_a in self.output_connections.values() for cons_b in cons_a]
        cons1.extend(cons2)       
        return cons1


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
                    hidden_neuron_output += c.weight * c.from_neuron.output # todo: check bias
            
            hidden_neuron.output = hidden_neuron.activationFunction(hidden_neuron_output)

        # forward output layer
        output:list = [0 for _ in range(len(self.output_neurons))]

        for i in range(len_output_neurons):
            output_neuron:Neuron = self.output_neurons[i]
            output_neuron_connections:list = self.output_connections.get(output_neuron.innovation_number,[])            
            output_neuron_output:float = 0
            for j in range(len(output_neuron_connections)):
                c:Connection = output_neuron_connections[j]
                if c.enabled:
                    output_neuron_output += c.weight * c.from_neuron.output # todo: check bias
            
            # print("output:",input, output_neuron_output)
            output_neuron.output = output_neuron.activationFunction(output_neuron_output)
            output[i] = output_neuron.output


        return output