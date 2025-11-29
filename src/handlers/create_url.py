"""
Lambda handler for creating short URLs.

Receives a long URL, generates a short code, stores in DynamoDB,
and returns the shortened URL.
"""

import json
import os
import hashlib
import time
from datetime import datetime, timezone

import boto3
import validators


# Get table name from environment variable
TABLE_NAME = os.environ.get("TABLE_NAME", "url-shortener")

# DynamoDB client (created outside handler for reuse across invocations)
dynamodb = boto3.resource("dynamodb")


def generate_short_code(url: str) -> str:
    """
    Generate a short code for the given URL.
    
    Uses MD5 hash of URL + timestamp, then takes first 7 characters.
    This gives us 62^7 ≈ 3.5 trillion possible combinations.
    """
    # Add timestamp to make codes unique even for same URL
    unique_string = f"{url}{time.time()}"
    
    # Create hash and take first 7 chars
    hash_object = hashlib.md5(unique_string.encode())
    short_code = hash_object.hexdigest()[:7]
    
    return short_code


def handler(event: dict, context) -> dict:
    """
    Lambda handler for POST /urls endpoint.
    
    Expected request body:
        {"url": "https://example.com/some/long/url"}
    
    Returns:
        201: Short URL created successfully
        400: Invalid request (missing URL or invalid format)
        500: Server error
    """
    try:
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        original_url = body.get("url")
        
        # Validate: URL is required
        if not original_url:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "URL is required"})
            }
        
        # Validate: must be a valid URL format
        if not validators.url(original_url):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid URL format"})
            }
        
        # Generate short code
        short_code = generate_short_code(original_url)
        
        # Current timestamp in ISO format
        created_at = datetime.now(timezone.utc).isoformat()
        
        # Save to DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(
            Item={
                "short_code": short_code,
                "original_url": original_url,
                "created_at": created_at,
                "click_count": 0
            }
        )
        
        # Build response
        # Note: BASE_URL will be set after deployment
        base_url = os.environ.get("BASE_URL", "http://localhost:3000")
        short_url = f"{base_url}/{short_code}"
        
        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "short_code": short_code,
                "short_url": short_url,
                "original_url": original_url,
                "created_at": created_at
            })
        }
        
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }
    except Exception as e:
        # Log error for debugging (visible in CloudWatch)
        print(f"Error: {str(e)}")
        
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"})
        }

