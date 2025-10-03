"""
Facade Pattern - Simplified Interface for Donation System

The Facade Pattern provides a simplified interface to a complex subsystem.
It hides the complexities of the system and provides an easier interface to the client.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from ..models.campaign import Campaign
from ..models.donation import Donation
from ..models.user import User, Donor, Admin
from .factory import UserFactory
from .singleton import DatabaseManager
from .repository import CampaignRepository, DonationRepository, UserRepository
from .strategy import CampaignSorter, PaymentProcessor
from .observer import get_donation_event_manager
from .proxy import create_cached_campaign_repository, create_cached_donation_repository, AccessControlProxy
from .chain_of_responsibility import DonationProcessingPipeline


class DonationSystemFacade:
    """
    FACADE PATTERN - Simplified interface for the donation system
    
    Provides a single, simplified interface to interact with all subsystems
    of the donation tracking application.
    """
    
    def __init__(self):
        """Initialize the facade with all required services"""
        # Initialize database connection
        self.db_manager = DatabaseManager()
        
        # Initialize repositories
        self.user_repository = UserRepository(self.db_manager.get_database())
        self.campaign_repository = CampaignRepository(self.db_manager.get_database())
        self.donation_repository = DonationRepository(self.db_manager.get_database())
        
        # Initialize cached repositories
        self.cached_campaign_repository = create_cached_campaign_repository(self.campaign_repository)
        self.cached_donation_repository = create_cached_donation_repository(self.donation_repository)
        
        # Initialize services
        self.user_factory = UserFactory()
        self.campaign_sorter = CampaignSorter()
        self.payment_processor = PaymentProcessor()
        self.event_manager = get_donation_event_manager()
        
        # Initialize processing pipeline
        self.donation_pipeline = DonationProcessingPipeline(
            self.payment_processor,
            self.donation_repository,
            self.campaign_repository,
            self.event_manager
        )
        
        # Current user context
        self.current_user: Optional[User] = None
        self.access_controlled_repositories = {}
    
    def authenticate_user(self, email: str, password: str) -> Tuple[bool, Optional[User], str]:
        """
        Authenticate user and set current context
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, user, message)
        """
        try:
            # Find user by email
            user = self.user_repository.find_by_email(email)
            if not user:
                return False, None, "User not found"
            
            # Verify password (in real app, use proper password hashing)
            if not user.verify_password(password):
                return False, None, "Invalid password"
            
            # Set current user context
            self.current_user = user
            
            # Initialize access-controlled repositories
            self.access_controlled_repositories = {
                'campaigns': AccessControlProxy(self.campaign_repository, user),
                'donations': AccessControlProxy(self.donation_repository, user),
                'users': AccessControlProxy(self.user_repository, user)
            }
            
            return True, user, "Authentication successful"
        
        except Exception as e:
            return False, None, f"Authentication error: {str(e)}"
    
    def logout_user(self) -> None:
        """Logout current user"""
        self.current_user = None
        self.access_controlled_repositories.clear()
    
    def register_user(self, user_data: Dict[str, Any]) -> Tuple[bool, Optional[User], str]:
        """
        Register a new user
        
        Args:
            user_data: User registration data
            
        Returns:
            Tuple of (success, user, message)
        """
        try:
            # Check if user already exists
            existing_user = self.user_repository.find_by_email(user_data['email'])
            if existing_user:
                return False, None, "User with this email already exists"
            
            # Create user using factory
            user_type = user_data.get('user_type', 'donor')
            user = self.user_factory.create_user(user_type, user_data)
            
            # Save user
            saved_user = self.user_repository.create(user)
            
            # Notify about new user registration
            self.event_manager.notify_user_registered(saved_user)
            
            return True, saved_user, "User registered successfully"
        
        except Exception as e:
            return False, None, f"Registration error: {str(e)}"
    
    def create_campaign(self, campaign_data: Dict[str, Any]) -> Tuple[bool, Optional[Campaign], str]:
        """
        Create a new campaign
        
        Args:
            campaign_data: Campaign data
            
        Returns:
            Tuple of (success, campaign, message)
        """
        try:
            if not self.current_user:
                return False, None, "Authentication required"
            
            # Create campaign
            campaign = Campaign(
                title=campaign_data['title'],
                description=campaign_data['description'],
                goal_amount=campaign_data['goal_amount'],
                creator_id=self.current_user.id,
                category=campaign_data.get('category', 'general'),
                end_date=campaign_data.get('end_date')
            )
            
            # Save campaign with access control
            controlled_repo = self.access_controlled_repositories.get('campaigns', self.campaign_repository)
            saved_campaign = controlled_repo.create(campaign)
            
            # Notify about new campaign
            self.event_manager.notify_campaign_created(saved_campaign)
            
            return True, saved_campaign, "Campaign created successfully"
        
        except PermissionError as e:
            return False, None, f"Access denied: {str(e)}"
        except Exception as e:
            return False, None, f"Campaign creation error: {str(e)}"
    
    def get_campaigns(self, sort_by: str = 'date_new', limit: Optional[int] = None, 
                     status: Optional[str] = None) -> List[Campaign]:
        """
        Get campaigns with sorting and filtering
        
        Args:
            sort_by: Sorting strategy key
            limit: Maximum number of campaigns
            status: Filter by status
            
        Returns:
            List of campaigns
        """
        try:
            # Get campaigns using cached repository
            campaigns = self.cached_campaign_repository.find_all(limit=limit, status=status)
            
            # Apply sorting strategy
            available_strategies = self.campaign_sorter.get_available_strategies()
            if sort_by in available_strategies:
                self.campaign_sorter.set_strategy(available_strategies[sort_by])
                campaigns = self.campaign_sorter.sort_campaigns(campaigns)
            
            return campaigns
        
        except Exception as e:
            print(f"Error getting campaigns: {str(e)}")
            return []
    
    def get_campaign_details(self, campaign_id: str) -> Optional[Campaign]:
        """
        Get detailed campaign information
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Campaign object or None
        """
        try:
            return self.cached_campaign_repository.find_by_id(campaign_id)
        except Exception as e:
            print(f"Error getting campaign details: {str(e)}")
            return None
    
    def make_donation(self, campaign_id: str, amount: float, 
                     payment_data: Dict[str, Any], anonymous: bool = False) -> Tuple[bool, Optional[Donation], str]:
        """
        Process a donation to a campaign
        
        Args:
            campaign_id: Campaign to donate to
            amount: Donation amount
            payment_data: Payment information
            anonymous: Whether donation is anonymous
            
        Returns:
            Tuple of (success, donation, message)
        """
        try:
            if not self.current_user:
                return False, None, "Authentication required"
            
            # Get campaign
            campaign = self.cached_campaign_repository.find_by_id(campaign_id)
            if not campaign:
                return False, None, "Campaign not found"
            
            # Create donation
            donation = Donation(
                campaign_id=campaign_id,
                donor_id=self.current_user.id,
                amount=amount,
                anonymous=anonymous,
                message=payment_data.get('message', '')
            )
            
            # Process donation through pipeline
            result = self.donation_pipeline.process_donation(
                donation, self.current_user, campaign, payment_data
            )
            
            if result.has_errors():
                error_messages = [error['message'] for error in result.errors]
                return False, None, "; ".join(error_messages)
            
            # Get saved donation from result
            saved_donation = result.get_context_value('saved_donation')
            return True, saved_donation, "Donation processed successfully"
        
        except Exception as e:
            return False, None, f"Donation processing error: {str(e)}"
    
    def get_donations(self, campaign_id: Optional[str] = None, 
                     donor_id: Optional[str] = None, limit: Optional[int] = None) -> List[Donation]:
        """
        Get donations with filtering
        
        Args:
            campaign_id: Filter by campaign
            donor_id: Filter by donor
            limit: Maximum number of donations
            
        Returns:
            List of donations
        """
        try:
            if campaign_id:
                return self.cached_donation_repository.find_by_campaign(campaign_id)
            elif donor_id:
                # Use regular repository for donor-specific queries
                return self.donation_repository.find_by_donor(donor_id)
            else:
                return self.cached_donation_repository.find_all(limit=limit)
        
        except Exception as e:
            print(f"Error getting donations: {str(e)}")
            return []
    
    def get_user_profile(self, user_id: Optional[str] = None) -> Optional[User]:
        """
        Get user profile information
        
        Args:
            user_id: User ID (defaults to current user)
            
        Returns:
            User object or None
        """
        try:
            target_user_id = user_id or (self.current_user.id if self.current_user else None)
            if not target_user_id:
                return None
            
            return self.user_repository.find_by_id(target_user_id)
        
        except Exception as e:
            print(f"Error getting user profile: {str(e)}")
            return None
    
    def update_user_profile(self, user_data: Dict[str, Any]) -> Tuple[bool, Optional[User], str]:
        """
        Update user profile
        
        Args:
            user_data: Updated user data
            
        Returns:
            Tuple of (success, user, message)
        """
        try:
            if not self.current_user:
                return False, None, "Authentication required"
            
            # Update user fields
            for field, value in user_data.items():
                if hasattr(self.current_user, field) and field != 'id':
                    setattr(self.current_user, field, value)
            
            # Save updated user
            updated_user = self.user_repository.update(self.current_user)
            
            return True, updated_user, "Profile updated successfully"
        
        except Exception as e:
            return False, None, f"Profile update error: {str(e)}"
    
    def get_campaign_statistics(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get comprehensive campaign statistics
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Dictionary with campaign statistics
        """
        try:
            campaign = self.cached_campaign_repository.find_by_id(campaign_id)
            if not campaign:
                return {}
            
            donations = self.cached_donation_repository.find_by_campaign(campaign_id)
            
            # Calculate statistics
            total_donations = len(donations)
            total_amount = sum(d.amount for d in donations)
            average_donation = total_amount / total_donations if total_donations > 0 else 0
            progress_percentage = (total_amount / campaign.goal_amount * 100) if campaign.goal_amount else 0
            
            # Get donor count (unique donors)
            unique_donors = len(set(d.donor_id for d in donations if not d.anonymous))
            
            return {
                'campaign_id': campaign_id,
                'title': campaign.title,
                'goal_amount': campaign.goal_amount,
                'current_amount': total_amount,
                'progress_percentage': round(progress_percentage, 2),
                'total_donations': total_donations,
                'unique_donors': unique_donors,
                'average_donation': round(average_donation, 2),
                'days_remaining': campaign.days_remaining,
                'status': campaign.status
            }
        
        except Exception as e:
            print(f"Error getting campaign statistics: {str(e)}")
            return {}
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get dashboard data for current user
        
        Returns:
            Dictionary with dashboard information
        """
        try:
            if not self.current_user:
                return {'error': 'Authentication required'}
            
            dashboard_data = {
                'user': {
                    'name': self.current_user.name,
                    'email': self.current_user.email,
                    'role': self.current_user.role,
                    'created_at': self.current_user.created_at
                },
                'recent_campaigns': self.get_campaigns(limit=5),
                'recent_donations': self.get_donations(limit=10)
            }
            
            # Add role-specific data
            if isinstance(self.current_user, Donor):
                # Donor-specific dashboard data
                my_donations = self.get_donations(donor_id=self.current_user.id, limit=5)
                total_donated = sum(d.amount for d in my_donations)
                
                dashboard_data.update({
                    'my_donations': my_donations,
                    'total_donated': total_donated,
                    'donations_count': len(my_donations)
                })
            
            elif isinstance(self.current_user, Admin):
                # Admin-specific dashboard data
                all_campaigns = self.get_campaigns()
                all_donations = self.get_donations()
                
                dashboard_data.update({
                    'total_campaigns': len(all_campaigns),
                    'total_donations_count': len(all_donations),
                    'total_amount_raised': sum(d.amount for d in all_donations),
                    'active_campaigns': len([c for c in all_campaigns if c.status == 'active'])
                })
            
            return dashboard_data
        
        except Exception as e:
            return {'error': f"Dashboard error: {str(e)}"}
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status information
        
        Returns:
            Dictionary with system status
        """
        try:
            # Get cache statistics
            cache_stats = self.cached_campaign_repository.get_cache_stats()
            
            # Get database connection status
            db_status = self.db_manager.get_connection_status()
            
            # Get pipeline status
            pipeline_status = self.donation_pipeline.get_pipeline_status()
            
            return {
                'database': db_status,
                'cache': cache_stats,
                'processing_pipeline': pipeline_status,
                'current_user': self.current_user.email if self.current_user else None,
                'available_payment_methods': self.payment_processor.get_available_payment_methods(),
                'available_sorting_options': list(self.campaign_sorter.get_available_strategies().keys())
            }
        
        except Exception as e:
            return {'error': f"System status error: {str(e)}"}
    
    def search_campaigns(self, query: str, category: Optional[str] = None) -> List[Campaign]:
        """
        Search campaigns by title or description
        
        Args:
            query: Search query
            category: Filter by category
            
        Returns:
            List of matching campaigns
        """
        try:
            # Get all campaigns
            campaigns = self.get_campaigns()
            
            # Filter by search query
            matching_campaigns = []
            query_lower = query.lower()
            
            for campaign in campaigns:
                if (query_lower in campaign.title.lower() or 
                    query_lower in campaign.description.lower()):
                    
                    if category is None or campaign.category == category:
                        matching_campaigns.append(campaign)
            
            return matching_campaigns
        
        except Exception as e:
            print(f"Error searching campaigns: {str(e)}")
            return []


# Global facade instance
_donation_system_facade = None

def get_donation_system_facade() -> DonationSystemFacade:
    """
    Get the global donation system facade instance
    
    Returns:
        DonationSystemFacade instance
    """
    global _donation_system_facade
    if _donation_system_facade is None:
        _donation_system_facade = DonationSystemFacade()
    return _donation_system_facade


# Usage examples:
"""
# Get facade instance
facade = get_donation_system_facade()

# User registration and authentication
success, user, message = facade.register_user({
    'name': 'John Doe',
    'email': 'john@example.com',
    'password': 'password123',
    'user_type': 'donor'
})

success, user, message = facade.authenticate_user('john@example.com', 'password123')

# Create campaign
success, campaign, message = facade.create_campaign({
    'title': 'Help Local School',
    'description': 'Raise funds for school supplies',
    'goal_amount': 5000.0,
    'category': 'education'
})

# Get campaigns with sorting
campaigns = facade.get_campaigns(sort_by='amount_high', limit=10)

# Make donation
success, donation, message = facade.make_donation(
    campaign_id=campaign.id,
    amount=100.0,
    payment_data={
        'method': 'credit_card',
        'card_number': '1234567890123456',
        'expiry_month': '12',
        'expiry_year': '2025',
        'cvv': '123'
    }
)

# Get dashboard data
dashboard = facade.get_dashboard_data()

# Search campaigns
results = facade.search_campaigns('school', category='education')

# Get system status
status = facade.get_system_status()
"""