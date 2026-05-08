from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Department, Subject
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/org", tags=["组织架构"])


@router.get("/departments")
def list_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).order_by(Department.sort_order, Department.id).all()
    result = []
    for d in depts:
        result.append({
            "id": d.id,
            "code": d.code,
            "name": d.name,
            "parent_id": d.parent_id,
            "level": d.level,
            "sort_order": d.sort_order,
            "is_active": d.is_active,
        })
    return result


@router.get("/departments/{dept_id}/subjects")
def get_dept_subjects(dept_id: int, db: Session = Depends(get_db)):
    subjects = (
        db.query(Subject)
        .filter(Subject.department_id == dept_id)
        .order_by(Subject.sort_order, Subject.id)
        .all()
    )
    if not subjects:
        raise HTTPException(status_code=404, detail="该部门无科目配置")
    return [
        {
            "id": s.id,
            "code": s.code,
            "name": s.name,
            "category": s.category,
            "formula": s.formula,
            "is_calculated": s.is_calculated,
            "is_required": s.is_required,
            "sort_order": s.sort_order,
            "unit": s.unit,
        }
        for s in subjects
    ]


@router.get("/my-department/subjects")
def get_my_dept_subjects(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.department_id:
        raise HTTPException(status_code=400, detail="未分配部门")
    return get_dept_subjects(current_user.department_id, db)
