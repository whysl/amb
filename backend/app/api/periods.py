from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Period, FormData
from app.utils.auth import require_role, get_current_user

router = APIRouter(prefix="/api/periods", tags=["填报周期"])


@router.get("")
def list_periods(db: Session = Depends(get_db)):
    periods = db.query(Period).order_by(Period.year.desc(), Period.month.desc(), Period.period_type).all()
    result = []
    for p in periods:
        form_count = db.query(FormData).filter(FormData.period_id == p.id).count()
        result.append({
            "id": p.id,
            "year": p.year,
            "month": p.month,
            "period_type": p.period_type,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "form_count": form_count,
        })
    return result


@router.delete("/{period_id}")
def delete_period(
    period_id: int,
    current_user=Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="周期不存在")

    form_count = db.query(FormData).filter(FormData.period_id == period_id).count()
    if form_count > 0:
        raise HTTPException(status_code=400, detail=f"该周期下有 {form_count} 条填报数据，无法删除")

    db.delete(period)
    db.commit()
    return {"message": "删除成功"}


@router.post("/create-monthly")
def create_monthly(
    year: int = Query(...),
    month: int = Query(...),
    current_user=Depends(require_role("super_admin")),
    db: Session = Depends(get_db),
):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="月份必须在1-12之间")

    planned_month = month + 1
    planned_year = year
    if planned_month > 12:
        planned_month = 1
        planned_year = year + 1

    target_periods = [
        ("actual", month, year),
        ("planned", planned_month, planned_year),
    ]

    has_data = False
    for pt, m, y in target_periods:
        p = db.query(Period).filter(
            Period.year == y, Period.month == m, Period.period_type == pt
        ).first()
        if p:
            fc = db.query(FormData).filter(FormData.period_id == p.id).count()
            if fc > 0:
                has_data = True

    if has_data:
        raise HTTPException(
            status_code=400,
            detail=f"{year}年{month}月相关周期下已有填报数据，无法重复创建。如需重建请先清空数据后删除旧周期。"
        )

    for pt, m, y in target_periods:
        p = db.query(Period).filter(
            Period.year == y, Period.month == m, Period.period_type == pt
        ).first()
        if p:
            db.delete(p)

    periods = []
    for pt, m, y in target_periods:
        p = Period(year=y, month=m, period_type=pt, status="open")
        db.add(p)
        periods.append({"type": pt, "year": y, "month": m})

    db.commit()
    return {"message": f"创建成功，共创建{len(periods)}条周期记录", "periods": periods}
