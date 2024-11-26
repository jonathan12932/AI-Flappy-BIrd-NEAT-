import pygame
import neat
import time
import os
import random

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

class Bird: 

    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
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
        self.vel = -10.5
        self.tick_count = 0
        self.tilt += 30
        self.height = self.y
    
    def move(self):
        self.tick_count += 1
        
        # Displacement
        d = min(self.vel*self.tick_count + 1.5*self.tick_count**2, 16)
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

    VELOCITY = 5
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

# Initialize Pygame
pygame.init()

# Create game window
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Create a Bird object
bird = Bird(200, 350)

# Create Base object
base = Base(730)

# Game loop
while True:
    clock.tick(30)  # Limit the game to 30 FPS

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.jump()

    # Move everything
    bird.move()
    base.move()  # Move the base

    # Draw everything
    win.blit(BG_IMG, (0, 0))  # Draw the background
    bird.draw(win)  # Draw the bird
    base.draw(win)  # Draw the base
    pygame.display.update()  # Refresh the screen