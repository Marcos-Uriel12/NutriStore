from pydantic import BaseModel

from app.models.pedido_item import UnidadMedida


class CartItemCreate(BaseModel):
    producto_id: int
    cantidad: float
    unidad_medida: UnidadMedida = UnidadMedida.KG


class CartItemResponse(BaseModel):
    producto_id: int
    cantidad: float
    unidad_medida: UnidadMedida
    nombre: str = ""
    precio: float = 0.0
    imagen_url: str = ""
    tipo_unidad: str = ""
