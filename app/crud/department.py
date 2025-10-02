from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.department import Department
from app.schemas.department import DepartmentCreate

async def get_departments(db: AsyncSession):
    result = await db.execute(select(Department))
    return result.scalars().all()

async def create_department(db: AsyncSession, department: DepartmentCreate):
    db_department = Department(**department.dict())
    db.add(db_department)
    await db.commit()
    await db.refresh(db_department)
    return db_department