from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.summary import calc_dept_summary, calc_rollup
from app.utils.auth import require_role, get_current_user

router = APIRouter(prefix="/api/summary", tags=["汇总报表"])


@router.get("/whgc")
def whgc_summary(
    year: int = Query(...),
    month: int = Query(...),
    period_type: str = Query("actual"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role("company_reviewer", "super_admin")),
):
    from app.models.models import Department

    whgc = db.query(Department).filter(Department.code == "whgc").first()
    if not whgc:
        return {"subjects": [], "message": "威高广场部门不存在"}

    child_dept_codes = [d.code for d in db.query(Department).filter(Department.parent_id == whgc.id).all()]
    _, subject_list = calc_dept_summary(db, child_dept_codes, year, month, period_type)
    return {"period": f"{year}年{month}月", "period_type": period_type, "subjects": subject_list}


@router.get("/company")
def company_summary(
    year: int = Query(...),
    month: int = Query(...),
    period_type: str = Query("actual"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role("company_reviewer", "super_admin")),
):
    from app.models.models import Department

    dept_codes = [d.code for d in db.query(Department).filter(Department.level.in_([2, 3]), Department.code != "company").all()]
    _, subject_list = calc_dept_summary(db, dept_codes, year, month, period_type)
    return {"period": f"{year}年{month}月", "period_type": period_type, "subjects": subject_list}


@router.get("/rollup")
def rollup(
    dept_code: str = Query(...),
    year: int = Query(...),
    period_type: str = Query("actual"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role in ("dept_filler", "dept_reviewer"):
        if dept_code != current_user.department.code:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="无权查看其他部门的数据")
    elif current_user.role == "company_reviewer":
        pass

    data, subject_map, sorted_codes = calc_rollup(db, dept_code, year, period_type)
    return {
        "dept_code": dept_code,
        "year": year,
        "period_type": period_type,
        "subjects": {k: v for k, v in subject_map.items() if k in sorted_codes},
        "subject_order": sorted_codes,
        "data": data,
    }


@router.get("/rollup-compare")
def rollup_compare(
    dept_code: str = Query(...),
    year: int = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role in ("dept_filler", "dept_reviewer"):
        if dept_code != current_user.department.code:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="无权查看其他部门的数据")

    budget_data, subject_map, sorted_codes = calc_rollup(db, dept_code, year, "budget")
    planned_data, _, _ = calc_rollup(db, dept_code, year, "planned")
    actual_data, _, _ = calc_rollup(db, dept_code, year, "actual")

    return {
        "dept_code": dept_code,
        "year": year,
        "subjects": {k: v for k, v in subject_map.items() if k in sorted_codes},
        "subject_order": sorted_codes,
        "budget": budget_data,
        "planned": planned_data,
        "actual": actual_data,
    }


@router.get("/dept-subjects")
def dept_subjects(
    dept_code: str = Query(...),
    db: Session = Depends(get_db),
):
    from app.models.models import Department, Subject

    dept_ids = [Department.id]
    if dept_code == "company":
        dept_ids = [d.id for d in db.query(Department).filter(Department.level.in_([2, 3])).all()]
    elif dept_code == "whgc":
        whgc = db.query(Department).filter(Department.code == "whgc").first()
        if whgc:
            dept_ids = [d.id for d in db.query(Department).filter(Department.parent_id == whgc.id).all()]

    subjects = (
        db.query(Subject)
        .filter(Subject.department_id.in_(dept_ids))
        .order_by(Subject.sort_order)
        .all()
    )

    seen = set()
    result = []
    for s in subjects:
        if s.code not in seen:
            seen.add(s.code)
            result.append({
                "code": s.code,
                "name": s.name,
                "category": s.category,
                "unit": s.unit,
                "is_calculated": s.is_calculated,
            })
    return result
