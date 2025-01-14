from datetime import datetime, date
from typing import Optional

from bson import ObjectId
from app.models.payment_status import PaymentStatus
from pydantic import BaseModel, Field, EmailStr, field_validator
from enum import Enum

class Payment(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    payee_first_name: str
    payee_last_name: str
    payee_payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    payee_added_date_utc: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))
    payee_due_date: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))
    payee_address_line_1: str
    payee_address_line_2: Optional[str] = None
    payee_city: str
    payee_country: str
    payee_province_or_state: Optional[str] = None
    payee_postal_code: str
    payee_phone_number: str
    payee_email: EmailStr
    currency: str
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    tax_percent: Optional[float] = Field(None, ge=0, le=100)
    due_amount: float = Field(default=0, ge=0) 
    total_due: Optional[float] = None
    evidence_file_url: Optional[str] = None

    class Config:
        populate_by_name = True