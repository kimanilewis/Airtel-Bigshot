"""
Unit tests for validators in the Airtel Kenya C2B IPN system.
"""
import unittest
from app.utils.validators import validate_bill_ref, validate_ref_type


class TestValidators(unittest.TestCase):
    """Test cases for validator functions."""

    def test_validate_bill_ref_valid(self):
        """Test valid bill reference numbers."""
        test_cases = [
            "12345",
            "INVOICE-123",
            "ACC_12345",
            "METER.123",
            "abcDEF123"
        ]
        
        for bill_ref in test_cases:
            with self.subTest(bill_ref=bill_ref):
                is_valid, error_message = validate_bill_ref(bill_ref)
                self.assertTrue(is_valid)
                self.assertIsNone(error_message)
    
    def test_validate_bill_ref_invalid(self):
        """Test invalid bill reference numbers."""
        test_cases = [
            ("", "Bill reference number cannot be empty"),
            ("A" * 51, "Bill reference number is too long"),
            ("INVOICE#123", "Bill reference number contains invalid characters"),
            ("BILL REF", "Bill reference number contains invalid characters"),
            ("INVOICE@123", "Bill reference number contains invalid characters")
        ]
        
        for bill_ref, expected_error in test_cases:
            with self.subTest(bill_ref=bill_ref):
                is_valid, error_message = validate_bill_ref(bill_ref)
                self.assertFalse(is_valid)
                self.assertEqual(error_message, expected_error)
    
    def test_validate_ref_type_valid(self):
        """Test valid reference types."""
        test_cases = [
            "MSISDN",
            "ACCOUNT",
            "INVOICE",
            "POLICY",
            "METER",
            "OTHER",
            # Test case insensitivity
            "msisdn",
            "account",
            "Invoice",
            "Policy",
            "meter",
            "other"
        ]
        
        for ref_type in test_cases:
            with self.subTest(ref_type=ref_type):
                is_valid, error_message = validate_ref_type(ref_type)
                self.assertTrue(is_valid)
                self.assertIsNone(error_message)
    
    def test_validate_ref_type_invalid(self):
        """Test invalid reference types."""
        test_cases = [
            ("", "Reference type cannot be empty"),
            ("UNKNOWN", "Reference type must be one of: MSISDN, ACCOUNT, INVOICE, POLICY, METER, OTHER"),
            ("CUSTOMER", "Reference type must be one of: MSISDN, ACCOUNT, INVOICE, POLICY, METER, OTHER"),
            ("123", "Reference type must be one of: MSISDN, ACCOUNT, INVOICE, POLICY, METER, OTHER")
        ]
        
        for ref_type, expected_error in test_cases:
            with self.subTest(ref_type=ref_type):
                is_valid, error_message = validate_ref_type(ref_type)
                self.assertFalse(is_valid)
                self.assertEqual(error_message, expected_error)


if __name__ == "__main__":
    unittest.main()
