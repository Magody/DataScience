import math

class ActivationFunction:

    @staticmethod
    def sigmoid(x:float):
        # default activation is sigmoid
        return 1 / (1 + math.exp(-x))
