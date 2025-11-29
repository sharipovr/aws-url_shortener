"""
Unit tests for redirect Lambda handler.
"""

import json
import pytest


class TestRedirectHandler:
    """Tests for the redirect endpoint."""
    
    def test_redirect_success(self, dynamodb_table, sample_event):
        """Test successful redirect to original URL."""
        from src.handlers.redirect import handler
        
        # Arrange - first add a URL to the table
        original_url = "https://example.com/original"
        dynamodb_table.put_item(Item={
            "short_code": "abc1234",
            "original_url": original_url,
            "created_at": "2024-01-01T00:00:00Z",
            "click_count": 0
        })
        
        event = sample_event(path_parameters={"short_code": "abc1234"})
        
        # Act
        response = handler(event, None)
        
        # Assert
        assert response["statusCode"] == 301
        assert response["headers"]["Location"] == original_url
    
    def test_redirect_not_found(self, dynamodb_table, sample_event):
        """Test 404 when short code doesn't exist."""
        from src.handlers.redirect import handler
        
        # Arrange - no URL in table
        event = sample_event(path_parameters={"short_code": "notexist"})
        
        # Act
        response = handler(event, None)
        body = json.loads(response["body"])
        
        # Assert
        assert response["statusCode"] == 404
        assert "not found" in body["error"].lower()
    
    def test_redirect_missing_short_code(self, dynamodb_table, sample_event):
        """Test error when short code is not provided."""
        from src.handlers.redirect import handler
        
        # Arrange - no path parameters
        event = sample_event(path_parameters=None)
        
        # Act
        response = handler(event, None)
        body = json.loads(response["body"])
        
        # Assert
        assert response["statusCode"] == 400
        assert "required" in body["error"].lower()
    
    def test_redirect_increments_click_count(self, dynamodb_table, sample_event):
        """Test that click counter is incremented on redirect."""
        from src.handlers.redirect import handler
        
        # Arrange
        dynamodb_table.put_item(Item={
            "short_code": "clicks1",
            "original_url": "https://example.com",
            "created_at": "2024-01-01T00:00:00Z",
            "click_count": 5
        })
        
        event = sample_event(path_parameters={"short_code": "clicks1"})
        
        # Act
        handler(event, None)
        
        # Assert - check click count increased
        item = dynamodb_table.get_item(Key={"short_code": "clicks1"})
        assert item["Item"]["click_count"] == 6
    
    def test_redirect_multiple_clicks(self, dynamodb_table, sample_event):
        """Test multiple redirects increment counter correctly."""
        from src.handlers.redirect import handler
        
        # Arrange
        dynamodb_table.put_item(Item={
            "short_code": "multi1",
            "original_url": "https://example.com",
            "created_at": "2024-01-01T00:00:00Z",
            "click_count": 0
        })
        
        event = sample_event(path_parameters={"short_code": "multi1"})
        
        # Act - simulate 3 clicks
        handler(event, None)
        handler(event, None)
        handler(event, None)
        
        # Assert
        item = dynamodb_table.get_item(Key={"short_code": "multi1"})
        assert item["Item"]["click_count"] == 3
