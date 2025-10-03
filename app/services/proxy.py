"""
Proxy Pattern - Database Caching and Access Control

The Proxy Pattern provides a placeholder/surrogate for another object to control access,
add functionality like caching, or implement lazy loading.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json
import time
from ..models.campaign import Campaign
from ..models.donation import Donation
from ..models.user import User
from .repository import CampaignRepository, DonationRepository, UserRepository


class CacheInterface(ABC):
    """
    PROXY PATTERN - Abstract cache interface
    
    Defines the interface for cache operations used by proxy classes.
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL (time to live)"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass


class InMemoryCache(CacheInterface):
    """
    PROXY PATTERN - In-memory cache implementation
    
    Simple in-memory cache with TTL support for development/testing.
    """
    
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self._cache:
            entry = self._cache[key]
            if entry['expires_at'] > datetime.utcnow():
                entry['hits'] = entry.get('hits', 0) + 1
                entry['last_accessed'] = datetime.utcnow()
                return entry['value']
            else:
                # Expired entry - remove it
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL"""
        self._cache[key] = {
            'value': value,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(seconds=ttl),
            'hits': 0,
            'last_accessed': datetime.utcnow()
        }
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        return self.get(key) is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.utcnow()
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if entry['expires_at'] <= now)
        total_hits = sum(entry.get('hits', 0) for entry in self._cache.values())
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'total_hits': total_hits,
            'cache_keys': list(self._cache.keys())
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry['expires_at'] <= now
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)


class CachedRepositoryProxy:
    """
    PROXY PATTERN - Base cached repository proxy
    
    Provides caching functionality for repository operations.
    """
    
    def __init__(self, repository, cache: CacheInterface, default_ttl: int = 300):
        """
        Initialize cached repository proxy
        
        Args:
            repository: Actual repository to proxy
            cache: Cache implementation
            default_ttl: Default cache TTL in seconds
        """
        self._repository = repository
        self._cache = cache
        self._default_ttl = default_ttl
        self._hit_count = 0
        self._miss_count = 0
    
    def _generate_cache_key(self, operation: str, *args, **kwargs) -> str:
        """
        Generate cache key for operation
        
        Args:
            operation: Operation name
            *args: Operation arguments
            **kwargs: Operation keyword arguments
            
        Returns:
            Cache key string
        """
        # Create a simple hash of the arguments
        key_parts = [operation]
        
        # Add args
        for arg in args:
            if hasattr(arg, '__dict__'):
                # Object with attributes
                key_parts.append(str(type(arg).__name__))
                if hasattr(arg, 'id'):
                    key_parts.append(str(arg.id))
            else:
                key_parts.append(str(arg))
        
        # Add sorted kwargs
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        return "_".join(key_parts)
    
    def _cache_result(self, key: str, result: Any, ttl: Optional[int] = None) -> Any:
        """Cache operation result"""
        cache_ttl = ttl or self._default_ttl
        
        # Serialize complex objects for caching
        if isinstance(result, list):
            # Convert list of objects to dictionaries
            cache_value = [
                item.to_dict() if hasattr(item, 'to_dict') else item
                for item in result
            ]
        elif hasattr(result, 'to_dict'):
            cache_value = result.to_dict()
        else:
            cache_value = result
        
        self._cache.set(key, cache_value, cache_ttl)
        return result
    
    def _get_cached_result(self, key: str, result_type: type = None) -> Optional[Any]:
        """Get cached result and convert back to objects if needed"""
        cached_value = self._cache.get(key)
        if cached_value is None:
            self._miss_count += 1
            return None
        
        self._hit_count += 1
        
        # Convert dictionaries back to objects if needed
        if result_type and isinstance(cached_value, list):
            return [result_type.from_dict(item) if isinstance(item, dict) else item 
                   for item in cached_value]
        elif result_type and isinstance(cached_value, dict):
            return result_type.from_dict(cached_value)
        
        return cached_value
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hit_count': self._hit_count,
            'miss_count': self._miss_count,
            'total_requests': total_requests,
            'hit_rate_percentage': round(hit_rate, 2)
        }
    
    def invalidate_cache_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        # Simple pattern matching for cache keys
        count = 0
        if hasattr(self._cache, '_cache'):
            keys_to_delete = [
                key for key in self._cache._cache.keys()
                if pattern in key
            ]
            for key in keys_to_delete:
                self._cache.delete(key)
                count += 1
        return count


class CachedCampaignRepositoryProxy(CachedRepositoryProxy):
    """
    PROXY PATTERN - Cached Campaign Repository
    
    Provides caching for campaign repository operations.
    """
    
    def __init__(self, campaign_repository: CampaignRepository, cache: CacheInterface):
        super().__init__(campaign_repository, cache, default_ttl=600)  # 10 minutes for campaigns
    
    def find_all(self, limit: Optional[int] = None, status: Optional[str] = None) -> List[Campaign]:
        """Find all campaigns with caching"""
        cache_key = self._generate_cache_key("find_all", limit=limit, status=status)
        
        # Try to get from cache
        cached_result = self._get_cached_result(cache_key, Campaign)
        if cached_result is not None:
            return cached_result
        
        # Get from repository and cache
        result = self._repository.find_all(limit=limit, status=status)
        return self._cache_result(cache_key, result)
    
    def find_by_id(self, campaign_id: str) -> Optional[Campaign]:
        """Find campaign by ID with caching"""
        cache_key = self._generate_cache_key("find_by_id", campaign_id)
        
        # Try to get from cache
        cached_result = self._get_cached_result(cache_key, Campaign)
        if cached_result is not None:
            return cached_result
        
        # Get from repository and cache
        result = self._repository.find_by_id(campaign_id)
        if result:
            return self._cache_result(cache_key, result)
        return result
    
    def create(self, campaign: Campaign) -> Campaign:
        """Create campaign and invalidate related cache"""
        result = self._repository.create(campaign)
        
        # Invalidate find_all cache entries
        self.invalidate_cache_pattern("find_all")
        
        return result
    
    def update(self, campaign: Campaign) -> Campaign:
        """Update campaign and invalidate related cache"""
        result = self._repository.update(campaign)
        
        # Invalidate specific campaign and find_all cache
        self.invalidate_cache_pattern(f"find_by_id_{campaign.id}")
        self.invalidate_cache_pattern("find_all")
        
        return result
    
    def delete(self, campaign_id: str) -> bool:
        """Delete campaign and invalidate related cache"""
        result = self._repository.delete(campaign_id)
        
        if result:
            # Invalidate specific campaign and find_all cache
            self.invalidate_cache_pattern(f"find_by_id_{campaign_id}")
            self.invalidate_cache_pattern("find_all")
        
        return result
    
    def find_by_creator(self, creator_id: str) -> List[Campaign]:
        """Find campaigns by creator with caching"""
        cache_key = self._generate_cache_key("find_by_creator", creator_id)
        
        # Try to get from cache
        cached_result = self._get_cached_result(cache_key, Campaign)
        if cached_result is not None:
            return cached_result
        
        # Get from repository and cache
        result = self._repository.find_by_creator(creator_id)
        return self._cache_result(cache_key, result)


class CachedDonationRepositoryProxy(CachedRepositoryProxy):
    """
    PROXY PATTERN - Cached Donation Repository
    
    Provides caching for donation repository operations with shorter TTL
    since donations change frequently.
    """
    
    def __init__(self, donation_repository: DonationRepository, cache: CacheInterface):
        super().__init__(donation_repository, cache, default_ttl=120)  # 2 minutes for donations
    
    def find_all(self, limit: Optional[int] = None) -> List[Donation]:
        """Find all donations with caching"""
        cache_key = self._generate_cache_key("find_all", limit=limit)
        
        # Try to get from cache
        cached_result = self._get_cached_result(cache_key, Donation)
        if cached_result is not None:
            return cached_result
        
        # Get from repository and cache
        result = self._repository.find_all(limit=limit)
        return self._cache_result(cache_key, result, ttl=60)  # Shorter TTL for all donations
    
    def find_by_campaign(self, campaign_id: str) -> List[Donation]:
        """Find donations by campaign with caching"""
        cache_key = self._generate_cache_key("find_by_campaign", campaign_id)
        
        # Try to get from cache
        cached_result = self._get_cached_result(cache_key, Donation)
        if cached_result is not None:
            return cached_result
        
        # Get from repository and cache
        result = self._repository.find_by_campaign(campaign_id)
        return self._cache_result(cache_key, result)
    
    def create(self, donation: Donation) -> Donation:
        """Create donation and invalidate related cache"""
        result = self._repository.create(donation)
        
        # Invalidate related cache entries
        self.invalidate_cache_pattern("find_all")
        self.invalidate_cache_pattern(f"find_by_campaign_{donation.campaign_id}")
        self.invalidate_cache_pattern(f"find_by_donor_{donation.donor_id}")
        
        return result


class AccessControlProxy:
    """
    PROXY PATTERN - Access Control Proxy
    
    Controls access to repository operations based on user permissions.
    """
    
    def __init__(self, repository, user_context: Optional[User] = None):
        """
        Initialize access control proxy
        
        Args:
            repository: Repository to control access to
            user_context: Current user context
        """
        self._repository = repository
        self._user_context = user_context
        self._access_log = []
    
    def set_user_context(self, user: User) -> None:
        """Set the current user context"""
        self._user_context = user
    
    def _log_access(self, operation: str, resource: str, allowed: bool, reason: str = "") -> None:
        """Log access attempt"""
        self._access_log.append({
            'timestamp': datetime.utcnow(),
            'user_id': self._user_context.id if self._user_context else None,
            'user_role': self._user_context.role if self._user_context else None,
            'operation': operation,
            'resource': resource,
            'allowed': allowed,
            'reason': reason
        })
    
    def _check_permission(self, operation: str, resource: Any = None) -> tuple[bool, str]:
        """
        Check if current user has permission for operation
        
        Args:
            operation: Operation being attempted
            resource: Resource being accessed (optional)
            
        Returns:
            Tuple of (allowed, reason)
        """
        if not self._user_context:
            return False, "No user context"
        
        # Admin can do everything
        if self._user_context.role == 'admin':
            return True, "Admin access"
        
        # Read operations are generally allowed
        if operation in ['read', 'find', 'get']:
            return True, "Read access allowed"
        
        # Write operations need ownership or admin
        if operation in ['create', 'update', 'delete']:
            # For create operations, check if user is authenticated
            if operation == 'create':
                return True, "Authenticated create access"
            
            # For update/delete, check ownership
            if hasattr(resource, 'creator_id') and resource.creator_id == self._user_context.id:
                return True, "Owner access"
            elif hasattr(resource, 'donor_id') and resource.donor_id == self._user_context.id:
                return True, "Donor access"
            else:
                return False, "Not owner or admin"
        
        return False, "Unknown operation"
    
    def find_all(self, *args, **kwargs):
        """Controlled find_all operation"""
        allowed, reason = self._check_permission('read')
        self._log_access('find_all', 'all', allowed, reason)
        
        if not allowed:
            raise PermissionError(f"Access denied: {reason}")
        
        return self._repository.find_all(*args, **kwargs)
    
    def find_by_id(self, resource_id: str):
        """Controlled find_by_id operation"""
        allowed, reason = self._check_permission('read')
        self._log_access('find_by_id', resource_id, allowed, reason)
        
        if not allowed:
            raise PermissionError(f"Access denied: {reason}")
        
        return self._repository.find_by_id(resource_id)
    
    def create(self, resource):
        """Controlled create operation"""
        allowed, reason = self._check_permission('create', resource)
        self._log_access('create', str(type(resource).__name__), allowed, reason)
        
        if not allowed:
            raise PermissionError(f"Access denied: {reason}")
        
        return self._repository.create(resource)
    
    def update(self, resource):
        """Controlled update operation"""
        allowed, reason = self._check_permission('update', resource)
        self._log_access('update', getattr(resource, 'id', 'unknown'), allowed, reason)
        
        if not allowed:
            raise PermissionError(f"Access denied: {reason}")
        
        return self._repository.update(resource)
    
    def delete(self, resource_id: str):
        """Controlled delete operation"""
        # First get the resource to check ownership
        resource = self._repository.find_by_id(resource_id)
        allowed, reason = self._check_permission('delete', resource)
        self._log_access('delete', resource_id, allowed, reason)
        
        if not allowed:
            raise PermissionError(f"Access denied: {reason}")
        
        return self._repository.delete(resource_id)
    
    def get_access_log(self, limit: int = 100) -> List[Dict]:
        """Get recent access log entries"""
        return self._access_log[-limit:]


# Global cache instance
_global_cache = InMemoryCache()

def get_global_cache() -> CacheInterface:
    """Get the global cache instance"""
    return _global_cache

def create_cached_campaign_repository(repository: CampaignRepository) -> CachedCampaignRepositoryProxy:
    """Create a cached campaign repository proxy"""
    return CachedCampaignRepositoryProxy(repository, get_global_cache())

def create_cached_donation_repository(repository: DonationRepository) -> CachedDonationRepositoryProxy:
    """Create a cached donation repository proxy"""
    return CachedDonationRepositoryProxy(repository, get_global_cache())


# Usage examples:
"""
# Create cached repositories
cached_campaign_repo = create_cached_campaign_repository(campaign_repository)
cached_donation_repo = create_cached_donation_repository(donation_repository)

# Use with caching
campaigns = cached_campaign_repo.find_all()  # Database query
campaigns = cached_campaign_repo.find_all()  # Cache hit

# Access control
controlled_repo = AccessControlProxy(campaign_repository, current_user)
try:
    campaign = controlled_repo.find_by_id(campaign_id)
except PermissionError as e:
    print(f"Access denied: {e}")

# Cache statistics
stats = cached_campaign_repo.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate_percentage']}%")
"""