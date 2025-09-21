# ontologia.py
from rdflib import Graph, Namespace, Literal, RDF, RDFS, XSD, URIRef
from rdflib.namespace import FOAF, DCTERMS
from owlrl import DeductiveClosure, RDFS_Semantics

# Namespaces propios
BASE = Namespace("http://ejemplo.org/inventario#")
SCHEMA = Namespace("http://schema.org/")

def build_ontology():
    g = Graph()
    g.bind("base", BASE)
    g.bind("foaf", FOAF)
    g.bind("dcterms", DCTERMS)
    g.bind("schema", SCHEMA)

    # --- Clases (>=10) ---
    clases = [
        "Producto", "Categoria", "Perecedero", "NoPerecedero", "Critico",
        "Proveedor", "ProveedorPreferido", "Pedido", "Demanda", "StockSnapshot",
        "Promocion"
    ]
    for c in clases:
        g.add((BASE[c], RDF.type, RDFS.Class))

    # Jerarquías (>=5)
    g.add((BASE.Perecedero, RDFS.subClassOf, BASE.Categoria))
    g.add((BASE.NoPerecedero, RDFS.subClassOf, BASE.Categoria))
    g.add((BASE.Critico, RDFS.subClassOf, BASE.Categoria))
    g.add((BASE.ProveedorPreferido, RDFS.subClassOf, BASE.Proveedor))
    g.add((BASE.PedidoUrgente, RDF.type, RDFS.Class))
    g.add((BASE.PedidoUrgente, RDFS.subClassOf, BASE.Pedido))

    # --- Propiedades (>=10) con domain/range, y una subProperty ---
    props = {
        "tieneProveedor": (BASE.Producto, BASE.Proveedor),
        "perteneceACategoria": (BASE.Producto, BASE.Categoria),
        "tieneStock": (BASE.Producto, XSD.integer),
        "tieneDemanda": (BASE.Producto, BASE.Demanda),
        "cantidadPedida": (BASE.Pedido, XSD.integer),
        "leadTimeDias": (BASE.Proveedor, XSD.integer),
        "calidad": (BASE.Proveedor, XSD.integer),
        "nombre": (BASE.Producto, XSD.string),           # usaremos FOAF.name también
        "nivelDemanda": (BASE.Demanda, XSD.string),
        "confiabilidadFinal": (BASE.Proveedor, XSD.float),
    }
    for p, (dom, ran) in props.items():
        g.add((BASE[p], RDF.type, RDF.Property))
        g.add((BASE[p], RDFS.domain, dom))
        if isinstance(ran, URIRef):
            g.add((BASE[p], RDFS.range, ran))
        else:
            g.add((BASE[p], RDFS.range, ran))

    # subPropertyOf: proveedorPrincipal ⊑ tieneProveedor
    g.add((BASE.proveedorPrincipal, RDF.type, RDF.Property))
    g.add((BASE.proveedorPrincipal, RDFS.domain, BASE.Producto))
    g.add((BASE.proveedorPrincipal, RDFS.range, BASE.ProveedorPreferido))
    g.add((BASE.proveedorPrincipal, RDFS.subPropertyOf, BASE.tieneProveedor))

    # --- Individuos (≥4 por clase principal) ---
    productos = ["Leche", "Arroz", "Pan", "Aceite", "Huevos", "Medicamentos", "Azucar", "Sal"]
    categorias = {
        "Leche": "Perecedero", "Arroz": "NoPerecedero", "Pan": "Perecedero",
        "Aceite": "NoPerecedero", "Huevos": "Perecedero", "Medicamentos": "Critico",
        "Azucar": "NoPerecedero", "Sal": "NoPerecedero"
    }
    demandas = {
        "Leche": "Alta", "Arroz": "Baja", "Pan": "Alta", "Aceite": "Media",
        "Huevos": "Alta", "Medicamentos": "Alta", "Azucar": "Media", "Sal": "Baja"
    }
    proveedores = {
        "ProveedorX": {"lead": 7, "calidad": 6},
        "ProveedorY": {"lead": 5, "calidad": 7},
        "ProveedorZ": {"lead": 10, "calidad": 8},
        "ProveedorPrincipal": {"lead": 3, "calidad": 9}
    }

    # crear individuos de proveedor
    for prov, attrs in proveedores.items():
        pv = BASE[prov]
        g.add((pv, RDF.type, BASE.ProveedorPreferido if prov=="ProveedorPrincipal" else BASE.Proveedor))
        g.add((pv, FOAF.name, Literal(prov)))
        g.add((pv, BASE.leadTimeDias, Literal(attrs["lead"], datatype=XSD.integer)))
        g.add((pv, BASE.calidad, Literal(attrs["calidad"], datatype=XSD.integer)))

    # crear individuos de demanda (una por producto)
    for p, nivel in demandas.items():
        d = BASE[f"Demanda_{p}"]
        g.add((d, RDF.type, BASE.Demanda))
        g.add((d, BASE.nivelDemanda, Literal(nivel)))

    # crear productos + propiedades
    stocks = {
        "Leche": 4, "Arroz": 60, "Pan": 0, "Aceite": 12,
        "Huevos": 8, "Medicamentos": 5, "Azucar": 3, "Sal": 55
    }
    asignacion_prov = {
        "Leche": "ProveedorX", "Arroz": "ProveedorY", "Pan": "ProveedorX",
        "Aceite": "ProveedorZ", "Huevos": "ProveedorX", "Medicamentos": "ProveedorPrincipal",
        "Azucar": "ProveedorSecundario",  # lo modelaremos como Proveedor genérico creado abajo
        "Sal": "ProveedorY"
    }
    # Si no existe ProveedorSecundario, créalo:
    sec = BASE["ProveedorSecundario"]
    g.add((sec, RDF.type, BASE.Proveedor))
    g.add((sec, FOAF.name, Literal("ProveedorSecundario")))
    g.add((sec, BASE.leadTimeDias, Literal(9, datatype=XSD.integer)))
    g.add((sec, BASE.calidad, Literal(7, datatype=XSD.integer)))

    for p in productos:
        pr = BASE[p]
        g.add((pr, RDF.type, BASE.Producto))
        g.add((pr, FOAF.name, Literal(p)))
        g.add((pr, BASE.nombre, Literal(p)))
        # categoría
        cat = BASE[categorias[p]]
        g.add((pr, BASE.perteneceACategoria, cat))
        # stock
        g.add((pr, BASE.tieneStock, Literal(stocks[p], datatype=XSD.integer)))
        # demanda
        d = BASE[f"Demanda_{p}"]
        g.add((pr, BASE.tieneDemanda, d))
        # proveedor (usa subProperty si es principal)
        prov_uri = BASE[asignacion_prov[p]]
        if asignacion_prov[p] == "ProveedorPrincipal":
            g.add((pr, BASE.proveedorPrincipal, prov_uri))
        else:
            g.add((pr, BASE.tieneProveedor, prov_uri))

    # crear pedidos (≥4)
    pedidos = [("Leche",10), ("Arroz",5), ("Pan",8), ("Medicamentos",12), ("Huevos",20)]
    for i,(prod,cant) in enumerate(pedidos, start=1):
        pe = BASE[f"Pedido_{i}"]
        g.add((pe, RDF.type, BASE.Pedido))
        g.add((pe, BASE.cantidadPedida, Literal(cant, datatype=XSD.integer)))
        # Enlazar pedido con producto (usaremos schema:itemOffered para ejemplificar externo)
        g.add((pe, SCHEMA.itemOffered, BASE[prod]))

    return g

def reason_and_compare(g: Graph):
    g_before = Graph()
    g_before += g  # copia
    DeductiveClosure(RDFS_Semantics).expand(g)  # RDFS closure
    # Devuelve conjuntos para comparar
    triples_before = set(g_before)
    triples_after = set(g)
    inferred = triples_after - triples_before
    return g_before, g, inferred

def serialize_turtle(g: Graph, path="ontologia.ttl"):
    g.serialize(destination=path, format="turtle")
    return path
