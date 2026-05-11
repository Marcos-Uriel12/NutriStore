from __future__ import annotations

import enum
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class MetodoPago(str, enum.Enum):
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"


class EstadoPago(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False)
    metodo: Mapped[MetodoPago] = mapped_column(Enum(MetodoPago), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estado: Mapped[EstadoPago] = mapped_column(
        Enum(EstadoPago), default=EstadoPago.PENDIENTE, nullable=False
    )

    pedido: Mapped["Pedido"] = relationship("Pedido", back_populates="pago")
