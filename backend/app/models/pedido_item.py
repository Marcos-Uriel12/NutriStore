from __future__ import annotations

import enum
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.pedido import Pedido
    from app.models.producto import Producto


class UnidadMedida(str, enum.Enum):
    KG = "KG"
    UNIDAD = "UNIDAD"


class PedidoItem(Base):
    __tablename__ = "pedido_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    cantidad: Mapped[float] = mapped_column(nullable=False)
    unidad_medida: Mapped[UnidadMedida] = mapped_column(Enum(UnidadMedida), nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    pedido: Mapped["Pedido"] = relationship("Pedido", back_populates="items")
    producto: Mapped["Producto"] = relationship("Producto", lazy="selectin")
