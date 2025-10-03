"""
Unit tests for the Strategy Pattern implementation.

Tests the sorting strategies and payment strategies.
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from app.services.strategy import (
    SortByAmountStrategy, SortByDateStrategy, SortByProgressStrategy,
    SortByDeadlineStrategy, SortByPopularityStrategy, CampaignSorter,
    CreditCardPaymentStrategy, PayPalPaymentStrategy, BankTransferPaymentStrategy,
    PaymentProcessor
)
from app.models.campaign import Campaign


class TestSortingStrategies:
    """Test cases for campaign sorting strategies."""
    
    @pytest.fixture
    def sample_campaigns(self):
        """Create sample campaigns for sorting tests."""
        campaigns = []
        
        # Campaign 1: High amount, old, low progress
        campaign1 = Mock(spec=Campaign)
        campaign1.current_amount = 1000.0
        campaign1.created_at = datetime.utcnow() - timedelta(days=30)
        campaign1.progress_percentage = 25.0
        campaign1.donation_count = 20
        campaign1.end_date = datetime.utcnow() + timedelta(days=5)
        campaigns.append(campaign1)
        
        # Campaign 2: Low amount, new, high progress
        campaign2 = Mock(spec=Campaign)
        campaign2.current_amount = 500.0
        campaign2.created_at = datetime.utcnow() - timedelta(days=5)
        campaign2.progress_percentage = 90.0
        campaign2.donation_count = 50
        campaign2.end_date = datetime.utcnow() + timedelta(days=20)
        campaigns.append(campaign2)
        
        # Campaign 3: Medium amount, medium age, medium progress
        campaign3 = Mock(spec=Campaign)
        campaign3.current_amount = 750.0
        campaign3.created_at = datetime.utcnow() - timedelta(days=15)
        campaign3.progress_percentage = 60.0
        campaign3.donation_count = 35
        campaign3.end_date = None  # No end date
        campaigns.append(campaign3)
        
        return campaigns
    
    def test_sort_by_amount_descending(self, sample_campaigns):
        """Test sorting campaigns by amount (highest first)."""
        strategy = SortByAmountStrategy(ascending=False)
        sorted_campaigns = strategy.sort(sample_campaigns)
        
        amounts = [c.current_amount for c in sorted_campaigns]
        assert amounts == [1000.0, 750.0, 500.0]
        assert strategy.get_name() == "Amount (Highest to Lowest)"
    
    def test_sort_by_amount_ascending(self, sample_campaigns):
        """Test sorting campaigns by amount (lowest first)."""
        strategy = SortByAmountStrategy(ascending=True)
        sorted_campaigns = strategy.sort(sample_campaigns)
        
        amounts = [c.current_amount for c in sorted_campaigns]
        assert amounts == [500.0, 750.0, 1000.0]
        assert strategy.get_name() == "Amount (Lowest to Highest)"
    
    def test_sort_by_date_newest_first(self, sample_campaigns):
        """Test sorting campaigns by date (newest first)."""
        strategy = SortByDateStrategy(newest_first=True)
        sorted_campaigns = strategy.sort(sample_campaigns)
        
        # Should be in order: campaign2, campaign3, campaign1
        assert sorted_campaigns[0].current_amount == 500.0  # newest
        assert sorted_campaigns[1].current_amount == 750.0  # medium
        assert sorted_campaigns[2].current_amount == 1000.0  # oldest
        assert strategy.get_name() == "Date (Newest First)"
    
    def test_sort_by_date_oldest_first(self, sample_campaigns):
        """Test sorting campaigns by date (oldest first)."""
        strategy = SortByDateStrategy(newest_first=False)
        sorted_campaigns = strategy.sort(sample_campaigns)
        
        # Should be in order: campaign1, campaign3, campaign2
        assert sorted_campaigns[0].current_amount == 1000.0  # oldest
        assert sorted_campaigns[1].current_amount == 750.0  # medium
        assert sorted_campaigns[2].current_amount == 500.0  # newest
        assert strategy.get_name() == "Date (Oldest First)"
    
    def test_sort_by_progress_highest_first(self, sample_campaigns):
        """Test sorting campaigns by progress (highest first)."""
        strategy = SortByProgressStrategy(highest_first=True)
        sorted_campaigns = strategy.sort(sample_campaigns)
        
        progress = [c.progress_percentage for c in sorted_campaigns]
        assert progress == [90.0, 60.0, 25.0]
        assert strategy.get_name() == "Progress (Highest First)"
    
    def test_sort_by_progress_lowest_first(self, sample_campaigns):
        """Test sorting campaigns by progress (lowest first)."""
        strategy = SortByProgressStrategy(highest_first=False)
        sorted_campaigns = strategy.sort(sample_campaigns)
        
        progress = [c.progress_percentage for c in sorted_campaigns]
        assert progress == [25.0, 60.0, 90.0]
        assert strategy.get_name() == "Progress (Lowest First)"
    
    def test_sort_by_deadline_urgent_first(self, sample_campaigns):
        """Test sorting campaigns by deadline (most urgent first)."""
        strategy = SortByDeadlineStrategy(urgent_first=True)
        sorted_campaigns = strategy.sort(sample_campaigns)
        
        # campaign1 (5 days), campaign2 (20 days), campaign3 (no deadline)
        assert sorted_campaigns[0].current_amount == 1000.0  # 5 days left
        assert sorted_campaigns[1].current_amount == 500.0   # 20 days left
        assert sorted_campaigns[2].current_amount == 750.0   # no deadline
        assert strategy.get_name() == "Deadline (Most Urgent First)"
    
    def test_sort_by_deadline_relaxed_first(self, sample_campaigns):
        """Test sorting campaigns by deadline (least urgent first)."""
        strategy = SortByDeadlineStrategy(urgent_first=False)
        sorted_campaigns = strategy.sort(sample_campaigns)
        
        # campaign3 (no deadline), campaign2 (20 days), campaign1 (5 days)
        assert sorted_campaigns[0].current_amount == 750.0   # no deadline
        assert sorted_campaigns[1].current_amount == 500.0   # 20 days left
        assert sorted_campaigns[2].current_amount == 1000.0  # 5 days left
        assert strategy.get_name() == "Deadline (Least Urgent First)"
    
    def test_sort_by_popularity_most_first(self, sample_campaigns):
        """Test sorting campaigns by popularity (most popular first)."""
        strategy = SortByPopularityStrategy(most_popular_first=True)
        sorted_campaigns = strategy.sort(sample_campaigns)
        
        donations = [c.donation_count for c in sorted_campaigns]
        assert donations == [50, 35, 20]
        assert strategy.get_name() == "Popularity (Most Popular First)"
    
    def test_sort_by_popularity_least_first(self, sample_campaigns):
        """Test sorting campaigns by popularity (least popular first)."""
        strategy = SortByPopularityStrategy(most_popular_first=False)
        sorted_campaigns = strategy.sort(sample_campaigns)
        
        donations = [c.donation_count for c in sorted_campaigns]
        assert donations == [20, 35, 50]
        assert strategy.get_name() == "Popularity (Least Popular First)"


class TestCampaignSorter:
    """Test cases for CampaignSorter context class."""
    
    def test_campaign_sorter_initialization(self):
        """Test CampaignSorter initialization with default strategy."""
        sorter = CampaignSorter()
        assert sorter._strategy is not None
        assert isinstance(sorter._strategy, SortByDateStrategy)
    
    def test_campaign_sorter_with_custom_strategy(self):
        """Test CampaignSorter initialization with custom strategy."""
        strategy = SortByAmountStrategy()
        sorter = CampaignSorter(strategy)
        assert sorter._strategy is strategy
    
    def test_set_strategy(self):
        """Test changing sorting strategy at runtime."""
        sorter = CampaignSorter()
        original_strategy = sorter._strategy
        
        new_strategy = SortByAmountStrategy()
        sorter.set_strategy(new_strategy)
        
        assert sorter._strategy is new_strategy
        assert sorter._strategy is not original_strategy
    
    def test_sort_campaigns(self, sample_campaigns):
        """Test sorting campaigns using the sorter."""
        sorter = CampaignSorter()
        sorter.set_strategy(SortByAmountStrategy(ascending=False))
        
        sorted_campaigns = sorter.sort_campaigns(sample_campaigns)
        amounts = [c.current_amount for c in sorted_campaigns]
        assert amounts == [1000.0, 750.0, 500.0]
    
    def test_get_current_strategy_name(self):
        """Test getting the name of current strategy."""
        sorter = CampaignSorter()
        sorter.set_strategy(SortByAmountStrategy(ascending=False))
        
        name = sorter.get_current_strategy_name()
        assert name == "Amount (Highest to Lowest)"
    
    def test_get_available_strategies(self):
        """Test getting all available strategies."""
        strategies = CampaignSorter.get_available_strategies()
        
        assert isinstance(strategies, dict)
        assert 'amount_high' in strategies
        assert 'amount_low' in strategies
        assert 'date_new' in strategies
        assert 'date_old' in strategies
        assert 'progress_high' in strategies
        assert 'progress_low' in strategies
        assert 'deadline_urgent' in strategies
        assert 'deadline_relaxed' in strategies
        assert 'popularity_high' in strategies
        assert 'popularity_low' in strategies
        
        # Check that all values are strategy instances
        for strategy in strategies.values():
            assert hasattr(strategy, 'sort')
            assert hasattr(strategy, 'get_name')


class TestPaymentStrategies:
    """Test cases for payment processing strategies."""
    
    def test_credit_card_payment_strategy(self):
        """Test credit card payment processing."""
        strategy = CreditCardPaymentStrategy()
        payment_data = {
            'card_number': '1234567890123456',
            'expiry_month': '12',
            'expiry_year': '2025',
            'cvv': '123'
        }
        
        result = strategy.process_payment(100.0, payment_data)
        
        assert result['success'] is True
        assert result['amount'] == 100.0
        assert result['fee'] == 3.0  # 3% fee
        assert result['net_amount'] == 97.0
        assert result['payment_method'] == 'credit_card'
        assert 'transaction_id' in result
        assert result['masked_card'] == '****-****-****-3456'
        assert strategy.get_payment_method_name() == "Credit Card"
    
    def test_credit_card_validation(self):
        """Test credit card payment data validation."""
        strategy = CreditCardPaymentStrategy()
        
        # Valid data
        valid_data = {
            'card_number': '1234567890123456',
            'expiry_month': '12',
            'expiry_year': '2025',
            'cvv': '123'
        }
        assert strategy.validate_payment_data(valid_data) is True
        
        # Invalid data (missing CVV)
        invalid_data = {
            'card_number': '1234567890123456',
            'expiry_month': '12',
            'expiry_year': '2025'
        }
        assert strategy.validate_payment_data(invalid_data) is False
    
    def test_paypal_payment_strategy(self):
        """Test PayPal payment processing."""
        strategy = PayPalPaymentStrategy()
        payment_data = {
            'paypal_email': 'user@example.com'
        }
        
        result = strategy.process_payment(100.0, payment_data)
        
        assert result['success'] is True
        assert result['amount'] == 100.0
        assert result['fee'] == 3.20  # 2.9% + $0.30
        assert result['net_amount'] == 96.80
        assert result['payment_method'] == 'paypal'
        assert 'transaction_id' in result
        assert result['masked_email'] == 'us***@example.com'
        assert strategy.get_payment_method_name() == "PayPal"
    
    def test_paypal_validation(self):
        """Test PayPal payment data validation."""
        strategy = PayPalPaymentStrategy()
        
        # Valid data
        valid_data = {'paypal_email': 'user@example.com'}
        assert strategy.validate_payment_data(valid_data) is True
        
        # Invalid data (missing email)
        invalid_data = {}
        assert strategy.validate_payment_data(invalid_data) is False
    
    def test_bank_transfer_payment_strategy(self):
        """Test bank transfer payment processing."""
        strategy = BankTransferPaymentStrategy()
        payment_data = {
            'account_number': '1234567890',
            'routing_number': '987654321',
            'account_holder_name': 'John Doe'
        }
        
        result = strategy.process_payment(100.0, payment_data)
        
        assert result['success'] is True
        assert result['amount'] == 100.0
        assert result['fee'] == 1.0  # 1% fee
        assert result['net_amount'] == 99.0
        assert result['payment_method'] == 'bank_transfer'
        assert 'transaction_id' in result
        assert result['masked_account'] == '****7890'
        assert strategy.get_payment_method_name() == "Bank Transfer"
    
    def test_bank_transfer_validation(self):
        """Test bank transfer payment data validation."""
        strategy = BankTransferPaymentStrategy()
        
        # Valid data
        valid_data = {
            'account_number': '1234567890',
            'routing_number': '987654321',
            'account_holder_name': 'John Doe'
        }
        assert strategy.validate_payment_data(valid_data) is True
        
        # Invalid data (missing routing number)
        invalid_data = {
            'account_number': '1234567890',
            'account_holder_name': 'John Doe'
        }
        assert strategy.validate_payment_data(invalid_data) is False


class TestPaymentProcessor:
    """Test cases for PaymentProcessor context class."""
    
    def test_payment_processor_initialization(self):
        """Test PaymentProcessor initialization."""
        processor = PaymentProcessor()
        
        assert 'credit_card' in processor._strategies
        assert 'paypal' in processor._strategies
        assert 'bank_transfer' in processor._strategies
    
    def test_process_payment_credit_card(self):
        """Test processing credit card payment through processor."""
        processor = PaymentProcessor()
        payment_data = {
            'card_number': '1234567890123456',
            'expiry_month': '12',
            'expiry_year': '2025',
            'cvv': '123'
        }
        
        result = processor.process_payment('credit_card', 100.0, payment_data)
        
        assert result['success'] is True
        assert result['payment_method'] == 'credit_card'
    
    def test_process_payment_invalid_method(self):
        """Test processing payment with invalid method."""
        processor = PaymentProcessor()
        
        with pytest.raises(ValueError, match="Unsupported payment method"):
            processor.process_payment('invalid_method', 100.0, {})
    
    def test_process_payment_invalid_data(self):
        """Test processing payment with invalid data."""
        processor = PaymentProcessor()
        
        result = processor.process_payment('credit_card', 100.0, {})
        
        assert result['success'] is False
        assert result['error'] == 'Invalid payment data'
    
    def test_get_available_payment_methods(self):
        """Test getting available payment methods."""
        processor = PaymentProcessor()
        methods = processor.get_available_payment_methods()
        
        assert isinstance(methods, dict)
        assert methods['credit_card'] == 'Credit Card'
        assert methods['paypal'] == 'PayPal'
        assert methods['bank_transfer'] == 'Bank Transfer'
    
    def test_validate_payment_data(self):
        """Test payment data validation."""
        processor = PaymentProcessor()
        
        # Valid credit card data
        valid_data = {
            'card_number': '1234567890123456',
            'expiry_month': '12',
            'expiry_year': '2025',
            'cvv': '123'
        }
        assert processor.validate_payment_data('credit_card', valid_data) is True
        
        # Invalid data
        assert processor.validate_payment_data('credit_card', {}) is False
        
        # Invalid method
        assert processor.validate_payment_data('invalid_method', valid_data) is False


class TestStrategyPatternIntegration:
    """Integration tests for strategy pattern components."""
    
    def test_strategy_switching_performance(self, sample_campaigns):
        """Test performance of strategy switching."""
        import time
        
        sorter = CampaignSorter()
        strategies = [
            SortByAmountStrategy(),
            SortByDateStrategy(),
            SortByProgressStrategy(),
            SortByPopularityStrategy()
        ]
        
        start_time = time.time()
        
        # Switch strategies and sort multiple times
        for _ in range(10):
            for strategy in strategies:
                sorter.set_strategy(strategy)
                sorted_campaigns = sorter.sort_campaigns(sample_campaigns)
                assert len(sorted_campaigns) == 3
        
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 0.1  # Less than 100ms
    
    def test_payment_strategy_error_handling(self):
        """Test error handling in payment strategies."""
        processor = PaymentProcessor()
        
        # Simulate payment processing error
        with pytest.raises(ValueError):
            processor.process_payment('unsupported_method', 100.0, {})
    
    def test_concurrent_strategy_usage(self, sample_campaigns):
        """Test concurrent usage of strategies."""
        import threading
        
        results = []
        
        def sort_campaigns():
            sorter = CampaignSorter()
            sorter.set_strategy(SortByAmountStrategy())
            sorted_campaigns = sorter.sort_campaigns(sample_campaigns)
            results.append(sorted_campaigns)
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=sort_campaigns)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All results should be the same
        assert len(results) == 5
        for result in results:
            amounts = [c.current_amount for c in result]
            assert amounts == [1000.0, 750.0, 500.0]