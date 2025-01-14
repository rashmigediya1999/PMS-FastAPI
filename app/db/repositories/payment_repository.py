from typing import List

from pymongo import DESCENDING

from app.db.mongodb import MongoDB
from app.core.config import settings
from app.models.payment import Payment
from pymongo.errors import PyMongoError


class PaymentRepository:
    def __init__(self):
        collection_name_payment = settings.config["mongodb"]["collections"]["payments"]
        collection_name_upload_evidence = settings.config["mongodb"]["collections"]["upload_evidence"]
        self.collection_payment = MongoDB.db[collection_name_payment]
        self.collection_upload_evidence = MongoDB.db[collection_name_upload_evidence]
        
    async def get_payments(self, query: dict = {}, skip: int = 0, limit: int = 50, sort_order: int = DESCENDING) -> List[dict]:
        try:
            payments = await self.collection_payment.find(query).sort("payee_added_date_utc", sort_order).skip(skip).limit(limit).to_list(length=limit)
            return payments
        except PyMongoError as e:
            print(f"An error occurred while retrieving payments: {str(e)}")
            raise e
        
    async def count_documents(self, query: dict) -> int:
        return await self.collection_payment.count_documents(query)

    async def get_payment(self, payment_id: str) -> dict:
        result = await self.collection_payment.find_one(
            {"_id": payment_id,}
        )
        result["status"] = "success"
        if not result:
            result["status"] = "error"
        
        return result
    
    async def update_payment(self, payment_id: str, update_data: dict) -> dict:
        result = await self.collection_payment.find_one_and_update(
            {"_id": payment_id},
            {"$set": update_data},
            return_document=True
        )
        return result
    
    async def delete_payment(self, payment_id: str) -> dict:
        try:
            result = await self.collection_payment.delete_one({"_id": payment_id,})
            if result.deleted_count == 0:
                raise ValueError("Payment not found")
            
            return {"status": "success", "message": "Payment deleted successfully"}
        except PyMongoError as e:
            raise ValueError(f"An error occurred while deleting the payment: {str(e)}")

    async def create_payment(self, payment_data: Payment) -> str:
        try:
            # Convert the Payment model instance to a dictionary
            payment_dict = payment_data.model_dump(by_alias=True)
            
            result = await self.collection_payment.insert_one(payment_dict)
            return str(result.inserted_id)
        except Exception as e:
            print(f"An error occurred while creating the payment: {str(e)}")
            raise e

    
    async def upload_evidence(self, payment_id: str, file_data: bytes, filename: str) -> str:
        try:
            result = await self.collection_upload_evidence.insert_one(
                {"_id": payment_id, "evidence_file": file_data, "filename": filename}
            )
            return str(result.inserted_id)
        except PyMongoError as e:
            print(f"An error occurred while uploading the evidence: {str(e)}")

    async def download_evidence(self, file_id: str) -> bytes:
        try:
            print(f"Downloading evidence file with id: {file_id}")
            result = await self.collection_upload_evidence.find_one(
                {"_id": file_id}
            )

            if not result:
                raise ValueError("File not found")
            return result
        except PyMongoError as e:
            print(f"An error occurred while downloading the evidence: {str(e)}")
            raise e