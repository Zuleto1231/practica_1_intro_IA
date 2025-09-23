# main.py 
from ontologia import build_ontology, reason_and_compare, serialize_turtle
from prueba.sistemaDifuso import build_fuzzy_system, eval_confiabilidad
from prueba.sistemaInventario import InventarioExpertSystem
from translator import graph_to_facts
from rdflib.namespace import FOAF
from ontologia import BASE

# 1) Ontología + razonamiento
g = build_ontology()
g_before, g_after, inferred = reason_and_compare(g)
print(f"Triples antes: {len(g_before)} | después: {len(g_after)} | inferidos: {len(inferred)}")
# (Para el PDF, imprime 4+ ejemplos)
ejemplos = list(inferred)[:6]
for t in ejemplos:
    print("INF:", t)
serialize_turtle(g_after, "ontologia_final.ttl")

# 2) Lógica Difusa → calcular confiabilidad por proveedor (desde ontología)
retraso, calidad, confiabilidad, sim = build_fuzzy_system()
confi_map = {}
for prov in g_after.subjects(None, None):
    # detecta proveedores por tipo
    if (prov, None, None) in g_after and ((prov, None, BASE.Proveedor) in g_after or (prov, None, BASE.ProveedorPreferido) in g_after):
        nombre = g_after.value(prov, FOAF.name)
        lead = g_after.value(prov, BASE.leadTimeDias)
        cal = g_after.value(prov, BASE.calidad)
        if nombre and lead and cal:
            conf = eval_confiabilidad(sim, int(lead.toPython()), int(cal.toPython()))
            confi_map[str(nombre)] = conf
print("Confiabilidades difusas:", confi_map)

# 3) Traducir todo el grafo razonado → hechos Experta + inyectar confiabilidad
engine = InventarioExpertSystem()
engine.reset()
graph_to_facts(g_after, engine, confi_map=confi_map)

# 4) Ejecutar motor
engine.run()

