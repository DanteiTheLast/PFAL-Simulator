import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def crear_sistema_lechuga():
    # ---------------------------
    # 1. Variables de Entrada 
    # ---------------------------
    temperatura = ctrl.Antecedent(np.arange(0, 41, 1), 'temperatura')
    temperatura['baja'] = fuzz.gaussmf(temperatura.universe, 10, 3)       # Centro en 10°C, ancho 3
    temperatura['optima'] = fuzz.gaussmf(temperatura.universe, 18, 2)     # Centro en 18°C
    temperatura['alta'] = fuzz.gaussmf(temperatura.universe, 28, 3)       # Centro en 28°C

    co2 = ctrl.Antecedent(np.arange(200, 2001, 10), 'co2')
    co2['bajo'] = fuzz.trapmf(co2.universe, [200, 200, 400, 600])   # <600 ppm
    co2['optimo'] = fuzz.trimf(co2.universe, [500, 1000, 1500])     # 500-1500 ppm
    co2['alto'] = fuzz.trapmf(co2.universe, [1400, 1600, 2000, 2000])

    humedad_sustrato = ctrl.Antecedent(np.arange(0, 101, 1), 'humedad_sustrato')
    humedad_sustrato['baja'] = fuzz.trapmf(humedad_sustrato.universe, [0, 0, 30, 50])
    humedad_sustrato['optima'] = fuzz.trimf(humedad_sustrato.universe, [40, 60, 80])
    humedad_sustrato['alta'] = fuzz.trapmf(humedad_sustrato.universe, [70, 90, 100, 100])

    luz_intensidad = ctrl.Antecedent(np.arange(0, 301, 1), 'luz_intensidad')
    luz_intensidad['baja'] = fuzz.trimf(luz_intensidad.universe, [0, 0, 150])
    luz_intensidad['media'] = fuzz.trimf(luz_intensidad.universe, [100, 200, 300])
    luz_intensidad['alta'] = fuzz.trimf(luz_intensidad.universe, [250, 300, 300])

    ajuste_luz = ctrl.Consequent(np.arange(0, 101, 1), 'ajuste_luz')
    ajuste_luz['reducir'] = fuzz.trimf(ajuste_luz.universe, [0, 0, 50])
    ajuste_luz['mantener'] = fuzz.trimf(ajuste_luz.universe, [40, 60, 80])
    ajuste_luz['aumentar'] = fuzz.trimf(ajuste_luz.universe, [70, 100, 100])


    # ---------------------------
    # 2. Variables de Salida 
    # ---------------------------
    calefaccion = ctrl.Consequent(np.arange(0, 101, 1), 'calefaccion')
    calefaccion['apagada'] = fuzz.trimf(calefaccion.universe, [0, 0, 20])
    calefaccion['baja'] = fuzz.trimf(calefaccion.universe, [15, 35, 55])
    calefaccion['media'] = fuzz.trimf(calefaccion.universe, [45, 65, 85])
    calefaccion['alta'] = fuzz.trimf(calefaccion.universe, [75, 100, 100])

    ventilacion = ctrl.Consequent(np.arange(0, 101, 1), 'ventilacion')
    ventilacion['apagada'] = fuzz.trimf(ventilacion.universe, [0, 0, 20])
    ventilacion['baja'] = fuzz.trimf(ventilacion.universe, [15, 30, 45])     
    ventilacion['media'] = fuzz.trimf(ventilacion.universe, [40, 60, 80]) 
    ventilacion['alta'] = fuzz.trimf(ventilacion.universe, [70, 85, 100])    

    inyector_co2 = ctrl.Consequent(np.arange(0, 101, 1), 'inyector_co2')
    inyector_co2['apagado'] = fuzz.trimf(inyector_co2.universe, [0, 0, 30])
    inyector_co2['bajo'] = fuzz.trimf(inyector_co2.universe, [20, 50, 80])
    inyector_co2['alto'] = fuzz.trimf(inyector_co2.universe, [70, 100, 100])

    riego = ctrl.Consequent(np.arange(0, 101, 1), 'riego')  # Nueva variable
    riego['apagado'] = fuzz.trimf(riego.universe, [0, 0, 30])
    riego['bajo'] = fuzz.trimf(riego.universe, [20, 50, 80])
    riego['alto'] = fuzz.trimf(riego.universe, [70, 100, 100])
    # --------------------------------------------
    # 3. Reglas Difusas 
    # --------------------------------------------
    rules = [
    # ==============================================
# ---- Prioridad 1: Temperatura ----
        ctrl.Rule(
        temperatura['optima'] & co2['bajo'] & humedad_sustrato['alta'], 
        ventilacion['apagada']
        ),
        # Temperatura baja
        ctrl.Rule(temperatura['baja'] & co2['optimo'], calefaccion['media']),
        ctrl.Rule(temperatura['baja'] & co2['bajo'], (calefaccion['media'], inyector_co2['alto'])),
        ctrl.Rule(temperatura['baja'] & co2['alto'], (calefaccion['alta'], ventilacion['media'])),
        ctrl.Rule(temperatura['baja'] & humedad_sustrato['optima'], calefaccion['media']),
        ctrl.Rule(temperatura['baja'] & humedad_sustrato['baja'], (calefaccion['baja'], riego['alto'])),
        ctrl.Rule(temperatura['baja'] & humedad_sustrato['alta'], calefaccion['alta']),
        ctrl.Rule(temperatura['baja'] & humedad_sustrato['baja'] & co2['alto'], 
                (calefaccion['baja'], ventilacion['baja'], riego['alto'])),
        ctrl.Rule(temperatura['baja'] & luz_intensidad['alta'], calefaccion['baja']),

        # Temperatura alta
        ctrl.Rule(temperatura['alta'] & co2['optimo'], ventilacion['media']),
        ctrl.Rule(temperatura['alta'] & co2['bajo'], (ventilacion['baja'], inyector_co2['alto'])),
        ctrl.Rule(temperatura['alta'] & co2['alto'], ventilacion['alta']),
        ctrl.Rule(temperatura['alta'] & luz_intensidad['baja'], ventilacion['media']),
        ctrl.Rule(temperatura['alta'] & luz_intensidad['alta'], ventilacion['alta']),

        # ---- Prioridad 2: Humedad ----
        ctrl.Rule(humedad_sustrato['baja'], riego['alto']),
        ctrl.Rule(humedad_sustrato['baja'] & luz_intensidad['alta'], (riego['alto'], ajuste_luz['mantener'])),
        ctrl.Rule(humedad_sustrato['baja'] & co2['bajo'], (riego['alto'], inyector_co2['alto'])),

        # ---- Prioridad 3: CO₂ ----
        ctrl.Rule(co2['bajo'], inyector_co2['alto']),
        ctrl.Rule(co2['alto'] & temperatura['optima'], ventilacion['media']),
        ctrl.Rule(co2['alto'] & humedad_sustrato['baja'], (ventilacion['baja'], riego['alto'])),
    ]

    sistema_ctrl = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(sistema_ctrl)

if __name__ == "__main__":
    sistema = crear_sistema_lechuga()
    sistema.input['temperatura'] = 12
    sistema.input['co2'] = 1300
    sistema.input['humedad'] = 60
    #sistema.input['ph'] = 6.8
    sistema.input['luz_intensidad'] = 270
    sistema.compute()
    print("Salidas:", sistema.output)