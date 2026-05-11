from __future__ import annotations

import enum
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, ForeignKey, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.imagen import Imagen


class TipoUnidad(str, enum.Enum):
    KG = "KG"
    UNIDAD = "UNIDAD"


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    precio_por_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    precio_por_unidad: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    tipo_unidad: Mapped[TipoUnidad] = mapped_column(Enum(TipoUnidad), nullable=False)
    stock_kg: Mapped[float | None] = mapped_column(nullable=True)
    stock_unidades: Mapped[int | None] = mapped_column(nullable=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)
    gramos: Mapped[int] = mapped_column(default=1000, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categoria: Mapped["Categoria"] = relationship("Categoria", lazy="selectin")
    imagenes: Mapped[list["Imagen"]] = relationship(
        "Imagen", back_populates="producto", lazy="selectin", cascade="all, delete-orphan"
    )
