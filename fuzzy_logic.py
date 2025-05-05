import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def crear_sistema_lechuga():
    # --------------------------------------------
    # 1. Variables de Entrada (Antecedentes)
    # --------------------------------------------
    temperatura = ctrl.Antecedent(np.arange(0, 41, 1), 'temperatura')
    temperatura['muy_baja'] = fuzz.trapmf(temperatura.universe, [0, 0, 5, 10])
    temperatura['baja'] = fuzz.trimf(temperatura.universe, [8, 13, 18])
    temperatura['optima'] = fuzz.trimf(temperatura.universe, [16, 17, 18])
    temperatura['alta'] = fuzz.trimf(temperatura.universe, [18, 22, 26])
    temperatura['muy_alta'] = fuzz.trapmf(temperatura.universe, [25, 27, 40, 40])

    humedad = ctrl.Antecedent(np.arange(0, 101, 1), 'humedad')
    humedad['baja'] = fuzz.trapmf(humedad.universe, [0, 0, 40, 50])
    humedad['optima'] = fuzz.trimf(humedad.universe, [45, 60, 75])
    humedad['alta'] = fuzz.trapmf(humedad.universe, [70, 80, 100, 100])

    co2 = ctrl.Antecedent(np.arange(200, 2001, 10), 'co2')
    co2['bajo'] = fuzz.trapmf(co2.universe, [200, 200, 1000, 1200])
    co2['optimo'] = fuzz.trimf(co2.universe, [1150, 1350, 1500])
    co2['alto'] = fuzz.trapmf(co2.universe, [1450, 1600, 2000, 2000])

    ph = ctrl.Antecedent(np.arange(5.0, 9.1, 0.1), 'ph')
    ph['acido'] = fuzz.trapmf(ph.universe, [5.0, 5.0, 6.3, 6.5])
    ph['optimo'] = fuzz.trimf(ph.universe, [6.4, 6.75, 7.0])
    ph['alcalino'] = fuzz.trapmf(ph.universe, [6.9, 7.1, 9.0, 9.0])

    luz_intensidad = ctrl.Antecedent(np.arange(0, 301, 10), 'luz_intensidad')
    luz_intensidad['baja'] = fuzz.trimf(luz_intensidad.universe, [0, 50, 100])
    luz_intensidad['media'] = fuzz.trimf(luz_intensidad.universe, [80, 150, 220])
    luz_intensidad['alta'] = fuzz.trapmf(luz_intensidad.universe, [200, 250, 300, 300])

    # --------------------------------------------
    # 2. Variables de Salida (Consecuentes)
    # --------------------------------------------
    inyector_co2 = ctrl.Consequent(np.arange(0, 101, 1), 'inyector_co2')
    inyector_co2['apagado'] = fuzz.trimf(inyector_co2.universe, [0, 0, 30])
    inyector_co2['bajo'] = fuzz.trimf(inyector_co2.universe, [20, 50, 80])
    inyector_co2['alto'] = fuzz.trimf(inyector_co2.universe, [70, 100, 100])

    ventilacion = ctrl.Consequent(np.arange(0, 101, 1), 'ventilacion')
    ventilacion['apagada'] = fuzz.trimf(ventilacion.universe, [0, 0, 30])
    ventilacion['moderada'] = fuzz.trimf(ventilacion.universe, [20, 50, 80])
    ventilacion['maxima'] = fuzz.trimf(ventilacion.universe, [70, 100, 100])

    ajuste_luz = ctrl.Consequent(np.arange(0, 101, 1), 'ajuste_luz')
    ajuste_luz['reducir'] = fuzz.trimf(ajuste_luz.universe, [0, 0, 50])
    ajuste_luz['mantener'] = fuzz.trimf(ajuste_luz.universe, [40, 60, 80])
    ajuste_luz['aumentar'] = fuzz.trimf(ajuste_luz.universe, [70, 100, 100])

    # --------------------------------------------
    # 3. Reglas Difusas (Simplificadas y Funcionales)
    # --------------------------------------------
    rules = [
        ctrl.Rule(temperatura['muy_alta'], ventilacion['maxima']),
        ctrl.Rule(temperatura['optima'], ventilacion['moderada']),
        ctrl.Rule(co2['bajo'], inyector_co2['alto']),
        ctrl.Rule(ph['alcalino'], ventilacion['maxima']),
        ctrl.Rule(luz_intensidad['alta'] & humedad['baja'], ajuste_luz['reducir']),
    ]

    sistema_ctrl = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(sistema_ctrl)

if __name__ == "__main__":
    sistema = crear_sistema_lechuga()
    sistema.input['temperatura'] = 28
    sistema.input['co2'] = 800
    sistema.input['humedad'] = 40
    sistema.input['ph'] = 6.8
    sistema.input['luz_intensidad'] = 270
    sistema.compute()
    print("Salidas:", sistema.output)