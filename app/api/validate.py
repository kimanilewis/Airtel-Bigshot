"""
Enhanced validation endpoint for Airtel Kenya C2B IPN system with customer verification.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional

from app.database import get_db
from app.models.repository import TransactionRepository, ValidationResultRepository
from app.models.customer import Customer
from app.utils.validators import validate_bill_ref, validate_ref_type
from app.utils.logger import setup_logger
from app.utils.security import get_current_active_user

router = APIRouter()
logger = setup_logger("validate_endpoint")

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

@router.post("")
async def validate_ipn(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_active_user)
):
    """
    Validate Airtel Kenya C2B IPN request.
    
    This endpoint validates the IPN request by:
    1. Checking if the customer exists in the database using billRef and refType
    2. Validating the bill reference number (billRef)
    3. Validating the reference type (refType)
    
    Args:
        request (Request): FastAPI request object
        db (Session): Database session
        current_user (Any): Current authenticated user
        
    Returns:
        Dict[str, Any]: Validation response in XML format
    """
    try:
        # Get request body
        body = await request.body()
        body_str = body.decode("utf-8")
        logger.info(f"Received validation request: {body_str}")
        
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
        bill_ref = payload.get("REFERENCE")
        ref_type = None
        amount = payload.get("AMOUNT")
        msisdn = payload.get("CUSTOMERMSISDN")
        merchant_msisdn = payload.get("MERCHANTMSISDN")
        
        # Determine ref_type based on the context or default to "ACCOUNT"
        # In a real implementation, this might come from the request or be determined by business logic
        if "TYPE" in payload and payload["TYPE"] == "C2B":
            # Try to determine ref_type from the bill_ref format or other business logic
            if bill_ref and bill_ref.startswith("INV"):
                ref_type = "INVOICE"
            elif bill_ref and bill_ref.startswith("MTR"):
                ref_type = "METER"
            elif bill_ref and bill_ref.startswith("POL"):
                ref_type = "POLICY"
            elif bill_ref and bill_ref.startswith("MSI"):
                ref_type = "MSISDN"
            else:
                ref_type = "ACCOUNT"
        
        # Check if required fields are present
        if not all([transaction_id, bill_ref, amount, msisdn]):
            logger.error("Missing required fields in validation request")
            return create_response(
                response_format,
                "FAILED",
                "Missing required fields",
                transaction_id
            )
        
        # Validate bill reference
        bill_ref_valid, bill_ref_error = validate_bill_ref(bill_ref)
        if not bill_ref_valid:
            logger.error(f"Invalid bill reference: {bill_ref_error}")
            return create_response(
                response_format,
                "FAILED",
                f"Invalid bill reference: {bill_ref_error}",
                transaction_id
            )
        
        # Validate reference type
        if ref_type:
            ref_type_valid, ref_type_error = validate_ref_type(ref_type)
            if not ref_type_valid:
                logger.error(f"Invalid reference type: {ref_type_error}")
                return create_response(
                    response_format,
                    "FAILED",
                    f"Invalid reference type: {ref_type_error}",
                    transaction_id
                )
        
        # Check if customer exists in the database
        customer = verify_customer(db, bill_ref, ref_type, msisdn)
        if not customer:
            logger.error(f"Customer not found for bill_ref: {bill_ref}, ref_type: {ref_type}")
            return create_response(
                response_format,
                "FAILED",
                "Customer not found or inactive",
                transaction_id
            )
        
        # Check if transaction already exists
        existing_transaction = TransactionRepository.get_transaction_by_transaction_id(db, transaction_id)
        if existing_transaction:
            logger.warning(f"Transaction {transaction_id} already exists")
            return create_response(
                response_format,
                "FAILED",
                "Transaction already processed",
                transaction_id
            )
        
        # Create transaction record
        transaction_data = {
            "transaction_id": transaction_id,
            "customer_id": customer.id,
            "bill_ref": bill_ref,
            "ref_type": ref_type or "ACCOUNT",
            "amount": float(amount),
            "msisdn": msisdn,
            "merchant_msisdn": merchant_msisdn,
            "airtel_reference": transaction_id,
            "raw_payload": body_str
        }
        
        transaction = TransactionRepository.create_transaction(db, transaction_data)
        
        # Create validation result
        ValidationResultRepository.create_validation_result(
            db, 
            transaction.id, 
            True, 
            "Transaction validated successfully"
        )
        
        logger.info(f"Transaction {transaction_id} validated successfully")
        
        # Return success response
        return create_response(
            response_format,
            "SUCCESS",
            "Transaction validated successfully",
            transaction_id
        )
        
    except Exception as e:
        logger.error(f"Error validating transaction: {str(e)}")
        return create_response(
            "xml",  # Default to XML if format can't be determined
            "FAILED",
            f"Internal server error: {str(e)}",
            payload.get("REFERENCE1", "unknown") if 'payload' in locals() else "unknown"
        )

def verify_customer(db: Session, bill_ref: str, ref_type: Optional[str], msisdn: str) -> Optional[Customer]:
    """
    Verify if customer exists in the database.
    
    Args:
        db (Session): Database session
        bill_ref (str): Bill reference
        ref_type (Optional[str]): Reference type
        msisdn (str): Customer phone number
        
    Returns:
        Optional[Customer]: Customer if found and active, None otherwise
    """
    query = db.query(Customer).filter(Customer.bill_ref == bill_ref)
    
    if ref_type:
        query = query.filter(Customer.ref_type == ref_type)
    
    # Additional check for msisdn
    query = query.filter(Customer.msisdn == msisdn)
    
    # Check for active status
    query = query.filter(Customer.status == "ACTIVE")
    
    return query.first()

def create_response(format_type: str, status: str, message: str, transaction_id: str) -> Dict[str, Any]:
    """
    Create response in the specified format.
    
    Args:
        format_type (str): Response format (xml or json)
        status (str): Status (SUCCESS or FAILED)
        message (str): Response message
        transaction_id (str): Transaction ID
        
    Returns:
        Dict[str, Any]: Response data
    """
    if format_type == "xml":
        xml_response = f"""
        <COMMAND>
            <STATUS>{status}</STATUS>
            <MESSAGE>{message}</MESSAGE>
        </COMMAND>
        """
        return {"content": xml_response, "media_type": "application/xml"}
    else:
        return {
            "status": status,
            "message": message,
            "transactionId": transaction_id
        }
