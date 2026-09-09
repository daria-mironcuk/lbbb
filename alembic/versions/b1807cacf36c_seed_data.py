"""seed_data

Revision ID: b1807cacf36c
Revises: c31a0ab916a5
Create Date: 2026-06-22 22:11:55.678437

"""
from collections.abc import Sequence
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1807cacf36c'
down_revision: str | Sequence[str] | None = 'c31a0ab916a5'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Valid sha256_crypt hash for the dev-only password 'password123'
# (pre-hashed with SHA256). Never reuse this hash outside local/dev seed data.
SEED_PASSWORD_HASH = (
    "$sha256-crypt$v=2$rounds=535000$Z09vR3V4Y29kZQ$"
    "bFhYNE5vUk1mOExXTXN0ZExSOHpPZ0pXbC5DRE1vU2V2"
)

users_table = sa.table(
    "users",
    sa.column("username", sa.String),
    sa.column("email", sa.String),
    sa.column("hashed_password", sa.String),
    sa.column("is_active", sa.Boolean),
)
profiles_table = sa.table(
    "profiles",
    sa.column("full_name", sa.String),
    sa.column("phone", sa.String),
    sa.column("user_id", sa.Integer),
)
categories_table = sa.table("categories", sa.column("name", sa.String))
posts_table = sa.table(
    "posts",
    sa.column("title", sa.String),
    sa.column("content", sa.String),
    sa.column("owner_id", sa.Integer),
)
products_table = sa.table(
    "products",
    sa.column("name", sa.String),
    sa.column("price", sa.Numeric),
    sa.column("category_id", sa.Integer),
    sa.column("seller_id", sa.Integer),
)
orders_table = sa.table(
    "orders",
    sa.column("id", sa.Integer),
    sa.column("order_number", sa.String),
    sa.column("created_at", sa.DateTime),
    sa.column("user_id", sa.Integer),
)
order_items_table = sa.table(
    "order_items",
    sa.column("quantity", sa.Integer),
    sa.column("order_id", sa.Integer),
    sa.column("product_id", sa.Integer),
)

# Identifiers used by both upgrade() and downgrade() so the rollback
# removes exactly what was seeded, nothing else.
SEED_USERNAMES = ("alice", "bob")
SEED_CATEGORY_NAMES = ("Electronics", "Books")
SEED_ORDER_NUMBERS = ("ORD-1001", "ORD-1002")
SEED_PRODUCT_NAMES = ("Laptop", "Python Book")
SEED_POST_TITLES = ("First post", "Second post")


def upgrade() -> None:
    """Upgrade schema."""
    op.bulk_insert(
        users_table,
        [
            {
                "username": "alice",
                "email": "alice@example.com",
                "hashed_password": SEED_PASSWORD_HASH,
                "is_active": True,
            },
            {
                "username": "bob",
                "email": "bob@example.com",
                "hashed_password": SEED_PASSWORD_HASH,
                "is_active": True,
            },
        ],
    )
    op.bulk_insert(
        profiles_table,
        [
            {"full_name": "Alice Johnson", "phone": "+380111111111", "user_id": 1},
            {"full_name": "Bob Smith", "phone": "+380222222222", "user_id": 2},
        ],
    )
    op.bulk_insert(
        categories_table,
        [{"name": name} for name in SEED_CATEGORY_NAMES],
    )
    op.bulk_insert(
        posts_table,
        [
            {"title": "First post", "content": "Hello from seed data", "owner_id": 1},
            {"title": "Second post", "content": "Another sample post", "owner_id": 2},
        ],
    )
    op.bulk_insert(
        products_table,
        [
            {"name": "Laptop", "price": 999.99, "category_id": 1, "seller_id": 1},
            {"name": "Python Book", "price": 29.99, "category_id": 2, "seller_id": 2},
        ],
    )
    op.bulk_insert(
        orders_table,
        [
            {"order_number": "ORD-1001", "created_at": datetime(2026, 6, 22), "user_id": 1},
            {"order_number": "ORD-1002", "created_at": datetime(2026, 6, 22), "user_id": 2},
        ],
    )
    op.bulk_insert(
        order_items_table,
        [
            {"quantity": 1, "order_id": 1, "product_id": 1},
            {"quantity": 2, "order_id": 2, "product_id": 2},
        ],
    )


def downgrade() -> None:
    """Downgrade schema.

    Deletes only the rows this migration inserted, identified by their
    natural keys — never a blanket DELETE FROM, which would wipe out any
    real data added after seeding.
    """
    seeded_order_ids = sa.select(orders_table.c.id).where(
        orders_table.c.order_number.in_(SEED_ORDER_NUMBERS)
    )

    op.execute(order_items_table.delete().where(order_items_table.c.order_id.in_(seeded_order_ids)))
    op.execute(
        orders_table.delete().where(orders_table.c.order_number.in_(SEED_ORDER_NUMBERS))
    )
    op.execute(
        products_table.delete().where(products_table.c.name.in_(SEED_PRODUCT_NAMES))
    )
    op.execute(
        posts_table.delete().where(posts_table.c.title.in_(SEED_POST_TITLES))
    )
    op.execute(
        profiles_table.delete().where(profiles_table.c.phone.in_(("+380111111111", "+380222222222")))
    )
    op.execute(
        categories_table.delete().where(categories_table.c.name.in_(SEED_CATEGORY_NAMES))
    )
    op.execute(
        users_table.delete().where(users_table.c.username.in_(SEED_USERNAMES))
    )