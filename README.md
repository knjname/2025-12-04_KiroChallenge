# Events Management System

A full-stack serverless application for managing events, built with FastAPI, AWS CDK, DynamoDB, Lambda, and API Gateway.

## Overview

This project provides a complete event management system with:

- **RESTful API** for CRUD operations on events
- **Serverless architecture** using AWS Lambda and API Gateway
- **NoSQL database** with DynamoDB for scalable data storage
- **Infrastructure as Code** using AWS CDK (TypeScript)
- **Python backend** with FastAPI and Pydantic validation

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   Client    │─────▶│ API Gateway  │─────▶│   Lambda    │─────▶│  DynamoDB    │
│             │      │              │      │  (FastAPI)  │      │   (Events)   │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
```

### Components

- **Backend**: FastAPI application with Mangum adapter for Lambda
- **Infrastructure**: AWS CDK stack defining all cloud resources
- **Database**: DynamoDB table with pay-per-request billing
- **API**: REST API with CORS support and comprehensive endpoints

## Project Structure

```
.
├── backend/                    # Python FastAPI backend
│   ├── src/backend/
│   │   ├── main.py            # FastAPI app and endpoints
│   │   ├── models.py          # Pydantic data models
│   │   ├── database.py        # DynamoDB client
│   │   └── __init__.py
│   ├── docs/                  # Generated API documentation
│   ├── pyproject.toml         # Python project config
│   ├── requirements.txt       # Python dependencies
│   ├── generate-docs.sh       # Documentation generator script
│   └── README.md              # Backend-specific docs
│
├── infrastructure/            # AWS CDK infrastructure
│   ├── lib/
│   │   └── infrastructure-stack.ts  # CDK stack definition
│   ├── bin/
│   │   └── infrastructure.ts        # CDK app entry point
│   ├── cdk.json              # CDK configuration
│   ├── package.json          # Node.js dependencies
│   └── README.md             # Infrastructure docs
│
├── test-api.sh               # API testing script
└── README.md                 # This file
```

## Prerequisites

- **Python 3.13+** with `uv` or `pip`
- **Node.js 18+** with `npm`
- **AWS CLI** configured with credentials
- **AWS CDK CLI**: `npm install -g aws-cdk`
- **AWS Account** with appropriate permissions

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Install dependencies
uv sync
# or: pip install -r requirements.txt

# Run locally (requires DynamoDB Local or AWS credentials)
export EVENTS_TABLE_NAME=Events
uv run uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

### 2. Infrastructure Deployment

```bash
cd infrastructure

# Install dependencies
npm install

# Build TypeScript
npm run build

# Deploy to AWS
cdk deploy
```

After deployment, note the API Gateway URL from the output.

### 3. Test the API

Update the `API_URL` in `test-api.sh` with your deployed API Gateway URL, then run:

```bash
chmod +x test-api.sh
./test-api.sh
```

## API Documentation

### Interactive Documentation

When running locally or after deployment:
- **Swagger UI**: `{API_URL}/docs`
- **ReDoc**: `{API_URL}/redoc`

### Code Documentation

Generated Python API documentation is available in `backend/docs/`. Open `backend/docs/index.html` in your browser.

To regenerate documentation:
```bash
cd backend
./generate-docs.sh
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/events` | List all events (optional `?status=` filter) |
| GET | `/events/{eventId}` | Get a specific event |
| POST | `/events` | Create a new event |
| PUT | `/events/{eventId}` | Update an event |
| DELETE | `/events/{eventId}` | Delete an event |

### Example: Create Event

```bash
curl -X POST https://your-api-url/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "event-001",
    "title": "Tech Conference 2025",
    "description": "Annual technology conference",
    "date": "2025-06-15",
    "location": "San Francisco, CA",
    "capacity": 500,
    "organizer": "Tech Corp",
    "status": "active"
  }'
```

### Example: List Events

```bash
# All events
curl https://your-api-url/prod/events

# Filter by status
curl https://your-api-url/prod/events?status=active
```

## Data Model

### Event Object

```typescript
{
  eventId: string;        // Unique identifier (1-100 chars)
  title: string;          // Event title (1-200 chars)
  description: string;    // Event description (1-1000 chars)
  date: string;           // Date in YYYY-MM-DD format
  location: string;       // Event location (1-200 chars)
  capacity: number;       // Maximum attendees (> 0)
  organizer: string;      // Event organizer (1-200 chars)
  status: string;         // "active" | "cancelled" | "completed"
}
```

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uv run uvicorn backend.main:app --reload

# Generate documentation
./generate-docs.sh

# Format code
black src/

# Lint code
ruff check src/
```

### Infrastructure Development

```bash
cd infrastructure

# Watch for changes
npm run watch

# Run tests
npm test

# Synthesize CloudFormation template
cdk synth

# Compare with deployed stack
cdk diff
```

## Deployment

### Deploy Infrastructure

```bash
cd infrastructure
cdk deploy
```

This will:
1. Create a DynamoDB table named "Events"
2. Package and deploy the Lambda function
3. Create an API Gateway REST API
4. Configure IAM permissions
5. Output the API URL

### Update Backend Code

After modifying backend code:

```bash
cd infrastructure
cdk deploy
```

CDK will automatically bundle the new code and update the Lambda function.

## Environment Variables

### Backend (Lambda)

- `EVENTS_TABLE_NAME`: DynamoDB table name (set by CDK)
- `AWS_REGION`: AWS region (set by Lambda runtime)

### Local Development

```bash
export EVENTS_TABLE_NAME=Events
export AWS_REGION=us-east-1

# For DynamoDB Local
export AWS_ENDPOINT_URL=http://localhost:8000
```

## AWS Resources

The CDK stack creates:

- **DynamoDB Table**: `Events` (pay-per-request billing)
- **Lambda Function**: Python 3.13 on ARM64 architecture
- **API Gateway**: REST API with CORS enabled
- **IAM Roles**: Lambda execution role with DynamoDB permissions
- **CloudWatch Logs**: Automatic logging for Lambda

### Cost Considerations

- DynamoDB: Pay-per-request (free tier: 25 GB storage, 25 WCU, 25 RCU)
- Lambda: Pay-per-invocation (free tier: 1M requests/month)
- API Gateway: Pay-per-request (free tier: 1M requests/month for 12 months)

## Testing

### Manual Testing

Use the provided test script:

```bash
./test-api.sh
```

### Unit Tests

```bash
# Backend tests
cd backend
pytest

# Infrastructure tests
cd infrastructure
npm test
```

## Troubleshooting

### Lambda Function Errors

Check CloudWatch Logs:
```bash
aws logs tail /aws/lambda/InfrastructureStack-EventsFunction --follow
```

### API Gateway Issues

Test the Lambda directly:
```bash
aws lambda invoke \
  --function-name InfrastructureStack-EventsFunction \
  --payload '{"httpMethod":"GET","path":"/events"}' \
  response.json
```

### DynamoDB Access

Verify table exists:
```bash
aws dynamodb describe-table --table-name Events
```

## Security

- API Gateway has CORS enabled for all origins (configure for production)
- Lambda function has minimal IAM permissions (DynamoDB read/write only)
- DynamoDB table uses encryption at rest (AWS managed keys)
- Input validation via Pydantic models

### Production Recommendations

1. Configure specific CORS origins
2. Add API Gateway authentication (API keys, Cognito, or Lambda authorizers)
3. Enable API Gateway throttling and rate limiting
4. Use AWS WAF for additional protection
5. Enable DynamoDB point-in-time recovery
6. Set up CloudWatch alarms for monitoring

## Cleanup

To remove all AWS resources:

```bash
cd infrastructure
cdk destroy
```

This will delete:
- API Gateway
- Lambda function
- DynamoDB table (including all data)
- IAM roles
- CloudWatch log groups

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **Boto3** - AWS SDK for Python
- **Mangum** - ASGI adapter for AWS Lambda
- **Uvicorn** - ASGI server

### Infrastructure
- **AWS CDK** - Infrastructure as Code
- **TypeScript** - CDK language
- **AWS Lambda** - Serverless compute
- **API Gateway** - REST API management
- **DynamoDB** - NoSQL database

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- Check the documentation in `backend/README.md` and `infrastructure/README.md`
- Review CloudWatch logs for runtime errors
- Consult AWS CDK documentation: https://docs.aws.amazon.com/cdk/

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
