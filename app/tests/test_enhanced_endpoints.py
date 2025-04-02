"""
Updated tests for enhanced Airtel Kenya C2B IPN system.
"""
import unittest
import json
import xml.etree.ElementTree as ET
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from app.database import Base, get_db
from app.main import app
from app.models.customer import Customer, CustomerStatus
from app.models.user import User
from app.utils.security import get_password_hash, create_access_token


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


# Override the get_current_active_user dependency
async def override_get_current_active_user():
    return {"username": "test_user", "email": "test@example.com", "is_active": True}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides["app.utils.security.get_current_active_user"] = override_get_current_active_user


class TestEnhancedEndpoints(unittest.TestCase):
    """Test cases for enhanced API endpoints."""

    def setUp(self):
        """Set up test database and client."""
        # Create tables
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)
        self.db = TestingSessionLocal()
        
        # Create test user
        test_user = User(
            username="test_user",
            password_hash=get_password_hash("test_password"),
            email="test@example.com",
            is_active=True
        )
        self.db.add(test_user)
        
        # Create test customers
        test_customers = [
            Customer(
                bill_ref="ACC123456",
                ref_type="ACCOUNT",
                msisdn="254712345678",
                full_name="John Doe",
                email="john.doe@example.com",
                id_number="12345678",
                address="123 Main St, Nairobi",
                status=CustomerStatus.ACTIVE
            ),
            Customer(
                bill_ref="INV789012",
                ref_type="INVOICE",
                msisdn="254723456789",
                full_name="Jane Smith",
                email="jane.smith@example.com",
                id_number="87654321",
                address="456 Park Ave, Nairobi",
                status=CustomerStatus.ACTIVE
            ),
            Customer(
                bill_ref="MTR456789",
                ref_type="METER",
                msisdn="254734567890",
                full_name="Bob Johnson",
                email="bob.johnson@example.com",
                id_number="23456789",
                address="789 Oak St, Nairobi",
                status=CustomerStatus.INACTIVE  # Inactive customer for testing
            )
        ]
        
        for customer in test_customers:
            self.db.add(customer)
        
        self.db.commit()
        
        # Get access token
        access_token = create_access_token(
            data={"sub": "test_user"},
            expires_delta=timedelta(minutes=30)
        )
        self.headers = {"Authorization": f"Bearer {access_token}"}
        
        # Sample valid XML payload
        self.valid_xml_payload = """
        <COMMAND>
            <TYPE>C2B</TYPE>
            <CUSTOMERMSISDN>254712345678</CUSTOMERMSISDN>
            <MERCHANTMSISDN>254700000000</MERCHANTMSISDN>
            <CUSTOMERNAME>John Doe</CUSTOMERNAME>
            <AMOUNT>1000.00</AMOUNT>
            <PIN></PIN>
            <REFERENCE>ACC123456</REFERENCE>
            <USERNAME></USERNAME>
            <PASSWORD></PASSWORD>
            <REFERENCE1>TRX123456789</REFERENCE1>
        </COMMAND>
        """
        
        # Sample valid JSON payload
        self.valid_json_payload = {
            "TYPE": "C2B",
            "CUSTOMERMSISDN": "254712345678",
            "MERCHANTMSISDN": "254700000000",
            "CUSTOMERNAME": "John Doe",
            "AMOUNT": "1000.00",
            "PIN": "",
            "REFERENCE": "ACC123456",
            "USERNAME": "",
            "PASSWORD": "",
            "REFERENCE1": "TRX123456789"
        }
        
        # Sample invalid customer payload
        self.invalid_customer_payload = {
            "TYPE": "C2B",
            "CUSTOMERMSISDN": "254799999999",  # Non-existent customer
            "MERCHANTMSISDN": "254700000000",
            "CUSTOMERNAME": "Unknown User",
            "AMOUNT": "1000.00",
            "PIN": "",
            "REFERENCE": "UNKNOWN123",
            "USERNAME": "",
            "PASSWORD": "",
            "REFERENCE1": "TRX987654321"
        }
        
        # Sample inactive customer payload
        self.inactive_customer_payload = {
            "TYPE": "C2B",
            "CUSTOMERMSISDN": "254734567890",  # Inactive customer
            "MERCHANTMSISDN": "254700000000",
            "CUSTOMERNAME": "Bob Johnson",
            "AMOUNT": "1000.00",
            "PIN": "",
            "REFERENCE": "MTR456789",
            "USERNAME": "",
            "PASSWORD": "",
            "REFERENCE1": "TRX456789012"
        }
    
    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        Base.metadata.drop_all(bind=engine)
    
    def test_auth_endpoint(self):
        """Test authentication endpoint."""
        response = self.client.post(
            "/auth/token",
            data={"username": "test_user", "password": "test_password"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
    
    def test_validate_endpoint_xml_valid_customer(self):
        """Test validation endpoint with valid XML payload and valid customer."""
        response = self.client.post(
            "/api/validate/",
            headers=self.headers,
            content=self.valid_xml_payload
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("<STATUS>SUCCESS</STATUS>", response.text)
        self.assertIn("Transaction validated successfully", response.text)
    
    def test_validate_endpoint_json_valid_customer(self):
        """Test validation endpoint with valid JSON payload and valid customer."""
        response = self.client.post(
            "/api/validate/",
            headers=self.headers,
            json=self.valid_json_payload
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["transactionId"], self.valid_json_payload["REFERENCE1"])
    
    def test_validate_endpoint_nonexistent_customer(self):
        """Test validation endpoint with non-existent customer."""
        response = self.client.post(
            "/api/validate/",
            headers=self.headers,
            json=self.invalid_customer_payload
        )
        self.assertEqual(response.status_code, 200)  # API returns 200 even for validation errors
        data = response.json()
        self.assertEqual(data["status"], "FAILED")
        self.assertIn("Customer not found", data["message"])
    
    def test_validate_endpoint_inactive_customer(self):
        """Test validation endpoint with inactive customer."""
        response = self.client.post(
            "/api/validate/",
            headers=self.headers,
            json=self.inactive_customer_payload
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "FAILED")
        self.assertIn("Customer not found or inactive", data["message"])
    
    def test_process_endpoint_after_validation(self):
        """Test processing endpoint after successful validation."""
        # First validate the transaction
        self.client.post(
            "/api/validate/",
            headers=self.headers,
            json=self.valid_json_payload
        )
        
        # Then process it
        process_payload = {
            "TYPE": "C2B",
            "REFERENCE1": self.valid_json_payload["REFERENCE1"],
            "REFERENCE2": "MOB123456789"
        }
        
        response = self.client.post(
            "/api/process/",
            headers=self.headers,
            json=process_payload
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["transactionId"], self.valid_json_payload["REFERENCE1"])
        self.assertEqual(data["billRef"], self.valid_json_payload["REFERENCE"])
        self.assertEqual(float(data["amount"]), float(self.valid_json_payload["AMOUNT"]))
    
    def test_process_endpoint_without_validation(self):
        """Test processing endpoint without prior validation."""
        process_payload = {
            "TYPE": "C2B",
            "REFERENCE1": "TRX_NOT_VALIDATED",
            "REFERENCE2": "MOB123456789"
        }
        
        response = self.client.post(
            "/api/process/",
            headers=self.headers,
            json=process_payload
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "FAILED")
        self.assertIn("Transaction not found", data["message"])
    
    def test_process_endpoint_xml_format(self):
        """Test processing endpoint with XML format."""
        # First validate the transaction
        self.client.post(
            "/api/validate/",
            headers=self.headers,
            content=self.valid_xml_payload
        )
        
        # Then process it with XML
        process_xml = f"""
        <COMMAND>
            <TYPE>C2B</TYPE>
            <REFERENCE1>{self.valid_json_payload["REFERENCE1"]}</REFERENCE1>
            <REFERENCE2>MOB123456789</REFERENCE2>
        </COMMAND>
        """
        
        response = self.client.post(
            "/api/process/",
            headers=self.headers,
            content=process_xml
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("<STATUS>SUCCESS</STATUS>", response.text)
        self.assertIn("Transaction processed successfully", response.text)
    
    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints."""
        # Remove the dependency override to test actual authentication
        app.dependency_overrides.pop("app.utils.security.get_current_active_user", None)
        
        try:
            # Try to access validate endpoint without token
            response = self.client.post(
                "/api/validate/",
                json=self.valid_json_payload
            )
            self.assertEqual(response.status_code, 401)
            
            # Try to access process endpoint without token
            response = self.client.post(
                "/api/process/",
                json={"REFERENCE1": self.valid_json_payload["REFERENCE1"]}
            )
            self.assertEqual(response.status_code, 401)
        finally:
            # Restore the dependency override
            app.dependency_overrides["app.utils.security.get_current_active_user"] = override_get_current_active_user


if __name__ == "__main__":
    unittest.main()
