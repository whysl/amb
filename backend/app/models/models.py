from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, Enum, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    level = Column(Integer, nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    parent = relationship("Department", remote_side=[id], backref="children")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50), nullable=False)
    role = Column(
        Enum("dept_filler", "dept_reviewer", "company_reviewer", "super_admin", name="user_role"),
        nullable=False
    )
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)

    department = relationship("Department", backref="users")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    formula = Column(String(200), nullable=True)
    is_calculated = Column(Boolean, default=False)
    is_required = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    unit = Column(String(20), default="元")

    department = relationship("Department", backref="subjects")


class Period(Base):
    __tablename__ = "periods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    period_type = Column(
        Enum("actual", "planned", "budget", name="period_type"),
        nullable=False
    )
    status = Column(
        Enum("open", "closed", name="period_status"),
        default="open"
    )
    created_at = Column(DateTime, default=datetime.utcnow)


class FormData(Base):
    __tablename__ = "form_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    status = Column(
        Enum("draft", "submitted", "dept_approved", "dept_rejected",
             "company_approved", "company_rejected", name="form_status"),
        default="draft"
    )
    filled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    dept_reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    company_reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    dept_review_comment = Column(Text, nullable=True)
    company_review_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    period = relationship("Period", backref="forms")
    department = relationship("Department", backref="forms")
    filler = relationship("User", foreign_keys=[filled_by], backref="filled_forms")
    dept_reviewer = relationship("User", foreign_keys=[dept_reviewed_by], backref="dept_reviewed_forms")
    company_reviewer = relationship("User", foreign_keys=[company_reviewed_by], backref="company_reviewed_forms")
    items = relationship("FormItem", back_populates="form", cascade="all, delete-orphan")


class FormItem(Base):
    __tablename__ = "form_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(Integer, ForeignKey("form_data.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    value = Column(Float, nullable=True)
    remark = Column(Text, nullable=True)

    form = relationship("FormData", back_populates="items")
    subject = relationship("Subject")


class BudgetItem(Base):
    __tablename__ = "budget_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    value = Column(Float, nullable=False, default=0)

    department = relationship("Department")
    subject = relationship("Subject")


class ReportConfig(Base):
    __tablename__ = "report_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    config_json = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
