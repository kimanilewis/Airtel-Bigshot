"""
Database repository for Airtel Kenya C2B IPN system.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionStatus
from app.models.validation import ValidationResult
from app.models.processing import ProcessingResult
from app.utils.logger import setup_logger

logger = setup_logger("db_repository")


class TransactionRepository:
    """
    Repository for Transaction model operations.
    """
    
    @staticmethod
    def create_transaction(db: Session, transaction_data: Dict[Any, Any]) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            db (Session): Database session
            transaction_data (Dict[Any, Any]): Transaction data
            
        Returns:
            Transaction: Created transaction
        """
        transaction = Transaction(
            transaction_id=transaction_data.get("transaction_id"),
            bill_ref=transaction_data.get("bill_ref"),
            ref_type=transaction_data.get("ref_type"),
            amount=float(transaction_data.get("amount", 0)),
            msisdn=transaction_data.get("msisdn"),
            payment_date=transaction_data.get("payment_date", datetime.utcnow()),
            currency=transaction_data.get("currency", "KES"),
            status=TransactionStatus.PENDING,
            raw_payload=transaction_data.get("raw_payload", "{}")
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"Created transaction with ID: {transaction.id}")
        
        return transaction
    
    @staticmethod
    def get_transaction_by_id(db: Session, transaction_id: int) -> Optional[Transaction]:
        """
        Get transaction by ID.
        
        Args:
            db (Session): Database session
            transaction_id (int): Transaction ID
            
        Returns:
            Optional[Transaction]: Transaction if found, None otherwise
        """
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    @staticmethod
    def get_transaction_by_transaction_id(db: Session, transaction_id: str) -> Optional[Transaction]:
        """
        Get transaction by transaction_id.
        
        Args:
            db (Session): Database session
            transaction_id (str): Transaction ID from Airtel
            
        Returns:
            Optional[Transaction]: Transaction if found, None otherwise
        """
        return db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    
    @staticmethod
    def get_transactions_by_bill_ref(db: Session, bill_ref: str) -> List[Transaction]:
        """
        Get transactions by bill reference.
        
        Args:
            db (Session): Database session
            bill_ref (str): Bill reference
            
        Returns:
            List[Transaction]: List of transactions
        """
        return db.query(Transaction).filter(Transaction.bill_ref == bill_ref).all()
    
    @staticmethod
    def update_transaction_status(db: Session, transaction_id: int, status: TransactionStatus) -> Optional[Transaction]:
        """
        Update transaction status.
        
        Args:
            db (Session): Database session
            transaction_id (int): Transaction ID
            status (TransactionStatus): New status
            
        Returns:
            Optional[Transaction]: Updated transaction if found, None otherwise
        """
        transaction = TransactionRepository.get_transaction_by_id(db, transaction_id)
        
        if transaction:
            transaction.status = status
            transaction.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(transaction)
            
            logger.info(f"Updated transaction {transaction_id} status to {status.value}")
            
            return transaction
        
        return None


class ValidationResultRepository:
    """
    Repository for ValidationResult model operations.
    """
    
    @staticmethod
    def create_validation_result(db: Session, transaction_id: int, is_valid: bool, message: Optional[str] = None) -> ValidationResult:
        """
        Create a new validation result.
        
        Args:
            db (Session): Database session
            transaction_id (int): Transaction ID
            is_valid (bool): Whether the transaction is valid
            message (Optional[str]): Validation message
            
        Returns:
            ValidationResult: Created validation result
        """
        validation_result = ValidationResult(
            transaction_id=transaction_id,
            is_valid=is_valid,
            validation_message=message,
            validation_date=datetime.utcnow()
        )
        
        db.add(validation_result)
        db.commit()
        db.refresh(validation_result)
        
        # Update transaction status
        transaction = TransactionRepository.get_transaction_by_id(db, transaction_id)
        if transaction:
            new_status = TransactionStatus.VALIDATED if is_valid else TransactionStatus.FAILED
            TransactionRepository.update_transaction_status(db, transaction_id, new_status)
        
        logger.info(f"Created validation result for transaction {transaction_id}: {'valid' if is_valid else 'invalid'}")
        
        return validation_result
    
    @staticmethod
    def get_validation_results_by_transaction_id(db: Session, transaction_id: int) -> List[ValidationResult]:
        """
        Get validation results by transaction ID.
        
        Args:
            db (Session): Database session
            transaction_id (int): Transaction ID
            
        Returns:
            List[ValidationResult]: List of validation results
        """
        return db.query(ValidationResult).filter(ValidationResult.transaction_id == transaction_id).all()


class ProcessingResultRepository:
    """
    Repository for ProcessingResult model operations.
    """
    
    @staticmethod
    def create_processing_result(db: Session, transaction_id: int, is_processed: bool, message: Optional[str] = None) -> ProcessingResult:
        """
        Create a new processing result.
        
        Args:
            db (Session): Database session
            transaction_id (int): Transaction ID
            is_processed (bool): Whether the transaction was processed successfully
            message (Optional[str]): Processing message
            
        Returns:
            ProcessingResult: Created processing result
        """
        processing_result = ProcessingResult(
            transaction_id=transaction_id,
            is_processed=is_processed,
            processing_message=message,
            processing_date=datetime.utcnow()
        )
        
        db.add(processing_result)
        db.commit()
        db.refresh(processing_result)
        
        # Update transaction status
        transaction = TransactionRepository.get_transaction_by_id(db, transaction_id)
        if transaction:
            new_status = TransactionStatus.PROCESSED if is_processed else TransactionStatus.FAILED
            TransactionRepository.update_transaction_status(db, transaction_id, new_status)
        
        logger.info(f"Created processing result for transaction {transaction_id}: {'processed' if is_processed else 'failed'}")
        
        return processing_result
    
    @staticmethod
    def get_processing_results_by_transaction_id(db: Session, transaction_id: int) -> List[ProcessingResult]:
        """
        Get processing results by transaction ID.
        
        Args:
            db (Session): Database session
            transaction_id (int): Transaction ID
            
        Returns:
            List[ProcessingResult]: List of processing results
        """
        return db.query(ProcessingResult).filter(ProcessingResult.transaction_id == transaction_id).all()
