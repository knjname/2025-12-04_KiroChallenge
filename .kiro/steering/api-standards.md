---
inclusion: fileMatch
fileMatchPattern: '**/*{api,route,endpoint,controller,handler}*.{py,ts,js}'
---

# API Standards and Conventions

## REST API Conventions

### HTTP Methods
- **GET**: Retrieve resources (read-only, idempotent)
- **POST**: Create new resources
- **PUT**: Update/replace entire resources (idempotent)
- **PATCH**: Partially update resources
- **DELETE**: Remove resources (idempotent)

### Status Codes
- **200 OK**: Successful GET, PUT, PATCH, or DELETE
- **201 Created**: Successful POST that creates a resource
- **204 No Content**: Successful request with no response body
- **400 Bad Request**: Invalid request data or parameters
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Request conflicts with current state
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server-side errors

### Error Response Format
All error responses must follow this JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context or validation errors"
    }
  }
}
```

Example error codes:
- `VALIDATION_ERROR`: Input validation failed
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `UNAUTHORIZED`: Authentication failed
- `FORBIDDEN`: Insufficient permissions
- `INTERNAL_ERROR`: Unexpected server error

## JSON Response Format Standards

### Success Response Structure
```json
{
  "data": {
    // Resource data or array of resources
  },
  "meta": {
    "timestamp": "ISO 8601 timestamp",
    "request_id": "unique-request-identifier"
  }
}
```

### Pagination Response Structure
```json
{
  "data": [],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  },
  "links": {
    "self": "/api/resource?page=1",
    "next": "/api/resource?page=2",
    "prev": null,
    "first": "/api/resource?page=1",
    "last": "/api/resource?page=5"
  }
}
```

### Naming Conventions
- Use snake_case for JSON keys
- Use plural nouns for collection endpoints: `/api/users`, `/api/products`
- Use singular nouns for single resource endpoints: `/api/user/{id}`
- Use kebab-case for URL paths: `/api/user-profiles`

### Best Practices
- Always include appropriate Content-Type headers (`application/json`)
- Use ISO 8601 format for timestamps
- Include request IDs for tracing and debugging
- Validate all input data before processing
- Return meaningful error messages
- Use consistent field names across all endpoints
