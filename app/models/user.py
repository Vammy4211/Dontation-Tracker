"""
Base User Model - Demonstrates OOP Inheritance and Encapsulation
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional
from bson import ObjectId


class User(ABC):
    """
    Abstract Base User Class - Demonstrates ABSTRACTION
    
    This serves as the base class for all user types in the system.
    Uses encapsulation to protect sensitive data and abstraction
    to define common user interface.
    """
    
    def __init__(self, username: str, email: str, password_hash: str, user_id: Optional[str] = None):
        """
        Initialize User with encapsulated attributes
        
        Args:
            username: User's display name
            email: User's email address
            password_hash: Hashed password (never store plain text)
            user_id: Optional MongoDB ObjectId as string
        """
        self._user_id = user_id or str(ObjectId())  # Encapsulated ID
        self._username = username  # Encapsulated username
        self._email = email  # Encapsulated email
        self._password_hash = password_hash  # Encapsulated password hash
        self._created_at = datetime.utcnow()
        self._is_active = True
        self._last_login = None
    
    # Public property getters - Controlled access to encapsulated data
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def last_login(self) -> Optional[datetime]:
        return self._last_login
    
    # Protected method for password verification
    def _verify_password(self, password_hash: str) -> bool:
        """Protected method to verify password hash"""
        return self._password_hash == password_hash
    
    # Public methods
    def update_last_login(self) -> None:
        """Update the last login timestamp"""
        self._last_login = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate user account"""
        self._is_active = False
    
    def activate(self) -> None:
        """Activate user account"""
        self._is_active = True
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary for database storage"""
        return {
            '_id': ObjectId(self._user_id),
            'username': self._username,
            'email': self._email,
            'password_hash': self._password_hash,
            'created_at': self._created_at,
            'is_active': self._is_active,
            'last_login': self._last_login,
            'user_type': self.get_user_type()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create User instance from dictionary data"""
        # This will be overridden by subclasses
        raise NotImplementedError("Subclasses must implement from_dict")
    
    # Abstract methods that subclasses must implement
    @abstractmethod
    def get_user_type(self) -> str:
        """Return the type of user (donor, admin, etc.)"""
        pass
    
    @abstractmethod
    def get_dashboard_data(self) -> Dict:
        """
        Return dashboard data specific to user type
        Demonstrates POLYMORPHISM - different dashboards for different user types
        """
        pass
    
    @abstractmethod
    def get_permissions(self) -> list:
        """Return list of permissions for this user type"""
        pass
    
    def __str__(self) -> str:
        return f"{self.get_user_type().title()}: {self._username}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(username='{self._username}', email='{self._email}')"