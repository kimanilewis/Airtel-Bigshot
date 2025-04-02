"""
Integration tests for API endpoints in the Airtel Kenya C2B IPN system.
"""
import unittest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app  # This will be created later


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


class TestEndpoints(unittest.TestCase):
    """Test cases for API endpoints."""

    def setUp(self):
        """Set up test database and client."""
        # Create tables
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)
        
        # Sample valid payload
        self.valid_payload = {
            "transactionId": "TRX123456789",
            "billRef": "INVOICE-123",
            "refType": "INVOICE",
            "amount": 1000.00,
            "msisdn": "254712345678",
            "paymentDate": "2025-04-01T12:00:00Z",
            "currency": "KES"
        }
        
        # Sample invalid payload (missing required fields)
        self.invalid_payload = {
            "transactionId": "TRX123456789",
            "amount": 1000.00
        }
    
    def tearDown(self):
        """Clean up test database."""
        Base.metadata.drop_all(bind=engine)
    
    def test_validate_endpoint_valid(self):
        """Test validation endpoint with valid payload."""
        response = self.client.post("/api/validate/", json=self.valid_payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["transactionId"], self.valid_payload["transactionId"])
    
    def test_validate_endpoint_invalid(self):
        """Test validation endpoint with invalid payload."""
        response = self.client.post("/api/validate/", json=self.invalid_payload)
        self.assertEqual(response.status_code, 200)  # API returns 200 even for validation errors
        
        data = response.json()
        self.assertEqual(data["status"], "FAILED")
        self.assertEqual(data["transactionId"], self.invalid_payload["transactionId"])
    
    def test_validate_endpoint_invalid_bill_ref(self):
        """Test validation endpoint with invalid bill reference."""
        payload = self.valid_payload.copy()
        payload["billRef"] = "INVOICE@123"  # Invalid character
        
        response = self.client.post("/api/validate/", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "FAILED")
        self.assertIn("Invalid bill reference", data["message"])
    
    def test_validate_endpoint_invalid_ref_type(self):
        """Test validation endpoint with invalid reference type."""
        payload = self.valid_payload.copy()
        payload["refType"] = "UNKNOWN"  # Not in allowed list
        
        response = self.client.post("/api/validate/", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "FAILED")
        self.assertIn("Invalid reference type", data["message"])
    
    def test_process_endpoint_without_validation(self):
        """Test processing endpoint without prior validation."""
        response = self.client.post("/api/process/", json={"transactionId": "TRX123456789"})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "FAILED")
        self.assertIn("Transaction not found", data["message"])
    
    def test_process_endpoint_after_validation(self):
        """Test processing endpoint after successful validation."""
        # First validate the transaction
        self.client.post("/api/validate/", json=self.valid_payload)
        
        # Then process it
        response = self.client.post("/api/process/", json={"transactionId": self.valid_payload["transactionId"]})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["transactionId"], self.valid_payload["transactionId"])
        self.assertEqual(data["billRef"], self.valid_payload["billRef"])
    
    def test_process_endpoint_duplicate(self):
        """Test processing endpoint with duplicate processing."""
        # First validate the transaction
        self.client.post("/api/validate/", json=self.valid_payload)
        
        # Process it first time
        self.client.post("/api/process/", json={"transactionId": self.valid_payload["transactionId"]})
        
        # Process it second time
        response = self.client.post("/api/process/", json={"transactionId": self.valid_payload["transactionId"]})
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("already processed", data["message"])


if __name__ == "__main__":
    unittest.main()
