# fuzzy.py
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def muy(mu):
    return mu ** 2

def mas_o_menos(mu):
    return np.sqrt(mu)

def build_fuzzy_system():
    # Universos
    retraso = ctrl.Antecedent(np.arange(0, 16, 1), 'retraso')         # días
    calidad = ctrl.Antecedent(np.arange(0, 11, 1), 'calidad')          # 0..10
    confiabilidad = ctrl.Consequent(np.arange(0, 11, 1), 'confiabilidad')
    # Defuzzificación explícita (requisito)
    confiabilidad.defuzzify_method = 'centroid'

    # Membresías
    confiabilidad['baja'] = fuzz.trimf(confiabilidad.universe, [0, 0, 4])
    confiabilidad['media'] = fuzz.trapmf(confiabilidad.universe, [2, 4, 6, 8])
    confiabilidad['alta'] = fuzz.gaussmf(confiabilidad.universe, 10, 1.5)
    confiabilidad['muy_alta'] = muy(fuzz.gaussmf(confiabilidad.universe, 10, 1.5))

    retraso['bajo'] = fuzz.trapmf(retraso.universe, [0, 0, 2, 4])
    retraso['medio'] = fuzz.trimf(retraso.universe, [2, 6, 10])
    retraso['alto'] = fuzz.trapmf(retraso.universe, [8, 12, 15, 15])
    retraso['mas_o_menos_alto'] = mas_o_menos(fuzz.trapmf(retraso.universe, [8, 12, 15, 15]))

    calidad['baja'] = fuzz.trapmf(calidad.universe, [0, 0, 2, 4])
    calidad['media'] = fuzz.trimf(calidad.universe, [2, 5, 8])
    calidad['alta'] = fuzz.gaussmf(calidad.universe, 10, 1.5)

    # Reglas (9)
    # 1. Si la calidad es alta Y el retraso es bajo, entonces la confiabilidad es alta
    regla1 = ctrl.Rule(calidad['alta'] & retraso['bajo'], confiabilidad['alta'])
    # 2. Si la calidad es baja O el retraso es alto, entonces la confiabilidad es baja
    regla2 = ctrl.Rule(calidad['baja'] | retraso['alto'], confiabilidad['baja'])
    # 3. Si la calidad es media Y el retraso es medio, entonces la confiabilidad es media
    regla3 = ctrl.Rule(calidad['media'] & retraso['medio'], confiabilidad['media'])
    # 4. Si la calidad es alta Y el retraso es medio, entonces la confiabilidad es media
    regla4 = ctrl.Rule(calidad['alta'] & retraso['medio'], confiabilidad['media'])
    # 5. Si la calidad es media Y el retraso es bajo, entonces la confiabilidad es media
    regla5 = ctrl.Rule(calidad['media'] & retraso['bajo'], confiabilidad['media'])
    # 6. Si la calidad es baja Y el retraso es bajo, entonces la confiabilidad es media
    regla6 = ctrl.Rule(calidad['baja'] & retraso['bajo'], confiabilidad['media'])
    # 7. Si la calidad es alta Y el retraso es alto, entonces la confiabilidad es media
    regla7 = ctrl.Rule(calidad['alta'] & retraso['alto'], confiabilidad['media'])
    # 8. Si la calidad es media O el retraso es alto, entonces la confiabilidad es baja
    regla8 = ctrl.Rule(calidad['media'] | retraso['alto'], confiabilidad['baja'])
    # 9. Si NO (retraso es alto) Y calidad es alta, entonces la confiabilidad es muy alta
    regla9 = ctrl.Rule(~retraso['alto'] & calidad['alta'], confiabilidad['muy_alta'])  # NOT

    control_system = ctrl.ControlSystem([regla1, regla2, regla3, regla4, regla5, regla6, regla7, regla8, regla9])
    simulador_confiabilidad = ctrl.ControlSystemSimulation(control_system)

    return (retraso, calidad, confiabilidad, simulador_confiabilidad)

def eval_confiabilidad(sim, retraso_dias:int, calidad_score:int) -> float:
    sim.input['retraso'] = retraso_dias
    sim.input['calidad'] = calidad_score
    sim.compute()
    return float(sim.output['confiabilidad'])
