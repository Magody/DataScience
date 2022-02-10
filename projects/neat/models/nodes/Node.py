import math

class Node:
    # crossed reference with Connection
    x:float = 0
    output:float = 0
    connections:list = []  # type: Connection

    def __init__(self,x:float):
        self.x = x
        self.output:float = 0
        self.connections:list = []  # type: Connection

    def calculate(self):
        s:float = 0
        for i in range(len(self.connections)):
            c:Connection = self.connections[i]
            if c.enabled:
                s += c.weight * c.from_node.output

        self.output = self.activationFunction(s)

    def activationFunction(self, x:float)->float:
        return float(1) / (1 + math.exp(-x))

    def compareTo(self, o):
        # o: Node
        if self.x > o.x:
            return -1
        if self.x < o.x:
            return 1
        return 0

class Connection:
    # crossed reference with Node
    from_node:Node = None
    to_node:Node = None
    weight:float = 0
    enabled:bool = True

    def __init__(self,from_node:Node,to_node:Node):
        self.from_node = from_node
        self.to_node = to_node
        self.weight:float = 0
        self.enabled:bool = True