"""
Unit tests for create_url Lambda handler.
"""

import json
import pytest


class TestCreateUrlHandler:
    """Tests for the create URL endpoint."""
    
    def test_create_url_success(self, dynamodb_table, sample_event):
        """Test successful URL creation."""
        # Import handler inside test (after mock is set up)
        from src.handlers.create_url import handler
        
        # Arrange
        event = sample_event(
            body={"url": "https://example.com/very/long/path"},
            http_method="POST"
        )
        
        # Act
        response = handler(event, None)
        body = json.loads(response["body"])
        
        # Assert
        assert response["statusCode"] == 201
        assert "short_code" in body
        assert len(body["short_code"]) == 7
        assert body["original_url"] == "https://example.com/very/long/path"
        assert "short_url" in body
        assert "created_at" in body
    
    def test_create_url_missing_url(self, dynamodb_table, sample_event):
        """Test error when URL is not provided."""
        from src.handlers.create_url import handler
        
        # Arrange - empty body
        event = sample_event(body={}, http_method="POST")
        
        # Act
        response = handler(event, None)
        body = json.loads(response["body"])
        
        # Assert
        assert response["statusCode"] == 400
        assert body["error"] == "URL is required"
    
    def test_create_url_invalid_url(self, dynamodb_table, sample_event):
        """Test error when URL format is invalid."""
        from src.handlers.create_url import handler
        
        # Arrange - invalid URL
        event = sample_event(
            body={"url": "not-a-valid-url"},
            http_method="POST"
        )
        
        # Act
        response = handler(event, None)
        body = json.loads(response["body"])
        
        # Assert
        assert response["statusCode"] == 400
        assert body["error"] == "Invalid URL format"
    
    def test_create_url_invalid_json(self, dynamodb_table, sample_event):
        """Test error when request body is not valid JSON."""
        from src.handlers.create_url import handler
        
        # Arrange - invalid JSON
        event = {
            "httpMethod": "POST",
            "body": "not valid json{{{",
            "headers": {}
        }
        
        # Act
        response = handler(event, None)
        body = json.loads(response["body"])
        
        # Assert
        assert response["statusCode"] == 400
        assert "Invalid JSON" in body["error"]
    
    def test_create_url_stores_in_dynamodb(self, dynamodb_table, sample_event):
        """Test that URL is actually stored in DynamoDB."""
        from src.handlers.create_url import handler
        
        # Arrange
        test_url = "https://example.com/test"
        event = sample_event(body={"url": test_url}, http_method="POST")
        
        # Act
        response = handler(event, None)
        body = json.loads(response["body"])
        short_code = body["short_code"]
        
        # Assert - check DynamoDB
        item = dynamodb_table.get_item(Key={"short_code": short_code})
        assert "Item" in item
        assert item["Item"]["original_url"] == test_url
        assert item["Item"]["click_count"] == 0


class TestGenerateShortCode:
    """Tests for the short code generation function."""
    
    def test_short_code_length(self):
        """Test that generated code has correct length."""
        from src.handlers.create_url import generate_short_code
        
        code = generate_short_code("https://example.com")
        
        assert len(code) == 7
    
    def test_short_code_alphanumeric(self):
        """Test that generated code contains only hex characters."""
        from src.handlers.create_url import generate_short_code
        
        code = generate_short_code("https://example.com")
        
        # MD5 produces hex characters (0-9, a-f)
        assert all(c in "0123456789abcdef" for c in code)
    
    def test_different_urls_different_codes(self):
        """Test that different URLs produce different codes."""
        from src.handlers.create_url import generate_short_code
        
        code1 = generate_short_code("https://example1.com")
        code2 = generate_short_code("https://example2.com")
        
        assert code1 != code2
