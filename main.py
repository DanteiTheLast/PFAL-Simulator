import pygame
from pygame.locals import *
import numpy as np
from fuzzy_logic import crear_sistema_lechuga

# Configuración inicial
pygame.init()
ANCHO, ALTO = 1280, 720
screen = pygame.display.set_mode((ANCHO, ALTO))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

# Colores
COLOR_FONDO = (30, 30, 30)
COLOR_SLIDER = (70, 130, 180)
COLOR_TEXTO = (255, 255, 255)

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.min = min_val
        self.max = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False

    def draw(self, surface):
        # Barra del slider
        pygame.draw.rect(surface, (100, 100, 100), self.rect)
        
        # Indicador
        pos_x = self.rect.x + (self.val - self.min)/(self.max - self.min) * self.rect.width
        pygame.draw.circle(surface, COLOR_SLIDER, (int(pos_x), self.rect.centery), 10)
        
        # Texto
        text = font.render(f"{self.label}: {self.val:.1f}", True, COLOR_TEXTO)
        surface.blit(text, (self.rect.x, self.rect.y - 25))

    def update(self, event):
        if event.type == MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
        if event.type == MOUSEBUTTONUP:
            self.dragging = False
        if self.dragging and event.type == MOUSEMOTION:
            rel_x = event.pos[0] - self.rect.x
            self.val = np.clip((rel_x / self.rect.width) * (self.max - self.min) + self.min, self.min, self.max)

class PFALSimulator:
    def __init__(self):
        self.fuzzy_system = crear_sistema_lechuga()
        self.time_factor = 1.0
        self.sliders = [
            Slider(50, 50, 200, 20, 0, 40, 18, "Temperatura (°C)"),
            Slider(50, 100, 200, 20, 0, 100, 60, "Humedad (%)"),
            Slider(50, 150, 200, 20, 200, 2000, 1200, "CO₂ (ppm)"),
            Slider(50, 200, 200, 20, 5.0, 9.0, 6.8, "pH")
        ]
        
        # Estado de los actuadores
        self.ventilacion = 0.0
        self.inyector_co2 = 0.0
        self.ajuste_luz = 100.0

    def actualizar_fuzzy(self):
        # Obtener valores de los sliders
        inputs = {
            'temperatura': self.sliders[0].val,
            'humedad': self.sliders[1].val,
            'co2': self.sliders[2].val,
            'ph': self.sliders[3].val,
            'luz_intensidad': 270  # Valor fijo
        }
        
        # Asignar valores al sistema difuso
        for key, val in inputs.items():
            self.fuzzy_system.input[key] = val
        
        # Calcular las salidas
        try:
            self.fuzzy_system.compute()
            # Convertir a float y manejar KeyError
            self.ventilacion = float(self.fuzzy_system.output.get('ventilacion', 0.0))
            self.inyector_co2 = float(self.fuzzy_system.output.get('inyector_co2', 0.0))
            self.ajuste_luz = float(self.fuzzy_system.output.get('ajuste_luz', 100.0))
            print("Salidas del sistema difuso:", self.fuzzy_system.output)
            
        except Exception as e:
            print(f"Error: {e}")
            self.ventilacion = 0.0
            self.inyector_co2 = 0.0
            self.ajuste_luz = 100.0

    def dibujar_panel_control(self):
        # Dibujar racks
        pygame.draw.rect(screen, (150, 75, 0), (400, 200, 600, 50))  # Rack superior
        pygame.draw.rect(screen, (150, 75, 0), (400, 300, 600, 50))  # Rack inferior
        
        # Dibujar plantas (ej: etapa de crecimiento 1)
        screen.blit(planta_etapa1, (420, 210))
        screen.blit(planta_etapa1, (520, 210))
        
        # Dibujar luces
        if self.ajuste_luz > 0:
            screen.blit(luz_encendida, (450, 180))
        else:
            screen.blit(luz_apagada, (450, 180))
        
        # Panel de control lateral
        pygame.draw.rect(screen, (40, 40, 40), (0, 0, 350, 720))  # Fondo del panel
        for slider in self.sliders:
            slider.draw(screen)
        # Sliders
        for slider in self.sliders:
            slider.draw(screen)
        
        # Indicadores de actuadores
        y = 250
        for label, value in [("Ventilación", self.ventilacion),
                           ("Inyector CO₂", self.inyector_co2),
                           ("Ajuste Luz", self.ajuste_luz)]:
            text = font.render(f"{label}: {value:.1f}%", True, COLOR_TEXTO)
            screen.blit(text, (50, y))
            y += 30

    def run(self):
        running = True
        while running:
            dt = clock.tick(60) * self.time_factor / 1000.0
            screen.fill(COLOR_FONDO)
            
            # Manejar eventos
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                for slider in self.sliders:
                    slider.update(event)
                if event.type == KEYDOWN:
                    if event.key == K_1: self.time_factor = 1.0
                    if event.key == K_2: self.time_factor = 2.0
                    if event.key == K_3: self.time_factor = 5.0
            
            # Actualizar lógica
            self.actualizar_fuzzy()
            
            # Dibujar interfaz
            self.dibujar_panel_control()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    simulador = PFALSimulator()
    simulador.run()