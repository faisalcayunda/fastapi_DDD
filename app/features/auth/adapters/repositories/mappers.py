from app.features.auth.entities.user import User
from app.platform.db.models import UserModel


def to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        name=model.name,
        email=model.email,
        password_hash=model.password_hash,
        address=model.address,
        phone=model.phone,
        gender=model.gender,
        avatar=model.avatar,
        role_id=model.role_id,
        is_enabled=model.is_enabled,
        is_verified=model.is_verified,
        created_by=model.created_by,
        updated_by=model.updated_by,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
