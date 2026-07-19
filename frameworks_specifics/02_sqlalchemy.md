# SQLAlchemy 2.0 ORM Specification (Comprehensive Masterclass)

SQLAlchemy is Python's premier Object Relational Mapper (ORM). SQLAlchemy 2.0 introduces a modernized, type-safe API that enforces explicit select queries and native Python type annotations (`Mapped` and `mapped_column`).

---

## 1. Core Mechanics & Session Lifecycle (Why & What)

### The Session States
An ORM object exists in one of five states relative to the active `Session` (Unit of Work):

1. **Transient**: The object is created in memory but is not associated with any database session and has no database row.
   * *Example*: `user = User(name="John")` (No ID assigned).
2. **Pending**: The object has been added to the session using `session.add()`. It will be written to the database during the next flush.
   * *Example*: `session.add(user)`.
3. **Persistent**: The object is associated with a database row. A flush has occurred (or database read), mapping the database fields to properties.
   * *Example*: After `await session.flush()` or `await session.commit()`.
4. **Deleted**: The object has been marked for deletion inside the session via `session.delete(user)`, but has not yet been flushed.
5. **Detached**: The session has been closed or expired, but the Python object still exists. Accessing lazily-loaded relationships on a detached object throws a `DetachedInstanceError`.

```mermaid
stateDiagram-v2
    [*] --> Transient : New instance
    Transient --> Pending : session.add()
    Pending --> Persistent : session.flush() / commit()
    Persistent --> Detached : session.close() / expire
    Persistent --> Deleted : session.delete()
    Deleted --> Detached : session.commit()
    Detached --> Persistent : session.add() / merge()
```

### Async Mechanics
In async environments, SQLAlchemy delegates standard database operations to the `greenlet` library, wrapping synchronous drivers (like `asyncpg` for PostgreSQL or `aiosqlite` for SQLite). 
* **Rule**: You must use async equivalents for connection and transactions. Call `await session.execute()` instead of legacy `query()`.

---

## 2. Basic Mapping & Core CRUD Operations (How)

### Declaring Models with 2.0 Syntax
SQLAlchemy 2.0 uses PEP-484 typing annotations via `Mapped` and `mapped_column` to declare schema mappings.

```python
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # One-to-Many Relationship: Eager load raises error if lazy loading occurs
    employees: Mapped[List["Employee"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="raise"
    )

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))

    company: Mapped["Company"] = relationship(back_populates="employees")
```

### Basic CRUD Execution (Async API)
```python
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

# 1. Create (Insert)
async def create_company(session: AsyncSession, name: str) -> Company:
    new_company = Company(name=name)
    session.add(new_company)
    await session.commit()
    return new_company

# 2. Read (Select with joins and filters)
async def get_company_by_name(session: AsyncSession, target_name: str) -> Optional[Company]:
    stmt = select(Company).where(Company.name == target_name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

# 3. Update
async def update_company_name(session: AsyncSession, company_id: int, new_name: str):
    stmt = (
        update(Company)
        .where(Company.id == company_id)
        .values(name=new_name)
    )
    await session.execute(stmt)
    await session.commit()

# 4. Delete
async def delete_company(session: AsyncSession, company_id: int):
    stmt = delete(Company).where(Company.id == company_id)
    await session.execute(stmt)
    await session.commit()
```

---

## 3. Advanced Querying & Eager Loading (How)

### Eager Loading Strategies
When fetching parent objects that have relationships, you must tell SQLAlchemy how to load child records. Failing to load them correctly causes **N+1 query bottlenecks**.

| Strategy | Function | SQL Implementation | Use Case |
|---|---|---|---|
| **Joined Load** | `joinedload()` | Performs a SQL `LEFT OUTER JOIN` in the same query. | **Many-to-One** relationships (e.g. fetching employee + company details). |
| **Select In Load** | `selectinload()` | Emits a second SELECT query using an `IN` clause with parent IDs. | **One-to-Many** or **Many-to-Many** collections (e.g. fetching company + employee list). |
| **Subquery Load** | `subqueryload()` | Emits a second query duplicating the entire parent select as a subquery. | Deprecated for most use cases; slower than `selectinload`. |

### Gist: eager_loading_mastery.py
Demonstrates joined loads, selectin loads, aggregations, and transaction rollbacks.

```python
# Gist: eager_loading_mastery.py
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models import Company, Employee  # Assume models are imported

# 1. Setup Async Engine
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/dbname"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# 2. SELECTINLOAD Example (One-to-Many list fetching)
async def get_company_with_employees(session: AsyncSession, company_id: int) -> Company:
    # Emits exactly 2 queries:
    # 1. SELECT * FROM companies WHERE id = :id
    # 2. SELECT * FROM employees WHERE company_id IN (:id)
    stmt = (
        select(Company)
        .options(selectinload(Company.employees))
        .where(Company.id == company_id)
    )
    result = await session.execute(stmt)
    company = result.scalar_one()
    return company

# 3. JOINEDLOAD Example (Many-to-One mapping)
async def get_employee_with_company(session: AsyncSession, employee_id: int) -> Employee:
    # Emits exactly 1 query using a LEFT OUTER JOIN:
    # SELECT employees.*, companies.* FROM employees LEFT OUTER JOIN companies ...
    stmt = (
        select(Employee)
        .options(joinedload(Employee.company))
        .where(Employee.id == employee_id)
    )
    result = await session.execute(stmt)
    employee = result.scalar_one()
    return employee

# 4. Aggregations and Complex Queries
async def get_companies_with_employee_counts(session: AsyncSession):
    # Emits 1 query returning aggregated columns
    stmt = (
        select(
            Company.id,
            Company.name,
            func.count(Employee.id).label("employee_count")
        )
        .outerjoin(Employee, Company.id == Employee.company_id)
        .group_by(Company.id, Company.name)
        .having(func.count(Employee.id) > 5)
    )
    result = await session.execute(stmt)
    return result.all()
```
