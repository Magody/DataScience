from multiprocessing import connection
import pygame
from models.Neat import *
import random
from models.evolution.Genome import Genome
from tqdm import tqdm

WHITE =     (255, 255, 255)
BLUE =      (  0,   0, 255)
GREEN =     (  0, 255,   0)
RED =       (255,   0,   0)
TEXTCOLOR = WHITE

CONNECTION_ENABLED = (108, 235, 226)
CONNECTION_DISABLED = (156, 87, 19)

BACKGROUND_COLOR = (  0,   0,  0)




(width, height) = (900, 600)

running = True

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("TUFF")
screen.fill(BACKGROUND_COLOR)
pygame.display.update()

font = pygame.font.Font(None, 24)
font_neuron_output =  pygame.font.Font(None, 20)


######
epochs = 100
global input_size, output_size
input_size = 2 # + 1 bias?

max_population = 200
output_size = 1

neat:Neat = Neat(input_size,output_size,max_population)

neat.WEIGHT_SHIFT_STRENGTH = 1
neat.WEIGHT_RANDOM_STRENGTH = 3 # for normal initialization

neat.PROBABILITY_MUTATE_LINK = 0.1
neat.PROBABILITY_MUTATE_NODE = 0.1
neat.PROBABILITY_MUTATE_WEIGHT_SHIFT = 0.3
neat.PROBABILITY_MUTATE_WEIGHT_RANDOM = 0.01
neat.PROBABILITY_MUTATE_TOGGLE_LINK = 0.001

def score(genome:Genome)->float:
    # fitness function: XOR
    global input_size, output_size

    fitness:float = 0

    for i in range(2):
        for j in range(2):

            inp:list = [i,j]

            output:list = genome.forward(inp)

            if inp[0] == inp[1]:
                # 0 XOR 0 = 0, 1 XOR 1 = 0
                fitness += (1 - output[0])
            else:
                # 1 XOR 0 = 1, 0 XOR 1 = 1
                fitness += (output[0] - 0)

    return fitness/4


print("EVOLVING PHASE")
for i in tqdm(range(epochs)):
    for j in range(len(neat.genomes.data)):
        genome:Genome = neat.genomes.data[j]
        genome.score = score(genome)
    
    neat.evolve()
    if (i+1)%10 == 0:
        neat.printSpecies()

best_genome = neat.getBestGenomeInSpecies()
    
print(f"BEST SCORE {best_genome.score}")
print(round(best_genome.forward([0,0])[0],2))
print(round(best_genome.forward([0,1])[0],2))
print(round(best_genome.forward([1,0])[0],2))
print(round(best_genome.forward([1,1])[0],2))

genome = best_genome
print("HIDDEN CHECK 1", genome.hidden_neurons)
print("HIDDEN CHECK 2", len(genome.hidden_connections))
#####

def clean():
    screen.fill(BACKGROUND_COLOR)
    pygame.display.update()

def getXYPixel(neuron):
    x = width * neuron.x
    y = height * neuron.y
    return (x,y)


def drawNeuron(neuron,offset=(0,0),color=BLUE):
    (x,y) = getXYPixel(neuron)
    x += offset[0]
    y += offset[1]
    pygame.draw.circle(screen, color, (x,y), 10)
    x -= 5
    y -= 3
    screen.blit(font_neuron_output.render(f"{round(neuron.output,2)}", True, WHITE), (x,y))




def drawConnections(connections:list):

    for i in range(len(connections)):
        connection:Connection = connections[i]

        point_start = getXYPixel(connection.from_neuron)
        point_end = getXYPixel(connection.to_neuron)

        pygame.draw.line(
            screen,
            CONNECTION_ENABLED if connection.enabled else CONNECTION_DISABLED, 
            point_start, 
            point_end
        )

        point_middle = (
            (point_end[0]+point_start[0])/2 - 30,
            (point_end[1]+point_start[1])/2,
        )
        screen.blit(font.render(f"{round(connection.weight,3)}", True, WHITE), point_middle)


def drawGenome(genome:Genome):
    clean()

    genome.forward([0,1])

    for neuron in genome.input_neurons:
        drawNeuron(neuron,color=BLUE)

    for neuron in genome.hidden_neurons:
        drawNeuron(neuron,color=(40, 206, 247))

    for i,neuron in enumerate(genome.output_neurons):
        drawNeuron(neuron,color=(125, 25, 60))

    drawConnections(genome.connections)

   
    

    pygame.display.update()

######

drawGenome(genome)

while running:
    ev = pygame.event.get()

    for event in ev:
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                genome = neat.empty_genome()
                clean()
                drawGenome(genome)

            if event.key == pygame.K_t:
                drawGenome(genome)

            if event.key == pygame.K_a:
                neat.mutateGenomeNode(genome)
                drawGenome(genome)
            
            if event.key == pygame.K_s:
                neat.mutateGenomeLink(genome)
                drawGenome(genome)

            if event.key == pygame.K_d:
                genome.mutateLinkToggle()
                drawGenome(genome)
            
            if event.key == pygame.K_w:
                genome.mutateWeightRandom(neat.WEIGHT_RANDOM_STRENGTH)
                drawGenome(genome)
            
            if event.key == pygame.K_e:
                genome.mutateWeightShift(neat.WEIGHT_SHIFT_STRENGTH)
                drawGenome(genome)


        if event.type == pygame.QUIT:
            running = False
