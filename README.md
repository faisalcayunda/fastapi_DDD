# Portal Satu Peta Backend

Backend for the Portal Satu Peta application.

## Folder Structure
```
├── .env.example                # Contoh file environment
├── .github/                    # Konfigurasi GitHub Actions
│   └── workflows/
│       └── deploy.yml          # Workflow untuk deployment
├── .gitignore                  # Daftar file/folder yang diabaikan Git
├── .pre-commit-config.yaml     # Konfigurasi pre-commit hooks
├── Dockerfile                  # Instruksi build Docker image
├── README.md                   # Dokumentasi proyek (file ini)
├── alembic.ini                 # Konfigurasi Alembic untuk migrasi database
├── app/                        # Direktori utama aplikasi
│   ├── api/                    # Layer API
│   │   ├── dependencies/       # Dependency Injection
│   │   ├── middlewares/        # Custom Middleware
│   │   └── v1/                 # API Versioning
│   ├── core/                   # Fungsi inti aplikasi
│   │   ├── config/             # Konfigurasi modular
│   │   │   ├── app.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── storage.py
│   │   ├── exceptions/         # Custom Exception
│   │   └── data_types.py       # Tipe data bersama
│   ├── domain/                 # Domain Layer
│   │   ├── interfaces/         # Interface abstrak
│   │   │   ├── repository_interface.py
│   │   │   ├── service_interface.py
│   │   │   ├── cache_interface.py
│   │   │   ├── storage_interface.py
│   │   │   └── auth_interface.py
│   │   └── models/             # Model domain
│   │       ├── base_model.py
│   │       ├── user.py
│   │       ├── role.py
│   │       ├── permission.py
│   │       └── navigation.py
│   ├── infrastructure/         # Infrastructure Layer
│   │   ├── database/
│   │   │   └── session.py
│   │   ├── cache/
│   │   │   └── redis_cache.py
│   │   ├── storage/
│   │   │   └── minio_storage.py
│   │   └── security/
│   │       ├── jwt.py
│   │       └── password.py
│   ├── repositories/           # Data Access Layer
│   ├── services/               # Business Logic Layer
│   └── utils/                  # Utility functions
├── assets/                     # File statis (jika ada)
├── docker-compose.yml          # Konfigurasi Docker Compose
├── migrations/                 # Script migrasi database Alembic
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   ├── scripts.py
│   └── versions/               # File versi migrasi
│       └── __init__.py
├── poetry.lock                 # File lock dependensi Poetry
├── pyproject.toml              # Konfigurasi proyek Poetry
├── run.py                      # Script menjalankan server Uvicorn lokal
└── tests/                      # Direktori unit & integration test
    ├── __init__.py
    ├── conftest.py             # Konfigurasi Pytest
    ├── test_api/
    │   └── __init__.py
    └── test_services/
        └── __init__.py
```
## How to Run the Project

### 1. Initial Setup

*   Ensure you have Python (version >=3.10, <4.0 recommended as per `pyproject.toml`) and Poetry installed.
*   Copy the `.env.example` file to `.env` and customize its configuration, especially for database and MinIO connections.
    ```bash
    cp .env.example .env
    ```
*   Edit the `.env` file as needed.

### 2. Running Locally (using Poetry and Uvicorn)

1.  **Install dependencies:**
    ```bash
    poetry install
    ```
2.  **Run database migrations (if necessary):**
    Ensure the database is running and the configuration in `.env` is correct.
    ```bash
    poetry run alembic upgrade head
    ```
    Alternatively, if there's a custom script for migrations as seen in `deploy.yml`:
    ```bash
    poetry run python migrations/scripts.py
    ```
    *(Check the content of `migrations/scripts.py` for the exact command if it differs)*

3.  **Run the application server:**
    ```bash
    poetry run python run.py
    ```
    Or directly using Uvicorn:
    ```bash
    poetry run uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
    ```
    The application will run at `http://localhost:5000` (or as configured in `.env` and `run.py`).

### 3. Running Using Docker

1.  **Ensure Docker and Docker Compose are installed.**
2.  **Build and run the container:**
    From the project root directory, run:
    ```bash
    docker-compose up --build
    ```
    If you have an `environment.env` file (as referenced in `docker-compose.yml`), ensure it exists and contains the necessary environment configurations. Otherwise, you might need to adjust `docker-compose.yml` to use the `.env` file or set environment variables directly.

    The application will run at `http://localhost:5000` (as per port mapping in `docker-compose.yml`).

## How to Create an Endpoint, Model, Repository, and Service

This project follows a layered architecture pattern commonly used in FastAPI applications.

### 1. Creating a Model (`app/models/`)

Models represent tables in your database. They are defined using SQLAlchemy.

Example (e.g., `app/models/item_model.py`):
```python
from sqlalchemy import Column, Integer, String, ForeignKey, UUID
from sqlalchemy.orm import relationship
import uuid6
from . import Base # Ensure Base is imported from app.models

class ItemModel(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id")) # Example relationship

    owner = relationship("UserModel", back_populates="items") # Adjust to your User model
```
*   Don't forget to add the new model to `app/models/__init__.py` if necessary and create a database migration using Alembic.
    ```bash
    poetry run alembic revision -m "create_items_table"
    ```
    Then edit the newly created migration file in `migrations/versions/` to define the `upgrade()` and `downgrade()` functions, and run:
    ```bash
    poetry run alembic upgrade head
    ```

### 2. Creating a Schema (`app/schemas/`)

Pydantic schemas are used for request data validation and response data formatting.

Example (e.g., `app/schemas/item_schema.py`):
```python
from pydantic import BaseModel
from app.core.data_types import UUID7Field # Or the appropriate UUID type
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

class ItemCreateSchema(ItemBase):
    pass

class ItemUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ItemSchema(ItemBase):
    id: UUID7Field
    owner_id: UUID7Field

    class Config:
        orm_mode = True # or from_attributes = True for Pydantic v2
```

### 3. Creating a Repository (`app/repositories/`)

Repositories are responsible for all database interactions related to a model.

Example (e.g., `app/repositories/item_repository.py`):
```python
from sqlalchemy import select
from fastapi_async_sqlalchemy import db # or the appropriate db session
from app.models.item_model import ItemModel # Import your model
from .base import BaseRepository # Import BaseRepository
from app.core.data_types import UUID7Field

class ItemRepository(BaseRepository[ItemModel]):
    def __init__(self):
        super().__init__(ItemModel)

    async def find_by_name(self, name: str) -> ItemModel | None:
        query = select(self.model).filter(self.model.name == name)
        result = await db.session.execute(query)
        return result.scalar_one_or_none()

    # Add other methods as needed (findById, create, update, delete, etc.)
    # Example find_by_id from UserRepository:
    async def find_by_id(self, id: UUID7Field) -> ItemModel | None:
        query = select(self.model).filter(self.model.id == id)
        result = await db.session.execute(query)
        return result.scalar_one_or_none()
```
*   Ensure to register the new repository in `app/api/dependencies/factory.py` if you are using the factory pattern for dependencies.

### 4. Creating a Service (`app/services/`)

Services contain the application's business logic. Services will use repositories to interact with data.

Example (e.g., `app/services/item_service.py`):
```python
from typing import Dict, List, Tuple, Union
from uuid6 import UUID # or from app.core.data_types import UUID7Field
from fastapi import HTTPException, status

from app.models.item_model import ItemModel
from app.repositories.item_repository import ItemRepository
from app.schemas.item_schema import ItemCreateSchema, ItemUpdateSchema, ItemSchema # Import your schemas
from app.schemas.user_schema import UserSchema # For user info performing the action
from .base import BaseService
from app.core.exceptions import NotFoundException

class ItemService(BaseService[ItemModel, ItemRepository]):
    def __init__(self, repository: ItemRepository):
        super().__init__(ItemModel, repository)
        # self.user_service = user_service # If other services are needed

    async def create_item(self, item_data: ItemCreateSchema, current_user: UserSchema) -> ItemModel:
        # Business logic before creating the item
        # For example, check if an item with the same name already exists
        existing_item = await self.repository.find_by_name(item_data.name)
        if existing_item:
            raise HTTPException(status_code=400, detail="Item with this name already exists")

        item_dict = item_data.model_dump()
        item_dict['owner_id'] = current_user.id # Example of setting the owner
        return await self.repository.create(item_dict)

    async def get_item_by_id(self, item_id: UUID, current_user: UserSchema) -> ItemModel:
        item = await self.repository.find_by_id(item_id)
        if not item:
            raise NotFoundException(f"Item with id {item_id} not found")
        # Business logic for authorization, for example:
        # if item.owner_id != current_user.id and not current_user.is_admin:
        #     raise HTTPException(status_code=403, detail="Not authorized to access this item")
        return item

    # Add other methods (update, delete, get_all, etc.)
```
*   Ensure to register the new service in `app/api/dependencies/factory.py`.

### 5. Creating an Endpoint (`app/api/v1/routes/`)

Endpoints are the HTTP entry points to your application. They are defined using FastAPI APIRouter.

Example (e.g., `app/api/v1/routes/item_route.py`):
```python
from typing import List
from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user # Authentication dependency
from app.api.dependencies.factory import Factory # Factory for service dependencies
from app.core.data_types import UUID7Field
from app.schemas.item_schema import ItemCreateSchema, ItemSchema, ItemUpdateSchema # Your schemas
from app.schemas.user_schema import UserSchema # User schema for auth dependency
from app.services.item_service import ItemService # Your service
from app.schemas.base import PaginatedResponse # If using pagination
from app.core.params import CommonParams # If using common parameters

router = APIRouter()

@router.post("/items", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_in: ItemCreateSchema,
    current_user: UserSchema = Depends(get_current_active_user),
    service: ItemService = Depends(Factory().get_item_service), # Get service from factory
):
    item = await service.create_item(item_data=item_in, current_user=current_user)
    return item

@router.get("/items/{item_id}", response_model=ItemSchema)
async def read_item(
    item_id: UUID7Field,
    current_user: UserSchema = Depends(get_current_active_user),
    service: ItemService = Depends(Factory().get_item_service),
):
    item = await service.get_item_by_id(item_id=item_id, current_user=current_user)
    return item

# Add other endpoints (GET all, PUT/PATCH, DELETE)
# Example GET all with pagination:
@router.get("/items", response_model=PaginatedResponse[ItemSchema])
async def get_items(
    params: CommonParams = Depends(),
    user_active: UserSchema = Depends(get_current_active_user),
    service: ItemService = Depends(Factory().get_item_service),
):
    # Assume your service has a find_all method similar to UserService
    items, total = await service.find_all(
        filters=params.filter,
        sort=params.sort,
        search=params.search,
        limit=params.limit,
        offset=params.offset,
        user=user_active, # For access control if needed
    )

    return PaginatedResponse(
        items=[ItemSchema.model_validate(item) for item in items],
        total=total,
        limit=params.limit,
        offset=params.offset,
        has_more=total > (offset + params.limit),
    )

```
*   Register the new router in `app/api/v1/__init__.py` or `app/main.py`.
    Example in `app/main.py`:
    ```python
    // ... existing code ...
    from app.api.v1.routes import item_route # Import your new router
    // ... existing code ...

    app.include_router(item_route.router, prefix="/api/v1", tags=["Items"])
    // ... existing code ...
    ```

## How to Deploy

This project is configured to be deployed using GitHub Actions when there is a push to the `main` branch or via manual trigger.

The deployment process defined in <mcfile path="/.github/workflows/deploy.yml" name="deploy.yml"></mcfile> is as follows:

1.  **Checkout Code**: The code from the repository is fetched.
2.  **Set up Docker Buildx**: Prepares the environment for building Docker images.
3.  **Build and Export Docker image**: The Docker image `portal-satu-peta-backend:latest` is built and exported as a `.tar` file.
    *   Uses cache from GitHub Actions (GHA) to speed up the build process.
4.  **Copy Docker image to server via SCP**: The `portal-satu-peta-backend.tar` file is copied to the target server (defined by secrets `SSH_HOST`, `SSH_USER`, `SSH_PORT`, `SSH_PASSWORD`).
5.  **Deploy container**: An SSH script is executed on the target server:
    *   **Load image**: The Docker image from the `.tar` file is loaded into Docker on the server.
    *   **Stop and Remove Old Container**: The old container named `portal-satu-peta-backend` is stopped and removed (if it exists).
    *   **Run New Container**: A new container is run from the newly loaded image:
        *   Container name: `portal-satu-peta-backend`
        *   Restart policy: `unless-stopped`
        *   Environment file: `/home/application/.env` (ensure this file exists and is configured on the server)
        *   Port mapping: `5000:5000` (host port 5000 to container port 5000)
        *   Health check configuration.
    *   **Run Migrations**: The command `docker exec portal-satu-peta-backend python migrations/scripts.py` is executed inside the newly running container to perform database migrations.
    *   **Prune Old Images**: Old, unused Docker images (older than 24 hours) are removed to save disk space.
    *   **Clean Up**: The copied `.tar` file is removed from the server.
    *   **Verify Status**: The status of the `portal-satu-peta-backend` container is verified.

### Server Requirements for Deployment:

*   Linux server with SSH access.
*   Docker installed on the server.
*   An environment file (e.g., `/home/application/.env`) must exist on the server and contain the correct configurations for production (database, secret keys, etc.).
*   The SSH user used must have permissions to run Docker commands and access the necessary paths.

### GitHub Secrets Configuration:

Ensure the following secrets are configured in your GitHub repository (Settings > Secrets and variables > Actions):

*   `SSH_HOST`: IP address or hostname of the deployment server.
*   `SSH_USER`: Username for SSH login to the server.
*   `SSH_PORT`: SSH server port (usually 22).
*   `SSH_PASSWORD`: Password for the SSH user. (Using SSH keys is highly recommended for security).
