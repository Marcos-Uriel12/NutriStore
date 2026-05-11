from decimal import Decimal

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.envio import EnvioConfig
from app.models.pedido import ZonaEnvio

DEFAULT_COSTS: dict[ZonaEnvio, Decimal] = {
    ZonaEnvio.CABA: Decimal("3500.00"),
    ZonaEnvio.GBA_NORTE: Decimal("3500.00"),
}


async def get_envios_config(db: AsyncSession) -> list[EnvioConfig]:
    result = await db.execute(select(EnvioConfig).order_by(EnvioConfig.zona))
    configs = list(result.scalars().all())

    if configs:
        return configs

    # Return defaults if DB is empty
    defaults: list[EnvioConfig] = []
    for zona, costo in DEFAULT_COSTS.items():
        cfg = EnvioConfig(zona=zona, costo=costo)
        defaults.append(cfg)
    return defaults


async def update_envios_config(
    db: AsyncSession,
    zonas: list[dict],
) -> list[EnvioConfig]:
    """Replace all zones: delete existing, insert new."""
    await db.execute(delete(EnvioConfig))

    configs: list[EnvioConfig] = []
    for z in zonas:
        cfg = EnvioConfig(zona=z["zona"], costo=z["costo"])
        db.add(cfg)
        configs.append(cfg)

    await db.commit()
    return configs
