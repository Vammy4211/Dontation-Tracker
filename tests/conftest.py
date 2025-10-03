# Basic test setup for donation tracker tests
import pytest
import sys
import os
from unittest.mock import MagicMock
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.donor import Donor
from app.models.admin import Admin
from app.models.campaign import Campaign


@pytest.fixture
def test_donor():
    # Simple donor for testing
    return {
        'username': 'john_doe',
        'email': 'john@email.com',
        'password_hash': 'hashed123',
        'anonymous_by_default': False
    }


@pytest.fixture  
def test_admin():
    # Simple admin for testing
    return {
        'username': 'admin_user',
        'email': 'admin@email.com', 
        'password_hash': 'admin_hash',
        'department': 'IT',
        'access_level': 'admin'
    }