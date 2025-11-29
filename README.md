# AWS URL Shortener

Serverless URL shortener built with AWS Lambda, API Gateway, and DynamoDB.

## Architecture

```
┌──────────┐     ┌─────────────────┐     ┌────────────────┐     ┌───────────┐
│  Client  │────▶│  API Gateway    │────▶│  Lambda        │────▶│ DynamoDB  │
│          │     │  /urls (POST)   │     │  create_url    │     │           │
└──────────┘     │  /{code} (GET)  │     │  redirect      │     └───────────┘
                 └─────────────────┘     └────────────────┘
```

**Services used:**
- AWS Lambda — serverless compute
- Amazon API Gateway — HTTP endpoints
- Amazon DynamoDB — NoSQL database
- AWS SAM — infrastructure as code

## Live Demo

**API Endpoint:** `https://4jgryzxjr0.execute-api.us-east-1.amazonaws.com/prod`

### Create Short URL

```bash
curl -X POST https://4jgryzxjr0.execute-api.us-east-1.amazonaws.com/prod/urls \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/sharipovr"}'
```

Response:
```json
{
  "short_code": "054317f",
  "short_url": "https://4jgryzxjr0.execute-api.us-east-1.amazonaws.com/prod/054317f",
  "original_url": "https://github.com/sharipovr",
  "created_at": "2025-11-29T05:03:32.563256+00:00"
}
```

### Redirect

Open in browser or use curl:
```bash
curl -L https://4jgryzxjr0.execute-api.us-east-1.amazonaws.com/prod/054317f
```

## Project Structure

```
aws-url_shortener/
├── src/handlers/
│   ├── create_url.py      # POST /urls — creates short URL
│   └── redirect.py        # GET /{code} — redirects to original
├── tests/
│   ├── conftest.py        # pytest fixtures with moto
│   └── unit/
│       ├── test_create_url.py
│       └── test_redirect.py
├── template.yaml          # AWS SAM template
├── requirements.txt       # production dependencies
└── requirements-dev.txt   # dev dependencies (pytest, moto)
```

## Local Development

### Prerequisites
- Python 3.12+
- AWS CLI
- AWS SAM CLI

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v
```

### Deploy

```bash
# Build
sam build

# Deploy (first time)
sam deploy --guided

# Deploy (subsequent)
sam deploy
```

## API Reference

### POST /urls

Create a short URL.

**Request:**
```json
{
  "url": "https://example.com/very/long/path"
}
```

**Response (201):**
```json
{
  "short_code": "abc1234",
  "short_url": "https://api.../prod/abc1234",
  "original_url": "https://example.com/very/long/path",
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Errors:**
- `400` — URL is required or invalid format

### GET /{short_code}

Redirect to original URL.

**Response:**
- `301` — Redirect to original URL
- `404` — Short code not found

## Tech Stack

| Component | Technology         |
|-----------|--------------------|
| Runtime   | Python 3.12        |
| Compute   | AWS Lambda         |
| API       | Amazon API Gateway |
| Database  | Amazon DynamoDB    |
| IaC       | AWS SAM            |
| Testing   | pytest + moto      |

## Cleanup

To delete all AWS resources:

```bash
sam delete --stack-name url-shortener
```

## License

MIT
