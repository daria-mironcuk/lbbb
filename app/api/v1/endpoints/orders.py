from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderItemCreate, OrderItemResponse, OrderResponse

router = APIRouter()


async def _get_order_or_404(order_id: int, db: AsyncSession) -> Order:
    order = await db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
) -> Order:
    user = await db.get(User, order_data.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    order = Order(**order_data.model_dump())
    db.add(order)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order with this order_number already exists",
        ) from exc
    await db.refresh(order)
    return order


@router.get("/", response_model=list[OrderResponse])
async def get_orders(db: AsyncSession = Depends(get_db)) -> list[Order]:
    result = await db.execute(select(Order).order_by(Order.id))
    return list(result.scalars().all())


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)) -> Order:
    return await _get_order_or_404(order_id, db)


@router.post(
    "/{order_id}/items",
    response_model=OrderItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_order_item(
    order_id: int,
    item_data: OrderItemCreate,
    db: AsyncSession = Depends(get_db),
) -> OrderItem:
    await _get_order_or_404(order_id, db)

    product = await db.get(Product, item_data.product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if item_data.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be positive"
        )

    item = OrderItem(
        order_id=order_id, product_id=item_data.product_id, quantity=item_data.quantity
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item