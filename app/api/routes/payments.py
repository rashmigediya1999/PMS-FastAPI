import base64
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from app.services.payment_service import PaymentService
from app.models.schemas.pagination_payment_response import PaginatedPaymentResponse
from app.models.payment import Payment

router = APIRouter()
# logger = Logger.get_logger(__name__)

@router.get("/payments")
async def get_payments(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    payee_payment_status: Optional[str] = Query(None),
    search_payee_name: Optional[str] = Query(None),
    payment_service: PaymentService = Depends()
):
    try:
        return await payment_service.get_payments(
            page=page,
            page_size=page_size,
            payee_payment_status = payee_payment_status,
            search_payee_name = search_payee_name
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # logger.error(f"Error retrieving payments: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/payment/{payment_id}")
async def get_payment_by_id(payment_id: str, payment_service: PaymentService = Depends()):

    # logger.info(f"Received request to get payment with id={payment_id}")
    try:
        return await payment_service.get_payment(payment_id)
    except ValueError as e:
        print(e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(e)
        # logger.error(f"Error updating payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.put("/payment/{payment_id}")
async def update_payment(payment_id: str, update_data: dict, payment_service: PaymentService = Depends()):
    # logger.info(f"Received request to update payment with id={payment_id}")
    try:
        return await payment_service.update_payment(payment_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # logger.error(f"Error updating payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/payment/{payment_id}")
async def delete_payment(payment_id: str, payment_service: PaymentService = Depends()):
    # logger.info(f"Received request to delete payment with id={payment_id}")
    try:
        return await payment_service.delete_payment(payment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # logger.error(f"Error deleting payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/payment")
async def create_payment(payment_data: Payment, payment_service: PaymentService = Depends()):
    # logger.info("Received request to create a new payment")
    try:
        return await payment_service.create_payment(payment_data)
    except Exception as e:
        # logger.error(f"Error creating payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/payment/{payment_id}/upload_evidence", response_model=str)
async def upload_evidence(payment_id: str, file: UploadFile = File(...), payment_service: PaymentService = Depends()):
    # logger.info(f"Received request to upload evidence for payment with id={payment_id}")
    try:
        
        file_data = base64.b64encode(file.file.read())
        file_id = await payment_service.upload_evidence(payment_id, file_data, file.filename)
        return file_id
    except Exception as e:
        # logger.error(f"Error uploading evidence: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/payment/download_evidence/{file_id}", response_model=bytes)
async def download_evidence(file_id: str, payment_service: PaymentService = Depends()):
    # logger.info(f"Received request to download evidence with file_id={file_id}")
    try:
        file_data = await payment_service.download_evidence(file_id)
        return file_data
    except Exception as e:
        # logger.error(f"Error downloading evidence: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")