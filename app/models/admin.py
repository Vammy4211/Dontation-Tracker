"""
Admin Model - Demonstrates OOP Inheritance and Polymorphism
"""
from typing import Dict, List, Optional
from datetime import datetime
from .user import User


class Admin(User):
    """
    Admin Class - Inherits from User (INHERITANCE)
    
    Represents an administrator with elevated privileges.
    Demonstrates polymorphism by providing admin-specific
    implementations of abstract methods.
    """
    
    def __init__(self, username: str, email: str, password_hash: str, 
                 user_id: Optional[str] = None, admin_level: int = 1):
        """
        Initialize Admin with additional admin-specific attributes
        
        Args:
            admin_level: Level of admin access (1=basic, 2=senior, 3=super)
        """
        super().__init__(username, email, password_hash, user_id)
        self._admin_level = admin_level
        self._actions_performed = []
        self._last_action_date = None
        self._campaigns_managed = []
        self._can_delete_campaigns = admin_level >= 2
        self._can_manage_users = admin_level >= 3
    
    # Admin-specific properties
    @property
    def admin_level(self) -> int:
        return self._admin_level
    
    @property
    def can_delete_campaigns(self) -> bool:
        return self._can_delete_campaigns
    
    @property
    def can_manage_users(self) -> bool:
        return self._can_manage_users
    
    @property
    def actions_performed(self) -> List[Dict]:
        return self._actions_performed.copy()  # Return copy to maintain encapsulation
    
    @property
    def campaigns_managed(self) -> List[str]:
        return self._campaigns_managed.copy()
    
    # Admin-specific methods
    def log_action(self, action: str, target_id: str = None, details: str = None) -> None:
        """
        Log an administrative action
        
        Args:
            action: Type of action performed
            target_id: ID of the target (campaign, user, etc.)
            details: Additional details about the action
        """
        action_record = {
            'action': action,
            'target_id': target_id,
            'details': details,
            'timestamp': datetime.utcnow(),
            'admin_id': self._user_id
        }
        self._actions_performed.append(action_record)
        self._last_action_date = datetime.utcnow()
    
    def assign_campaign_management(self, campaign_id: str) -> None:
        """Assign campaign management to this admin"""
        if campaign_id not in self._campaigns_managed:
            self._campaigns_managed.append(campaign_id)
            self.log_action('campaign_assigned', campaign_id, 'Campaign management assigned')
    
    def remove_campaign_management(self, campaign_id: str) -> None:
        """Remove campaign management from this admin"""
        if campaign_id in self._campaigns_managed:
            self._campaigns_managed.remove(campaign_id)
            self.log_action('campaign_unassigned', campaign_id, 'Campaign management removed')
    
    def upgrade_admin_level(self, new_level: int) -> bool:
        """
        Upgrade admin level (can only upgrade, not downgrade for security)
        
        Args:
            new_level: New admin level
            
        Returns:
            True if upgrade successful, False otherwise
        """
        if new_level > self._admin_level and new_level <= 3:
            old_level = self._admin_level
            self._admin_level = new_level
            self._can_delete_campaigns = new_level >= 2
            self._can_manage_users = new_level >= 3
            self.log_action('admin_level_upgraded', 
                          details=f'Level upgraded from {old_level} to {new_level}')
            return True
        return False
    
    def can_perform_action(self, action: str) -> bool:
        """
        Check if admin can perform specific action based on level
        
        Args:
            action: Action to check permission for
            
        Returns:
            True if action is allowed, False otherwise
        """
        action_permissions = {
            'view_campaigns': 1,
            'approve_campaigns': 1,
            'edit_campaigns': 1,
            'delete_campaigns': 2,
            'view_users': 2,
            'manage_users': 3,
            'system_settings': 3
        }
        
        required_level = action_permissions.get(action, 999)  # Default to highest level
        return self._admin_level >= required_level
    
    # Implementation of abstract methods (POLYMORPHISM)
    def get_user_type(self) -> str:
        """Return user type as 'admin'"""
        return "admin"
    
    def get_dashboard_data(self) -> Dict:
        """
        Return admin-specific dashboard data
        Demonstrates POLYMORPHISM - different from Donor dashboard
        """
        return {
            'user_type': 'admin',
            'username': self._username,
            'admin_level': self._admin_level,
            'can_delete_campaigns': self._can_delete_campaigns,
            'can_manage_users': self._can_manage_users,
            'campaigns_managed_count': len(self._campaigns_managed),
            'recent_actions': self._actions_performed[-10:],  # Last 10 actions
            'last_action_date': self._last_action_date,
            'member_since': self._created_at.strftime('%B %Y'),
            'total_actions': len(self._actions_performed)
        }
    
    def get_permissions(self) -> List[str]:
        """Return admin-specific permissions based on level"""
        base_permissions = [
            'view_campaigns',
            'approve_campaigns',
            'edit_campaigns',
            'view_donations',
            'view_metrics'
        ]
        
        if self._admin_level >= 2:
            base_permissions.extend([
                'delete_campaigns',
                'view_users',
                'moderate_content'
            ])
        
        if self._admin_level >= 3:
            base_permissions.extend([
                'manage_users',
                'system_settings',
                'view_admin_logs',
                'manage_admins'
            ])
        
        return base_permissions
    
    def to_dict(self) -> Dict:
        """Convert admin to dictionary for database storage"""
        base_dict = super().to_dict()
        base_dict.update({
            'admin_level': self._admin_level,
            'actions_performed': self._actions_performed,
            'last_action_date': self._last_action_date,
            'campaigns_managed': self._campaigns_managed,
            'can_delete_campaigns': self._can_delete_campaigns,
            'can_manage_users': self._can_manage_users
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Admin':
        """Create Admin instance from dictionary data"""
        admin = cls(
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            user_id=str(data['_id']),
            admin_level=data.get('admin_level', 1)
        )
        
        # Set additional attributes
        admin._created_at = data.get('created_at', datetime.utcnow())
        admin._is_active = data.get('is_active', True)
        admin._last_login = data.get('last_login')
        admin._actions_performed = data.get('actions_performed', [])
        admin._last_action_date = data.get('last_action_date')
        admin._campaigns_managed = data.get('campaigns_managed', [])
        admin._can_delete_campaigns = data.get('can_delete_campaigns', admin._admin_level >= 2)
        admin._can_manage_users = data.get('can_manage_users', admin._admin_level >= 3)
        
        return admin
    
    def __str__(self) -> str:
        return f"Admin: {self._username} (Level {self._admin_level})"