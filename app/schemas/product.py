from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    price: Decimal = Field(..., ge=0, decimal_places=2)


class ProductCreate(ProductBase):
    category_id: int


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    category_id: int | None = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    seller_id: int