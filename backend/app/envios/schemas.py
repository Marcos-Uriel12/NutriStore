from decimal import Decimal

from pydantic import BaseModel

from app.models.pedido import ZonaEnvio


class EnvioConfigItem(BaseModel):
    zona: ZonaEnvio
    costo: Decimal


class EnvioConfigUpdate(BaseModel):
    zonas: list[EnvioConfigItem]
