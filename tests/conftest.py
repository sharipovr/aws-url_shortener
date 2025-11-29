"""
Pytest configuration and shared fixtures.

This file is automatically loaded by pytest.
Fixtures defined here are available to all tests.
"""

import os
import pytest
import boto3
from moto import mock_dynamodb


@pytest.fixture(autouse=True)
def aws_credentials():
    """
    Mock AWS credentials for moto.
    
    autouse=True means this runs before every test automatically.
    """
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def dynamodb_table():
    """
    Create a mock DynamoDB table for testing.
    
    Usage in tests:
        def test_something(dynamodb_table):
            # Table is already created and ready to use
            ...
    """
    with mock_dynamodb():
        # Set table name in environment
        os.environ["TABLE_NAME"] = "test-url-shortener"
        
        # Create DynamoDB table
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        
        table = dynamodb.create_table(
            TableName="test-url-shortener",
            KeySchema=[
                {"AttributeName": "short_code", "KeyType": "HASH"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "short_code", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        
        # Wait for table to be created
        table.wait_until_exists()
        
        yield table


@pytest.fixture
def sample_event():
    """
    Factory fixture for creating API Gateway events.
    
    Usage:
        def test_something(sample_event):
            event = sample_event(body={"url": "https://example.com"})
    """
    def _create_event(
        body: dict = None,
        path_parameters: dict = None,
        http_method: str = "GET"
    ) -> dict:
        import json
        
        return {
            "httpMethod": http_method,
            "body": json.dumps(body) if body is not None else None,
            "pathParameters": path_parameters,
            "headers": {"Content-Type": "application/json"},
            "requestContext": {
                "requestId": "test-request-id"
            }
        }
    
    return _create_event

