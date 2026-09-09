from typing import Optional, List, Dict, Any

from app.schemas.user import UserCreate, UserUpdate


class CRUDUser:
    """Ізольована In-Memory база даних всередині сервісного шару."""

    def __init__(self) -> None:
        self._db: Dict[int, Dict[str, Any]] = {}
        self._next_id: int = 1

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._db.values())

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self._db.get(user_id)

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return next(
            (user for user in self._db.values() if user["email"] == email),
            None,
        )

    def create(self, user_data: UserCreate) -> Dict[str, Any]:
        new_user = {
            "id": self._next_id,
            "username": user_data.username,
            "email": user_data.email,
            "is_active": user_data.is_active,
        }
        self._db[self._next_id] = new_user
        self._next_id += 1
        return new_user

    def update(self, user_id: int, user_data: UserUpdate) -> Optional[Dict[str, Any]]:
        stored_user = self._db.get(user_id)
        if stored_user is None:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        stored_user.update(update_data)
        return stored_user

    def delete(self, user_id: int) -> bool:
        return self._db.pop(user_id, None) is not None


# Експортуємо інстанс класу для використання в роутерах
crud_user = CRUDUser()