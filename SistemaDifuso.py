import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np

#Definimos tres variables difusas para el sistema que buscará el nivel de confiabilidad de un proveedor y su universo del discurso
confiabilidad = ctrl.Consequent(np.arange(0, 11, 1), 'confiabilidad')
retraso = ctrl.Antecedent(np.arange(0, 16, 1), 'retraso')
calidad = ctrl.Antecedent(np.arange(0, 11, 1), 'calidad')

#Definimos los modiificadores muy y mas o menos para las variables difusas
def muy(conjunto):
    return conjunto ** 2

def mas_o_menos(conjunto):
    return np.sqrt(conjunto)


#Definimos los valores difusos para cada variable y sus funciones de pertenencia

confiabilidad['baja'] = fuzz.trimf(confiabilidad.universe, [0, 0, 4])           
confiabilidad['media'] = fuzz.trapmf(confiabilidad.universe, [2, 4, 6, 8])      
confiabilidad['alta'] = fuzz.gaussmf(confiabilidad.universe, 10, 1.5)  
confiabilidad['muy alta'] = muy(fuzz.gaussmf(confiabilidad.universe, 10, 1.5))      

retraso['bajo'] = fuzz.trapmf(retraso.universe, [0, 0, 2, 4])
retraso['medio'] = fuzz.trimf(retraso.universe, [2, 6, 10])
retraso['mas o menos alto'] = mas_o_menos(fuzz.trapmf(retraso.universe, [8, 12, 15, 15]))
retraso['alto'] = fuzz.trapmf(retraso.universe, [8, 12, 15, 15])

calidad['baja'] = fuzz.trapmf(calidad.universe, [0, 0, 2, 4])
calidad['media'] = fuzz.trimf(calidad.universe, [2, 5, 8])
calidad['alta'] = fuzz.gaussmf(calidad.universe, 10, 1.5)



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
regla9 = ctrl.Rule(~retraso['alto'] & calidad['alta'], confiabilidad['muy alta'])

# Construir el sistema de control y crear una simulación
control_system = ctrl.ControlSystem([regla1, regla2, regla3, regla4, regla5, regla6, regla7, regla8, regla9])
simulador_confiabilidad = ctrl.ControlSystemSimulation(control_system)

# Ejemplo de uso:
# Supongamos que un proveedor tiene: retraso = 3 días, calidad = 8, confiabilidad previa = 6
simulador_confiabilidad.input['retraso'] = 3
simulador_confiabilidad.input['calidad'] = 8

simulador_confiabilidad.compute()

print(f"Confiabilidad final del proveedor: {simulador_confiabilidad.output['confiabilidad']:.2f}")
