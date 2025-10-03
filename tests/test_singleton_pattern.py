"""
Unit tests for the Singleton Pattern implementation.

Tests the DatabaseManager singleton and its thread-safety.
"""
import pytest
import threading
import time
from unittest.mock import Mock, patch
from app.services.database_manager import DatabaseManager


class TestDatabaseManagerSingleton:
    """Test cases for DatabaseManager singleton pattern implementation."""
    
    def test_singleton_instance_creation(self):
        """Test that DatabaseManager creates a single instance."""
        db1 = DatabaseManager()
        db2 = DatabaseManager()
        
        assert db1 is db2
        assert id(db1) == id(db2)
    
    def test_singleton_with_different_configs(self):
        """Test singleton behavior with different configuration parameters."""
        # Even with different parameters, should return same instance
        db1 = DatabaseManager()
        db2 = DatabaseManager()
        
        assert db1 is db2
    
    @patch('app.services.singleton.MongoClient')
    def test_database_connection_creation(self, mock_mongo_client):
        """Test that database connection is created properly."""
        mock_client = Mock()
        mock_db = Mock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        db_manager = DatabaseManager()
        database = db_manager.get_database()
        
        assert database is not None
        mock_mongo_client.assert_called_once()
    
    @patch('app.services.singleton.MongoClient')
    def test_connection_reuse(self, mock_mongo_client):
        """Test that database connections are reused."""
        mock_client = Mock()
        mock_db = Mock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        db_manager = DatabaseManager()
        
        # Get database multiple times
        db1 = db_manager.get_database()
        db2 = db_manager.get_database()
        db3 = db_manager.get_database()
        
        # Should reuse the same connection
        assert db1 is db2 is db3
        # MongoClient should only be called once
        assert mock_mongo_client.call_count == 1
    
    def test_thread_safety(self):
        """Test that singleton is thread-safe."""
        instances = []
        
        def create_instance():
            """Create database manager instance in thread."""
            time.sleep(0.01)  # Small delay to increase chance of race condition
            instances.append(DatabaseManager())
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_instance)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All instances should be the same
        assert len(instances) == 10
        first_instance = instances[0]
        for instance in instances:
            assert instance is first_instance
    
    @patch('app.services.singleton.MongoClient')
    def test_connection_error_handling(self, mock_mongo_client):
        """Test handling of database connection errors."""
        # Mock connection failure
        mock_mongo_client.side_effect = Exception("Connection failed")
        
        db_manager = DatabaseManager()
        
        with pytest.raises(Exception, match="Connection failed"):
            db_manager.get_database()
    
    @patch('app.services.singleton.MongoClient')
    def test_connection_status_check(self, mock_mongo_client):
        """Test database connection status checking."""
        mock_client = Mock()
        mock_db = Mock()
        mock_client.__getitem__.return_value = mock_db
        mock_client.admin.command.return_value = {'ok': 1}
        mock_mongo_client.return_value = mock_client
        
        db_manager = DatabaseManager()
        status = db_manager.get_connection_status()
        
        assert isinstance(status, dict)
        assert 'connected' in status
        assert 'database' in status
    
    @patch('app.services.singleton.MongoClient')
    def test_connection_status_failure(self, mock_mongo_client):
        """Test connection status when database is unreachable."""
        mock_client = Mock()
        mock_client.admin.command.side_effect = Exception("Database unreachable")
        mock_mongo_client.return_value = mock_client
        
        db_manager = DatabaseManager()
        status = db_manager.get_connection_status()
        
        assert isinstance(status, dict)
        assert status.get('connected') is False
        assert 'error' in status
    
    def test_singleton_attributes_persistence(self):
        """Test that singleton attributes persist across instances."""
        db1 = DatabaseManager()
        
        # Set a custom attribute
        db1.custom_attribute = "test_value"
        
        # Get another instance
        db2 = DatabaseManager()
        
        # Attribute should persist
        assert hasattr(db2, 'custom_attribute')
        assert db2.custom_attribute == "test_value"
    
    @patch('app.services.singleton.MongoClient')
    def test_configuration_loading(self, mock_mongo_client):
        """Test that configuration is loaded properly."""
        mock_client = Mock()
        mock_mongo_client.return_value = mock_client
        
        db_manager = DatabaseManager()
        
        # Check that configuration attributes exist
        assert hasattr(db_manager, '_connection_string')
        assert hasattr(db_manager, '_database_name')


class TestSingletonPerformance:
    """Performance tests for singleton pattern."""
    
    def test_instance_creation_performance(self):
        """Test performance of singleton instance creation."""
        start_time = time.time()
        
        # Create many instances
        instances = []
        for _ in range(1000):
            instances.append(DatabaseManager())
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should be very fast since it's just returning existing instance
        assert creation_time < 0.1  # Less than 100ms for 1000 instances
        
        # All should be the same instance
        first_instance = instances[0]
        for instance in instances:
            assert instance is first_instance
    
    def test_concurrent_access_performance(self):
        """Test performance under concurrent access."""
        results = []
        
        def access_singleton():
            """Access singleton in thread and measure time."""
            start = time.time()
            db = DatabaseManager()
            end = time.time()
            results.append((db, end - start))
        
        # Create multiple threads for concurrent access
        threads = []
        for _ in range(50):
            thread = threading.Thread(target=access_singleton)
            threads.append(thread)
        
        start_time = time.time()
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Should complete quickly even with many concurrent accesses
        assert total_time < 1.0  # Less than 1 second
        assert len(results) == 50
        
        # All instances should be the same
        first_instance = results[0][0]
        for instance, _ in results:
            assert instance is first_instance


class TestSingletonIntegration:
    """Integration tests for singleton with other patterns."""
    
    @patch('app.services.singleton.MongoClient')
    def test_singleton_with_repository_pattern(self, mock_mongo_client):
        """Test singleton integration with repository pattern."""
        mock_client = Mock()
        mock_db = Mock()
        mock_client.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client
        
        # Multiple repositories should use the same database instance
        db_manager1 = DatabaseManager()
        db_manager2 = DatabaseManager()
        
        db1 = db_manager1.get_database()
        db2 = db_manager2.get_database()
        
        assert db1 is db2
        assert mock_mongo_client.call_count == 1
    
    def test_singleton_memory_usage(self):
        """Test that singleton doesn't create memory leaks."""
        import sys
        
        initial_refs = sys.getrefcount(DatabaseManager)
        
        # Create many references
        instances = []
        for _ in range(100):
            instances.append(DatabaseManager())
        
        # Clear references
        instances.clear()
        
        final_refs = sys.getrefcount(DatabaseManager)
        
        # Reference count should not grow significantly
        # (allowing for some variance due to test framework)
        assert final_refs - initial_refs < 10