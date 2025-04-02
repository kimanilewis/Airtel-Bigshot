#!/usr/bin/env python3
"""
Create ERD diagram for Airtel Kenya C2B IPN System
"""
from diagrams import Diagram
from diagrams.custom import Custom
import os

# Create a directory for the ERD diagram
os.makedirs("diagrams", exist_ok=True)

# Create a simple text-based ERD
with open("diagrams/database_erd.txt", "w") as f:
    f.write("""
+------------------------+       +------------------------+       +------------------------+
|      Transaction       |       |   ValidationResult    |       |    ProcessingResult    |
+------------------------+       +------------------------+       +------------------------+
| id (PK)                |       | id (PK)               |       | id (PK)                |
| transaction_id         |       | transaction_id (FK)   |       | transaction_id (FK)    |
| bill_ref               |       | is_valid              |       | is_processed           |
| ref_type               |       | validation_message    |       | processing_message     |
| amount                 |       | validation_date       |       | processing_date        |
| msisdn                 |       +------------------------+       +------------------------+
| payment_date           |                |                                |
| currency               |                |                                |
| status                 |                |                                |
| raw_payload            |                |                                |
| created_at             |                |                                |
| updated_at             |                |                                |
+------------------------+                |                                |
        | 1                               |                                |
        |                                 |                                |
        | 0..*                            | 0..*                           | 0..*
+-------v-----------------+  +------------v-------------+  +---------------v--------+
| Transaction has many    |  | Transaction has many     |  | Transaction has many   |
| ValidationResults       |  | ValidationResults        |  | ProcessingResults      |
+------------------------+   +------------------------+   +------------------------+
""")

# Create a more visual ERD using graphviz
with Diagram("Airtel Kenya C2B IPN Database ERD", filename="diagrams/database_erd", show=False):
    # This is a placeholder. In a real environment, we would create a proper graphviz diagram
    # but for simplicity, we'll just use the text-based ERD above
    pass

print("ERD diagram created in diagrams directory")
