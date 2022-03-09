import math
import random
from .Gene import Gene, GeneAttributeFloat, GeneAttributeBool
from .Neuron import Neuron
from ..Colors import wc

class Connection(Gene):
    # GLOBAL/STATIC variables
    ALL_CONNECTIONS:dict = dict() # type hashmap<hashcode, ConnectionGene>

    ## GENE ATTRIBUTES
    weight:GeneAttributeFloat = None
    enabled:GeneAttributeBool = None
    
    # Internal innovation numbers for reference
    neuronFrom:Neuron = None
    neuronTo:Neuron = None

    replace_index:int = 0

    def __init__(self,from_neuron:Neuron,to_neuron:Neuron):
        self.neuronFrom = from_neuron
        self.neuronTo = to_neuron
        self.weight = GeneAttributeFloat(min_value=-2,max_value=2)
        self.enabled = GeneAttributeBool(mutate_rate=0.01, value=True, default="True", rate_to_false_add=0, rate_to_true_add=0)
        self.replace_index:int = 0
        
    def mutate(self):
        history = {"summary": "Nothing"}
        s_weight = self.weight.mutate()['summary']
        if s_weight != "Nothing":
            history["summary"] = f"WEIGHT:{s_weight}"
            
        s = self.enabled.mutate()['summary']
        if s != "Nothing":
            if s_weight != "Nothing":
                history["summary"] += f". ENABLED:{s}" 
            else:
                history["summary"] = f". ENABLED:{s}" 
        return history
        
    def distance(self, other, compatibility_weight_coefficient):
        d = abs(self.weight.value - other.weight.value)
        if self.enabled.value != other.enabled.value:
            d += 1.0
        return d * compatibility_weight_coefficient        

    def setInnovationNumber(self, innovation_number):
        self.innovation_number = innovation_number
        self.key = innovation_number

    def getConnectionType(self):
        return self.neuronTo.getNeuronType()

    @staticmethod
    def copy(connection,from_neuron_new:Neuron,to_neuron_new:Neuron):
        # todo: optimize?
        """
        We have to pass containers by reference for neurons!!
        Creates a connection from new neurons replicated from innovation numbers in connection
        """
        connection_copy:Connection = Connection(from_neuron_new, to_neuron_new)
        connection_copy.weight = connection.weight.copy()
        connection_copy.enabled = connection.enabled.copy()
        connection_copy.replace_index = connection.replace_index # todo: check replace index
        connection_copy.setInnovationNumber(connection.innovation_number)


        return connection_copy

    def equals(self, object):
        if not type(object) is Connection:
            return False
        return self.neuronFrom.innovation_number == object.neuronFrom.innovation_number and self.neuronTo.innovation_number == object.neuronTo.innovation_number

    def __str__(self):
        return f"{self.neuronFrom}{wc('fail', '-(' +str(round(self.weight.value,2))+ ')>')}{str(self.neuronTo)}"
        
    def hashCode(self)->int:
        MAX_NODES = math.pow(2,20)
        return int(self.neuronFrom.innovation_number * MAX_NODES + self.neuronTo.innovation_number)


    @staticmethod
    def getConnection(node1:Neuron, node2:Neuron):
        # return Connection

        # have to be a new object with same existing innovation number or new one
        connectionGene:Connection = Connection(node1,node2)

        key = connectionGene.hashCode()
        if key in Connection.ALL_CONNECTIONS:
            # just copy the innovation_number
            connectionGene.setInnovationNumber(Connection.ALL_CONNECTIONS[key].innovation_number)
        else:
            connectionGene.setInnovationNumber(len(Connection.ALL_CONNECTIONS) + 1)
            Connection.ALL_CONNECTIONS[key] = connectionGene
        
        return connectionGene

    @staticmethod
    def setReplaceIndex(node1:Neuron, node2:Neuron, index:int)->None:
        connectionGene:Connection = Connection(node1,node2)
        key = connectionGene.hashCode()
        Connection.ALL_CONNECTIONS[key].replace_index = index

    @staticmethod
    def getReplaceIndex(node1:Neuron, node2:Neuron)->int:
        connectionGene:Connection = Connection(node1,node2)
        key = connectionGene.hashCode()
        data:Connection = Connection.ALL_CONNECTIONS.get(key, None)

        if data is None:
            return 0, key
        return data.replace_index, key
