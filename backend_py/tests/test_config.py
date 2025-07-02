import pytest
import os
from unittest.mock import patch, Mock

from app.config import Settings, get_settings, get_r2_client


def test_settings_required_fields():
    """Test that Settings requires all necessary fields"""
    # Test with all required fields
    with patch.dict(os.environ, {
        "DATABASE_URL": "postgresql://test",
        "GOOGLE_CLIENT_ID": "test_client_id",
        "GOOGLE_CLIENT_SECRET": "test_secret",
        "JWT_SECRET": "test_jwt_secret"
    }):
        settings = Settings()
        assert settings.DATABASE_URL == "postgresql://test"
        assert settings.GOOGLE_CLIENT_ID == "test_client_id"
        assert settings.GOOGLE_CLIENT_SECRET == "test_secret"
        assert settings.JWT_SECRET == "test_jwt_secret"


def test_settings_missing_required_field():
    """Test that Settings raises error when required fields are missing"""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            Settings()


def test_get_settings_cached():
    """Test that get_settings returns cached instance"""
    with patch.dict(os.environ, {
        "DATABASE_URL": "postgresql://test",
        "GOOGLE_CLIENT_ID": "test_client_id",
        "GOOGLE_CLIENT_SECRET": "test_secret",
        "JWT_SECRET": "test_jwt_secret"
    }):
        # Clear cache first
        get_settings.cache_clear()
        
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Should be the same instance (cached)
        assert settings1 is settings2


def test_get_r2_client_with_config():
    """Test R2 client creation with proper configuration"""
    with patch.dict(os.environ, {
        "R2_ACCOUNT_ID": "test_account",
        "R2_BUCKET": "test_bucket",
        "R2_ENDPOINT": "https://test.r2.cloudflarestorage.com",
        "R2_TOKEN": "test_token"
    }):
        with patch("app.config.boto3.client") as mock_boto_client:
            mock_client = Mock()
            mock_boto_client.return_value = mock_client
            
            client = get_r2_client()
            
            # Verify boto3 was called with correct parameters
            mock_boto_client.assert_called_once_with(
                "s3",
                endpoint_url="https://test.r2.cloudflarestorage.com",
                aws_access_key_id="test_account",
                aws_secret_access_key="test_token",
                region_name="auto"
            )
            
            assert client == mock_client


def test_get_r2_client_without_config():
    """Test R2 client creation without configuration"""
    with patch.dict(os.environ, {}, clear=True):
        with patch("app.config.boto3.client") as mock_boto_client:
            mock_client = Mock()
            mock_boto_client.return_value = mock_client
            
            client = get_r2_client()
            
            # Should still create client but with None values
            mock_boto_client.assert_called_once_with(
                "s3",
                endpoint_url=None,
                aws_access_key_id=None,
                aws_secret_access_key=None,
                region_name="auto"
            )