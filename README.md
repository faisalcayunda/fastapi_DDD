# ARCHITECTURE — Modular Monolith by Feature (DDD-friendly)

> This project uses a **Modular Monolith by Feature (Vertical Slice)**. Each feature encapsulates its own domain (`entities`), application logic (`use_cases`), adapters (repositories/presenters), and API layer (routers/schemas). Frameworks (FastAPI), persistence (SQLAlchemy), and configuration live at the **platform edge**.

---

## 1. Core Principles

- **Feature-first packaging**: `features/<context>` keeps code cohesive and extractable later.
- **Dependency rule** (inward only):
  `api → use_cases → entities` and `use_cases → (ports) → adapters`.
  Domain (entities) **never imports** FastAPI/SQLAlchemy/Pydantic.
- **Pure domain**: Entities/VOs are plain Python; persistence & transport concerns are adapters.
- **Testability**: Unit test the domain + use cases with fakes; integration tests cover adapters; API tests use `TestClient`.

---

## 2. Directory Layout

```
app/
  features/
    <feature>/
      entities/            # Domain (Entities/Value Objects) — pure Python
      use_cases/           # Application orchestrations per scenario (CreateX/ListY)
        ports.py           # Protocol interfaces (Repo/Presenter/etc)
      adapters/            # Infrastructure adapters for this feature
        repositories/      # SQLAlchemy/HTTP/etc implementing ports
        presenters/        # Entity → DTO/response mapper
      api/                 # FastAPI routers & feature-specific dependencies
        routes.py
        schemas.py         # Pydantic models (only here)
  platform/
    fastapi/
      app.py               # create_app(), include feature routers
      dependencies.py      # global DI: session, id_gen, event bus, etc.
    db/
      engine.py            # engine/session factory
      models.py            # (optional) ORM models; or split per feature
    config.py              # Pydantic BaseSettings (.env)
  shared/                  # Small cross-cutting helpers (Result/Errors), keep tiny!
main.py                    # uvicorn entry: from app.platform.fastapi.app import create_app
```

**Absolute imports** recommended: `from app.features.users.entities.user import User`.

---

## 3. Data Flow

1. **HTTP request** hits `api/routes.py` (FastAPI).
2. Router **builds a use case** with DI: `repo`, `presenter`, `id_gen`, etc.
3. **Use case** executes business flows on **entities**, calls **repo (ports)**.
4. **Repo adapter** uses ORM to persist/fetch rows and maps them ↔ **entities**.
5. **Presenter** returns DTO/dict/Pydantic for HTTP response.

```
HTTP (Pydantic) → API → UseCase → Entities ↔ Repo(ORM) → Presenter → HTTP (Pydantic)
```

---

## 4. Entities vs ORM vs Pydantic

- **Entities (domain)**: no FastAPI/SQLAlchemy/Pydantic.
- **ORM models**: in `platform/db/models.py` (or per-feature under adapters). Never imported by entities/use_cases.
- **Pydantic schemas**: in `api/schemas.py` only; never imported by entities/use_cases.

**Why** domain w/o ORM/Pydantic?
- Fast, deterministic unit tests.
- Low coupling; infrastructure can change without touching business logic.
- Clear boundaries prevent “big ball of mud”.

---

## 5. Minimal Templates

### 5.1 Entity (Domain)
```python
# app/features/users/entities/user.py
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
  id: str
  name: str
  email: str
```

### 5.2 Ports (Use Case Interfaces)
```python
# app/features/users/use_cases/ports.py
from typing import Protocol, Optional, Iterable
from app.features.users.entities.user import User

class UserRepo(Protocol):
    def by_id(self, user_id: str) -> Optional[User]: ...
    def by_email(self, email: str) -> Optional[User]: ...
    def list(self) -> Iterable[User]: ...
    def save(self, u: User) -> User: ...

class UserPresenter(Protocol):
    def present(self, u: User) -> dict: ...
    def present_many(self, items: Iterable[User]) -> list[dict]: ...
```

### 5.3 Use Case (Application)
```python
# app/features/users/use_cases/create_user.py
from app.features.users.entities.user import User
from .ports import UserRepo, UserPresenter

class CreateUser:
    def __init__(self, repo: UserRepo, presenter: UserPresenter, id_gen):
        self.repo = repo; self.presenter = presenter; self.id_gen = id_gen

    def execute(self, name: str, email: str) -> dict:
        if self.repo.by_email(email):
            raise ValueError("Email exists")
        u = User(id=self.id_gen(), name=name, email=email)
        saved = self.repo.save(u)
        return self.presenter.present(saved)
```

### 5.4 ORM Model (Infrastructure)
```python
# app/platform/db/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String

class Base(DeclarativeBase): pass

class SAUser(Base):
    __tablename__ = "users"
    id: Mapped[str]    = mapped_column(String, primary_key=True)
    name: Mapped[str]  = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True)
```

### 5.5 Mapper (Infrastructure Adapter)
```python
# app/features/users/adapters/repositories/mappers.py
from app.features.users.entities.user import User
from app.platform.db.models import SAUser

def to_entity(row: SAUser) -> User:
    return User(id=row.id, name=row.name, email=row.email)

def to_row(entity: User) -> SAUser:
    return SAUser(id=entity.id, name=entity.name, email=entity.email)
```

### 5.6 Repository (Infrastructure Adapter)
```python
# app/features/users/adapters/repositories/user_repo_sqlalchemy.py
from sqlalchemy.orm import Session
from sqlalchemy import select
from .mappers import to_entity, to_row
from app.platform.db.models import SAUser
from app.features.users.use_cases.ports import UserRepo
from app.features.users.entities.user import User

class SAUserRepo(UserRepo):
    def __init__(self, session: Session): self.s = session

    def by_id(self, user_id: str):
        row = self.s.get(SAUser, user_id)
        return to_entity(row) if row else None

    def by_email(self, email: str):
        row = self.s.execute(select(SAUser).where(SAUser.email == email)).scalar_one_or_none()
        return to_entity(row) if row else None

    def list(self):
        for row in self.s.execute(select(SAUser)).scalars():
            yield to_entity(row)

    def save(self, u: User) -> User:
        self.s.merge(to_row(u))
        self.s.flush()
        row = self.s.get(SAUser, u.id)
        return to_entity(row)
```

### 5.7 Pydantic Schemas (Interface)
```python
# app/features/users/api/schemas.py
from pydantic import BaseModel, EmailStr

class CreateUserIn(BaseModel):
    name: str
    email: EmailStr

class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
```

### 5.8 Presenter (Interface Adapter)
```python
# app/features/users/adapters/presenters/user_presenter.py
from app.features.users.entities.user import User
from app.features.users.api.schemas import UserOut

class UserPresenter:
    def present(self, u: User) -> dict:
        return UserOut(id=u.id, name=u.name, email=u.email).model_dump()

    def present_many(self, items):
        return [self.present(i) for i in items]
```

### 5.9 Router (Interface)
```python
# app/features/users/api/routes.py
from fastapi import APIRouter, Depends
from .schemas import CreateUserIn, UserOut
from app.platform.fastapi.dependencies import get_user_repo, get_id_gen
from app.features.users.use_cases.create_user import CreateUser
from app.features.users.adapters.presenters.user_presenter import UserPresenter

router = APIRouter()

@router.post("/users", response_model=UserOut)
def create_user(payload: CreateUserIn,
                repo = Depends(get_user_repo),
                id_gen = Depends(get_id_gen)):
    uc = CreateUser(repo=repo, presenter=UserPresenter(), id_gen=id_gen)
    return uc.execute(name=payload.name, email=payload.email)
```

---

## 6. Platform Wiring

### 6.1 FastAPI App
```python
# app/platform/fastapi/app.py
from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI()
    # Import and include routers per feature
    from app.features.users.api.routes import router as users_router
    app.include_router(users_router, prefix="/users", tags=["users"])
    return app
```

**Entry point**: `main.py`
```python
from app.platform.fastapi.app import create_app
app = create_app()
```

### 6.2 Dependencies
```python
# app/platform/fastapi/dependencies.py
from functools import lru_cache
from fastapi import Depends
from app.platform.db.engine import session_factory
from app.features.users.adapters.repositories.user_repo_sqlalchemy import SAUserRepo

def get_session():
    with session_factory() as s:
        yield s

def get_user_repo(s = Depends(get_session)):
    return SAUserRepo(session=s)

@lru_cache
def get_id_gen():
    import uuid
    return lambda: uuid.uuid4().hex
```

### 6.3 Database & Config
```python
# app/platform/db/engine.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.platform.config import Settings

settings = Settings()
_engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)

def session_factory():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# app/platform/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str = "change-me"
    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

## 7. Testing Strategy

- **Unit (fast)**: domain & use cases with **fakes** (no FastAPI/ORM).
- **Integration**: repositories against test DB (transaction rollback).
- **API/E2E**: `TestClient(app)`; override DI for test isolation.

Example unit test:

```python
# tests/unit/features/users/test_create_user.py
from app.features.users.use_cases.create_user import CreateUser
from app.features.users.entities.user import User

class FakeRepo:
    def __init__(self): self._emails=set()
    def by_email(self, email): return None if email not in self._emails else User("1","dup",email)
    def list(self): return []
    def save(self, u: User): return u

class FakePresenter:
    def present(self, u: User): return u.__dict__
    def present_many(self, items): return [i.__dict__ for i in items]

def test_create_user_ok():
    uc = CreateUser(repo=FakeRepo(), presenter=FakePresenter(), id_gen=lambda: "X")
    out = uc.execute(name="Faisal", email="f@x.com")
    assert out["id"] == "X"
```

---

## 8. Add a New Feature (Checklist)

1. `mkdir -p app/features/<feature>/{entities,use_cases,adapters/repositories,adapters/presenters,api}`
2. Add **entities** (domain).
3. Define **ports** + **use cases**.
4. Implement **repo adapter** + **mappers**; add **presenter**.
5. Create **schemas** + **routes**.
6. Register router in `create_app()` (or rely on auto-include pattern if implemented).
7. Write **unit tests** first; then integration tests for repo.

---

## 9. Guardrails

- Enforce imports with `import-linter` (optional but recommended):
  ```ini
  [importlinter]
  root_package=app

  [contract:vertical_slices]
  name=Vertical Slice Boundaries
  type=layers
  layers=app.features.*.api; app.features.*.use_cases; app.features.*.entities
  containers=app.features.*
  ```
- Keep `shared/` tiny to avoid a “god module”.
- Never raise `HTTPException` in use cases; map errors in API layer.

---

## 10. FAQ / Trade-offs

- **“Kenapa pisahkan entity dari ORM/Pydantic?”** → Test cepat, coupling rendah, batas jelas untuk evolusi.
- **“Terlalu banyak file?”** → Betul di awal. Balasnya: maintainability & reusability tinggi; mudah dipecah ke service terpisah nanti.
- **“Bisa langsung pakai ORM sebagai entity?”** → Untuk CRUD simpel, bisa pragmatis. Tapi set mappers dari hari pertama agar migrasi ke domain murni mudah saat kompleksitas tumbuh.
- **“DI bikin lambat?”** → Overhead Python-level kecil; bottleneck nyata biasanya di IO/DB. Boundary ini justru memudahkan caching/batching.

---

## 11. Quickstart

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# visit http://127.0.0.1:8000/docs
```

> If an import error appears after refactor, check your new module path and keep the dependency rule intact.
