import math

class ActivationFunction:

    @staticmethod
    def sigmoid(x:float):
        # default activation is sigmoid
        return float(1) / (1 + math.exp(-x))
