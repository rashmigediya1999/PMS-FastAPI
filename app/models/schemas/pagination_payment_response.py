from typing import  List

from pydantic import BaseModel

from app.models.payment import Payment

class PaginatedPaymentResponse(BaseModel):
    items: List[Payment]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
