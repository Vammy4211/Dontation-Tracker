"""
Campaign Model - Represents donation campaigns
"""
from typing import Dict, List, Optional
from datetime import datetime
from bson import ObjectId
from enum import Enum


class CampaignStatus(Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Campaign:
    """
    Campaign Class - Represents a donation campaign
    
    Encapsulates campaign data and provides methods for
    campaign management and progress tracking.
    """
    
    def __init__(self, title: str, description: str, goal_amount: float,
                 creator_id: str, category: str = "General", 
                 campaign_id: Optional[str] = None):
        """
        Initialize Campaign
        
        Args:
            title: Campaign title
            description: Campaign description
            goal_amount: Target amount to raise
            creator_id: ID of the user who created the campaign
            category: Campaign category
            campaign_id: Optional MongoDB ObjectId as string
        """
        self._campaign_id = campaign_id or str(ObjectId())
        self._title = title
        self._description = description
        self._goal_amount = float(goal_amount)
        self._current_amount = 0.0
        self._creator_id = creator_id
        self._category = category
        self._status = CampaignStatus.DRAFT
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        self._start_date = None
        self._end_date = None
        self._image_url = None
        self._donation_count = 0
        self._donors = []  # List of donor IDs
        self._tags = []
        self._is_featured = False
    
    # Properties with controlled access
    @property
    def campaign_id(self) -> str:
        return self._campaign_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def goal_amount(self) -> float:
        return self._goal_amount
    
    @property
    def current_amount(self) -> float:
        return self._current_amount
    
    @property
    def creator_id(self) -> str:
        return self._creator_id
    
    @property
    def category(self) -> str:
        return self._category
    
    @property
    def status(self) -> CampaignStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def start_date(self) -> Optional[datetime]:
        return self._start_date
    
    @property
    def end_date(self) -> Optional[datetime]:
        return self._end_date
    
    @property
    def image_url(self) -> Optional[str]:
        return self._image_url
    
    @property
    def donation_count(self) -> int:
        return self._donation_count
    
    @property
    def donors(self) -> List[str]:
        return self._donors.copy()
    
    @property
    def tags(self) -> List[str]:
        return self._tags.copy()
    
    @property
    def is_featured(self) -> bool:
        return self._is_featured
    
    # Calculated properties
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self._goal_amount <= 0:
            return 0.0
        return min((self._current_amount / self._goal_amount) * 100, 100.0)
    
    @property
    def is_active(self) -> bool:
        """Check if campaign is currently active"""
        if self._status != CampaignStatus.ACTIVE:
            return False
        
        now = datetime.utcnow()
        if self._start_date and now < self._start_date:
            return False
        if self._end_date and now > self._end_date:
            return False
        
        return True
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Calculate days remaining until end date"""
        if not self._end_date:
            return None
        
        remaining = self._end_date - datetime.utcnow()
        return max(0, remaining.days)
    
    @property
    def is_completed(self) -> bool:
        """Check if campaign has reached its goal"""
        return self._current_amount >= self._goal_amount
    
    # Campaign management methods
    def update_details(self, title: str = None, description: str = None, 
                      goal_amount: float = None, category: str = None) -> None:
        """Update campaign details"""
        if title:
            self._title = title
        if description:
            self._description = description
        if goal_amount and goal_amount > 0:
            self._goal_amount = float(goal_amount)
        if category:
            self._category = category
        
        self._updated_at = datetime.utcnow()
    
    def set_dates(self, start_date: datetime = None, end_date: datetime = None) -> None:
        """Set campaign start and end dates"""
        if start_date:
            self._start_date = start_date
        if end_date:
            self._end_date = end_date
        
        self._updated_at = datetime.utcnow()
    
    def set_image(self, image_url: str) -> None:
        """Set campaign image URL"""
        self._image_url = image_url
        self._updated_at = datetime.utcnow()
    
    def add_tags(self, tags: List[str]) -> None:
        """Add tags to campaign"""
        for tag in tags:
            if tag not in self._tags:
                self._tags.append(tag.lower())
        self._updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """Remove tag from campaign"""
        tag_lower = tag.lower()
        if tag_lower in self._tags:
            self._tags.remove(tag_lower)
            self._updated_at = datetime.utcnow()
    
    def set_featured(self, featured: bool) -> None:
        """Set campaign as featured or not"""
        self._is_featured = featured
        self._updated_at = datetime.utcnow()
    
    # Status management
    def activate(self) -> bool:
        """Activate the campaign"""
        if self._status == CampaignStatus.DRAFT:
            self._status = CampaignStatus.ACTIVE
            if not self._start_date:
                self._start_date = datetime.utcnow()
            self._updated_at = datetime.utcnow()
            return True
        return False
    
    def pause(self) -> bool:
        """Pause the campaign"""
        if self._status == CampaignStatus.ACTIVE:
            self._status = CampaignStatus.PAUSED
            self._updated_at = datetime.utcnow()
            return True
        return False
    
    def resume(self) -> bool:
        """Resume paused campaign"""
        if self._status == CampaignStatus.PAUSED:
            self._status = CampaignStatus.ACTIVE
            self._updated_at = datetime.utcnow()
            return True
        return False
    
    def complete(self) -> bool:
        """Mark campaign as completed"""
        if self._status in [CampaignStatus.ACTIVE, CampaignStatus.PAUSED]:
            self._status = CampaignStatus.COMPLETED
            self._updated_at = datetime.utcnow()
            return True
        return False
    
    def cancel(self) -> bool:
        """Cancel the campaign"""
        if self._status != CampaignStatus.COMPLETED:
            self._status = CampaignStatus.CANCELLED
            self._updated_at = datetime.utcnow()
            return True
        return False
    
    # Donation tracking
    def add_donation(self, amount: float, donor_id: str) -> None:
        """
        Add a donation to this campaign
        
        Args:
            amount: Donation amount
            donor_id: ID of the donor
        """
        self._current_amount += amount
        self._donation_count += 1
        
        if donor_id not in self._donors:
            self._donors.append(donor_id)
        
        self._updated_at = datetime.utcnow()
        
        # Auto-complete if goal reached
        if self.is_completed and self._status == CampaignStatus.ACTIVE:
            self.complete()
    
    def get_summary(self) -> Dict:
        """Get campaign summary for display"""
        return {
            'campaign_id': self._campaign_id,
            'title': self._title,
            'description': self._description[:200] + '...' if len(self._description) > 200 else self._description,
            'goal_amount': self._goal_amount,
            'current_amount': self._current_amount,
            'progress_percentage': self.progress_percentage,
            'category': self._category,
            'status': self._status.value,
            'is_active': self.is_active,
            'donation_count': self._donation_count,
            'days_remaining': self.days_remaining,
            'is_completed': self.is_completed,
            'is_featured': self._is_featured,
            'created_at': self._created_at,
            'image_url': self._image_url
        }
    
    def to_dict(self) -> Dict:
        """Convert campaign to dictionary for database storage"""
        return {
            '_id': ObjectId(self._campaign_id),
            'title': self._title,
            'description': self._description,
            'goal_amount': self._goal_amount,
            'current_amount': self._current_amount,
            'creator_id': self._creator_id,
            'category': self._category,
            'status': self._status.value,
            'created_at': self._created_at,
            'updated_at': self._updated_at,
            'start_date': self._start_date,
            'end_date': self._end_date,
            'image_url': self._image_url,
            'donation_count': self._donation_count,
            'donors': self._donors,
            'tags': self._tags,
            'is_featured': self._is_featured
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Campaign':
        """Create Campaign instance from dictionary data"""
        campaign = cls(
            title=data['title'],
            description=data['description'],
            goal_amount=data['goal_amount'],
            creator_id=data['creator_id'],
            category=data.get('category', 'General'),
            campaign_id=str(data['_id'])
        )
        
        # Set additional attributes
        campaign._current_amount = data.get('current_amount', 0.0)
        campaign._status = CampaignStatus(data.get('status', 'draft'))
        campaign._created_at = data.get('created_at', datetime.utcnow())
        campaign._updated_at = data.get('updated_at', datetime.utcnow())
        campaign._start_date = data.get('start_date')
        campaign._end_date = data.get('end_date')
        campaign._image_url = data.get('image_url')
        campaign._donation_count = data.get('donation_count', 0)
        campaign._donors = data.get('donors', [])
        campaign._tags = data.get('tags', [])
        campaign._is_featured = data.get('is_featured', False)
        
        return campaign
    
    def __str__(self) -> str:
        return f"Campaign: {self._title} (${self._current_amount:.2f}/${self._goal_amount:.2f})"
    
    def __repr__(self) -> str:
        return f"Campaign(title='{self._title}', goal=${self._goal_amount}, status='{self._status.value}')"