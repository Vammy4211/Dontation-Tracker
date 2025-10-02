"""
Donor Model - Demonstrates OOP Inheritance and Polymorphism
"""
from typing import Dict, List, Optional
from datetime import datetime
from .user import User


class Donor(User):
    """
    Donor Class - Inherits from User (INHERITANCE)
    
    Represents a donor who can make donations to campaigns.
    Demonstrates polymorphism by providing donor-specific
    implementations of abstract methods.
    """
    
    def __init__(self, username: str, email: str, password_hash: str, 
                 user_id: Optional[str] = None, anonymous_by_default: bool = False):
        """
        Initialize Donor with additional donor-specific attributes
        
        Args:
            anonymous_by_default: Whether this donor prefers to be anonymous
        """
        super().__init__(username, email, password_hash, user_id)
        self._anonymous_by_default = anonymous_by_default
        self._total_donated = 0.0
        self._donation_count = 0
        self._favorite_campaigns = []
        self._donation_history = []
    
    # Donor-specific properties
    @property
    def anonymous_by_default(self) -> bool:
        return self._anonymous_by_default
    
    @property
    def total_donated(self) -> float:
        return self._total_donated
    
    @property
    def donation_count(self) -> int:
        return self._donation_count
    
    @property
    def favorite_campaigns(self) -> List[str]:
        return self._favorite_campaigns.copy()  # Return copy to maintain encapsulation
    
    @property
    def donation_history(self) -> List[Dict]:
        return self._donation_history.copy()  # Return copy to maintain encapsulation
    
    # Donor-specific methods
    def set_anonymous_preference(self, anonymous: bool) -> None:
        """Set the donor's anonymity preference"""
        self._anonymous_by_default = anonymous
    
    def add_donation(self, amount: float, campaign_id: str, donation_id: str) -> None:
        """
        Record a new donation for this donor
        
        Args:
            amount: Donation amount
            campaign_id: ID of the campaign donated to
            donation_id: ID of the donation record
        """
        self._total_donated += amount
        self._donation_count += 1
        
        donation_record = {
            'donation_id': donation_id,
            'campaign_id': campaign_id,
            'amount': amount,
            'date': datetime.utcnow()
        }
        self._donation_history.append(donation_record)
    
    def add_favorite_campaign(self, campaign_id: str) -> None:
        """Add a campaign to favorites"""
        if campaign_id not in self._favorite_campaigns:
            self._favorite_campaigns.append(campaign_id)
    
    def remove_favorite_campaign(self, campaign_id: str) -> None:
        """Remove a campaign from favorites"""
        if campaign_id in self._favorite_campaigns:
            self._favorite_campaigns.remove(campaign_id)
    
    def get_display_name(self, force_anonymous: bool = False) -> str:
        """
        Get display name for public listings
        
        Args:
            force_anonymous: Force anonymous display regardless of preference
            
        Returns:
            Either full name, first initial, or "Anonymous"
        """
        if force_anonymous or self._anonymous_by_default:
            return "Anonymous"
        else:
            # Return first initial + last name or just first initial
            names = self._username.split()
            if len(names) > 1:
                return f"{names[0][0]}. {names[-1]}"
            else:
                return f"{names[0][0]}."
    
    # Implementation of abstract methods (POLYMORPHISM)
    def get_user_type(self) -> str:
        """Return user type as 'donor'"""
        return "donor"
    
    def get_dashboard_data(self) -> Dict:
        """
        Return donor-specific dashboard data
        Demonstrates POLYMORPHISM - different from Admin dashboard
        """
        return {
            'user_type': 'donor',
            'username': self._username,
            'total_donated': self._total_donated,
            'donation_count': self._donation_count,
            'favorite_campaigns_count': len(self._favorite_campaigns),
            'recent_donations': self._donation_history[-5:],  # Last 5 donations
            'member_since': self._created_at.strftime('%B %Y'),
            'anonymous_by_default': self._anonymous_by_default
        }
    
    def get_permissions(self) -> List[str]:
        """Return donor-specific permissions"""
        return [
            'view_campaigns',
            'make_donations',
            'view_own_donations',
            'update_own_profile',
            'favorite_campaigns'
        ]
    
    def to_dict(self) -> Dict:
        """Convert donor to dictionary for database storage"""
        base_dict = super().to_dict()
        base_dict.update({
            'anonymous_by_default': self._anonymous_by_default,
            'total_donated': self._total_donated,
            'donation_count': self._donation_count,
            'favorite_campaigns': self._favorite_campaigns,
            'donation_history': self._donation_history
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Donor':
        """Create Donor instance from dictionary data"""
        donor = cls(
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            user_id=str(data['_id']),
            anonymous_by_default=data.get('anonymous_by_default', False)
        )
        
        # Set additional attributes
        donor._created_at = data.get('created_at', datetime.utcnow())
        donor._is_active = data.get('is_active', True)
        donor._last_login = data.get('last_login')
        donor._total_donated = data.get('total_donated', 0.0)
        donor._donation_count = data.get('donation_count', 0)
        donor._favorite_campaigns = data.get('favorite_campaigns', [])
        donor._donation_history = data.get('donation_history', [])
        
        return donor
    
    def __str__(self) -> str:
        return f"Donor: {self._username} (${self._total_donated:.2f} donated)"