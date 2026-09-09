from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderItemBase(BaseModel):
    quantity: int = Field(default=1, ge=1)


class OrderItemCreate(OrderItemBase):
    product_id: int


class OrderItemResponse(OrderItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_id: int


class OrderBase(BaseModel):
    order_number: str = Field(..., min_length=3, max_length=50)


class OrderCreate(OrderBase):
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderResponse(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    user_id: int
    items: list[OrderItemResponse] = []