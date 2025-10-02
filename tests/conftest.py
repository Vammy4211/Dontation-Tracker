"""
Test configuration and fixtures for the donation tracker application.

This module provides common fixtures and configuration for all tests.
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta

# Add the app directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.user import User
from app.models.donor import Donor  
from app.models.admin import Admin
from app.models.campaign import Campaign
from app.models.donation import Donation
from app.services.user_factory import UserFactory
from app.services.database_manager import DatabaseManager
from app.services.repositories import CampaignRepository, DonationRepository, UserRepository


@pytest.fixture
def mock_database():
    """Mock database for testing."""
    mock_db = Mock()
    mock_collection = Mock()
    mock_db.__getitem__.return_value = mock_collection
    return mock_db


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'password123',
        'phone': '+1234567890'
    }


@pytest.fixture
def sample_donor(sample_user_data):
    """Create a sample donor for testing."""
    return Donor(
        name=sample_user_data['name'],
        email=sample_user_data['email'],
        password=sample_user_data['password'],
        phone=sample_user_data['phone']
    )


@pytest.fixture
def sample_admin(sample_user_data):
    """Create a sample admin for testing."""
    admin_data = sample_user_data.copy()
    admin_data['name'] = 'Admin User'
    admin_data['email'] = 'admin@example.com'
    return Admin(
        name=admin_data['name'],
        email=admin_data['email'],
        password=admin_data['password'],
        phone=admin_data['phone']
    )


@pytest.fixture
def sample_campaign_data():
    """Sample campaign data for testing."""
    return {
        'title': 'Help Local School',
        'description': 'Raise funds for school supplies and equipment for underprivileged children.',
        'goal_amount': 5000.0,
        'creator_id': 'user123',
        'category': 'education',
        'end_date': datetime.utcnow() + timedelta(days=30)
    }


@pytest.fixture
def sample_campaign(sample_campaign_data):
    """Create a sample campaign for testing."""
    return Campaign(
        title=sample_campaign_data['title'],
        description=sample_campaign_data['description'],
        goal_amount=sample_campaign_data['goal_amount'],
        creator_id=sample_campaign_data['creator_id'],
        category=sample_campaign_data['category'],
        end_date=sample_campaign_data['end_date']
    )


@pytest.fixture
def sample_donation_data():
    """Sample donation data for testing."""
    return {
        'campaign_id': 'campaign123',
        'donor_id': 'donor123',
        'amount': 100.0,
        'message': 'Great cause!',
        'anonymous': False
    }


@pytest.fixture
def sample_donation(sample_donation_data):
    """Create a sample donation for testing."""
    return Donation(
        campaign_id=sample_donation_data['campaign_id'],
        donor_id=sample_donation_data['donor_id'],
        amount=sample_donation_data['amount'],
        message=sample_donation_data['message'],
        anonymous=sample_donation_data['anonymous']
    )


@pytest.fixture
def user_factory():
    """User factory instance for testing."""
    return UserFactory()


@pytest.fixture
def mock_campaign_repository(mock_database):
    """Mock campaign repository for testing."""
    return CampaignRepository(mock_database)


@pytest.fixture
def mock_donation_repository(mock_database):
    """Mock donation repository for testing."""
    return DonationRepository(mock_database)


@pytest.fixture
def mock_user_repository(mock_database):
    """Mock user repository for testing."""
    return UserRepository(mock_database)


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset singleton instances between tests."""
    # Reset DatabaseManager singleton
    if hasattr(DatabaseManager, '_instances'):
        DatabaseManager._instances.clear()
    if hasattr(DatabaseManager, '_instance'):
        DatabaseManager._instance = None
    
    yield
    
    # Clean up after test
    if hasattr(DatabaseManager, '_instances'):
        DatabaseManager._instances.clear()
    if hasattr(DatabaseManager, '_instance'):
        DatabaseManager._instance = None


@pytest.fixture
def mock_payment_data():
    """Sample payment data for testing."""
    return {
        'method': 'credit_card',
        'card_number': '1234567890123456',
        'expiry_month': '12',
        'expiry_year': '2025',
        'cvv': '123',
        'cardholder_name': 'John Doe'
    }


@pytest.fixture
def mock_event_manager():
    """Mock event manager for testing."""
    mock = Mock()
    mock.notify_donation_completed = Mock()
    mock.notify_donation_pending_review = Mock()
    mock.notify_campaign_goal_reached = Mock()
    mock.notify_campaign_created = Mock()
    mock.notify_user_registered = Mock()
    return mock


@pytest.fixture
def mock_payment_processor():
    """Mock payment processor for testing."""
    mock = Mock()
    mock.process_payment = Mock(return_value={
        'success': True,
        'transaction_id': 'test_transaction_123',
        'amount': 100.0,
        'fee': 3.0,
        'net_amount': 97.0,
        'payment_method': 'credit_card'
    })
    mock.get_available_payment_methods = Mock(return_value={
        'credit_card': 'Credit Card',
        'paypal': 'PayPal',
        'bank_transfer': 'Bank Transfer'
    })
    mock.validate_payment_data = Mock(return_value=True)
    return mock


@pytest.fixture
def mock_cache():
    """Mock cache for testing."""
    cache_data = {}
    
    mock = Mock()
    mock.get = Mock(side_effect=lambda key: cache_data.get(key))
    mock.set = Mock(side_effect=lambda key, value, ttl=300: cache_data.update({key: value}))
    mock.delete = Mock(side_effect=lambda key: cache_data.pop(key, None))
    mock.clear = Mock(side_effect=lambda: cache_data.clear())
    mock.exists = Mock(side_effect=lambda key: key in cache_data)
    
    return mock


class MockObjectId:
    """Mock ObjectId for testing."""
    
    def __init__(self, oid=None):
        self._id = oid or 'mock_object_id_123'
    
    def __str__(self):
        return self._id
    
    def __eq__(self, other):
        if isinstance(other, MockObjectId):
            return self._id == other._id
        return self._id == str(other)


# Test utilities
def assert_model_equality(model1, model2, exclude_fields=None):
    """Assert that two model instances are equal, excluding specified fields."""
    exclude_fields = exclude_fields or ['created_at', 'updated_at', 'id']
    
    for field in model1.__dict__:
        if field not in exclude_fields:
            assert getattr(model1, field) == getattr(model2, field), \
                f"Field {field} differs: {getattr(model1, field)} != {getattr(model2, field)}"


def create_mock_cursor(data_list):
    """Create a mock cursor that returns the given data list."""
    mock_cursor = Mock()
    mock_cursor.__iter__ = Mock(return_value=iter(data_list))
    mock_cursor.sort = Mock(return_value=mock_cursor)
    mock_cursor.limit = Mock(return_value=mock_cursor)
    mock_cursor.count = Mock(return_value=len(data_list))
    return mock_cursor