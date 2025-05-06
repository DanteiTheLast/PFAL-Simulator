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
        pygame.draw.rect(surface, (100, 100, 100), self.rect)
        pos_x = self.rect.x + (self.val - self.min)/(self.max - self.min) * self.rect.width
        pygame.draw.circle(surface, COLOR_SLIDER, (int(pos_x), self.rect.centery), 10)
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
        
        # Sliders
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
        self.ventilacion_angle = 0  # Para la animación
        
        # Cargar gráficos
        try:
            # Elementos principales
            self.rack_img = pygame.image.load("PFAL_Simulator/PFAL-Simulator/assets/rack.png").convert_alpha()
            self.planta_img = pygame.image.load("PFAL_Simulator/PFAL-Simulator/assets/lettuce.png").convert_alpha()
            self.luz_on = pygame.image.load("PFAL_Simulator/PFAL-Simulator/assets/luz_on.png").convert_alpha()
            self.luz_off = pygame.image.load("PFAL_Simulator/PFAL-Simulator/assets/luz_off.png").convert_alpha()
            
            # Nuevas imágenes de ventilación
            self.ventilacion_on = pygame.image.load("PFAL_Simulator/PFAL-Simulator/assets/ventilacion_on.png").convert_alpha()
            self.ventilacion_off = pygame.image.load("PFAL_Simulator/PFAL-Simulator/assets/ventilacion_off.png").convert_alpha()
            
        except Exception as e:
            print(f"Error cargando imágenes: {e}")
            pygame.quit()
            exit()

    def actualizar_fuzzy(self):
        inputs = {
            'temperatura': self.sliders[0].val,
            'humedad': self.sliders[1].val,
            'co2': self.sliders[2].val,
            'ph': self.sliders[3].val,
            'luz_intensidad': 270
        }
        
        for key, val in inputs.items():
            self.fuzzy_system.input[key] = val
        
        try:
            self.fuzzy_system.compute()
            self.ventilacion = float(self.fuzzy_system.output.get('ventilacion', 0.0))
            self.inyector_co2 = float(self.fuzzy_system.output.get('inyector_co2', 0.0))
            self.ajuste_luz = float(self.fuzzy_system.output.get('ajuste_luz', 100.0))
        except Exception as e:
            print(f"Error: {e}")
            self.ventilacion, self.inyector_co2, self.ajuste_luz = 0.0, 0.0, 100.0

    def dibujar_pfab(self):
        config = {
            'ventilador_pos': (1150, 100),
            'rack_y_positions': [200, 320, 440],
            'offset_rack_y': 90,
            'posicion_luces_y': 130,
            'ancho_rack': 600,  # Ancho del sprite del rack
            'num_lechugas': 5,
            'separacion_lechugas': 120  # Espacio entre centros de lechugas
        }

        # Calcular posiciones centralizadas
        for y_lechugas in config['rack_y_positions']:
            # 1. Calcular posición inicial para centrar las lechugas
            centro_rack_x = 400 + (config['ancho_rack'] // 2)  # 400 + 300 = 700px
            ancho_total_lechugas = (config['num_lechugas'] - 1) * config['separacion_lechugas']
            inicio_x = centro_rack_x - (ancho_total_lechugas // 2)

            # 2. Dibujar lechugas centradas
            for i in range(config['num_lechugas']):
                x_planta = inicio_x + (i * config['separacion_lechugas'])
                screen.blit(self.planta_img, (x_planta - self.planta_img.get_width()//2, y_lechugas))  # Centrar sprite
                
                # 3. Dibujar luces centradas sobre lechugas
                luz_x = x_planta - self.luz_on.get_width()//2
                screen.blit(self.luz_on if self.ajuste_luz > 30 else self.luz_off, 
                        (luz_x, config['posicion_luces_y']))

            # 4. Dibujar rack centrado (ya está en posición X=400 que es el centro)
            screen.blit(self.rack_img, (400, y_lechugas + config['offset_rack_y']))

        # Ventilador (posición mantenida)
        ventilacion_img = self.ventilacion_on if self.ventilacion > 0 else self.ventilacion_off
        if self.ventilacion > 0:
            self.ventilacion_angle = (self.ventilacion_angle + self.ventilacion * 0.7) % 360
            ventilacion_img = pygame.transform.rotate(self.ventilacion_on, self.ventilacion_angle)
        
        screen.blit(ventilacion_img, ventilacion_img.get_rect(center=config['ventilador_pos']))

    def dibujar_panel_control(self):
        # Fondo del panel
        pygame.draw.rect(screen, (40, 40, 40), (0, 0, 350, ALTO))
        
        # Sliders
        for slider in self.sliders:
            slider.draw(screen)
        
        # Indicadores
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
            
            # Actualizar y dibujar
            self.actualizar_fuzzy()
            self.dibujar_pfab()
            self.dibujar_panel_control()
            
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    simulador = PFALSimulator()
    simulador.run()