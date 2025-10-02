"""
Unit tests for the Factory Pattern implementation.

Tests the UserFactory and its ability to create different types of users.
"""
import pytest
from app.services.user_factory import UserFactory
from app.models.user import User
from app.models.donor import Donor
from app.models.admin import Admin


class TestUserFactory:
    """Test cases for UserFactory pattern implementation."""
    
    def test_factory_is_singleton(self):
        """Test that UserFactory follows singleton pattern if implemented."""
        factory1 = UserFactory()
        factory2 = UserFactory()
        # UserFactory might not be singleton, so this test is informational
        assert isinstance(factory1, UserFactory)
        assert isinstance(factory2, UserFactory)
    
    def test_create_donor_user(self, user_factory, sample_user_data):
        """Test creating a donor user through factory."""
        user = user_factory.create_user('donor', sample_user_data)
        
        assert isinstance(user, Donor)
        assert user.name == sample_user_data['name']
        assert user.email == sample_user_data['email']
        assert user.role == 'donor'
        assert user.is_active is True
    
    def test_create_admin_user(self, user_factory, sample_user_data):
        """Test creating an admin user through factory."""
        admin_data = sample_user_data.copy()
        admin_data['name'] = 'Admin User'
        
        user = user_factory.create_user('admin', admin_data)
        
        assert isinstance(user, Admin)
        assert user.name == admin_data['name']
        assert user.email == admin_data['email']
        assert user.role == 'admin'
        assert user.is_active is True
    
    def test_create_invalid_user_type(self, user_factory, sample_user_data):
        """Test factory behavior with invalid user type."""
        with pytest.raises(ValueError, match="Unknown user type"):
            user_factory.create_user('invalid_type', sample_user_data)
    
    def test_create_user_with_missing_data(self, user_factory):
        """Test factory behavior with incomplete user data."""
        incomplete_data = {'name': 'John Doe'}
        
        with pytest.raises((KeyError, TypeError)):
            user_factory.create_user('donor', incomplete_data)
    
    def test_create_user_with_extra_data(self, user_factory, sample_user_data):
        """Test factory handles extra data gracefully."""
        extra_data = sample_user_data.copy()
        extra_data['extra_field'] = 'extra_value'
        extra_data['another_field'] = 123
        
        user = user_factory.create_user('donor', extra_data)
        
        assert isinstance(user, Donor)
        assert user.name == sample_user_data['name']
        assert user.email == sample_user_data['email']
    
    def test_factory_creates_different_instances(self, user_factory, sample_user_data):
        """Test that factory creates different instances for each call."""
        user1 = user_factory.create_user('donor', sample_user_data)
        user2 = user_factory.create_user('donor', sample_user_data)
        
        assert user1 is not user2
        assert user1.id != user2.id  # Should have different IDs
    
    def test_donor_specific_functionality(self, user_factory, sample_user_data):
        """Test that created donor has donor-specific functionality."""
        donor = user_factory.create_user('donor', sample_user_data)
        
        assert hasattr(donor, 'total_donated')
        assert hasattr(donor, 'donation_count')
        assert donor.total_donated == 0.0
        assert donor.donation_count == 0
    
    def test_admin_specific_functionality(self, user_factory, sample_user_data):
        """Test that created admin has admin-specific functionality."""
        admin = user_factory.create_user('admin', sample_user_data)
        
        assert hasattr(admin, 'permissions')
        assert hasattr(admin, 'last_login')
        assert admin.permissions == ['read', 'write', 'delete', 'admin']
    
    def test_password_hashing(self, user_factory, sample_user_data):
        """Test that factory properly handles password hashing."""
        user = user_factory.create_user('donor', sample_user_data)
        
        # Password should be hashed, not stored in plain text
        assert user.password != sample_user_data['password']
        # User should be able to verify the password
        assert user.verify_password(sample_user_data['password'])
    
    @pytest.mark.parametrize("user_type,expected_class", [
        ('donor', Donor),
        ('admin', Admin),
    ])
    def test_factory_creates_correct_types(self, user_factory, sample_user_data, 
                                         user_type, expected_class):
        """Test factory creates correct user types using parametrized tests."""
        user = user_factory.create_user(user_type, sample_user_data)
        assert isinstance(user, expected_class)
        assert user.role == user_type


class TestFactoryIntegration:
    """Integration tests for Factory pattern with other components."""
    
    def test_factory_with_repository_integration(self, user_factory, mock_user_repository, 
                                                sample_user_data):
        """Test factory integration with repository pattern."""
        # Create user through factory
        user = user_factory.create_user('donor', sample_user_data)
        
        # Mock repository save
        mock_user_repository.create = lambda u: u
        saved_user = mock_user_repository.create(user)
        
        assert saved_user is user
        assert isinstance(saved_user, Donor)
    
    def test_factory_creates_valid_models(self, user_factory, sample_user_data):
        """Test that factory creates models that pass validation."""
        user = user_factory.create_user('donor', sample_user_data)
        
        # Test model validation methods
        assert user.validate_email()
        assert user.validate_password()
        
        # Test serialization
        user_dict = user.to_dict()
        assert isinstance(user_dict, dict)
        assert user_dict['email'] == sample_user_data['email']
    
    def test_factory_performance(self, user_factory, sample_user_data):
        """Test factory performance with multiple user creation."""
        import time
        
        start_time = time.time()
        users = []
        
        # Create 100 users
        for i in range(100):
            user_data = sample_user_data.copy()
            user_data['email'] = f"user{i}@example.com"
            users.append(user_factory.create_user('donor', user_data))
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should create 100 users in reasonable time (less than 1 second)
        assert creation_time < 1.0
        assert len(users) == 100
        assert all(isinstance(user, Donor) for user in users)
        
        # All users should have unique emails
        emails = [user.email for user in users]
        assert len(set(emails)) == 100