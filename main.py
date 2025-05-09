import pygame
from pygame.locals import *
import numpy as np
from fuzzy_logic import crear_sistema_lechuga
from pfal_config import CULTIVOS

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
COLOR_BOTON = (80, 140, 200)
COLOR_BOTON_SEL = (110, 170, 230)

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

class BotonVelocidad:
    def __init__(self, x, y, w, h, texto, factor):
        self.rect = pygame.Rect(x, y, w, h)
        self.texto = texto
        self.factor = factor
        self.seleccionado = False

    def dibujar(self, superficie):
        color = COLOR_BOTON_SEL if self.seleccionado else COLOR_BOTON
        pygame.draw.rect(superficie, color, self.rect)
        texto = font.render(self.texto, True, COLOR_TEXTO)
        texto_rect = texto.get_rect(center=self.rect.center)
        superficie.blit(texto, texto_rect)

class PFALSimulator:
    def __init__(self):
        self.fuzzy_system = crear_sistema_lechuga()
        self.time_factor = 288  # Valor inicial 1x (5 minutos)
        self.tiempo_transcurrido = 0  # Segundos simulados
        self.dias_transcurridos = 1
        self.luz_encendida = True

        # Sliders
        self.sliders = [
            Slider(50, 50, 200, 20, 0, 40, 18, "Temperatura (°C)"),
            Slider(50, 100, 200, 20, 0, 100, 60, "Humedad (%)"),
            Slider(50, 150, 200, 20, 200, 2000, 1200, "CO₂ (ppm)"),
            Slider(50, 200, 200, 20, 5.0, 9.0, 6.8, "pH"),
            Slider(50, 250, 200, 20, 0, 300, 270, "Luz (µmol)")
        ]

        # Botones de velocidad
        self.botones_velocidad = [
            BotonVelocidad(50, 640, 80, 30, "1x (5m)", 288),     # 24h en 5 min
            BotonVelocidad(140, 640, 80, 30, "2x (1m)", 1440),   # 24h en 1 min
            BotonVelocidad(230, 640, 100, 30, "3x (30s)", 2880) # 24h en 30 seg
        ]
        self.botones_velocidad[0].seleccionado = True

        # Cargar gráficos
        try:
            self.rack_img = pygame.image.load("PFAL_Simulator/PFAL-Simulator/assets/rack.png").convert_alpha()
            self.planta_img = pygame.image.load("PFAL_Simulator/PFAL-Simulator/assets/lettuce.png").convert_alpha()
            self.luz_on = pygame.image.load("PFAL_Simulator/PFAL-Simulator/assets/luz_on.png").convert_alpha()
            self.luz_off = pygame.image.load("PFAL_Simulator/PFAL-Simulator/assets/luz_off.png").convert_alpha()
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
            'luz_intensidad': self.sliders[4].val if self.luz_encendida else 0
        }
        
        for key, val in inputs.items():
            self.fuzzy_system.input[key] = val
        
        try:
            self.fuzzy_system.compute()
            self.ventilacion = float(self.fuzzy_system.output.get('ventilacion', 0.0))
            self.inyector_co2 = float(self.fuzzy_system.output.get('inyector_co2', 0.0))
            self.ajuste_luz = float(self.fuzzy_system.output.get('ajuste_luz', 100.0))
        except Exception as e:
            print(f"Error en lógica difusa: {e}")
            self.ventilacion, self.inyector_co2, self.ajuste_luz = 0.0, 0.0, 100.0

    def actualizar_ciclo_luz(self):
        horas_actuales = (self.tiempo_transcurrido // 3600) % 24
        inicio_luz, fin_luz = CULTIVOS["lechuga"]["fotoperiodo"]
        
        if inicio_luz < fin_luz:
            self.luz_encendida = inicio_luz <= horas_actuales < fin_luz
        else:
            self.luz_encendida = horas_actuales >= inicio_luz or horas_actuales < fin_luz

    def obtener_hora_actual(self):
        horas = int(self.tiempo_transcurrido // 3600) % 24
        minutos = int((self.tiempo_transcurrido % 3600) // 60)
        am_pm = "AM" if horas < 12 else "PM"
        horas_12 = horas % 12 or 12
        return f"{horas_12:02d}:{minutos:02d} {am_pm}"

    def dibujar_pfab(self):
        config = {
            'ventilador_pos': (1150, 100),
            'rack_y_positions': [200, 320, 440],
            'offset_rack_y': 90,
            'posicion_luces_y': 130,
            'ancho_rack': 600,
            'num_lechugas': 5,
            'separacion_lechugas': 120
        }

        # Dibujar plantas y luces
        for y_lechugas in config['rack_y_positions']:
            centro_rack_x = 400 + (config['ancho_rack'] // 2)
            inicio_x = centro_rack_x - ((config['num_lechugas'] - 1) * config['separacion_lechugas'] // 2)

            for i in range(config['num_lechugas']):
                x_planta = inicio_x + (i * config['separacion_lechugas'])
                screen.blit(self.planta_img, (x_planta - self.planta_img.get_width()//2, y_lechugas))
                
                luz_img = self.luz_on if self.luz_encendida else self.luz_off
                screen.blit(luz_img, (x_planta - luz_img.get_width()//2, config['posicion_luces_y']))

            screen.blit(self.rack_img, (400, y_lechugas + config['offset_rack_y']))

        # Ventilador
        if self.ventilacion > 0:
            self.ventilacion_angle = (self.ventilacion_angle + self.ventilacion * 0.7) % 360
            ventilacion_img = pygame.transform.rotate(self.ventilacion_on, self.ventilacion_angle)
        else:
            ventilacion_img = self.ventilacion_off
        screen.blit(ventilacion_img, ventilacion_img.get_rect(center=config['ventilador_pos']))

    def dibujar_panel_control(self):
        pygame.draw.rect(screen, (40, 40, 40), (0, 0, 350, ALTO))
        
        # Sliders
        for slider in self.sliders:
            slider.draw(screen)
        
        # Indicadores
        y = 300
        indicadores = [
            ("Ventilación", self.ventilacion),
            ("Inyector CO₂", self.inyector_co2),
            ("Ajuste Luz", self.ajuste_luz),
        ]
        
        for label, value in indicadores:
            texto = f"{label}: {value:.1f}%" if isinstance(value, float) else f"{label}: {value}"
            text = font.render(texto, True, COLOR_TEXTO)
            screen.blit(text, (50, y))
            y += 30

        # Tiempo
        texto_tiempo = font.render(f"Día {self.dias_transcurridos} - {self.obtener_hora_actual()}", 
                                True, COLOR_TEXTO)
        screen.blit(texto_tiempo, (50, 500))
        
        # Botones velocidad
        leyenda = font.render("Velocidad:", True, COLOR_TEXTO)
        screen.blit(leyenda, (50, 600))
        
        for boton in self.botones_velocidad:
            boton.dibujar(screen)

    def run(self):
        running = True
        while running:
            dt_real = clock.tick(60) / 1000.0  # Tiempo real en segundos
            
            # Actualizar tiempo
            tiempo_anterior = self.tiempo_transcurrido
            self.tiempo_transcurrido += dt_real * self.time_factor
            self.dias_transcurridos += int(self.tiempo_transcurrido // 86400)
            self.tiempo_transcurrido %= 86400
            
            # Manejar eventos
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                
                # Sliders primero
                for slider in self.sliders:
                    slider.update(event)
                
                # Botones después
                if event.type == MOUSEBUTTONDOWN:
                    for boton in self.botones_velocidad:
                        if boton.rect.collidepoint(event.pos):
                            self.time_factor = boton.factor
                            for b in self.botones_velocidad:
                                b.seleccionado = False
                            boton.seleccionado = True
            
            # Actualizar lógica
            self.actualizar_ciclo_luz()
            self.actualizar_fuzzy()
            
            # Dibujar
            screen.fill(COLOR_FONDO)
            self.dibujar_pfab()
            self.dibujar_panel_control()
            
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    simulador = PFALSimulator()
    simulador.run()