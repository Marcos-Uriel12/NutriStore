from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


from app.models.admin import Admin
from app.models.categoria import Categoria
from app.models.producto import Producto, TipoUnidad
from app.models.imagen import Imagen
from app.models.pedido import Pedido, EstadoPedido, TipoEntrega, ZonaEnvio
from app.models.pedido_item import PedidoItem, UnidadMedida
from app.models.pago import Pago, MetodoPago, EstadoPago
from app.models.envio import EnvioConfig

__all__ = [
    "Base",
    "Admin",
    "Categoria",
    "Producto",
    "TipoUnidad",
    "Imagen",
    "Pedido",
    "EstadoPedido",
    "TipoEntrega",
    "ZonaEnvio",
    "PedidoItem",
    "UnidadMedida",
    "Pago",
    "MetodoPago",
    "EstadoPago",
    "EnvioConfig",
]
