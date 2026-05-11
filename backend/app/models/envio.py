from decimal import Decimal

from sqlalchemy import Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base
from app.models.pedido import ZonaEnvio


class EnvioConfig(Base):
    __tablename__ = "envios_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    zona: Mapped[ZonaEnvio] = mapped_column(Enum(ZonaEnvio), unique=True, nullable=False)
    costo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
