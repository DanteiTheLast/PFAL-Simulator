import pygame
from pygame.locals import *

# Inicializar PyGame
pygame.init()
screen = pygame.display.set_mode((800, 600))

# Bucle principal
running = True
time_factor = 1.0
clock = pygame.time.Clock()

while running:
    dt = clock.tick(60) * time_factor / 1000.0  # Delta time ajustado

    # Eventos (ej: acelerar tiempo con teclas)
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_1: time_factor = 1.0
            if event.key == K_2: time_factor = 2.0

    # Actualizar lógica de simulación aquí (usar dt)
    update_pfal_simulation(dt)

    # Dibujar interfaz
    screen.fill((255, 255, 255))
    draw_pfal_graphics()
    pygame.display.flip()