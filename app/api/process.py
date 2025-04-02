"""
Enhanced processing endpoint for Airtel Kenya C2B IPN system with customer verification.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from datetime import datetime

from app.database import get_db
from app.models.repository import TransactionRepository, ProcessingResultRepository
from app.models.transaction import TransactionStatus
from app.models.customer import Customer
from app.utils.logger import setup_logger
from app.utils.security import get_current_active_user

router = APIRouter()
logger = setup_logger("process_endpoint")

def parse_xml_request(xml_content: str) -> Dict[str, Any]:
    """
    Parse XML request from Airtel.
    
    Args:
        xml_content (str): XML content
        
    Returns:
        Dict[str, Any]: Parsed data
    """
    try:
        root = ET.fromstring(xml_content)
        data = {}
        
        for child in root:
            data[child.tag] = child.text
        
        return data
    except Exception as e:
        logger.error(f"Error parsing XML: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid XML format: {str(e)}"
        )

@router.post("/")
async def process_ipn(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user)
):
    """
    Process Airtel Kenya C2B IPN request.
    
    This endpoint processes the IPN request after validation:
    1. Retrieves the transaction from the database
    2. Verifies the customer exists and is active
    3. Processes the payment
    4. Updates the transaction status
    
    Args:
        request (Request): FastAPI request object
        db (Session): Database session
        current_user (Any): Current authenticated user
        
    Returns:
        Dict[str, Any]: Processing response in XML or JSON format
    """
    try:
        # Get request body
        body = await request.body()
        body_str = body.decode("utf-8")
        logger.info(f"Received processing request: {body_str}")
        
        # Check if request is XML or JSON
        if body_str.strip().startswith("<"):
            # Parse XML
            payload = parse_xml_request(body_str)
            response_format = "xml"
        else:
            # Parse JSON
            payload = await request.json()
            response_format = "json"
        
        # Extract required fields based on Airtel documentation
        transaction_id = payload.get("REFERENCE1")
        reference2 = payload.get("REFERENCE2")  # Mobiquity reference
        
        # Check if required fields are present
        if not transaction_id:
            logger.error("Missing transaction ID in processing request")
            return create_response(
                response_format,
                "FAILED",
                "Missing transaction ID",
                "unknown"
            )
        
        # Get transaction from database
        transaction = TransactionRepository.get_transaction_by_transaction_id(db, transaction_id)
        
        # Check if transaction exists
        if not transaction:
            logger.error(f"Transaction {transaction_id} not found")
            return create_response(
                response_format,
                "FAILED",
                "Transaction not found",
                transaction_id
            )
        
        # Check if transaction is already processed
        if transaction.status == TransactionStatus.PROCESSED:
            logger.warning(f"Transaction {transaction_id} already processed")
            return create_response(
                response_format,
                "SUCCESS",
                "Transaction already processed",
                transaction_id
            )
        
        # Check if transaction is validated
        if transaction.status != TransactionStatus.VALIDATED:
            logger.error(f"Transaction {transaction_id} not validated")
            return create_response(
                response_format,
                "FAILED",
                "Transaction not validated",
                transaction_id
            )
        
        # Verify customer is still active
        customer = db.query(Customer).filter(Customer.id == transaction.customer_id).first()
        if not customer or customer.status != "ACTIVE":
            logger.error(f"Customer for transaction {transaction_id} not found or inactive")
            return create_response(
                response_format,
                "FAILED",
                "Customer not found or inactive",
                transaction_id
            )
        
        # Update transaction with Mobiquity reference if provided
        if reference2:
            transaction.mobiquity_reference = reference2
            db.commit()
        
        # Process the payment (in a real system, this would involve business logic)
        # For example, updating account balances, sending notifications, etc.
        processing_result = process_payment(db, transaction, customer)
        
        if not processing_result.is_processed:
            logger.error(f"Failed to process transaction {transaction_id}: {processing_result.processing_message}")
            return create_response(
                response_format,
                "FAILED",
                processing_result.processing_message or "Payment processing failed",
                transaction_id
            )
        
        logger.info(f"Transaction {transaction_id} processed successfully")
        
        # Return success response
        return create_response(
            response_format,
            "SUCCESS",
            "Transaction processed successfully",
            transaction_id,
            {
                "billRef": transaction.bill_ref,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "customerName": customer.full_name,
                "msisdn": customer.msisdn
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing transaction: {str(e)}")
        return create_response(
            "xml",  # Default to XML if format can't be determined
            "FAILED",
            f"Internal server error: {str(e)}",
            payload.get("REFERENCE1", "unknown") if 'payload' in locals() else "unknown"
        )

def process_payment(db: Session, transaction, customer) -> Any:
    """
    Process payment for transaction.
    
    Args:
        db (Session): Database session
        transaction: Transaction to process
        customer: Customer making the payment
        
    Returns:
        ProcessingResult: Result of payment processing
    """
    try:
        # In a real implementation, this would include:
        # 1. Updating account balances
        # 2. Recording the payment in financial systems
        # 3. Sending notifications
        # 4. Other business-specific logic
        
        # For this example, we'll simulate successful processing
        processing_message = f"Payment of {transaction.amount} {transaction.currency} processed for {customer.full_name}"
        
        # Create processing result
        processing_result = ProcessingResultRepository.create_processing_result(
            db, 
            transaction.id, 
            True, 
            processing_message
        )
        
        return processing_result
    except Exception as e:
        # Log the error and create a failed processing result
        logger.error(f"Payment processing error: {str(e)}")
        return ProcessingResultRepository.create_processing_result(
            db,
            transaction.id,
            False,
            f"Payment processing error: {str(e)}"
        )

def create_response(format_type: str, status: str, message: str, transaction_id: str, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create response in the specified format.
    
    Args:
        format_type (str): Response format (xml or json)
        status (str): Status (SUCCESS or FAILED)
        message (str): Response message
        transaction_id (str): Transaction ID
        additional_data (Dict[str, Any], optional): Additional data to include in response
        
    Returns:
        Dict[str, Any]: Response data
    """
    if format_type == "xml":
        # Create XML response
        xml_response = f"""
        <COMMAND>
            <STATUS>{status}</STATUS>
            <MESSAGE>{message}</MESSAGE>
        </COMMAND>
        """
        return {"content": xml_response, "media_type": "application/xml"}
    else:
        # Create JSON response
        response = {
            "status": status,
            "message": message,
            "transactionId": transaction_id
        }
        
        # Add additional data if provided
        if additional_data:
            response.update(additional_data)
            
        return response
