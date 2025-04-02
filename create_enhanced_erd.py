#!/usr/bin/env python3
"""
Create enhanced ERD diagram for Airtel Kenya C2B IPN System with Customers table
"""
from diagrams import Diagram
from diagrams.custom import Custom
import os

# Create a directory for the ERD diagram
os.makedirs("diagrams", exist_ok=True)

# Create a text-based ERD
with open("diagrams/enhanced_database_erd.txt", "w") as f:
    f.write("""
+------------------------+       +------------------------+       +------------------------+
|       Customer         |       |      Transaction       |       |   ValidationResult    |
+------------------------+       +------------------------+       +------------------------+
| id (PK)                |       | id (PK)                |       | id (PK)               |
| bill_ref               |       | transaction_id         |       | transaction_id (FK)   |
| ref_type               |<----->| customer_id (FK)       |<----->| is_valid              |
| msisdn                 |       | bill_ref               |       | validation_message    |
| full_name              |       | ref_type               |       | validation_date       |
| email                  |       | amount                 |       +------------------------+
| id_number              |       | msisdn                 |                |
| address                |       | merchant_msisdn        |                |
| status                 |       | payment_date           |                |
| created_at             |       | currency               |                |
| updated_at             |       | status                 |                |
+------------------------+       | airtel_reference       |                |
        | 1                      | mobiquity_reference    |                |
        |                        | raw_payload            |                |
        |                        | created_at             |                |
        |                        | updated_at             |                |
        |                        +------------------------+                |
        |                                | 1                               |
        |                                |                                 |
        | 0..*                           | 0..*                            | 0..*
+-------v-----------------+  +------------v-------------+  +---------------v--------+
| Customer has many       |  | Transaction has many     |  | Transaction has many   |
| Transactions            |  | ValidationResults        |  | ValidationResults      |
+------------------------+   +------------------------+   +------------------------+

+------------------------+       +------------------------+
|   ProcessingResult     |       |         User           |
+------------------------+       +------------------------+
| id (PK)                |       | id (PK)                |
| transaction_id (FK)    |       | username               |
| is_processed           |       | password_hash          |
| processing_message     |       | email                  |
| processing_date        |       | is_active              |
+------------------------+       | created_at             |
        |                        | updated_at             |
        |                        +------------------------+
        |
        | 0..*
+-------v-----------------+
| Transaction has many    |
| ProcessingResults       |
+------------------------+
""")

# Create a more visual ERD using graphviz
with Diagram("Airtel Kenya C2B IPN Enhanced Database ERD", filename="diagrams/enhanced_database_erd", show=False):
    # This is a placeholder. In a real environment, we would create a proper graphviz diagram
    # but for simplicity, we'll just use the text-based ERD above
    pass

print("Enhanced ERD diagram created in diagrams directory")
