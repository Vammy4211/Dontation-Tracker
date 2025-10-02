"""
Donation Model - Represents individual donations
"""
from typing import Dict, Optional
from datetime import datetime
from bson import ObjectId
from enum import Enum


class DonationStatus(Enum):
    """Donation status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Donation:
    """
    Donation Class - Represents a single donation transaction
    
    Encapsulates donation data and provides methods for
    donation management and tracking.
    """
    
    def __init__(self, amount: float, donor_id: str, campaign_id: str,
                 payment_method: str = "credit_card", is_anonymous: bool = False,
                 message: str = None, donation_id: Optional[str] = None):
        """
        Initialize Donation
        
        Args:
            amount: Donation amount
            donor_id: ID of the donor
            campaign_id: ID of the campaign
            payment_method: Payment method used
            is_anonymous: Whether donation should be anonymous
            message: Optional message from donor
            donation_id: Optional MongoDB ObjectId as string
        """
        self._donation_id = donation_id or str(ObjectId())
        self._amount = float(amount)
        self._donor_id = donor_id
        self._campaign_id = campaign_id
        self._payment_method = payment_method
        self._is_anonymous = is_anonymous
        self._message = message
        self._status = DonationStatus.PENDING
        self._created_at = datetime.utcnow()
        self._completed_at = None
        self._transaction_id = None
        self._receipt_id = None
        self._refund_id = None
        self._refunded_at = None
        self._fee_amount = 0.0  # Processing fee
        self._net_amount = amount  # Amount after fees
    
    # Properties with controlled access
    @property
    def donation_id(self) -> str:
        return self._donation_id
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @property
    def donor_id(self) -> str:
        return self._donor_id
    
    @property
    def campaign_id(self) -> str:
        return self._campaign_id
    
    @property
    def payment_method(self) -> str:
        return self._payment_method
    
    @property
    def is_anonymous(self) -> bool:
        return self._is_anonymous
    
    @property
    def message(self) -> Optional[str]:
        return self._message
    
    @property
    def status(self) -> DonationStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def completed_at(self) -> Optional[datetime]:
        return self._completed_at
    
    @property
    def transaction_id(self) -> Optional[str]:
        return self._transaction_id
    
    @property
    def receipt_id(self) -> Optional[str]:
        return self._receipt_id
    
    @property
    def refund_id(self) -> Optional[str]:
        return self._refund_id
    
    @property
    def refunded_at(self) -> Optional[datetime]:
        return self._refunded_at
    
    @property
    def fee_amount(self) -> float:
        return self._fee_amount
    
    @property
    def net_amount(self) -> float:
        return self._net_amount
    
    # Calculated properties
    @property
    def is_completed(self) -> bool:
        """Check if donation is completed"""
        return self._status == DonationStatus.COMPLETED
    
    @property
    def is_refunded(self) -> bool:
        """Check if donation has been refunded"""
        return self._status == DonationStatus.REFUNDED
    
    @property
    def can_be_refunded(self) -> bool:
        """Check if donation can be refunded"""
        return (self._status == DonationStatus.COMPLETED and 
                self._refunded_at is None)
    
    # Donation management methods
    def set_transaction_details(self, transaction_id: str, fee_amount: float = 0.0) -> None:
        """
        Set transaction details after payment processing
        
        Args:
            transaction_id: Payment processor transaction ID
            fee_amount: Processing fee amount
        """
        self._transaction_id = transaction_id
        self._fee_amount = fee_amount
        self._net_amount = self._amount - fee_amount
    
    def generate_receipt_id(self) -> str:
        """Generate a receipt ID for this donation"""
        if not self._receipt_id:
            # Format: ORD-YYYYMMDD-XXXX
            date_part = self._created_at.strftime('%Y%m%d')
            id_part = self._donation_id[-4:].upper()
            self._receipt_id = f"ORD-{date_part}-{id_part}"
        return self._receipt_id
    
    def complete_donation(self, transaction_id: str = None) -> bool:
        """
        Mark donation as completed
        
        Args:
            transaction_id: Optional transaction ID from payment processor
            
        Returns:
            True if donation was successfully completed
        """
        if self._status == DonationStatus.PENDING:
            self._status = DonationStatus.COMPLETED
            self._completed_at = datetime.utcnow()
            if transaction_id:
                self._transaction_id = transaction_id
            self.generate_receipt_id()
            return True
        return False
    
    def fail_donation(self, reason: str = None) -> bool:
        """
        Mark donation as failed
        
        Args:
            reason: Optional reason for failure
            
        Returns:
            True if donation was successfully marked as failed
        """
        if self._status == DonationStatus.PENDING:
            self._status = DonationStatus.FAILED
            if reason:
                self._message = f"Failed: {reason}"
            return True
        return False
    
    def refund_donation(self, refund_id: str = None) -> bool:
        """
        Process refund for this donation
        
        Args:
            refund_id: Optional refund transaction ID
            
        Returns:
            True if refund was successfully processed
        """
        if self.can_be_refunded:
            self._status = DonationStatus.REFUNDED
            self._refunded_at = datetime.utcnow()
            self._refund_id = refund_id
            return True
        return False
    
    def update_anonymity(self, is_anonymous: bool) -> None:
        """Update anonymity setting for this donation"""
        self._is_anonymous = is_anonymous
    
    def update_message(self, message: str) -> None:
        """Update donation message"""
        self._message = message
    
    def get_display_info(self, show_donor_name: bool = True) -> Dict:
        """
        Get donation info for display purposes
        
        Args:
            show_donor_name: Whether to include donor information
            
        Returns:
            Dictionary with display-appropriate donation info
        """
        info = {
            'donation_id': self._donation_id,
            'amount': self._amount,
            'campaign_id': self._campaign_id,
            'is_anonymous': self._is_anonymous,
            'message': self._message,
            'status': self._status.value,
            'created_at': self._created_at,
            'completed_at': self._completed_at
        }
        
        if show_donor_name and not self._is_anonymous:
            info['donor_id'] = self._donor_id
        
        return info
    
    def get_receipt_data(self) -> Dict:
        """Get receipt data for this donation"""
        return {
            'receipt_id': self.generate_receipt_id(),
            'donation_id': self._donation_id,
            'amount': self._amount,
            'fee_amount': self._fee_amount,
            'net_amount': self._net_amount,
            'campaign_id': self._campaign_id,
            'donor_id': self._donor_id,
            'payment_method': self._payment_method,
            'transaction_id': self._transaction_id,
            'completed_at': self._completed_at,
            'status': self._status.value
        }
    
    def to_dict(self) -> Dict:
        """Convert donation to dictionary for database storage"""
        return {
            '_id': ObjectId(self._donation_id),
            'amount': self._amount,
            'donor_id': self._donor_id,
            'campaign_id': self._campaign_id,
            'payment_method': self._payment_method,
            'is_anonymous': self._is_anonymous,
            'message': self._message,
            'status': self._status.value,
            'created_at': self._created_at,
            'completed_at': self._completed_at,
            'transaction_id': self._transaction_id,
            'receipt_id': self._receipt_id,
            'refund_id': self._refund_id,
            'refunded_at': self._refunded_at,
            'fee_amount': self._fee_amount,
            'net_amount': self._net_amount
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Donation':
        """Create Donation instance from dictionary data"""
        donation = cls(
            amount=data['amount'],
            donor_id=data['donor_id'],
            campaign_id=data['campaign_id'],
            payment_method=data.get('payment_method', 'credit_card'),
            is_anonymous=data.get('is_anonymous', False),
            message=data.get('message'),
            donation_id=str(data['_id'])
        )
        
        # Set additional attributes
        donation._status = DonationStatus(data.get('status', 'pending'))
        donation._created_at = data.get('created_at', datetime.utcnow())
        donation._completed_at = data.get('completed_at')
        donation._transaction_id = data.get('transaction_id')
        donation._receipt_id = data.get('receipt_id')
        donation._refund_id = data.get('refund_id')
        donation._refunded_at = data.get('refunded_at')
        donation._fee_amount = data.get('fee_amount', 0.0)
        donation._net_amount = data.get('net_amount', donation._amount)
        
        return donation
    
    def __str__(self) -> str:
        return f"Donation: ${self._amount:.2f} to campaign {self._campaign_id} ({self._status.value})"
    
    def __repr__(self) -> str:
        return f"Donation(amount=${self._amount}, status='{self._status.value}', donor_id='{self._donor_id}')"