# translator.py
from rdflib import RDF, RDFS, Literal, XSD
from rdflib.namespace import FOAF
from ontologia import BASE
from ontologia import SCHEMA

from prueba.sistemaInventario import (Producto, Stock, Demanda, Proveedor, Pedido, Categoria, ConfiabilidadProveedor)

def graph_to_facts(g, engine, confi_map=None):
    """
    Traduce TODO el grafo razonado a hechos del motor Experta.
    - confi_map: dict opcional { proveedor_name: confiabilidad_float }
    """
    # Productos: nombre, categoria, stock, demanda, proveedor
    # 1) Productos
    for pr in g.subjects(RDF.type, BASE.Producto):
        nombre = str(g.value(pr, FOAF.name) or g.value(pr, BASE.nombre))
        engine.declare(Producto(nombre=nombre))

        # Categoria(s) por perteneceACategoria
        for cat in g.objects(pr, BASE.perteneceACategoria):
            # Obtener nombre de clase concreta
            if (cat, RDF.type, RDFS.Class) in g or True:
                cat_name = cat.split("#")[-1]
                engine.declare(Categoria(producto=nombre, nombre=cat_name))

        # Stock (literal)
        stock_val = g.value(pr, BASE.tieneStock)
        if isinstance(stock_val, Literal) and stock_val.datatype in (XSD.integer, XSD.int, None):
            engine.declare(Stock(producto=nombre, cantidad=int(stock_val)))

        # Demanda
        d = g.value(pr, BASE.tieneDemanda)
        if d:
            nivel = g.value(d, BASE.nivelDemanda)
            if isinstance(nivel, Literal):
                engine.declare(Demanda(producto=nombre, nivel=str(nivel)))

        # Proveedor (normal y principal por subPropertyOf)
        for prov in g.objects(pr, BASE.tieneProveedor):
            pname = str(g.value(prov, FOAF.name))
            engine.declare(Proveedor(producto=nombre, nombre=pname))
        for prov in g.objects(pr, BASE.proveedorPrincipal):
            pname = str(g.value(prov, FOAF.name))
            engine.declare(Proveedor(producto=nombre, nombre=pname))

    # Pedidos (usar schema:itemOffered para enlazar producto)
    for pe in g.subjects(RDF.type, BASE.Pedido):
        prod = g.value(pe, SCHEMA.itemOffered)
        cant = g.value(pe, BASE.cantidadPedida)
        if prod and isinstance(cant, Literal):
            pname = str(prod.split("#")[-1])
            engine.declare(Pedido(producto=pname, cantidad=int(cant)))

    # Confiabilidad difusa (si viene)
    if confi_map:
        for n, val in confi_map.items():
            engine.declare(ConfiabilidadProveedor(nombre=n, valor=float(val)))
