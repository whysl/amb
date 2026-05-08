from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from app.database import get_db
from app.models.models import User
from app.utils.auth import create_access_token, get_current_user, require_role

router = APIRouter(prefix="/api/auth", tags=["认证"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateUserRequest(BaseModel):
    username: str
    password: str
    real_name: str
    role: str
    department_id: int | None = None
    phone: str | None = None


class UpdateUserRequest(BaseModel):
    username: str | None = None
    real_name: str | None = None
    role: str | None = None
    department_id: int | None = None
    phone: str | None = None
    is_active: bool | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str | None = None
    new_password: str


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户已被禁用")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "user_info": {
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "role": user.role,
            "department_id": user.department_id,
            "phone": user.phone,
        },
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    dept_code = None
    dept_name = None
    if current_user.department:
        dept_code = current_user.department.code
        dept_name = current_user.department.name

    return {
        "id": current_user.id,
        "username": current_user.username,
        "real_name": current_user.real_name,
        "role": current_user.role,
        "department_id": current_user.department_id,
        "dept_code": dept_code,
        "dept_name": dept_name,
        "phone": current_user.phone,
    }


@router.put("/me/password")
def change_my_password(req: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.old_password and not pwd_context.verify(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
    current_user.password_hash = pwd_context.hash(req.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.get("/users")
def list_users(
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.id).all()
    result = []
    for u in users:
        dept_code = u.department.code if u.department else None
        dept_name = u.department.name if u.department else None
        result.append({
            "id": u.id,
            "username": u.username,
            "real_name": u.real_name,
            "role": u.role,
            "department_id": u.department_id,
            "dept_code": dept_code,
            "dept_name": dept_name,
            "phone": u.phone,
            "is_active": u.is_active,
        })
    return result


@router.post("/users")
def create_user(
    req: CreateUserRequest,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    if req.role not in ("dept_filler", "dept_reviewer", "company_reviewer", "super_admin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的角色")

    user = User(
        username=req.username,
        password_hash=pwd_context.hash(req.password),
        real_name=req.real_name,
        role=req.role,
        department_id=req.department_id,
        phone=req.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "用户创建成功", "user_id": user.id}


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    req: UpdateUserRequest,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    if req.username is not None:
        existing = db.query(User).filter(User.username == req.username, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
        user.username = req.username
    if req.real_name is not None:
        user.real_name = req.real_name
    if req.role is not None:
        if req.role not in ("dept_filler", "dept_reviewer", "company_reviewer", "super_admin"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的角色")
        user.role = req.role
    if req.department_id is not None:
        user.department_id = req.department_id
    if req.phone is not None:
        user.phone = req.phone
    if req.is_active is not None:
        user.is_active = req.is_active

    db.commit()
    return {"message": "用户修改成功"}


@router.put("/users/{user_id}/password")
def reset_user_password(
    user_id: int,
    req: ChangePasswordRequest,
    current_user: User = Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    user.password_hash = pwd_context.hash(req.new_password)
    db.commit()
    return {"message": "密码重置成功"}
