from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.admin import Admin
from app.envios.schemas import EnvioConfigItem, EnvioConfigUpdate
from app.envios import service as envios_service

router = APIRouter()


@router.get("/config", response_model=list[EnvioConfigItem])
async def get_config(db: AsyncSession = Depends(get_db)):
    return await envios_service.get_envios_config(db)


@router.put("/config", response_model=list[EnvioConfigItem])
async def update_config(
    data: EnvioConfigUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    zonas_dicts = [{"zona": z.zona, "costo": z.costo} for z in data.zonas]
    configs = await envios_service.update_envios_config(db, zonas_dicts)
    return configs
