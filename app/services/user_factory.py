"""
Factory Pattern - User Factory for creating different user types
"""
from typing import Dict, Union
from ..models.user import User
from ..models.donor import Donor
from ..models.admin import Admin


class UserFactory:
    """
    FACTORY PATTERN Implementation
    
    Creates different types of users (Donor, Admin) based on user type.
    This pattern encapsulates object creation logic and allows for
    easy extension of new user types without modifying existing code.
    
    Benefits:
    - Centralized user creation logic
    - Easy to add new user types
    - Follows Open/Closed Principle
    - Reduces code duplication
    """
    
    # Registry of user types and their corresponding classes
    _user_types = {
        'donor': Donor,
        'admin': Admin
    }
    
    @classmethod
    def create_user(cls, user_type: str, username: str, email: str, 
                   password_hash: str, **kwargs) -> User:
        """
        Factory method to create users of different types
        
        Args:
            user_type: Type of user to create ('donor', 'admin')
            username: Username for the user
            email: Email address
            password_hash: Hashed password
            **kwargs: Additional arguments specific to user type
            
        Returns:
            User instance of the specified type
            
        Raises:
            ValueError: If user_type is not supported
        """
        user_type = user_type.lower()
        
        if user_type not in cls._user_types:
            raise ValueError(f"Unsupported user type: {user_type}. "
                           f"Supported types: {list(cls._user_types.keys())}")
        
        user_class = cls._user_types[user_type]
        
        # Create user with type-specific parameters
        if user_type == 'donor':
            return user_class(
                username=username,
                email=email,
                password_hash=password_hash,
                user_id=kwargs.get('user_id'),
                anonymous_by_default=kwargs.get('anonymous_by_default', False)
            )
        elif user_type == 'admin':
            return user_class(
                username=username,
                email=email,
                password_hash=password_hash,
                user_id=kwargs.get('user_id'),
                admin_level=kwargs.get('admin_level', 1)
            )
    
    @classmethod
    def create_user_from_dict(cls, data: Dict) -> User:
        """
        Factory method to create user from dictionary data
        
        Args:
            data: Dictionary containing user data with 'user_type' field
            
        Returns:
            User instance of the appropriate type
            
        Raises:
            ValueError: If user_type is missing or not supported
        """
        user_type = data.get('user_type')
        if not user_type:
            raise ValueError("user_type field is required in data")
        
        user_type = user_type.lower()
        
        if user_type not in cls._user_types:
            raise ValueError(f"Unsupported user type: {user_type}")
        
        user_class = cls._user_types[user_type]
        return user_class.from_dict(data)
    
    @classmethod
    def get_supported_user_types(cls) -> list:
        """
        Get list of supported user types
        
        Returns:
            List of supported user type strings
        """
        return list(cls._user_types.keys())
    
    @classmethod
    def register_user_type(cls, user_type: str, user_class: type) -> None:
        """
        Register a new user type (for extensibility)
        
        Args:
            user_type: String identifier for the user type
            user_class: Class that implements the User interface
            
        Raises:
            TypeError: If user_class doesn't inherit from User
        """
        if not issubclass(user_class, User):
            raise TypeError(f"user_class must inherit from User")
        
        cls._user_types[user_type.lower()] = user_class
    
    @classmethod
    def create_default_admin(cls, username: str = "admin", 
                           email: str = "admin@donationtracker.com",
                           password_hash: str = "hashed_admin_password") -> Admin:
        """
        Factory method to create a default admin user
        
        Args:
            username: Admin username (default: 'admin')
            email: Admin email
            password_hash: Hashed password
            
        Returns:
            Admin instance with level 3 permissions
        """
        return cls.create_user(
            user_type='admin',
            username=username,
            email=email,
            password_hash=password_hash,
            admin_level=3  # Super admin
        )
    
    @classmethod
    def create_demo_donor(cls, username: str, email: str) -> Donor:
        """
        Factory method to create a demo donor (for testing/demo purposes)
        
        Args:
            username: Donor username
            email: Donor email
            
        Returns:
            Donor instance configured for demo
        """
        return cls.create_user(
            user_type='donor',
            username=username,
            email=email,
            password_hash='demo_password_hash',
            anonymous_by_default=False
        )


# Usage examples:
"""
# Create a donor
donor = UserFactory.create_user(
    user_type='donor',
    username='john_doe',
    email='john@example.com',
    password_hash='hashed_password',
    anonymous_by_default=True
)

# Create an admin
admin = UserFactory.create_user(
    user_type='admin',
    username='admin_user',
    email='admin@example.com',
    password_hash='hashed_password',
    admin_level=2
)

# Create from database data
user_data = {
    'user_type': 'donor',
    'username': 'jane_doe',
    'email': 'jane@example.com',
    'password_hash': 'hashed_password',
    '_id': 'some_object_id'
}
user = UserFactory.create_user_from_dict(user_data)
"""