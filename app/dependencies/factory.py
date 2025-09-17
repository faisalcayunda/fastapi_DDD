from functools import partial
from typing import Callable

from app.api.dependencies.database import get_db
from app.core.minio_client import MinioClient
from app.models import (
    AttachmentModel,
    FileModel,
    ForestryAreaModel,
    ForestryLandModel,
    ForestryProposalModel,
    ForestrySchemaModel,
    NavigationModel,
    PermitModel,
    PiapsModel,
    ProposalforestryStatusModel,
    RefreshTokenModel,
    RegionalModel,
    RolesModel,
    UserModel,
)
from app.repositories import (
    AttachmentRepository,
    FileRepository,
    ForestryAreaRepository,
    ForestryLandRepository,
    ForestryProposalRepository,
    ForestrySchemaRepository,
    NavigationRepository,
    PermitRepository,
    PiapsRepository,
    ProposalforestryStatusRepository,
    RegionalRepository,
    RolesRepository,
    TokenRepository,
    UserRepository,
)
from app.services import (
    AttachmentService,
    AuthService,
    FileService,
    ForestryAreaService,
    ForestryLandService,
    ForestrySchemaService,
    ForestyProposalService,
    NavigationService,
    PermitService,
    PiapsService,
    ProposalforestryStatusService,
    RegionalService,
    RolesService,
    UserService,
)


class RepositoryFactory:
    """Factory untuk membuat repository instances dengan dependency injection."""

    @staticmethod
    def create_user_repository() -> UserRepository:
        return UserRepository(UserModel)

    @staticmethod
    def create_token_repository() -> TokenRepository:
        return TokenRepository(RefreshTokenModel)

    @staticmethod
    def create_file_repository() -> FileRepository:
        return FileRepository(FileModel)

    @staticmethod
    def create_regional_repository() -> RegionalRepository:
        return RegionalRepository(RegionalModel)

    @staticmethod
    def create_forestry_schema_repository() -> ForestrySchemaRepository:
        return ForestrySchemaRepository(ForestrySchemaModel)

    @staticmethod
    def create_proposal_forestry_status_repository() -> ProposalforestryStatusRepository:
        return ProposalforestryStatusRepository(ProposalforestryStatusModel)

    @staticmethod
    def create_piaps_repository() -> PiapsRepository:
        return PiapsRepository(PiapsModel)

    @staticmethod
    def create_forestry_proposal_repository() -> ForestryProposalRepository:
        return ForestryProposalRepository(ForestryProposalModel)

    @staticmethod
    def create_attachment_repository() -> AttachmentRepository:
        return AttachmentRepository(AttachmentModel)

    @staticmethod
    def create_forestry_land_repository() -> ForestryLandRepository:
        return ForestryLandRepository(ForestryLandModel)

    @staticmethod
    def create_permit_repository() -> PermitRepository:
        return PermitRepository(PermitModel)

    @staticmethod
    def create_navigation_repository() -> NavigationRepository:
        return NavigationRepository(NavigationModel)

    @staticmethod
    def create_roles_repository() -> RolesRepository:
        return RolesRepository(RolesModel)

    @staticmethod
    def create_forestry_area_repository() -> ForestryAreaRepository:
        return ForestryAreaRepository(ForestryAreaModel)


class ServiceFactory:
    """Factory untuk membuat service instances."""

    def __init__(self):
        self.repository_factory = RepositoryFactory()

    def get_auth_service(self) -> AuthService:
        """Get AuthService instance."""
        return AuthService(
            user_repository=self.repository_factory.create_user_repository(),
            token_repository=self.repository_factory.create_token_repository(),
        )

    def get_user_service(self) -> UserService:
        """Get UserService instance."""
        return UserService(self.repository_factory.create_user_repository())

    def get_file_service(self) -> FileService:
        """Get FileService instance."""
        return FileService(self.repository_factory.create_file_repository(), MinioClient())

    def get_regional_service(self) -> RegionalService:
        """Get RegionalService instance."""
        return RegionalService(self.repository_factory.create_regional_repository())

    def get_forestry_schema_service(self) -> ForestrySchemaService:
        """Get ForestrySchemaService instance."""
        return ForestrySchemaService(self.repository_factory.create_forestry_schema_repository())

    def get_proposal_forestry_status_service(self) -> ProposalforestryStatusService:
        """Get ProposalforestryStatusService instance."""
        return ProposalforestryStatusService(self.repository_factory.create_proposal_forestry_status_repository())

    def get_piaps_service(self) -> PiapsService:
        """Get PiapsService instance."""
        return PiapsService(self.repository_factory.create_piaps_repository())

    def get_proposal_forestry_service(self) -> ForestyProposalService:
        """Get ForestyProposalService instance."""
        return ForestyProposalService(self.repository_factory.create_forestry_proposal_repository())

    def get_attachment_service(self) -> AttachmentService:
        """Get AttachmentService instance."""
        return AttachmentService(self.repository_factory.create_attachment_repository())

    def get_forestry_land_service(self) -> ForestryLandService:
        """Get ForestryLandService instance."""
        return ForestryLandService(self.repository_factory.create_forestry_land_repository())

    def get_permit_service(self) -> PermitService:
        """Get PermitService instance."""
        return PermitService(self.repository_factory.create_permit_repository())

    def get_navigation_service(self) -> NavigationService:
        """Get NavigationService instance."""
        return NavigationService(self.repository_factory.create_navigation_repository())

    def get_roles_service(self) -> RolesService:
        """Get RolesService instance."""
        return RolesService(self.repository_factory.create_roles_repository())

    def get_forestry_area_service(self) -> ForestryAreaService:
        """Get ForestryAreaService instance."""
        return ForestryAreaService(self.repository_factory.create_forestry_area_repository())


# Backward compatibility - maintain existing interface
class Factory(ServiceFactory):
    """Legacy Factory class for backward compatibility."""

    def __init__(self):
        super().__init__()
        # Keep static methods for backward compatibility
        self.user_repository = staticmethod(partial(UserRepository, UserModel))
        self.token_repository = staticmethod(partial(TokenRepository, RefreshTokenModel))
        self.file_repository = staticmethod(partial(FileRepository, FileModel))
        self.regional_repository = staticmethod(partial(RegionalRepository, RegionalModel))
        self.forestry_schema_repository = staticmethod(partial(ForestrySchemaRepository, ForestrySchemaModel))
        self.proposal_forestry_status_repository = staticmethod(
            partial(ProposalforestryStatusRepository, ProposalforestryStatusModel)
        )
        self.piaps_repository = staticmethod(partial(PiapsRepository, PiapsModel))
        self.forestry_proposal_repository = staticmethod(partial(ForestryProposalRepository, ForestryProposalModel))
        self.attachment_repository = staticmethod(partial(AttachmentRepository, AttachmentModel))
        self.forestry_land_repository = staticmethod(partial(ForestryLandRepository, ForestryLandModel))
        self.permit_repository = staticmethod(partial(PermitRepository, PermitModel))
        self.navigation_repository = staticmethod(partial(NavigationRepository, NavigationModel))
        self.roles_repository = staticmethod(partial(RolesRepository, RolesModel))
        self.forestry_area_repository = staticmethod(partial(ForestryAreaRepository, ForestryAreaModel))
