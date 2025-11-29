"""
Lambda handler for redirecting short URLs to original URLs.

Looks up the short code in DynamoDB and returns a 301 redirect.
"""

import json
import os

import boto3


# Get table name from environment variable
TABLE_NAME = os.environ.get("TABLE_NAME", "url-shortener")


def handler(event: dict, context) -> dict:
    """
    Lambda handler for GET /{short_code} endpoint.
    
    Looks up the short code in DynamoDB and redirects to original URL.
    Also increments the click counter.
    
    Returns:
        301: Redirect to original URL
        404: Short code not found
        500: Server error
    """
    try:
        # Get short code from path parameters
        # API Gateway passes it as: {"pathParameters": {"short_code": "abc1234"}}
        path_params = event.get("pathParameters", {}) or {}
        short_code = path_params.get("short_code")
        
        if not short_code:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Short code is required"})
            }
        
        # Look up in DynamoDB
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(TABLE_NAME)
        response = table.get_item(Key={"short_code": short_code})
        
        # Check if item exists
        item = response.get("Item")
        if not item:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Short URL not found"})
            }
        
        original_url = item["original_url"]
        
        # Increment click counter (fire and forget, don't wait)
        table.update_item(
            Key={"short_code": short_code},
            UpdateExpression="SET click_count = click_count + :inc",
            ExpressionAttributeValues={":inc": 1}
        )
        
        # Return 301 redirect
        return {
            "statusCode": 301,
            "headers": {
                "Location": original_url,
                "Cache-Control": "no-cache"
            },
            "body": ""
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"})
        }

