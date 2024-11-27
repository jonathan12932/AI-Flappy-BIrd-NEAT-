import pygame
import neat
import time
import os
import random 
from collections import deque

# Default screen size
WIN_WIDTH = 600
WIN_HEIGHT = 800

# Scales image by 2x, loads image by finding its directory/file path location using os package
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
BG_IMG = pygame.transform.scale(BG_IMG, (WIN_WIDTH, WIN_HEIGHT))

class Bird: 

    def get_rect(self):
        # Return the bird's bounding rectangle
        return pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())

    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 30
    ANIMATION = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.imgcount = 0
        self.img = self.IMGS[0]
     
    def jump(self):
        self.vel = -8.75
        self.tick_count = 0
        self.tilt = 30
        self.height = self.y
    
    def move(self):
        self.tick_count += .5
        
        # Displacement
        d = min((self.vel*self.tick_count + 1.5*self.tick_count**2), 8)
        self.y += d

        # Set Rotation
        if d < 0 or self.y < self.height + 50:
            self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.imgcount += 1

        # Animate Flapping
        if self.imgcount < self.ANIMATION:
            self.img = self.IMGS[0]
        elif self.imgcount < self.ANIMATION * 2:
            self.img = self.IMGS[1]
        elif self.imgcount < self.ANIMATION * 3:
            self.img = self.IMGS[2]
        elif self.imgcount < self.ANIMATION * 4:
            self.img = self.IMGS[1]
        elif self.imgcount < self.ANIMATION * 4 + 1:
            self.img = self.IMGS[0]
            self.imgcount = 0

        # If bird is falling
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.imgcount = self.ANIMATION * 2

        # Rotate image around its center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

# Floor moving alonside bird
class Base:

    VELOCITY = 3.5
    WIDTH = BASE_IMG.get_width()

    # Creates two floor images to ensure floor is contantly fills up the width
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):

        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.WIDTH

    def draw(self, win):

        # Draw both parts of the base
        win.blit(BASE_IMG, (self.x1, self.y))
        win.blit(BASE_IMG, (self.x2, self.y))

class Pipe:

    VELOCITY = 3.5
    PIPE_GAP = 200  # Distance between top and bottom pipes
    PASSED = False

    def __init__(self):
        self.x = WIN_WIDTH
        self.y1 = random.randint(-500, -175)  # Random top pipe position
        self.y2 = self.y1 + PIPE_IMG.get_height() + self.PIPE_GAP  # Bottom pipe position
        self.top_rect = None
        self.bottom_rect = None

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, win):        
        rotated_image = pygame.transform.rotate(PIPE_IMG, 180)
        win.blit(rotated_image, (self.x, self.y1))  # Top pipe
        win.blit(PIPE_IMG, (self.x, self.y2))  # Bottom pipe

        # Update the collision rectangles
        self.top_rect = rotated_image.get_rect(topleft=(self.x, self.y1))
        self.bottom_rect = PIPE_IMG.get_rect(topleft=(self.x, self.y2))

    def collide(self, bird_rect):
        # Check collision with either top or bottom pipe
        if self.top_rect.colliderect(bird_rect) or self.bottom_rect.colliderect(bird_rect):
            return True
        return False

def draw_counter(win, pipes_crossed):
    # Shadow
    shadow_text = FONT.render(f"{pipes_crossed}", 1, (0, 0, 0))  # Black shadow
    win.blit(shadow_text, (WIN_WIDTH // 2 - shadow_text.get_width() // 2 + 2, 52))  # Offset shadow slightly

    # Main text
    counter_text = FONT.render(f"{pipes_crossed}", 1, (255, 255, 255))  # White text
    win.blit(counter_text, (WIN_WIDTH // 2 - counter_text.get_width() // 2, 50))  # Center the counter

# Initialize Pygame
pygame.init()
pygame.font.init()
FONT = pygame.font.SysFont("comicsans", 50)

# Create game window
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Load the configuration file
config_path = "config-feedforward.txt"  # Replace with your actual config file path
config = neat.config.Config(
    neat.DefaultGenome,
    neat.DefaultReproduction,
    neat.DefaultSpeciesSet,
    neat.DefaultStagnation,
    config_path,
)

# Create a NEAT population
population = neat.Population(config)

# Add reporters to monitor progress
population.add_reporter(neat.StdOutReporter(True))  # Print stats in the terminal
stats = neat.StatisticsReporter()
population.add_reporter(stats)

def fitness_function(genomes, config):
    birds = []
    nets = []
    genomes_list = []  # Keep track of genomes in the same order as birds

    for genome_id, genome in genomes:
        # Create a neural network for the genome
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(200, 350))  # Replace Bird() with your bird initialization logic
        genomes_list.append(genome)  # Keep track of the genome
        genome.fitness = 0  # Initialize fitness for this genome

    base = Base(730)
    pipes = deque([Pipe()])  # Start with one pipe
    spawnRate = 1
    pipes_crossed = 0

    # Game loop
    while len(birds) > 0:
        spawnRate += 1
        clock.tick(60)  # Limit the game to 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Spawn new pipes
        if spawnRate % 100 == 0:
            spawnRate = 1
            pipes.append(Pipe())

        # Move base and draw background
        base.move()
        win.blit(BG_IMG, (0, 0))  # Draw the background
        base.draw(win)

        # Move pipes and draw them
        for pipe in pipes:
            pipe.move()
            pipe.draw(win)

        # Remove pipes that are out of bounds
        if pipes and pipes[0].x + PIPE_IMG.get_width() < 0:
            pipes.popleft()

        # Birds to be removed
        birds_to_remove = []

        for i, bird in enumerate(birds):
            bird.move()
            bird.draw(win)

            # Update fitness: Give a small reward for staying alive
            genomes_list[i].fitness += 0.1

            # Check collision or out-of-bounds
            if bird.y + bird.img.get_height() >= base.y or bird.y < 0:
                birds_to_remove.append(i)  # Mark for removal
                continue

            # Check pipe collision
            for pipe in pipes:
                if pipe.collide(bird.get_rect()):
                    birds_to_remove.append(i)  # Mark for removal
                    break

            # Check if bird has passed a pipe
            for pipe in pipes:
                if not pipe.PASSED and pipe.x <= bird.x:
                    pipe.PASSED = True
                    pipes_crossed += 1
                    genomes_list[i].fitness += 10  # Reward for passing a pipe

            # Neural network output for bird
            if len(pipes) > 0:
                inputs = [
                    (pipes[0].y1 + PIPE_IMG.get_height() + (pipes[0].PIPE_GAP / 2) - bird.y) / WIN_HEIGHT,  # Distance to gap center
                    (pipes[0].x - bird.x) / WIN_WIDTH,  # Horizontal distance to pipe
                    bird.vel / 10, # Bird's vertical velocity
                ]
                output = nets[i].activate(inputs) # Get output from the neural network

                if output[0] > 0.5:  # Flap if output > 0.5
                    bird.jump()

        # Remove birds marked for removal
        for index in sorted(birds_to_remove, reverse=True):
            birds.pop(index)
            nets.pop(index)
            genomes_list.pop(index)

        draw_counter(win, pipes_crossed)  # Draw the counter
        pygame.display.update()  # Refresh the screen


    
def main():

    # Run NEAT with the fitness function
    winner = population.run(fitness_function, 50)  # 50 generations
    print(f"Best genome: {winner}")

# Start the game
main()