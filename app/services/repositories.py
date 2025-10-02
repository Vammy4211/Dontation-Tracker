"""
Repository Pattern - Abstract Base Repository and Implementations

The Repository Pattern abstracts data access logic and provides
a more object-oriented view of the persistence layer.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo.collection import Collection
from ..services.database_manager import get_collection
from ..models.user import User
from ..models.donor import Donor
from ..models.admin import Admin
from ..models.campaign import Campaign
from ..models.donation import Donation


class BaseRepository(ABC):
    """
    REPOSITORY PATTERN - Abstract Base Repository
    
    Defines the interface for all repositories and provides
    common database operations. This pattern separates
    business logic from data access logic.
    
    Benefits:
    - Separation of concerns
    - Testability (can mock repositories)
    - Consistent data access interface
    - Easy to switch database implementations
    """
    
    def __init__(self, collection_name: str):
        """
        Initialize repository with collection name
        
        Args:
            collection_name: Name of the MongoDB collection
        """
        self._collection_name = collection_name
        self._collection: Optional[Collection] = None
    
    @property
    def collection(self) -> Collection:
        """Get MongoDB collection (lazy loading)"""
        if self._collection is None:
            self._collection = get_collection(self._collection_name)
        return self._collection
    
    @abstractmethod
    def create(self, entity: Any) -> str:
        """Create a new entity"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[Any]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    def update(self, entity: Any) -> bool:
        """Update an existing entity"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    def get_all(self, **filters) -> List[Any]:
        """Get all entities with optional filters"""
        pass
    
    def exists(self, entity_id: str) -> bool:
        """Check if entity exists"""
        return self.collection.count_documents({'_id': ObjectId(entity_id)}) > 0
    
    def count(self, **filters) -> int:
        """Count entities with optional filters"""
        query = self._build_query(filters)
        return self.collection.count_documents(query)
    
    def _build_query(self, filters: Dict) -> Dict:
        """Build MongoDB query from filters"""
        query = {}
        for key, value in filters.items():
            if key == 'id':
                query['_id'] = ObjectId(value)
            else:
                query[key] = value
        return query


class UserRepository(BaseRepository):
    """
    REPOSITORY PATTERN - User Repository Implementation
    
    Handles all user-related database operations including
    both Donor and Admin users.
    """
    
    def __init__(self):
        super().__init__('users')
    
    def create(self, user: User) -> str:
        """
        Create a new user
        
        Args:
            user: User instance to create
            
        Returns:
            Created user ID
        """
        user_data = user.to_dict()
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User instance or None if not found
        """
        try:
            user_data = self.collection.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return self._create_user_from_data(user_data)
            return None
        except Exception:
            return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address
        
        Args:
            email: Email address to search for
            
        Returns:
            User instance or None if not found
        """
        user_data = self.collection.find_one({'email': email})
        if user_data:
            return self._create_user_from_data(user_data)
        return None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username to search for
            
        Returns:
            User instance or None if not found
        """
        user_data = self.collection.find_one({'username': username})
        if user_data:
            return self._create_user_from_data(user_data)
        return None
    
    def update(self, user: User) -> bool:
        """
        Update an existing user
        
        Args:
            user: User instance with updated data
            
        Returns:
            True if update successful, False otherwise
        """
        user_data = user.to_dict()
        user_id = user_data.pop('_id')
        
        result = self.collection.update_one(
            {'_id': user_id},
            {'$set': user_data}
        )
        return result.modified_count > 0
    
    def delete(self, user_id: str) -> bool:
        """
        Delete user by ID (soft delete - deactivate)
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        result = self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'is_active': False}}
        )
        return result.modified_count > 0
    
    def hard_delete(self, user_id: str) -> bool:
        """
        Permanently delete user by ID
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        result = self.collection.delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0
    
    def get_all(self, **filters) -> List[User]:
        """
        Get all users with optional filters
        
        Args:
            **filters: Optional filters (user_type, is_active, etc.)
            
        Returns:
            List of User instances
        """
        query = self._build_query(filters)
        users_data = self.collection.find(query)
        
        users = []
        for user_data in users_data:
            user = self._create_user_from_data(user_data)
            if user:
                users.append(user)
        
        return users
    
    def get_donors(self, active_only: bool = True) -> List[Donor]:
        """
        Get all donors
        
        Args:
            active_only: Whether to return only active donors
            
        Returns:
            List of Donor instances
        """
        filters = {'user_type': 'donor'}
        if active_only:
            filters['is_active'] = True
        
        users = self.get_all(**filters)
        return [user for user in users if isinstance(user, Donor)]
    
    def get_admins(self, active_only: bool = True) -> List[Admin]:
        """
        Get all admins
        
        Args:
            active_only: Whether to return only active admins
            
        Returns:
            List of Admin instances
        """
        filters = {'user_type': 'admin'}
        if active_only:
            filters['is_active'] = True
        
        users = self.get_all(**filters)
        return [user for user in users if isinstance(user, Admin)]
    
    def _create_user_from_data(self, user_data: Dict) -> Optional[User]:
        """
        Create User instance from database data
        
        Args:
            user_data: User data from database
            
        Returns:
            User instance or None if user_type unknown
        """
        from ..services.user_factory import UserFactory
        
        try:
            return UserFactory.create_user_from_dict(user_data)
        except (ValueError, KeyError):
            return None


class CampaignRepository(BaseRepository):
    """
    REPOSITORY PATTERN - Campaign Repository Implementation
    
    Handles all campaign-related database operations.
    """
    
    def __init__(self):
        super().__init__('campaigns')
    
    def create(self, campaign: Campaign) -> str:
        """
        Create a new campaign
        
        Args:
            campaign: Campaign instance to create
            
        Returns:
            Created campaign ID
        """
        campaign_data = campaign.to_dict()
        result = self.collection.insert_one(campaign_data)
        return str(result.inserted_id)
    
    def get_by_id(self, campaign_id: str) -> Optional[Campaign]:
        """
        Get campaign by ID
        
        Args:
            campaign_id: Campaign ID to search for
            
        Returns:
            Campaign instance or None if not found
        """
        try:
            campaign_data = self.collection.find_one({'_id': ObjectId(campaign_id)})
            if campaign_data:
                return Campaign.from_dict(campaign_data)
            return None
        except Exception:
            return None
    
    def update(self, campaign: Campaign) -> bool:
        """
        Update an existing campaign
        
        Args:
            campaign: Campaign instance with updated data
            
        Returns:
            True if update successful, False otherwise
        """
        campaign_data = campaign.to_dict()
        campaign_id = campaign_data.pop('_id')
        
        result = self.collection.update_one(
            {'_id': campaign_id},
            {'$set': campaign_data}
        )
        return result.modified_count > 0
    
    def delete(self, campaign_id: str) -> bool:
        """
        Delete campaign by ID
        
        Args:
            campaign_id: Campaign ID to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        result = self.collection.delete_one({'_id': ObjectId(campaign_id)})
        return result.deleted_count > 0
    
    def get_all(self, **filters) -> List[Campaign]:
        """
        Get all campaigns with optional filters
        
        Args:
            **filters: Optional filters (status, category, creator_id, etc.)
            
        Returns:
            List of Campaign instances
        """
        query = self._build_query(filters)
        campaigns_data = self.collection.find(query)
        
        campaigns = []
        for campaign_data in campaigns_data:
            try:
                campaign = Campaign.from_dict(campaign_data)
                campaigns.append(campaign)
            except Exception:
                continue
        
        return campaigns
    
    def get_active_campaigns(self) -> List[Campaign]:
        """Get all active campaigns"""
        return self.get_all(status='active')
    
    def get_featured_campaigns(self, limit: int = 3) -> List[Campaign]:
        """
        Get featured campaigns
        
        Args:
            limit: Maximum number of campaigns to return
            
        Returns:
            List of featured Campaign instances
        """
        campaigns_data = self.collection.find(
            {'is_featured': True, 'status': 'active'}
        ).limit(limit)
        
        campaigns = []
        for campaign_data in campaigns_data:
            try:
                campaign = Campaign.from_dict(campaign_data)
                campaigns.append(campaign)
            except Exception:
                continue
        
        return campaigns
    
    def get_by_creator(self, creator_id: str) -> List[Campaign]:
        """
        Get campaigns by creator
        
        Args:
            creator_id: Creator user ID
            
        Returns:
            List of Campaign instances
        """
        return self.get_all(creator_id=creator_id)
    
    def search_campaigns(self, query: str, category: str = None) -> List[Campaign]:
        """
        Search campaigns by title/description
        
        Args:
            query: Search query
            category: Optional category filter
            
        Returns:
            List of matching Campaign instances
        """
        search_filter = {
            '$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        if category:
            search_filter['category'] = category
        
        campaigns_data = self.collection.find(search_filter)
        
        campaigns = []
        for campaign_data in campaigns_data:
            try:
                campaign = Campaign.from_dict(campaign_data)
                campaigns.append(campaign)
            except Exception:
                continue
        
        return campaigns


class DonationRepository(BaseRepository):
    """
    REPOSITORY PATTERN - Donation Repository Implementation
    
    Handles all donation-related database operations.
    """
    
    def __init__(self):
        super().__init__('donations')
    
    def create(self, donation: Donation) -> str:
        """
        Create a new donation
        
        Args:
            donation: Donation instance to create
            
        Returns:
            Created donation ID
        """
        donation_data = donation.to_dict()
        result = self.collection.insert_one(donation_data)
        return str(result.inserted_id)
    
    def get_by_id(self, donation_id: str) -> Optional[Donation]:
        """
        Get donation by ID
        
        Args:
            donation_id: Donation ID to search for
            
        Returns:
            Donation instance or None if not found
        """
        try:
            donation_data = self.collection.find_one({'_id': ObjectId(donation_id)})
            if donation_data:
                return Donation.from_dict(donation_data)
            return None
        except Exception:
            return None
    
    def update(self, donation: Donation) -> bool:
        """
        Update an existing donation
        
        Args:
            donation: Donation instance with updated data
            
        Returns:
            True if update successful, False otherwise
        """
        donation_data = donation.to_dict()
        donation_id = donation_data.pop('_id')
        
        result = self.collection.update_one(
            {'_id': donation_id},
            {'$set': donation_data}
        )
        return result.modified_count > 0
    
    def delete(self, donation_id: str) -> bool:
        """
        Delete donation by ID
        
        Args:
            donation_id: Donation ID to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        result = self.collection.delete_one({'_id': ObjectId(donation_id)})
        return result.deleted_count > 0
    
    def get_all(self, **filters) -> List[Donation]:
        """
        Get all donations with optional filters
        
        Args:
            **filters: Optional filters (donor_id, campaign_id, status, etc.)
            
        Returns:
            List of Donation instances
        """
        query = self._build_query(filters)
        donations_data = self.collection.find(query)
        
        donations = []
        for donation_data in donations_data:
            try:
                donation = Donation.from_dict(donation_data)
                donations.append(donation)
            except Exception:
                continue
        
        return donations
    
    def get_by_donor(self, donor_id: str) -> List[Donation]:
        """
        Get donations by donor
        
        Args:
            donor_id: Donor user ID
            
        Returns:
            List of Donation instances
        """
        return self.get_all(donor_id=donor_id)
    
    def get_by_campaign(self, campaign_id: str) -> List[Donation]:
        """
        Get donations by campaign
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            List of Donation instances
        """
        return self.get_all(campaign_id=campaign_id)
    
    def get_recent_donations(self, limit: int = 10) -> List[Donation]:
        """
        Get recent donations
        
        Args:
            limit: Maximum number of donations to return
            
        Returns:
            List of recent Donation instances
        """
        donations_data = self.collection.find(
            {'status': 'completed'}
        ).sort('completed_at', -1).limit(limit)
        
        donations = []
        for donation_data in donations_data:
            try:
                donation = Donation.from_dict(donation_data)
                donations.append(donation)
            except Exception:
                continue
        
        return donations
    
    def get_total_amount_by_campaign(self, campaign_id: str) -> float:
        """
        Get total donation amount for a campaign
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Total donation amount
        """
        pipeline = [
            {'$match': {'campaign_id': campaign_id, 'status': 'completed'}},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return result[0]['total'] if result else 0.0