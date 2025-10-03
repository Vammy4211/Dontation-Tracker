"""
Unit tests for the Repository Pattern implementation.

Tests the repository classes and their data access functionality.
"""
import pytest
from unittest.mock import Mock, MagicMock
from bson import ObjectId
from app.services.repositories import (
    BaseRepository, CampaignRepository, DonationRepository, UserRepository
)
from app.models.campaign import Campaign
from app.models.donation import Donation
from app.models.user import User
from app.models.donor import Donor
from tests.conftest import MockObjectId, create_mock_cursor


class TestBaseRepository:
    """Test cases for BaseRepository abstract class."""
    
    def test_base_repository_is_abstract(self):
        """Test that BaseRepository cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseRepository(Mock())
    
    def test_base_repository_interface(self):
        """Test that BaseRepository defines the required interface."""
        # Check that abstract methods exist
        assert hasattr(BaseRepository, 'find_all')
        assert hasattr(BaseRepository, 'find_by_id')
        assert hasattr(BaseRepository, 'create')
        assert hasattr(BaseRepository, 'update')
        assert hasattr(BaseRepository, 'delete')


class TestCampaignRepository:
    """Test cases for CampaignRepository implementation."""
    
    def test_campaign_repository_initialization(self, mock_database):
        """Test repository initialization with database."""
        repo = CampaignRepository(mock_database)
        assert repo.db is mock_database
        assert repo.collection_name == 'campaigns'
    
    def test_find_all_campaigns(self, mock_campaign_repository, sample_campaign):
        """Test finding all campaigns."""
        # Mock database response
        campaign_data = sample_campaign.to_dict()
        campaign_data['_id'] = MockObjectId()
        
        mock_cursor = create_mock_cursor([campaign_data])
        mock_campaign_repository.collection.find.return_value = mock_cursor
        
        campaigns = mock_campaign_repository.find_all()
        
        assert len(campaigns) == 1
        assert isinstance(campaigns[0], Campaign)
        assert campaigns[0].title == sample_campaign.title
        
        mock_campaign_repository.collection.find.assert_called_once()
    
    def test_find_all_campaigns_with_limit(self, mock_campaign_repository):
        """Test finding campaigns with limit."""
        mock_cursor = create_mock_cursor([])
        mock_campaign_repository.collection.find.return_value = mock_cursor
        
        mock_campaign_repository.find_all(limit=5)
        
        mock_cursor.limit.assert_called_once_with(5)
    
    def test_find_all_campaigns_with_status_filter(self, mock_campaign_repository):
        """Test finding campaigns with status filter."""
        mock_cursor = create_mock_cursor([])
        mock_campaign_repository.collection.find.return_value = mock_cursor
        
        mock_campaign_repository.find_all(status='active')
        
        mock_campaign_repository.collection.find.assert_called_with({'status': 'active'})
    
    def test_find_campaign_by_id(self, mock_campaign_repository, sample_campaign):
        """Test finding campaign by ID."""
        campaign_id = str(MockObjectId())
        campaign_data = sample_campaign.to_dict()
        campaign_data['_id'] = MockObjectId(campaign_id)
        
        mock_campaign_repository.collection.find_one.return_value = campaign_data
        
        campaign = mock_campaign_repository.find_by_id(campaign_id)
        
        assert isinstance(campaign, Campaign)
        assert campaign.title == sample_campaign.title
        mock_campaign_repository.collection.find_one.assert_called_once_with({'_id': ObjectId(campaign_id)})
    
    def test_find_campaign_by_id_not_found(self, mock_campaign_repository):
        """Test finding non-existent campaign."""
        mock_campaign_repository.collection.find_one.return_value = None
        
        campaign = mock_campaign_repository.find_by_id('nonexistent')
        
        assert campaign is None
    
    def test_create_campaign(self, mock_campaign_repository, sample_campaign):
        """Test creating a new campaign."""
        campaign_id = MockObjectId()
        mock_campaign_repository.collection.insert_one.return_value.inserted_id = campaign_id
        
        created_campaign = mock_campaign_repository.create(sample_campaign)
        
        assert created_campaign.id == str(campaign_id)
        assert created_campaign.title == sample_campaign.title
        mock_campaign_repository.collection.insert_one.assert_called_once()
    
    def test_update_campaign(self, mock_campaign_repository, sample_campaign):
        """Test updating an existing campaign."""
        sample_campaign.id = str(MockObjectId())
        mock_campaign_repository.collection.update_one.return_value.modified_count = 1
        
        updated_campaign = mock_campaign_repository.update(sample_campaign)
        
        assert updated_campaign is sample_campaign
        mock_campaign_repository.collection.update_one.assert_called_once()
    
    def test_update_campaign_not_found(self, mock_campaign_repository, sample_campaign):
        """Test updating non-existent campaign."""
        sample_campaign.id = str(MockObjectId())
        mock_campaign_repository.collection.update_one.return_value.modified_count = 0
        
        with pytest.raises(ValueError, match="Campaign not found"):
            mock_campaign_repository.update(sample_campaign)
    
    def test_delete_campaign(self, mock_campaign_repository):
        """Test deleting a campaign."""
        campaign_id = str(MockObjectId())
        mock_campaign_repository.collection.delete_one.return_value.deleted_count = 1
        
        result = mock_campaign_repository.delete(campaign_id)
        
        assert result is True
        mock_campaign_repository.collection.delete_one.assert_called_once_with({'_id': ObjectId(campaign_id)})
    
    def test_delete_campaign_not_found(self, mock_campaign_repository):
        """Test deleting non-existent campaign."""
        mock_campaign_repository.collection.delete_one.return_value.deleted_count = 0
        
        result = mock_campaign_repository.delete('nonexistent')
        
        assert result is False
    
    def test_find_campaigns_by_creator(self, mock_campaign_repository, sample_campaign):
        """Test finding campaigns by creator ID."""
        creator_id = 'creator123'
        campaign_data = sample_campaign.to_dict()
        campaign_data['_id'] = MockObjectId()
        campaign_data['creator_id'] = creator_id
        
        mock_cursor = create_mock_cursor([campaign_data])
        mock_campaign_repository.collection.find.return_value = mock_cursor
        
        campaigns = mock_campaign_repository.find_by_creator(creator_id)
        
        assert len(campaigns) == 1
        assert campaigns[0].creator_id == creator_id
        mock_campaign_repository.collection.find.assert_called_with({'creator_id': creator_id})


class TestDonationRepository:
    """Test cases for DonationRepository implementation."""
    
    def test_donation_repository_initialization(self, mock_database):
        """Test repository initialization."""
        repo = DonationRepository(mock_database)
        assert repo.db is mock_database
        assert repo.collection_name == 'donations'
    
    def test_find_all_donations(self, mock_donation_repository, sample_donation):
        """Test finding all donations."""
        donation_data = sample_donation.to_dict()
        donation_data['_id'] = MockObjectId()
        
        mock_cursor = create_mock_cursor([donation_data])
        mock_donation_repository.collection.find.return_value = mock_cursor
        
        donations = mock_donation_repository.find_all()
        
        assert len(donations) == 1
        assert isinstance(donations[0], Donation)
        assert donations[0].amount == sample_donation.amount
    
    def test_find_donations_by_campaign(self, mock_donation_repository, sample_donation):
        """Test finding donations by campaign ID."""
        campaign_id = 'campaign123'
        donation_data = sample_donation.to_dict()
        donation_data['_id'] = MockObjectId()
        donation_data['campaign_id'] = campaign_id
        
        mock_cursor = create_mock_cursor([donation_data])
        mock_donation_repository.collection.find.return_value = mock_cursor
        
        donations = mock_donation_repository.find_by_campaign(campaign_id)
        
        assert len(donations) == 1
        assert donations[0].campaign_id == campaign_id
        mock_donation_repository.collection.find.assert_called_with({'campaign_id': campaign_id})
    
    def test_find_donations_by_donor(self, mock_donation_repository, sample_donation):
        """Test finding donations by donor ID."""
        donor_id = 'donor123'
        donation_data = sample_donation.to_dict()
        donation_data['_id'] = MockObjectId()
        donation_data['donor_id'] = donor_id
        
        mock_cursor = create_mock_cursor([donation_data])
        mock_donation_repository.collection.find.return_value = mock_cursor
        
        donations = mock_donation_repository.find_by_donor(donor_id)
        
        assert len(donations) == 1
        assert donations[0].donor_id == donor_id
        mock_donation_repository.collection.find.assert_called_with({'donor_id': donor_id})
    
    def test_create_donation(self, mock_donation_repository, sample_donation):
        """Test creating a new donation."""
        donation_id = MockObjectId()
        mock_donation_repository.collection.insert_one.return_value.inserted_id = donation_id
        
        created_donation = mock_donation_repository.create(sample_donation)
        
        assert created_donation.id == str(donation_id)
        assert created_donation.amount == sample_donation.amount
        mock_donation_repository.collection.insert_one.assert_called_once()


class TestUserRepository:
    """Test cases for UserRepository implementation."""
    
    def test_user_repository_initialization(self, mock_database):
        """Test repository initialization."""
        repo = UserRepository(mock_database)
        assert repo.db is mock_database
        assert repo.collection_name == 'users'
    
    def test_find_user_by_email(self, mock_user_repository, sample_donor):
        """Test finding user by email."""
        user_data = sample_donor.to_dict()
        user_data['_id'] = MockObjectId()
        
        mock_user_repository.collection.find_one.return_value = user_data
        
        user = mock_user_repository.find_by_email(sample_donor.email)
        
        assert isinstance(user, User)
        assert user.email == sample_donor.email
        mock_user_repository.collection.find_one.assert_called_with({'email': sample_donor.email})
    
    def test_find_user_by_email_not_found(self, mock_user_repository):
        """Test finding non-existent user by email."""
        mock_user_repository.collection.find_one.return_value = None
        
        user = mock_user_repository.find_by_email('nonexistent@example.com')
        
        assert user is None
    
    def test_create_user(self, mock_user_repository, sample_donor):
        """Test creating a new user."""
        user_id = MockObjectId()
        mock_user_repository.collection.insert_one.return_value.inserted_id = user_id
        
        created_user = mock_user_repository.create(sample_donor)
        
        assert created_user.id == str(user_id)
        assert created_user.email == sample_donor.email
        mock_user_repository.collection.insert_one.assert_called_once()


class TestRepositoryErrorHandling:
    """Test error handling in repository implementations."""
    
    def test_database_connection_error(self, mock_database):
        """Test handling of database connection errors."""
        mock_database.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception):
            CampaignRepository(mock_database)
    
    def test_invalid_object_id(self, mock_campaign_repository):
        """Test handling of invalid ObjectId."""
        with pytest.raises(Exception):
            mock_campaign_repository.find_by_id('invalid_object_id')
    
    def test_collection_operation_error(self, mock_campaign_repository):
        """Test handling of collection operation errors."""
        mock_campaign_repository.collection.find.side_effect = Exception("Collection error")
        
        with pytest.raises(Exception):
            mock_campaign_repository.find_all()


class TestRepositoryPerformance:
    """Performance tests for repository operations."""
    
    def test_batch_operations_performance(self, mock_campaign_repository):
        """Test performance of batch operations."""
        import time
        
        # Mock multiple campaigns
        campaign_data_list = [
            {'_id': MockObjectId(f'id_{i}'), 'title': f'Campaign {i}', 'description': f'Description {i}'}
            for i in range(100)
        ]
        
        mock_cursor = create_mock_cursor(campaign_data_list)
        mock_campaign_repository.collection.find.return_value = mock_cursor
        
        start_time = time.time()
        campaigns = mock_campaign_repository.find_all()
        end_time = time.time()
        
        # Should process 100 campaigns quickly
        assert end_time - start_time < 0.1  # Less than 100ms
        assert len(campaigns) == 100


class TestRepositoryIntegration:
    """Integration tests for repository pattern with other components."""
    
    def test_repository_with_models(self, mock_campaign_repository, sample_campaign):
        """Test repository integration with model classes."""
        # Test that repository correctly serializes/deserializes models
        campaign_id = MockObjectId()
        mock_campaign_repository.collection.insert_one.return_value.inserted_id = campaign_id
        
        created_campaign = mock_campaign_repository.create(sample_campaign)
        
        # Should return same type of object
        assert type(created_campaign) == type(sample_campaign)
        assert created_campaign.title == sample_campaign.title
    
    def test_repository_transaction_simulation(self, mock_campaign_repository, sample_campaign):
        """Test repository behavior in transaction-like scenarios."""
        # Simulate successful transaction
        campaign_id = MockObjectId()
        mock_campaign_repository.collection.insert_one.return_value.inserted_id = campaign_id
        mock_campaign_repository.collection.update_one.return_value.modified_count = 1
        
        # Create and immediately update
        created_campaign = mock_campaign_repository.create(sample_campaign)
        created_campaign.title = "Updated Title"
        updated_campaign = mock_campaign_repository.update(created_campaign)
        
        assert updated_campaign.title == "Updated Title"