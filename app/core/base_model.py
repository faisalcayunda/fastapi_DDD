from typing import Any, Dict

from sqlmodel import SQLModel

from app.utils.helpers import orm_to_dict


class Base(SQLModel):
    __abstract__ = True

    def to_dict(self) -> Dict[str, Any]:
        return orm_to_dict(self)
