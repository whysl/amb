from sqlalchemy.orm import Session
from app.models.models import FormData, FormItem, Subject, Period, Department


def calc_dept_summary(db: Session, dept_codes: list[str], year: int, month: int, period_type: str):
    dept_ids = [d.id for d in db.query(Department).filter(Department.code.in_(dept_codes)).all()]
    if not dept_ids:
        return {}, []

    period = (
        db.query(Period)
        .filter(Period.year == year, Period.month == month, Period.period_type == period_type)
        .first()
    )
    if not period:
        return {}, []

    forms = (
        db.query(FormData)
        .filter(
            FormData.period_id == period.id,
            FormData.department_id.in_(dept_ids),
            FormData.status == "company_approved",
        )
        .all()
    )

    subjects = {}
    all_subjects = (
        db.query(Subject)
        .filter(Subject.department_id.in_(dept_ids))
        .order_by(Subject.sort_order)
        .all()
    )
    for s in all_subjects:
        if s.code not in subjects:
            subjects[s.code] = {"name": s.name, "category": s.category, "unit": s.unit, "is_calculated": s.is_calculated}

    result = {}
    for code in subjects:
        result[code] = 0.0

    for form in forms:
        for item in form.items:
            if item.subject and item.subject.code in result:
                if item.value is not None:
                    result[item.subject.code] += item.value

    subject_list = []
    ordered = sorted(subjects.items(), key=lambda x: all_subjects.index(next((s for s in all_subjects if s.code == x[0]), None)) if any(s.code == x[0] for s in all_subjects) else 9999)
    for code, info in ordered:
        subject_list.append({
            "code": code,
            "name": info["name"],
            "category": info["category"],
            "unit": info["unit"],
            "is_calculated": info["is_calculated"],
            "value": round(result.get(code, 0), 2),
        })

    return result, subject_list


def calc_rollup(db: Session, dept_code: str, year: int, period_type: str):
    dept_ids = [d.id for d in db.query(Department).filter(Department.code.in_([dept_code])).all()]
    if period_type == "all" or dept_code in ("company", "whgc"):
        if dept_code == "company":
            dept_ids = [d.id for d in db.query(Department).filter(Department.level.in_([2, 3])).all()]
        elif dept_code == "whgc":
            whgc_dept = db.query(Department).filter(Department.code == "whgc").first()
            if whgc_dept:
                dept_ids = [d.id for d in db.query(Department).filter(Department.parent_id == whgc_dept.id).all()]

    subjects = (
        db.query(Subject)
        .filter(Subject.department_id.in_(dept_ids))
        .order_by(Subject.sort_order)
        .all()
    )

    subject_map = {}
    for s in subjects:
        if s.code not in subject_map:
            subject_map[s.code] = {"name": s.name, "category": s.category, "unit": s.unit, "is_calculated": s.is_calculated}

    sorted_codes = []
    seen = set()
    for s in subjects:
        if s.code not in seen:
            sorted_codes.append(s.code)
            seen.add(s.code)

    monthly_data = []
    for month in range(1, 13):
        period = (
            db.query(Period)
            .filter(Period.year == year, Period.month == month, Period.period_type == period_type)
            .first()
        )
        month_values = {}
        if period:
            forms = (
                db.query(FormData)
                .filter(
                    FormData.period_id == period.id,
                    FormData.department_id.in_(dept_ids),
                    FormData.status == "company_approved",
                )
                .all()
            )
            for form in forms:
                for item in form.items:
                    if item.subject and item.value is not None:
                        code = item.subject.code
                        month_values[code] = month_values.get(code, 0) + item.value

        monthly_data.append({"month": month, "subjects": month_values})

    cumulative = {}
    result = []
    for md in monthly_data:
        for code, val in md["subjects"].items():
            cumulative[code] = cumulative.get(code, 0) + val
        result.append({
            "month": md["month"],
            "subjects": {k: round(v, 2) for k, v in md["subjects"].items()},
            "cumulative": {k: round(v, 2) for k, v in cumulative.items()},
        })

    return result, subject_map, sorted_codes
