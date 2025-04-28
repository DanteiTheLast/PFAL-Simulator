import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def crear_sistema_lechuga():
    # Antecedentes (Inputs)
    temperatura = ctrl.Antecedent(np.arange(0, 40, 1), 'temperatura')
    humedad = ctrl.Antecedent(np.arange(0, 100, 1), 'humedad')
    co2 = ctrl.Antecedent(np.arange(200, 2000, 10), 'co2')
    ph = ctrl.Antecedent(np.arange(5.0, 9.0, 0.1), 'ph')
    luz_intensidad = ctrl.Antecedent(np.arange(0, 300, 10), 'luz_intensidad')

    # Consecuentes (Outputs)
    inyector_co2 = ctrl.Consequent(np.arange(0, 100, 1), 'inyector_co2')
    ventilacion = ctrl.Consequent(np.arange(0, 100, 1), 'ventilacion')
    ajuste_luz = ctrl.Consequent(np.arange(0, 100, 1), 'ajuste_luz')

    # Funciones de membresía (ejemplo para temperatura)
    temperatura.automf(5, names=['muy_baja', 'baja', 'optima', 'alta', 'muy_alta'])
    co2['bajo'] = fuzz.trimf(co2.universe, [200, 200, 1200])
    co2['optimo'] = fuzz.trimf(co2.universe, [1200, 1350, 1500])
    co2['alto'] = fuzz.trimf(co2.universe, [1500, 2000, 2000])

    # Reglas difusas para lechuga
    regla1 = ctrl.Rule(
        temperatura['optima'] & co2['bajo'],
        inyector_co2['max']
    )
    regla2 = ctrl.Rule(
        temperatura['muy_alta'],
        ventilacion['max']
    )

    # Sistema de control
    sistema_ctrl = ctrl.ControlSystem([regla1, regla2])
    return ctrl.ControlSystemSimulation(sistema_ctrl)