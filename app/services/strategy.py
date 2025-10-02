"""
Strategy Pattern - Campaign Sorting and Payment Strategies

The Strategy Pattern defines a family of algorithms, encapsulates each one,
and makes them interchangeable at runtime.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from ..models.campaign import Campaign


class SortingStrategy(ABC):
    """
    STRATEGY PATTERN - Abstract Sorting Strategy
    
    Defines the interface for different campaign sorting algorithms.
    This allows for flexible sorting behavior that can be changed at runtime.
    """
    
    @abstractmethod
    def sort(self, campaigns: List[Campaign]) -> List[Campaign]:
        """
        Sort campaigns using this strategy
        
        Args:
            campaigns: List of campaigns to sort
            
        Returns:
            Sorted list of campaigns
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get human-readable name of this sorting strategy"""
        pass


class SortByAmountStrategy(SortingStrategy):
    """
    STRATEGY PATTERN - Sort campaigns by donation amount
    """
    
    def __init__(self, ascending: bool = False):
        """
        Initialize sorting strategy
        
        Args:
            ascending: If True, sort from lowest to highest amount
        """
        self.ascending = ascending
    
    def sort(self, campaigns: List[Campaign]) -> List[Campaign]:
        """Sort campaigns by current donation amount"""
        return sorted(
            campaigns,
            key=lambda c: c.current_amount,
            reverse=not self.ascending
        )
    
    def get_name(self) -> str:
        direction = "Lowest to Highest" if self.ascending else "Highest to Lowest"
        return f"Amount ({direction})"


class SortByDateStrategy(SortingStrategy):
    """
    STRATEGY PATTERN - Sort campaigns by creation date
    """
    
    def __init__(self, newest_first: bool = True):
        """
        Initialize sorting strategy
        
        Args:
            newest_first: If True, sort newest campaigns first
        """
        self.newest_first = newest_first
    
    def sort(self, campaigns: List[Campaign]) -> List[Campaign]:
        """Sort campaigns by creation date"""
        return sorted(
            campaigns,
            key=lambda c: c.created_at,
            reverse=self.newest_first
        )
    
    def get_name(self) -> str:
        direction = "Newest First" if self.newest_first else "Oldest First"
        return f"Date ({direction})"


class SortByProgressStrategy(SortingStrategy):
    """
    STRATEGY PATTERN - Sort campaigns by progress percentage
    """
    
    def __init__(self, highest_first: bool = True):
        """
        Initialize sorting strategy
        
        Args:
            highest_first: If True, sort highest progress first
        """
        self.highest_first = highest_first
    
    def sort(self, campaigns: List[Campaign]) -> List[Campaign]:
        """Sort campaigns by progress percentage"""
        return sorted(
            campaigns,
            key=lambda c: c.progress_percentage,
            reverse=self.highest_first
        )
    
    def get_name(self) -> str:
        direction = "Highest First" if self.highest_first else "Lowest First"
        return f"Progress ({direction})"


class SortByDeadlineStrategy(SortingStrategy):
    """
    STRATEGY PATTERN - Sort campaigns by deadline urgency
    """
    
    def __init__(self, urgent_first: bool = True):
        """
        Initialize sorting strategy
        
        Args:
            urgent_first: If True, sort most urgent deadlines first
        """
        self.urgent_first = urgent_first
    
    def sort(self, campaigns: List[Campaign]) -> List[Campaign]:
        """Sort campaigns by deadline urgency"""
        # Separate campaigns with and without deadlines
        with_deadline = [c for c in campaigns if c.end_date]
        without_deadline = [c for c in campaigns if not c.end_date]
        
        # Sort campaigns with deadlines by days remaining
        with_deadline.sort(
            key=lambda c: (c.end_date - datetime.utcnow()).days,
            reverse=not self.urgent_first
        )
        
        # Combine lists (campaigns without deadlines go to end)
        if self.urgent_first:
            return with_deadline + without_deadline
        else:
            return without_deadline + with_deadline
    
    def get_name(self) -> str:
        direction = "Most Urgent First" if self.urgent_first else "Least Urgent First"
        return f"Deadline ({direction})"


class SortByPopularityStrategy(SortingStrategy):
    """
    STRATEGY PATTERN - Sort campaigns by popularity (donation count)
    """
    
    def __init__(self, most_popular_first: bool = True):
        """
        Initialize sorting strategy
        
        Args:
            most_popular_first: If True, sort most popular first
        """
        self.most_popular_first = most_popular_first
    
    def sort(self, campaigns: List[Campaign]) -> List[Campaign]:
        """Sort campaigns by donation count"""
        return sorted(
            campaigns,
            key=lambda c: c.donation_count,
            reverse=self.most_popular_first
        )
    
    def get_name(self) -> str:
        direction = "Most Popular First" if self.most_popular_first else "Least Popular First"
        return f"Popularity ({direction})"


class CampaignSorter:
    """
    STRATEGY PATTERN - Context class for campaign sorting
    
    Uses different sorting strategies to sort campaigns.
    The strategy can be changed at runtime.
    """
    
    def __init__(self, strategy: SortingStrategy = None):
        """
        Initialize sorter with a strategy
        
        Args:
            strategy: Initial sorting strategy (defaults to SortByDateStrategy)
        """
        self._strategy = strategy or SortByDateStrategy()
    
    def set_strategy(self, strategy: SortingStrategy) -> None:
        """
        Change the sorting strategy
        
        Args:
            strategy: New sorting strategy to use
        """
        self._strategy = strategy
    
    def sort_campaigns(self, campaigns: List[Campaign]) -> List[Campaign]:
        """
        Sort campaigns using the current strategy
        
        Args:
            campaigns: List of campaigns to sort
            
        Returns:
            Sorted list of campaigns
        """
        return self._strategy.sort(campaigns)
    
    def get_current_strategy_name(self) -> str:
        """
        Get the name of the current sorting strategy
        
        Returns:
            Human-readable strategy name
        """
        return self._strategy.get_name()
    
    @staticmethod
    def get_available_strategies() -> Dict[str, SortingStrategy]:
        """
        Get all available sorting strategies
        
        Returns:
            Dictionary of strategy name to strategy instance
        """
        return {
            'amount_high': SortByAmountStrategy(ascending=False),
            'amount_low': SortByAmountStrategy(ascending=True),
            'date_new': SortByDateStrategy(newest_first=True),
            'date_old': SortByDateStrategy(newest_first=False),
            'progress_high': SortByProgressStrategy(highest_first=True),
            'progress_low': SortByProgressStrategy(highest_first=False),
            'deadline_urgent': SortByDeadlineStrategy(urgent_first=True),
            'deadline_relaxed': SortByDeadlineStrategy(urgent_first=False),
            'popularity_high': SortByPopularityStrategy(most_popular_first=True),
            'popularity_low': SortByPopularityStrategy(most_popular_first=False)
        }


# Payment Strategy Pattern
class PaymentStrategy(ABC):
    """
    STRATEGY PATTERN - Abstract Payment Strategy
    
    Defines the interface for different payment processing methods.
    """
    
    @abstractmethod
    def process_payment(self, amount: float, payment_data: Dict) -> Dict[str, Any]:
        """
        Process payment using this strategy
        
        Args:
            amount: Payment amount
            payment_data: Payment-specific data
            
        Returns:
            Payment result with transaction details
        """
        pass
    
    @abstractmethod
    def validate_payment_data(self, payment_data: Dict) -> bool:
        """
        Validate payment data for this strategy
        
        Args:
            payment_data: Payment data to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_payment_method_name(self) -> str:
        """Get the name of this payment method"""
        pass


class CreditCardPaymentStrategy(PaymentStrategy):
    """
    STRATEGY PATTERN - Credit Card Payment Implementation
    """
    
    def process_payment(self, amount: float, payment_data: Dict) -> Dict[str, Any]:
        """Process credit card payment"""
        # Simulate credit card processing
        card_number = payment_data.get('card_number', '')
        masked_card = f"****-****-****-{card_number[-4:]}" if len(card_number) >= 4 else "****"
        
        # Simulate processing fee (3%)
        fee = amount * 0.03
        net_amount = amount - fee
        
        # Simulate transaction ID
        import uuid
        transaction_id = f"cc_{uuid.uuid4().hex[:8]}"
        
        return {
            'success': True,
            'transaction_id': transaction_id,
            'amount': amount,
            'fee': fee,
            'net_amount': net_amount,
            'payment_method': 'credit_card',
            'masked_card': masked_card,
            'processed_at': datetime.utcnow()
        }
    
    def validate_payment_data(self, payment_data: Dict) -> bool:
        """Validate credit card data"""
        required_fields = ['card_number', 'expiry_month', 'expiry_year', 'cvv']
        return all(field in payment_data for field in required_fields)
    
    def get_payment_method_name(self) -> str:
        return "Credit Card"


class PayPalPaymentStrategy(PaymentStrategy):
    """
    STRATEGY PATTERN - PayPal Payment Implementation
    """
    
    def process_payment(self, amount: float, payment_data: Dict) -> Dict[str, Any]:
        """Process PayPal payment"""
        email = payment_data.get('paypal_email', '')
        masked_email = f"{email.split('@')[0][:2]}***@{email.split('@')[1]}" if '@' in email else "***"
        
        # Simulate processing fee (2.9% + $0.30)
        fee = amount * 0.029 + 0.30
        net_amount = amount - fee
        
        # Simulate transaction ID
        import uuid
        transaction_id = f"pp_{uuid.uuid4().hex[:8]}"
        
        return {
            'success': True,
            'transaction_id': transaction_id,
            'amount': amount,
            'fee': fee,
            'net_amount': net_amount,
            'payment_method': 'paypal',
            'masked_email': masked_email,
            'processed_at': datetime.utcnow()
        }
    
    def validate_payment_data(self, payment_data: Dict) -> bool:
        """Validate PayPal data"""
        required_fields = ['paypal_email']
        return all(field in payment_data for field in required_fields)
    
    def get_payment_method_name(self) -> str:
        return "PayPal"


class BankTransferPaymentStrategy(PaymentStrategy):
    """
    STRATEGY PATTERN - Bank Transfer Payment Implementation
    """
    
    def process_payment(self, amount: float, payment_data: Dict) -> Dict[str, Any]:
        """Process bank transfer payment"""
        account_number = payment_data.get('account_number', '')
        masked_account = f"****{account_number[-4:]}" if len(account_number) >= 4 else "****"
        
        # Simulate processing fee (1%)
        fee = amount * 0.01
        net_amount = amount - fee
        
        # Simulate transaction ID
        import uuid
        transaction_id = f"bt_{uuid.uuid4().hex[:8]}"
        
        return {
            'success': True,
            'transaction_id': transaction_id,
            'amount': amount,
            'fee': fee,
            'net_amount': net_amount,
            'payment_method': 'bank_transfer',
            'masked_account': masked_account,
            'processed_at': datetime.utcnow()
        }
    
    def validate_payment_data(self, payment_data: Dict) -> bool:
        """Validate bank transfer data"""
        required_fields = ['account_number', 'routing_number', 'account_holder_name']
        return all(field in payment_data for field in required_fields)
    
    def get_payment_method_name(self) -> str:
        return "Bank Transfer"


class PaymentProcessor:
    """
    STRATEGY PATTERN - Context class for payment processing
    
    Uses different payment strategies to process payments.
    """
    
    def __init__(self):
        self._strategies = {
            'credit_card': CreditCardPaymentStrategy(),
            'paypal': PayPalPaymentStrategy(),
            'bank_transfer': BankTransferPaymentStrategy()
        }
    
    def process_payment(self, payment_method: str, amount: float, payment_data: Dict) -> Dict[str, Any]:
        """
        Process payment using the specified method
        
        Args:
            payment_method: Payment method to use
            amount: Payment amount
            payment_data: Payment-specific data
            
        Returns:
            Payment result
            
        Raises:
            ValueError: If payment method is not supported
        """
        if payment_method not in self._strategies:
            raise ValueError(f"Unsupported payment method: {payment_method}")
        
        strategy = self._strategies[payment_method]
        
        # Validate payment data
        if not strategy.validate_payment_data(payment_data):
            return {
                'success': False,
                'error': 'Invalid payment data',
                'payment_method': payment_method
            }
        
        try:
            return strategy.process_payment(amount, payment_data)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'payment_method': payment_method
            }
    
    def get_available_payment_methods(self) -> Dict[str, str]:
        """
        Get available payment methods
        
        Returns:
            Dictionary of method key to method name
        """
        return {
            key: strategy.get_payment_method_name()
            for key, strategy in self._strategies.items()
        }
    
    def validate_payment_data(self, payment_method: str, payment_data: Dict) -> bool:
        """
        Validate payment data for a specific method
        
        Args:
            payment_method: Payment method
            payment_data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if payment_method not in self._strategies:
            return False
        
        return self._strategies[payment_method].validate_payment_data(payment_data)


# Usage examples:
"""
# Campaign Sorting Strategy
sorter = CampaignSorter()

# Sort by amount (highest first)
sorter.set_strategy(SortByAmountStrategy(ascending=False))
sorted_campaigns = sorter.sort_campaigns(campaigns)

# Change strategy to sort by date
sorter.set_strategy(SortByDateStrategy(newest_first=True))
sorted_campaigns = sorter.sort_campaigns(campaigns)

# Payment Processing Strategy
processor = PaymentProcessor()

# Process credit card payment
result = processor.process_payment('credit_card', 100.0, {
    'card_number': '1234567890123456',
    'expiry_month': '12',
    'expiry_year': '2025',
    'cvv': '123'
})

# Process PayPal payment
result = processor.process_payment('paypal', 50.0, {
    'paypal_email': 'user@example.com'
})
"""