from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentListResponse
from app.schemas.api_key import ApiKeyCreate, ApiKeyListResponse, ApiKey
from app.crud import department as crud_department
from app.crud import api_key as crud_api_key

router = APIRouter()

@router.get("/api/system/dept/list", response_model=DepartmentListResponse)
async def get_department_list(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    departments = await crud_department.get_departments(db)
    return DepartmentListResponse(code=0, data=departments, message="ok")

@router.post("/api/system/dept", status_code=200)
async def create_department(department: DepartmentCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await crud_department.create_department(db, department=department)
    return {"code": 0, "message": "ok"}

@router.get("/api/system/exchanges", response_model=ApiKeyListResponse)
async def get_api_key_list(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    api_keys = await crud_api_key.get_api_keys(db)
    return ApiKeyListResponse(code=0, data=api_keys, message="ok")

@router.post("/api/system/exchanges", status_code=200)
async def create_api_key(api_key: ApiKeyCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await crud_api_key.create_api_key(db, api_key=api_key)
    return {"code": 0, "message": "ok"}

@router.put("/api/system/exchanges/{id}", status_code=200)
async def update_api_key(id: int, api_key: ApiKeyCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_api_key = await crud_api_key.get_api_key(db, id=id)
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API Key not found")
    await crud_api_key.update_api_key(db, db_obj=db_api_key, obj_in=api_key)
    return {"code": 0, "message": "ok"}

@router.delete("/api/system/exchanges/{id}", status_code=200)
async def delete_api_key(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await crud_api_key.delete_api_key(db, id=id)
    return {"code": 0, "message": "ok"}