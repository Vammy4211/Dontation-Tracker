"""
Singleton Pattern - Database Connection Manager
"""
import threading
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseManager:
    """
    SINGLETON PATTERN Implementation
    
    Ensures only one database connection instance exists throughout
    the application lifecycle. This pattern is useful for resource
    management and preventing multiple database connections.
    
    Benefits:
    - Single point of database access
    - Resource efficiency (one connection)
    - Configuration centralization
    - Thread-safe implementation
    """
    
    _instance: Optional['DatabaseManager'] = None
    _lock = threading.Lock()  # Thread safety
    
    def __new__(cls) -> 'DatabaseManager':
        """
        Override __new__ to implement Singleton pattern
        
        Returns:
            Single instance of DatabaseManager
        """
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking pattern
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialize the database manager (only once)
        """
        if not getattr(self, '_initialized', False):
            self._client: Optional[MongoClient] = None
            self._database: Optional[Database] = None
            self._connection_string = None
            self._database_name = None
            self._is_connected = False
            self._initialized = True
    
    def initialize(self, connection_string: str = None, database_name: str = None) -> None:
        """
        Initialize database connection
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database to use
        """
        self._connection_string = connection_string or os.getenv('MONGODB_URI')
        self._database_name = database_name or os.getenv('DATABASE_NAME', 'donordb')
        
        if not self._connection_string:
            raise ValueError("MongoDB connection string is required")
        
        try:
            self._client = MongoClient(self._connection_string)
            self._database = self._client[self._database_name]
            
            # Test connection
            self._client.admin.command('ping')
            self._is_connected = True
            print(f"✅ Database connection established to: {self._database_name}")
            
        except Exception as e:
            self._is_connected = False
            print(f"❌ Database connection failed: {e}")
            raise
    
    def get_database(self) -> Database:
        """
        Get database instance
        
        Returns:
            MongoDB Database instance
            
        Raises:
            RuntimeError: If database is not initialized or connected
        """
        if not self._is_connected or not self._database:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        return self._database
    
    def get_client(self) -> MongoClient:
        """
        Get MongoDB client instance
        
        Returns:
            MongoDB Client instance
            
        Raises:
            RuntimeError: If database is not initialized or connected
        """
        if not self._is_connected or not self._client:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        return self._client
    
    def is_connected(self) -> bool:
        """
        Check if database is connected
        
        Returns:
            True if connected, False otherwise
        """
        return self._is_connected
    
    def get_collection(self, collection_name: str):
        """
        Get a specific collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            MongoDB Collection instance
        """
        database = self.get_database()
        return database[collection_name]
    
    def close_connection(self) -> None:
        """
        Close database connection
        """
        if self._client:
            self._client.close()
            self._is_connected = False
            print("📡 Database connection closed")
    
    def reset_connection(self) -> None:
        """
        Reset database connection (useful for testing)
        """
        self.close_connection()
        if self._connection_string and self._database_name:
            self.initialize(self._connection_string, self._database_name)
    
    def get_connection_info(self) -> dict:
        """
        Get connection information
        
        Returns:
            Dictionary with connection details
        """
        return {
            'database_name': self._database_name,
            'is_connected': self._is_connected,
            'has_client': self._client is not None,
            'has_database': self._database is not None
        }
    
    @classmethod
    def get_instance(cls) -> 'DatabaseManager':
        """
        Get the singleton instance
        
        Returns:
            DatabaseManager singleton instance
        """
        return cls()
    
    def __del__(self):
        """
        Cleanup when instance is destroyed
        """
        if hasattr(self, '_client') and self._client:
            self.close_connection()


class DatabaseConfig:
    """
    SINGLETON PATTERN for Configuration
    
    Manages application configuration as a singleton.
    Ensures consistent configuration across the application.
    """
    
    _instance: Optional['DatabaseConfig'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'DatabaseConfig':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseConfig, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not getattr(self, '_initialized', False):
            self._config = {
                'MONGODB_URI': os.getenv('MONGODB_URI'),
                'DATABASE_NAME': os.getenv('DATABASE_NAME', 'donordb'),
                'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key'),
                'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'jwt-secret-key'),
                'FLASK_ENV': os.getenv('FLASK_ENV', 'development'),
                'DEBUG': os.getenv('FLASK_ENV') == 'development'
            }
            self._initialized = True
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value) -> None:
        """Set configuration value"""
        self._config[key] = value
    
    def get_all(self) -> dict:
        """Get all configuration"""
        return self._config.copy()
    
    @classmethod
    def get_instance(cls) -> 'DatabaseConfig':
        """Get the singleton instance"""
        return cls()


# Convenience functions for accessing the singleton
def get_database() -> Database:
    """
    Convenience function to get database instance
    
    Returns:
        MongoDB Database instance
    """
    return DatabaseManager.get_instance().get_database()


def get_collection(collection_name: str):
    """
    Convenience function to get collection
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        MongoDB Collection instance
    """
    return DatabaseManager.get_instance().get_collection(collection_name)


def get_config(key: str = None, default=None):
    """
    Convenience function to get configuration
    
    Args:
        key: Configuration key to get
        default: Default value if key not found
        
    Returns:
        Configuration value or all config if key is None
    """
    config = DatabaseConfig.get_instance()
    return config.get(key, default) if key else config.get_all()


# Usage examples:
"""
# Initialize database connection
db_manager = DatabaseManager()
db_manager.initialize()

# Get database (from anywhere in the application)
database = get_database()
users_collection = get_collection('users')

# Get configuration
secret_key = get_config('SECRET_KEY')
all_config = get_config()

# The same instance is returned everywhere
manager1 = DatabaseManager()
manager2 = DatabaseManager()
assert manager1 is manager2  # True - same instance
"""