import base64
from datetime import datetime
import mimetypes
from typing import List, Optional

from fastapi import Response
from app.models.schemas.pagination_payment_response import PaginatedPaymentResponse
from app.models.payment import Payment
from app.db.repositories.payment_repository import PaymentRepository

class PaymentService:
    def __init__(self):
        self.repository = PaymentRepository()

    async def get_payments(
        self,
        page: int = 1,
        page_size: int = 50,
        search_payee_name: Optional[str] = None,
        payee_payment_status = None
    ) -> PaginatedPaymentResponse:
        try:
            skip = (page - 1) * page_size
            
            # Build query based on filters and search
            query = {}
            if search_payee_name:
                query["$or"] = [
                    {"payee_first_name": {"$regex": search_payee_name, "$options": "i"}},
                    {"payee_last_name": {"$regex": search_payee_name, "$options": "i"}},
                    {"payee_email": {"$regex": search_payee_name, "$options": "i"}}
                ]
            if payee_payment_status is not None:
                query.update({"payee_payment_status": payee_payment_status})
            
            # Get total count for pagination
            total_count = await self.repository.count_documents(query)

            # Get paginated results
            payments = await self.repository.get_payments(skip=skip, limit=page_size, query=query)

            # Process payments
            for payment in payments:
                self.calculate_total_due(payment)
                self.calculate_status(payment)

            # Calculate pagination metadata
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_previous = page > 1

            return PaginatedPaymentResponse(
                items=[Payment(**payment) for payment in payments],
                total=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
        except Exception as e:
            print(e)
            raise e

    def calculate_status(self, payment: dict) -> None:
        today = datetime.now().date()
        due_date = datetime.strptime(payment["payee_due_date"], '%Y-%m-%dT%H:%M:%SZ').date()
        
        if(payment["payee_payment_status"] != "completed"):
            if due_date == today:
                payment["payee_payment_status"] = "due_now"
            elif due_date < today:
                payment["payee_payment_status"] = "overdue"
            else:
                payment["payee_payment_status"] = "pending"
        
    def calculate_total_due(self, payment: dict) -> None:
       
        discount = payment.get("discount_percent", 0) / 100
        tax = payment.get("tax_percent", 0) / 100

        due_amount = payment["due_amount"]
        payment["total_due"] = due_amount * (1 - discount) * (1 + tax)
            
        

    async def get_payment(self, payment_id: str) -> dict:
        result = await self.repository.get_payment(payment_id)
        if result["status"] == "error":
            raise ValueError(result["message"])
        self.calculate_total_due(result)
        self.calculate_status(result) 
        return result

    async def update_payment(self, payment_id: str, update_data: dict, file_data: Optional[bytes] = None, filename: Optional[str] = None) -> Payment:
        self.calculate_status(update_data)         
        updated_payment = await self.repository.update_payment(payment_id, update_data)
        if not updated_payment:
            raise ValueError("Payment not found")
        return Payment(**updated_payment)

    async def delete_payment(self, payment_id: str) -> dict:
        result = await self.repository.delete_payment(payment_id)
        if result["status"] == "error":
            raise ValueError(result["message"])
        return result

    async def create_payment(self, payment_data: dict) -> str:
        try:
            date_string = payment_data.payee_due_date
            date_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
            payment_data.payee_due_date = date_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
            payment_id = await self.repository.create_payment(payment_data)
            return payment_id
        except Exception as e:
            print(f"An error occurred while creating the payment: {str(e)}")
            raise e

    async def upload_evidence(self, payment_id: str, file_data: bytes, filename: str) -> str:
        file_id = await self.repository.upload_evidence(payment_id, file_data, filename)
        return file_id

    async def download_evidence(self, file_id: str) -> bytes:
        try:
            file_data = await self.repository.download_evidence(file_id)

            file_content = base64.b64decode(file_data["evidence_file"])
            
            # Get the appropriate content type
            content_type = self.get_content_type(file_data['filename'])
            
            # Create response with file content and proper content type
            response = Response(
                content=file_content,
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename={file_data['filename']}"
                }
            )
            return response
        except ValueError as e:
            print(f"An error occurred while downloading the evidence: {str(e)}")
            raise e
    def get_content_type(self, filename: str) -> str:
        """Determine content type based on file extension"""
        content_type, _ = mimetypes.guess_type(filename)
        
        # Handle common image and PDF types
        extension_mapping = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.pdf': 'application/pdf'
        }
        
        file_extension = filename[filename.rfind('.'):].lower()
        return extension_mapping.get(file_extension, content_type or 'application/octet-stream')
