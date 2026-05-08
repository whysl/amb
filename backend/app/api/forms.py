from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from app.database import get_db
from app.models.models import FormData, FormItem, Subject, Period, Department, User
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/forms", tags=["填报表单"])


class FormItemInput(BaseModel):
    subject_id: int
    value: float | None = None
    remark: str | None = None


class SaveFormRequest(BaseModel):
    period_id: int
    items: list[FormItemInput]


class ReviewRequest(BaseModel):
    action: str
    comment: str | None = None


def form_to_dict(form: FormData):
    items = []
    for item in form.items:
        items.append({
            "id": item.id,
            "subject_id": item.subject_id,
            "subject_code": item.subject.code if item.subject else "",
            "subject_name": item.subject.name if item.subject else "",
            "category": item.subject.category if item.subject else "",
            "is_calculated": item.subject.is_calculated if item.subject else False,
            "formula": item.subject.formula if item.subject else None,
            "unit": item.subject.unit if item.subject else "元",
            "value": item.value,
            "remark": item.remark,
        })

    dept_code = form.department.code if form.department else None
    dept_name = form.department.name if form.department else None

    return {
        "id": form.id,
        "period_id": form.period_id,
        "period_year": form.period.year if form.period else None,
        "period_month": form.period.month if form.period else None,
        "period_type": form.period.period_type if form.period else None,
        "department_id": form.department_id,
        "dept_code": dept_code,
        "dept_name": dept_name,
        "status": form.status,
        "filled_by": form.filled_by,
        "filler_name": form.filler.real_name if form.filler else None,
        "dept_reviewed_by": form.dept_reviewed_by,
        "dept_reviewer_name": form.dept_reviewer.real_name if form.dept_reviewer else None,
        "company_reviewed_by": form.company_reviewed_by,
        "company_reviewer_name": form.company_reviewer.real_name if form.company_reviewer else None,
        "dept_review_comment": form.dept_review_comment,
        "company_review_comment": form.company_review_comment,
        "created_at": form.created_at.isoformat() if form.created_at else None,
        "updated_at": form.updated_at.isoformat() if form.updated_at else None,
        "items": items,
    }


@router.get("/my")
def list_my_forms(
    year: int | None = Query(None),
    month: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role("dept_filler", "dept_reviewer", "company_reviewer", "super_admin")),
):
    query = db.query(FormData).options(
        joinedload(FormData.period), joinedload(FormData.department),
        joinedload(FormData.filler), joinedload(FormData.items).joinedload(FormItem.subject)
    )

    if current_user.role in ("dept_filler", "dept_reviewer"):
        query = query.filter(FormData.department_id == current_user.department_id)
    elif current_user.role == "super_admin":
        pass
    else:
        query = query.filter(FormData.filled_by == current_user.id)

    if year:
        query = query.join(FormData.period).filter(Period.year == year)
    if month:
        query = query.join(FormData.period).filter(Period.month == month)

    query = query.order_by(FormData.updated_at.desc())
    forms = query.all()
    return [form_to_dict(f) for f in forms]


@router.get("/{form_id}")
def get_form(form_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    form = (
        db.query(FormData)
        .options(
            joinedload(FormData.period),
            joinedload(FormData.department),
            joinedload(FormData.filler),
            joinedload(FormData.dept_reviewer),
            joinedload(FormData.company_reviewer),
            joinedload(FormData.items).joinedload(FormItem.subject),
        )
        .filter(FormData.id == form_id)
        .first()
    )
    if not form:
        raise HTTPException(status_code=404, detail="表单不存在")

    if current_user.role in ("dept_filler", "dept_reviewer"):
        if form.department_id != current_user.department_id:
            raise HTTPException(status_code=403, detail="无权查看其他部门的表单")

    return form_to_dict(form)


@router.post("")
def save_form(
    req: SaveFormRequest,
    db: Session = Depends(get_db),
    dept_id: int | None = Query(None),
    current_user=Depends(require_role("dept_filler", "dept_reviewer", "company_reviewer", "super_admin")),
):
    period = db.query(Period).filter(Period.id == req.period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="周期不存在")

    actual_dept_id = dept_id if (current_user.role == "super_admin" and dept_id) else current_user.department_id
    if not actual_dept_id:
        raise HTTPException(status_code=400, detail="未分配部门")

    dept = db.query(Department).filter(Department.id == actual_dept_id).first()
    if not dept:
        raise HTTPException(status_code=400, detail="部门不存在")

    existing = (
        db.query(FormData)
        .filter(
            FormData.period_id == req.period_id,
            FormData.department_id == actual_dept_id,
        )
        .first()
    )

    if existing:
        if existing.status in ("company_approved", "submitted", "dept_approved"):
            raise HTTPException(status_code=400, detail="该表单已提交或已审核，无法修改")
        form = existing
        form.status = "draft"
        db.query(FormItem).filter(FormItem.form_id == form.id).delete()
    else:
        form = FormData(period_id=req.period_id, department_id=actual_dept_id, filled_by=current_user.id, status="draft")
        db.add(form)
        db.flush()

    for item_input in req.items:
        item = FormItem(form_id=form.id, subject_id=item_input.subject_id, value=item_input.value, remark=item_input.remark)
        db.add(item)

    db.commit()
    db.refresh(form)
    return {"message": "保存成功", "form_id": form.id}


@router.put("/{form_id}/submit")
def submit_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("dept_filler", "dept_reviewer", "company_reviewer", "super_admin")),
):
    form = db.query(FormData).filter(FormData.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="表单不存在")
    if current_user.role in ("dept_filler", "dept_reviewer"):
        if form.department_id != current_user.department_id:
            raise HTTPException(status_code=403, detail="无权操作")
    if form.status not in ("draft", "dept_rejected"):
        raise HTTPException(status_code=400, detail="当前状态不可提交")
    form.status = "submitted"
    form.filled_by = current_user.id
    db.commit()
    return {"message": "提交成功"}


@router.get("/pending/dept")
def pending_dept(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("dept_reviewer", "company_reviewer", "super_admin")),
):
    query = (
        db.query(FormData)
        .options(
            joinedload(FormData.period),
            joinedload(FormData.department),
            joinedload(FormData.filler),
            joinedload(FormData.items).joinedload(FormItem.subject),
        )
        .filter(FormData.status == "submitted")
    )
    if current_user.role == "dept_reviewer":
        query = query.filter(FormData.department_id == current_user.department_id)

    forms = query.order_by(FormData.updated_at.desc()).all()
    return [form_to_dict(f) for f in forms]


@router.put("/{form_id}/dept-review")
def dept_review(
    form_id: int,
    req: ReviewRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("dept_reviewer", "company_reviewer", "super_admin")),
):
    form = db.query(FormData).filter(FormData.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="表单不存在")
    if current_user.role == "dept_reviewer":
        if form.department_id != current_user.department_id:
            raise HTTPException(status_code=403, detail="无权操作本部门以外的表单")
    if form.status != "submitted":
        raise HTTPException(status_code=400, detail="当前状态不可进行部门审核")

    if req.action == "approve":
        form.status = "dept_approved"
    elif req.action == "reject":
        form.status = "dept_rejected"
        form.dept_review_comment = req.comment
    else:
        raise HTTPException(status_code=400, detail="无效的审核操作")

    form.dept_reviewed_by = current_user.id
    if req.comment and req.action == "approve":
        form.dept_review_comment = req.comment
    db.commit()
    return {"message": "审核完成"}


@router.get("/pending/company")
def pending_company(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("company_reviewer", "super_admin")),
):
    forms = (
        db.query(FormData)
        .options(
            joinedload(FormData.period),
            joinedload(FormData.department),
            joinedload(FormData.filler),
            joinedload(FormData.items).joinedload(FormItem.subject),
        )
        .filter(FormData.status == "dept_approved")
        .order_by(FormData.updated_at.desc())
        .all()
    )
    return [form_to_dict(f) for f in forms]


@router.put("/{form_id}/company-review")
def company_review(
    form_id: int,
    req: ReviewRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("company_reviewer", "super_admin")),
):
    form = db.query(FormData).filter(FormData.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="表单不存在")
    if form.status != "dept_approved":
        raise HTTPException(status_code=400, detail="当前状态不可进行公司审核")

    if req.action == "approve":
        form.status = "company_approved"
    elif req.action == "reject":
        form.status = "company_rejected"
        form.company_review_comment = req.comment
    else:
        raise HTTPException(status_code=400, detail="无效的审核操作")

    form.company_reviewed_by = current_user.id
    if req.comment and req.action == "approve":
        form.company_review_comment = req.comment
    db.commit()
    return {"message": "审核完成"}


@router.get("/by-period/{period_id}")
def list_forms_by_period(
    period_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("super_admin")),
):
    forms = (
        db.query(FormData)
        .options(
            joinedload(FormData.period),
            joinedload(FormData.department),
            joinedload(FormData.filler),
            joinedload(FormData.items).joinedload(FormItem.subject),
        )
        .filter(FormData.period_id == period_id)
        .order_by(FormData.updated_at.desc())
        .all()
    )
    return [form_to_dict(f) for f in forms]


@router.delete("/{form_id}/force")
def force_delete_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("super_admin")),
):
    form = db.query(FormData).filter(FormData.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="表单不存在")
    db.query(FormItem).filter(FormItem.form_id == form_id).delete()
    db.delete(form)
    db.commit()
    return {"message": "表单已彻底删除"}
