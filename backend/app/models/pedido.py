from __future__ import annotations

import datetime
import enum
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.pedido_item import PedidoItem
    from app.models.pago import Pago


class EstadoPedido(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class TipoEntrega(str, enum.Enum):
    ENVIO = "ENVIO"
    RETIRO = "RETIRO"


class ZonaEnvio(str, enum.Enum):
    CABA = "CABA"
    GBA_NORTE = "GBA_NORTE"
    GBA_SUR = "GBA_SUR"
    GBA_OESTE = "GBA_OESTE"


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False)
    cliente_nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    cliente_direccion: Mapped[str] = mapped_column(String(500), nullable=False)
    cliente_telefono: Mapped[str] = mapped_column(String(50), nullable=False)
    direccion_entrega: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_entrega: Mapped[TipoEntrega] = mapped_column(Enum(TipoEntrega), nullable=False)
    zona_envio: Mapped[ZonaEnvio | None] = mapped_column(Enum(ZonaEnvio), nullable=True)
    costo_envio: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    estado: Mapped[EstadoPedido] = mapped_column(
        Enum(EstadoPedido), default=EstadoPedido.PENDIENTE, nullable=False
    )
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.now(datetime.timezone.utc),
    )

    items: Mapped[list["PedidoItem"]] = relationship(
        "PedidoItem", back_populates="pedido", lazy="selectin", cascade="all, delete-orphan"
    )
    pago: Mapped["Pago | None"] = relationship(
        "Pago", back_populates="pedido", lazy="selectin", uselist=False, cascade="all, delete-orphan"
    )
