# Para compatibilidad con versiones anteriores, siempre utilizarlo.
import collections.abc
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping

from experta import *

# ------------------------------
# Definición de Clases de Hechos
# ------------------------------
class Producto(Fact):
    """Hecho sobre un producto"""
    pass

class Stock(Fact):
    """Hecho sobre el nivel de existencias"""
    pass

class Demanda(Fact):
    """Hecho sobre el nivel de demanda (Alta, Media, Baja)"""
    pass

class Proveedor(Fact):
    """Hecho sobre el proveedor de un producto"""
    pass

class Pedido(Fact):
    """Hecho sobre pedidos pendientes"""
    pass

class Categoria(Fact):
    """Hecho sobre la categoría del producto"""
    pass


# ------------------------------
# Motor del Sistema Experto
# ------------------------------
class InventarioExpertSystem(KnowledgeEngine):

    # 📌 1. Reposición urgente
    @Rule(Stock(producto=MATCH.p, cantidad=MATCH.c), salience=40)
    def reponer_urgente(self, p, c):
        if c < 5:
            print(f"⚠️ Reposición urgente para {p}, stock muy bajo (cantidad={c})")

    # 📌 2. Reposición programada
    @Rule(Stock(producto=MATCH.p, cantidad=MATCH.c), salience=30)
    def reponer_pronto(self, p, c):
        if 5 <= c < 10:
            print(f"🔄 Programar reposición para {p}, stock bajo (cantidad={c})")

    # 📌 3. Sobrestock
    @Rule(Stock(producto=MATCH.p, cantidad=MATCH.c), salience=20)
    def sobrestock(self, p, c):
        if c >= 50:
            print(f"📦 {p} está en sobrestock, considerar promoción (cantidad={c})")

    # 📌 4. Stock agotado
    @Rule(AS.s << Stock(producto=MATCH.p, cantidad=MATCH.c), salience=50)
    def stock_agotado(self, s, p, c):
        if c == 0:
            print(f"❌ {p} agotado. Bloqueando ventas.")
            self.retract(s)

    # 📌 5. Alta demanda + bajo stock
    @Rule(Demanda(producto=MATCH.p, nivel="Alta"),
        Stock(producto=MATCH.p, cantidad=MATCH.c),
        salience=35)
    def alta_demanda_bajo_stock(self, p, c):
        if c < 20:
            print(f"🔥 Alta demanda y poco stock en {p}, aumentar pedido (cantidad={c})")

    # 📌 6. Baja demanda + alto stock
    @Rule(Demanda(producto=MATCH.p, nivel="Baja"),
        Stock(producto=MATCH.p, cantidad=MATCH.c),
        salience=25)
    def baja_demanda_alto_stock(self, p, c):
        if c > 30:
            print(f"🛑 {p} tiene baja demanda y sobrestock, reducir compras (cantidad={c})")

    # 📌 7. Demanda media
    @Rule(Demanda(producto=MATCH.p, nivel="Media"),
        Stock(producto=MATCH.p, cantidad=MATCH.c),
        salience=25)
    def demanda_media(self, p, c):
        if c < 10:
            print(f"➖ {p} con demanda media y poco stock, reponer moderadamente (cantidad={c})")

    # 📌 8. Proveedor poco confiable
    @Rule(Proveedor(producto=MATCH.p, nombre="ProveedorX"),
        Stock(producto=MATCH.p, cantidad=MATCH.c),
        salience=30)
    def cambiar_proveedor(self, p, c):
        if c < 10:
            print(f"🔄 {p} con ProveedorX y stock crítico. Considerar otro proveedor (cantidad={c})")

    # 📌 9. Proveedor alternativo
    @Rule(Proveedor(producto=MATCH.p, nombre=MATCH.n),
        Stock(producto=MATCH.p, cantidad=MATCH.c),
        salience=20)
    def proveedor_alternativo(self, p, n, c):
        if c < 5 and n != "ProveedorPrincipal":
            print(f"📌 {p} tiene proveedor {n} pero stock crítico. Consultar ProveedorPrincipal (cantidad={c})")

    # 📌 10. Pedido supera stock
    @Rule(Pedido(producto=MATCH.p, cantidad=MATCH.q),
        Stock(producto=MATCH.p, cantidad=MATCH.s),
        salience=35)
    def verificar_pedido(self, p, q, s):
        if q > s:
            print(f"🚚 Pedido de {q} {p} supera stock ({s}), generar reposición")
        else:
            print(f"✅ Pedido de {q} {p} puede cubrirse con stock disponible")

    # 📌 11. Pedido cubierto
    @Rule(Pedido(producto=MATCH.p, cantidad=MATCH.q),
        Stock(producto=MATCH.p, cantidad=MATCH.s),
        salience=15)
    def pedido_cubierto(self, p, q, s):
        if q <= s:
            print(f"📦 Pedido de {q} {p} se cubre sin problema (stock={s})")

    # 📌 12. Perecederos en sobrestock
    @Rule(Categoria(producto=MATCH.p, nombre="Perecedero"),
        Stock(producto=MATCH.p, cantidad=MATCH.c),
        salience=20)
    def sobrestock_perecedero(self, p, c):
        if c > 30:
            print(f"⚠️ {p} es perecedero y tiene sobrestock, aplicar promoción (cantidad={c})")

    # 📌 13. No perecederos críticos
    @Rule(Categoria(producto=MATCH.p, nombre="NoPerecedero"),
        Stock(producto=MATCH.p, cantidad=MATCH.c),
        salience=15)
    def no_perecedero_critico(self, p, c):
        if c < 5:
            print(f"📦 {p} no perecedero con stock crítico, reponer sin urgencia (cantidad={c})")

    # 📌 14. Producto crítico
    @Rule(Categoria(producto=MATCH.p, nombre="Crítico"),
        Stock(producto=MATCH.p, cantidad=MATCH.c),
        salience=35)
    def producto_critico(self, p, c):
        if c < 10:
            print(f"🚨 {p} es CRÍTICO y su stock es muy bajo. Reposición inmediata (cantidad={c})")

    # 📌 15. Evitar duplicados / datos inválidos
    @Rule(AS.s << Stock(producto=MATCH.p, cantidad=MATCH.c),
        salience=100)
    def evitar_duplicados(self, s, p, c):
        if c < 0:
            print(f"⚠️ {p} tiene stock inválido ({c}), corrigiendo.")
            self.retract(s)



# ------------------------------
# Base de Hechos Inicial
# ------------------------------
engine = InventarioExpertSystem()
engine.reset()

productos = [
    ("Leche", 4, "Alta", "ProveedorX", "Perecedero"),
    ("Arroz", 60, "Baja", "ProveedorY", "NoPerecedero"),
    ("Pan", 0, "Alta", "ProveedorX", "Perecedero"),
    ("Aceite", 12, "Media", "ProveedorZ", "NoPerecedero"),
    ("Huevos", 8, "Alta", "ProveedorX", "Perecedero"),
    ("Medicamentos", 5, "Alta", "ProveedorPrincipal", "Crítico"),
    ("Azúcar", 3, "Media", "ProveedorSecundario", "NoPerecedero"),
    ("Sal", 55, "Baja", "ProveedorY", "NoPerecedero"),
]

# Declarar hechos (Producto + Stock + Demanda + Proveedor + Categoria)
for nombre, stock, demanda, prov, cat in productos:
    engine.declare(Producto(nombre=nombre))
    engine.declare(Stock(producto=nombre, cantidad=stock))
    engine.declare(Demanda(producto=nombre, nivel=demanda))
    engine.declare(Proveedor(producto=nombre, nombre=prov))
    engine.declare(Categoria(producto=nombre, nombre=cat))

# Declarar pedidos
engine.declare(Pedido(producto="Leche", cantidad=10))
engine.declare(Pedido(producto="Arroz", cantidad=5))
engine.declare(Pedido(producto="Pan", cantidad=8))
engine.declare(Pedido(producto="Medicamentos", cantidad=12))
engine.declare(Pedido(producto="Huevos", cantidad=20))


engine.run()

