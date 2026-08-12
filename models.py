"""Table creation templates in SQL"""

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Integer, String, ForeignKey, Column, DateTime, Float, Boolean
from datetime import datetime, timezone

Base = declarative_base()


class User(Base):
    """Template for user creation"""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name_user = Column(String, nullable=False, unique=False, index=True)
    password_user = Column(String, nullable=False)
    role_user = Column(String, nullable=False)
    my_number = Column(Integer, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    manager_department_relationship = relationship(
        "Department", back_populates="manager_relationship"
    )
    employee_timerecord_relationship = relationship(
        "TimeRecord", back_populates="employee_relationship"
    )
    payment_relationship = relationship(
        "MonthlyPayroll", back_populates="user_payment_relationship"
    )


class Department(Base):
    """Template for Department creation"""

    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    id_manager = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_title = Column(String, nullable=False)
    manager_relationship = relationship(
        "User", back_populates="manager_department_relationship"
    )
    inventory_relationship = relationship(
        "DailyInventory", back_populates="department_relationship"
    )


class TimeRecord(Base):
    """Table template for time record creation"""

    __tablename__ = "time_records"
    id = Column(
        Integer,
        primary_key=True,
    )
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    clock_in = Column(DateTime, nullable=False)
    clock_out = Column(DateTime, nullable=True)
    hour_worked = Column(Float, nullable=True)
    employee_relationship = relationship(
        "User", back_populates="employee_timerecord_relationship"
    )


class MonthlyPayroll(Base):
    """Table template for monthly payment"""

    __tablename__ = "monthly_payroll"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    datetime_payment = Column(DateTime, nullable=False)
    salary = Column(Float, nullable=False)
    user_payment_relationship = relationship(
        "User", back_populates="payment_relationship"
    )


class DailyInventory(Base):
    """Table template for enterprise products inventory"""

    __tablename__ = "daily_inventory"
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    product_in_stock = Column(Integer, nullable=False)
    product_to_come = Column(Integer, nullable=False)
    product_removed = Column(Boolean, default=False)
    department_relationship = relationship(
        "Department", back_populates="inventory_relationship"
    )
