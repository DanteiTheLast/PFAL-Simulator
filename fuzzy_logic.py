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
    luz_intensidad['optima'] = fuzz.trimf(luz_intensidad.universe, [80, 150, 220])
    luz_intensidad['alta'] = fuzz.trapmf(luz_intensidad.universe, [200, 250, 300, 300])

    hum_sustrato = ctrl.Antecedent(np.arange(0, 101, 1), 'hum_sustrato')
    hum_sustrato['muy_baja'] = fuzz.trapmf(hum_sustrato.universe, [0, 0, 20, 40])
    hum_sustrato['baja'] = fuzz.trimf(hum_sustrato.universe, [30, 45, 60])
    hum_sustrato['optima'] = fuzz.trimf(hum_sustrato.universe, [50, 65, 80])
    hum_sustrato['alta'] = fuzz.trimf(hum_sustrato.universe, [70, 85, 100])
    hum_sustrato['saturada'] = fuzz.trapmf(hum_sustrato.universe, [90, 100, 100, 100])

    # --------------------------------------------
    # 2. Variables de Salida (Consecuentes)
    # --------------------------------------------
    calefaccion = ctrl.Consequent(np.arange(0, 101, 1), 'calefaccion')
    calefaccion['apagada'] = fuzz.trimf(calefaccion.universe, [0, 0, 20])
    calefaccion['baja'] = fuzz.trimf(calefaccion.universe, [10, 30, 50])
    calefaccion['media'] = fuzz.trimf(calefaccion.universe, [40, 60, 80])
    calefaccion['alta'] = fuzz.trimf(calefaccion.universe, [70, 90, 100])

    ventilacion = ctrl.Consequent(np.arange(0, 101, 1), 'ventilacion')
    ventilacion['apagada'] = fuzz.trimf(ventilacion.universe, [0, 0, 20])
    ventilacion['baja'] = fuzz.trimf(ventilacion.universe, [10, 30, 50])
    ventilacion['media'] = fuzz.trimf(ventilacion.universe, [40, 60, 80])
    ventilacion['alta'] = fuzz.trimf(ventilacion.universe, [70, 90, 100])

    inyector_co2 = ctrl.Consequent(np.arange(0, 101, 1), 'inyector_co2')
    inyector_co2['apagado'] = fuzz.trimf(inyector_co2.universe, [0, 0, 20])
    inyector_co2['bajo'] = fuzz.trimf(inyector_co2.universe, [10, 30, 50])
    inyector_co2['alto'] = fuzz.trimf(inyector_co2.universe, [40, 70, 100])

    riego = ctrl.Consequent(np.arange(0, 2, 1), 'riego')
    riego['off'] = fuzz.trimf(riego.universe, [0, 0, 0])
    riego['on'] = fuzz.trimf(riego.universe, [1, 1, 1])

    ajuste_luz = ctrl.Consequent(np.arange(0, 101, 1), 'ajuste_luz')
    ajuste_luz['reducir'] = fuzz.trimf(ajuste_luz.universe, [0, 0, 50])
    ajuste_luz['mantener'] = fuzz.trimf(ajuste_luz.universe, [40, 60, 80])
    ajuste_luz['aumentar'] = fuzz.trimf(ajuste_luz.universe, [70, 100, 100])

    # --------------------------------------------
    # 3. Reglas Difusas (Completo)
    # --------------------------------------------
    rules = []
    # Calefacción (H1-H9)
    rules.append(ctrl.Rule(temperatura['baja'] & co2['optimo'], calefaccion['media']))
    rules.append(ctrl.Rule(temperatura['baja'] & co2['bajo'], [calefaccion['media'], inyector_co2['alto']]))
    rules.append(ctrl.Rule(temperatura['baja'] & co2['alto'], [calefaccion['alta'], ventilacion['media']]))
    rules.append(ctrl.Rule(temperatura['baja'] & hum_sustrato['optima'], calefaccion['media']))
    rules.append(ctrl.Rule(temperatura['baja'] & hum_sustrato['baja'], [calefaccion['baja'], riego['on']]))
    rules.append(ctrl.Rule(temperatura['baja'] & hum_sustrato['alta'], calefaccion['alta']))
    rules.append(ctrl.Rule(temperatura['baja'] & hum_sustrato['baja'] & co2['alto'], [calefaccion['baja'], ventilacion['baja'], riego['on']]))
    rules.append(ctrl.Rule(temperatura['baja'] & luz_intensidad['alta'], calefaccion['baja']))
    rules.append(ctrl.Rule(temperatura['optima'] & co2['optimo'], calefaccion['apagada']))

    # Ventilación (V1-V7)
    rules.append(ctrl.Rule(temperatura['alta'] & co2['optimo'], ventilacion['media']))
    rules.append(ctrl.Rule(temperatura['alta'] & co2['bajo'], [ventilacion['baja'], inyector_co2['alto']]))
    rules.append(ctrl.Rule(temperatura['alta'] & co2['alto'], ventilacion['alta']))
    rules.append(ctrl.Rule(temperatura['alta'] & luz_intensidad['baja'], ventilacion['media']))
    rules.append(ctrl.Rule(temperatura['alta'] & luz_intensidad['alta'], ventilacion['alta']))
    rules.append(ctrl.Rule(co2['alto'] & temperatura['optima'], ventilacion['media']))
    rules.append(ctrl.Rule(co2['alto'] & hum_sustrato['baja'], [ventilacion['baja'], riego['on']]))

    # Inyector de CO2 (C1-C5)
    rules.append(ctrl.Rule(co2['bajo'], inyector_co2['alto']))
    rules.append(ctrl.Rule(co2['bajo'] & ph['acido'], inyector_co2['alto']))
    rules.append(ctrl.Rule(co2['optimo'], inyector_co2['bajo']))
    rules.append(ctrl.Rule(co2['alto'] | ph['alcalino'], inyector_co2['apagado']))
    rules.append(ctrl.Rule(temperatura['alta'] & co2['bajo'], [inyector_co2['bajo'], ventilacion['baja']]))

    # Riego (R1-R3)
    rules.append(ctrl.Rule(hum_sustrato['baja'], riego['on']))
    rules.append(ctrl.Rule(hum_sustrato['baja'] & luz_intensidad['alta'], [riego['on'], ajuste_luz['mantener']]))
    rules.append(ctrl.Rule(hum_sustrato['baja'] & co2['bajo'], [riego['on'], inyector_co2['alto']]))

    # Ajuste de Luz (L1-L8)
    rules.append(ctrl.Rule(luz_intensidad['baja'], ajuste_luz['aumentar']))
    rules.append(ctrl.Rule(luz_intensidad['optima'] & humedad['optima'], ajuste_luz['mantener']))
    rules.append(ctrl.Rule(luz_intensidad['alta'] & humedad['baja'], ajuste_luz['reducir']))
    rules.append(ctrl.Rule(luz_intensidad['alta'] & temperatura['muy_alta'], ajuste_luz['reducir']))
    rules.append(ctrl.Rule(luz_intensidad['baja'] & co2['optimo'], ajuste_luz['mantener']))
    rules.append(ctrl.Rule(luz_intensidad['baja'] & ph['acido'], ajuste_luz['aumentar']))
    rules.append(ctrl.Rule(luz_intensidad['alta'] | ph['alcalino'], ajuste_luz['reducir']))
    rules.append(ctrl.Rule(luz_intensidad['optima'] & co2['optimo'], ajuste_luz['mantener']))

    # Crear sistema de control
    sistema_ctrl = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(sistema_ctrl)

if __name__ == "__main__":
    sistema = crear_sistema_lechuga()
    # Ejemplo de uso
    sistema.input['temperatura'] = 10
    sistema.input['humedad'] = 50
    sistema.input['co2'] = 800
    sistema.input['ph'] = 6.8
    sistema.input['luz_intensidad'] = 150
    sistema.input['hum_sustrato'] = 40
    sistema.compute()
    print("Salidas:", sistema.output)
