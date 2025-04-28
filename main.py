import pygame
from pygame.locals import *
from fuzzy_logic import crear_sistema_lechuga
from pfal_config import CULTIVOS

class PFALSimulator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        self.clock = pygame.time.Clock()
        self.fuzzy_system = crear_sistema_lechuga()
        self.cultivo_actual = CULTIVOS["lechuga"]
        self.time_factor = 1.0  # 1x, 2x, 5x

    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return False
            # Ej: Tecla '2' acelera a 2x
            if event.type == KEYDOWN and event.key == K_2:
                self.time_factor = 2.0
        return True

    def actualizar_simulacion(self, dt):
        # Aquí iría la lógica de actualización usando el sistema difuso
        pass

    def dibujar_interfaz(self):
        self.screen.fill((0, 0, 0))
        # Dibujar racks, luces, etc.
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) * self.time_factor / 1000.0
            running = self.manejar_eventos()
            self.actualizar_simulacion(dt)
            self.dibujar_interfaz()

if __name__ == "__main__":
    simulador = PFALSimulator()
    simulador.run()