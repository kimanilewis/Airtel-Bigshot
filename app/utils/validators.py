"""
Validators utility for Airtel Kenya C2B IPN system.
"""
import re
from typing import Tuple, Optional


def validate_bill_ref(bill_ref: str) -> Tuple[bool, Optional[str]]:
    """
    Validate the bill reference number.
    
    Args:
        bill_ref (str): Bill reference number to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Check if bill_ref is empty
    if not bill_ref:
        return False, "Bill reference number cannot be empty"
    
    # Check if bill_ref is too long (assuming max length of 50 characters)
    if len(bill_ref) > 50:
        return False, "Bill reference number is too long"
    
    # Check if bill_ref contains only alphanumeric characters and some special characters
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', bill_ref):
        return False, "Bill reference number contains invalid characters"
    
    return True, None


def validate_ref_type(ref_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate the reference type.
    
    Args:
        ref_type (str): Reference type to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Check if ref_type is empty
    if not ref_type:
        return False, "Reference type cannot be empty"
    
    # Define allowed reference types
    allowed_ref_types = ["MSISDN", "ACCOUNT", "INVOICE", "POLICY", "METER", "OTHER"]
    
    # Check if ref_type is in allowed list (case insensitive)
    if ref_type.upper() not in allowed_ref_types:
        return False, f"Reference type must be one of: {', '.join(allowed_ref_types)}"
    
    return True, None
