import datetime
from decimal import Decimal

from pydantic import BaseModel, model_validator

from app.models.pago import MetodoPago, EstadoPago
from app.models.pedido import EstadoPedido, TipoEntrega, ZonaEnvio
from app.models.pedido_item import UnidadMedida


class PedidoCreate(BaseModel):
    cliente_nombre: str
    cliente_direccion: str
    cliente_telefono: str
    direccion_entrega: str | None = None
    tipo_entrega: TipoEntrega
    zona_envio: ZonaEnvio | None = None
    metodo_pago: MetodoPago


class PedidoItemResponse(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str = ""
    cantidad: float
    unidad_medida: UnidadMedida
    precio_unitario: Decimal

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _fill_producto_nombre(cls, data):
        if isinstance(data, dict):
            return data
        # data is a PedidoItem ORM instance
        try:
            producto = getattr(data, "producto", None)
            if producto is not None:
                data.producto_nombre = producto.nombre
        except Exception:
            pass
        return data


class PagoResponse(BaseModel):
    id: int
    metodo: MetodoPago
    monto: Decimal
    estado: EstadoPago

    model_config = {"from_attributes": True}


class PedidoResponse(BaseModel):
    id: int
    session_id: str
    cliente_nombre: str
    cliente_direccion: str
    cliente_telefono: str
    direccion_entrega: str
    tipo_entrega: TipoEntrega
    zona_envio: ZonaEnvio | None = None
    costo_envio: Decimal
    estado: EstadoPedido
    total: Decimal
    created_at: datetime.datetime
    items: list[PedidoItemResponse] = []
    pago: PagoResponse | None = None

    model_config = {"from_attributes": True}


class EstadoUpdate(BaseModel):
    estado: EstadoPedido
