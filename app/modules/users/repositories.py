import logging
from typing import Dict, Optional, Union

from fastapi_async_sqlalchemy import db
from sqlalchemy import String, cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PermitModel, RolesModel, UserModel
from app.models.navigation_model import NavigationModel

from . import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[UserModel]):
    def __init__(self, model: UserModel, session: Optional[AsyncSession] = None):
        super().__init__(model, session)

    async def find_by_username(self, username: str) -> Optional[UserModel]:
        """Find user by username."""
        query = select(self.model).filter(self.model.name == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> Optional[UserModel]:
        """Find user by email."""
        query = select(self.model).filter(self.model.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_user_basic_info(self, user_id: str) -> Optional[Dict]:
        """Get basic user information."""
        user_query = select(
            self.model.id.label("id"),
            self.model.name.label("name"),
            self.model.address.label("address"),
            self.model.phone.label("phone"),
            self.model.gender.label("gender"),
            self.model.agency_name.label("agency_name"),
            self.model.agency_type.label("agency_type"),
            self.model.file.label("file"),
            self.model.avatar.label("avatar"),
            self.model.email.label("email"),
            self.model.password.label("password"),
            self.model.enable.label("enable"),
            self.model.last_login.label("last_login"),
            self.model.role_id.label("role_id"),
        ).where(self.model.id == user_id)

        user_result = await self.session.execute(user_query)
        user_row = user_result.mappings().first()
        return dict(user_row) if user_row else None

    async def _get_role_info(self, role_id: str) -> Optional[Dict]:
        """Get role information."""
        role_query = select(
            RolesModel.id.label("id"),
            RolesModel.name.label("name"),
        ).where(RolesModel.id == role_id)

        role_result = await self.session.execute(role_query)
        role_row = role_result.mappings().first()
        return dict(role_row) if role_row else None

    async def _get_role_permissions(self, role_id: str) -> list:
        """Get permissions for a specific role."""
        permissions_query = (
            select(
                NavigationModel.id.label("id"),
                NavigationModel.name.label("name"),
                NavigationModel.parent.label("parent"),
                NavigationModel.is_enabled.label("is_enabled"),
                NavigationModel.icon.label("icon"),
                NavigationModel.url.label("url"),
                NavigationModel.sort_order.label("sort_order"),
                NavigationModel.sign.label("sign"),
                PermitModel.permit_content.label("permit_content"),
            )
            .select_from(PermitModel)
            .join(
                NavigationModel,
                NavigationModel.id == PermitModel.navigation_id,
            )
            .where(
                PermitModel.role_id == role_id,
                or_(
                    PermitModel.permit_content["read"].is_(True),
                    PermitModel.permit_content["create"].is_(True),
                    PermitModel.permit_content["update"].is_(True),
                    PermitModel.permit_content["delete"].is_(True),
                    cast(PermitModel.permit_content["read"], String) == "true",
                    cast(PermitModel.permit_content["create"], String) == "true",
                    cast(PermitModel.permit_content["update"], String) == "true",
                    cast(PermitModel.permit_content["delete"], String) == "true",
                ),
            )
        )

        permissions_result = await self.session.execute(permissions_query)
        permissions = []

        for row in permissions_result.mappings().all():
            permission_dict = dict(row)
            permit_content = permission_dict.pop("permit_content", {})

            def normalize_permission(value: Union[bool, str]) -> bool:
                """Normalize permission value to boolean."""
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    return value.lower() == "true"
                else:
                    return False

            permission_dict["permissions"] = {
                "read": normalize_permission(permit_content.get("read", False)),
                "create": normalize_permission(permit_content.get("create", False)),
                "update": normalize_permission(permit_content.get("update", False)),
                "delete": normalize_permission(permit_content.get("delete", False)),
            }
            permissions.append(permission_dict)

        logger.info(f"Found {len(permissions)} permissions for role {role_id}")
        return permissions

    async def find_by_id_with_permissions(self, id: str) -> Optional[Dict]:
        """Find user by ID with role and permissions information."""
        # Get basic user info
        user_dict = await self._get_user_basic_info(id)
        if not user_dict:
            return None

        role_id = user_dict.get("role_id")
        if not role_id:
            user_dict.pop("role_id", None)
            user_dict["role"] = None
            return user_dict

        # Get role info
        role_info = await self._get_role_info(role_id)
        if not role_info:
            user_dict.pop("role_id", None)
            user_dict["role"] = None
            return user_dict

        # Get permissions
        permissions = await self._get_role_permissions(role_id)

        # Build role object
        role = {
            "id": role_info["id"],
            "name": role_info["name"],
            "navigations": permissions,
        }

        # Clean up user dict
        user_dict.pop("role_id", None)
        user_dict["role"] = role

        return user_dict
