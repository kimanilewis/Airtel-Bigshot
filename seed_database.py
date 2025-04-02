"""
Database seeding functionality for Airtel Kenya C2B IPN system.
"""
import argparse
import csv
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.customer import Customer, CustomerStatus
from app.models.user import User
from app.utils.security import get_password_hash
from app.config import DB_URL

def create_session():
    """Create a database session."""
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def seed_customers(csv_file=None):
    """
    Seed the customers table with sample data or from a CSV file.
    
    Args:
        csv_file (str, optional): Path to CSV file with customer data.
    """
    session = create_session()
    
    if csv_file and os.path.exists(csv_file):
        # Seed from CSV file
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                customer = Customer(
                    bill_ref=row['bill_ref'],
                    ref_type=row['ref_type'],
                    msisdn=row['msisdn'],
                    full_name=row['full_name'],
                    email=row.get('email'),
                    id_number=row.get('id_number'),
                    address=row.get('address'),
                    status=CustomerStatus[row.get('status', 'ACTIVE').upper()]
                )
                session.add(customer)
        
        print(f"Seeded customers from {csv_file}")
    else:
        # Seed with sample data
        sample_customers = [
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
                status=CustomerStatus.ACTIVE
            ),
            Customer(
                bill_ref="POL567890",
                ref_type="POLICY",
                msisdn="254745678901",
                full_name="Alice Brown",
                email="alice.brown@example.com",
                id_number="34567890",
                address="012 Pine St, Nairobi",
                status=CustomerStatus.ACTIVE
            ),
            Customer(
                bill_ref="MSI678901",
                ref_type="MSISDN",
                msisdn="254756789012",
                full_name="Charlie Wilson",
                email="charlie.wilson@example.com",
                id_number="45678901",
                address="345 Elm St, Nairobi",
                status=CustomerStatus.ACTIVE
            )
        ]
        
        for customer in sample_customers:
            session.add(customer)
        
        print("Seeded customers with sample data")
    
    session.commit()
    session.close()

def seed_users():
    """Seed the users table with sample data."""
    session = create_session()
    
    # Create admin user
    admin_user = User(
        username="admin",
        password_hash=get_password_hash("admin123"),
        email="admin@example.com",
        is_active=True
    )
    
    # Create API user
    api_user = User(
        username="airtel_api",
        password_hash=get_password_hash("airtel123"),
        email="api@example.com",
        is_active=True
    )
    
    session.add(admin_user)
    session.add(api_user)
    session.commit()
    
    print("Seeded users with sample data")
    session.close()

def export_customers_template(output_file):
    """
    Export a template CSV file for customer data.
    
    Args:
        output_file (str): Path to output CSV file.
    """
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'bill_ref', 'ref_type', 'msisdn', 'full_name', 
            'email', 'id_number', 'address', 'status'
        ])
        # Add a sample row
        writer.writerow([
            'ACC123456', 'ACCOUNT', '254712345678', 'John Doe',
            'john.doe@example.com', '12345678', '123 Main St, Nairobi', 'ACTIVE'
        ])
    
    print(f"Exported customer template to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database for Airtel Kenya C2B IPN system")
    parser.add_argument('--customers', action='store_true', help='Seed customers table')
    parser.add_argument('--users', action='store_true', help='Seed users table')
    parser.add_argument('--all', action='store_true', help='Seed all tables')
    parser.add_argument('--csv', type=str, help='CSV file with customer data')
    parser.add_argument('--template', type=str, help='Export customer template to CSV file')
    
    args = parser.parse_args()
    
    if args.template:
        export_customers_template(args.template)
    elif args.all:
        seed_customers(args.csv)
        seed_users()
    elif args.customers:
        seed_customers(args.csv)
    elif args.users:
        seed_users()
    else:
        parser.print_help()
