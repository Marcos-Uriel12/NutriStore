from pydantic import BaseModel, field_validator
from typing import Self

from app.models.producto import TipoUnidad


class ImagenCreate(BaseModel):
    url: str


class ImagenResponse(BaseModel):
    id: int
    url: str

    model_config = {"from_attributes": True}


class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: str | None = None


class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None = None

    model_config = {"from_attributes": True}


class ProductoCreate(BaseModel):
    nombre: str
    descripcion: str | None = None
    precio_por_kg: float
    precio_por_unidad: float | None = None
    tipo_unidad: TipoUnidad
    stock_kg: float | None = None
    stock_unidades: int | None = None
    categoria_id: int
    gramos: int = 1000
    imagenes: list[ImagenCreate] = []

    @field_validator("imagenes")
    @classmethod
    def max_two_images(cls, v: list[ImagenCreate]) -> list[ImagenCreate]:
        if len(v) > 2:
            raise ValueError("Maximum 2 images per product")
        return v


class ProductoUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    precio_por_kg: float | None = None
    precio_por_unidad: float | None = None
    tipo_unidad: TipoUnidad | None = None
    stock_kg: float | None = None
    stock_unidades: int | None = None
    categoria_id: int | None = None
    gramos: int | None = None
    activo: bool | None = None


class ProductoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None = None
    precio_por_kg: float
    precio_por_unidad: float | None = None
    tipo_unidad: TipoUnidad
    stock_kg: float | None = None
    stock_unidades: int | None = None
    categoria_id: int
    gramos: int
    activo: bool
    categoria: CategoriaResponse | None = None
    imagenes: list[ImagenResponse] = []

    model_config = {"from_attributes": True}
