"""
SQLAlchemy ORM models representing the core business entities.
"""

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Loan(Base):
    __tablename__ = "loans"
    
    # ==========================================
    # Identifiers
    # ==========================================
    id: Mapped[str] = mapped_column(String, primary_key=True)

    # ==========================================
    # Applicant Snapshot (Point-in-Time)
    # ==========================================
    # Represents the applicant's profile at the time of origination.
    # The official Lending Club dataset lacks persistent borrower IDs.
    annual_inc: Mapped[Optional[float]] = mapped_column(Float)
    home_ownership: Mapped[Optional[str]] = mapped_column(String)
    addr_state: Mapped[Optional[str]] = mapped_column(String)

    # ==========================================
    # Credit Profile (Point-in-Time)
    # ==========================================
    fico_range_low: Mapped[Optional[float]] = mapped_column(Float)
    fico_range_high: Mapped[Optional[float]] = mapped_column(Float)

    # ==========================================
    # Loan Characteristics
    # ==========================================
    loan_amnt: Mapped[Optional[float]] = mapped_column(Float)
    int_rate: Mapped[Optional[float]] = mapped_column(Float)
    term: Mapped[Optional[str]] = mapped_column(String)
    grade: Mapped[Optional[str]] = mapped_column(String)
    issue_d: Mapped[Optional[date]] = mapped_column(Date)

    # ==========================================
    # Loan Outcome
    # ==========================================
    loan_status: Mapped[Optional[str]] = mapped_column(String)

    # ==========================================
    # Relationships
    # ==========================================
    payments: Mapped[List["Payment"]] = relationship(back_populates="loan")
    # predictions: Mapped[List["Prediction"]] = relationship(back_populates="loan")


class Payment(Base):
    __tablename__ = "payments"
    payment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    loan_id: Mapped[str] = mapped_column(ForeignKey("loans.id"))
    payment_date: Mapped[Optional[date]] = mapped_column(Date)
    amount_received: Mapped[Optional[float]] = mapped_column(Float)

    loan: Mapped["Loan"] = relationship(back_populates="payments")


class Prediction(Base):
    __tablename__ = "predictions"
    prediction_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    loan_id: Mapped[str] = mapped_column(ForeignKey("loans.id"))
    predicted_default_prob: Mapped[float] = mapped_column(Float)
    inference_timestamp: Mapped[datetime] = mapped_column(DateTime)

