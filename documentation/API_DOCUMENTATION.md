# SEBI Sentinel AI - API Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: `https://api.sebisentinel.com`

## Authentication

All API endpoints (except auth endpoints) require a valid JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### POST /api/v1/auth/signup
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "password": "securepassword123",
  "role": "investor"
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "investor",
  "is_active": true
}
```

#### POST /api/v1/auth/login
Authenticate user and receive JWT token.

**Request Body (form-data):**
```
username: user@example.com
password: securepassword123
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "role": "investor"
  }
}
```

#### POST /api/v1/auth/forgot-password
Initiate password reset.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "Password reset email sent"
}
```

#### POST /api/v1/auth/reset-password
Reset password with token.

**Request Body:**
```json
{
  "token": "reset_token_here",
  "new_password": "newpassword123"
}
```

**Response (200):**
```json
{
  "message": "Password reset successful"
}
```

#### GET /api/v1/auth/me
Get current user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "investor",
  "is_active": true
}
```

### Scans

#### POST /api/v1/scans/upload
Upload a file for scanning.

**Headers:**
```
Authorization: Bearer <token>
```

**Request (multipart/form-data):**
```
file: <file>
scan_type: email|url|pdf|image|video|audio|social_media|text
```

**Response (202):**
```json
{
  "scan_id": "scan_123",
  "status": "processing",
  "message": "Scan initiated"
}
```

#### POST /api/v1/scans/scan-url
Scan a URL for security issues.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "url": "https://example.com",
  "scan_type": "url"
}
```

**Response (202):**
```json
{
  "scan_id": "scan_124",
  "status": "processing",
  "message": "URL scan initiated"
}
```

#### GET /api/v1/scans/{scan_id}
Get scan results by ID.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "scan_id": "scan_123",
  "scan_type": "email",
  "status": "completed",
  "trust_score": 35.0,
  "risk_level": "high",
  "confidence": 0.85,
  "reasons": [
    "Suspicious sender domain detected",
    "Urgency keywords found in subject line"
  ],
  "evidence": [
    {
      "check": "sender_analysis",
      "metric": "domain_reputation",
      "value": 0.2
    }
  ],
  "recommendations": [
    "Do not click on any links in this email",
    "Verify the sender through official channels"
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### GET /api/v1/scans/history
Get user's scan history.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 50)
- `scan_type`: Filter by scan type (optional)
- `risk_level`: Filter by risk level (optional)

**Response (200):**
```json
{
  "scans": [
    {
      "scan_id": "scan_123",
      "scan_type": "email",
      "file_name": "suspicious.eml",
      "trust_score": 35.0,
      "risk_level": "high",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 50
}
```

### Dashboard

#### GET /api/v1/dashboard/stats
Get dashboard statistics.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "total_scans": 247,
  "high_risk_scans": 23,
  "avg_trust_score": 78.5,
  "threats_blocked": 156,
  "recent_scans": [...],
  "risk_distribution": {
    "low": 180,
    "medium": 30,
    "high": 23,
    "critical": 14
  }
}
```

#### GET /api/v1/dashboard/threat-heatmap
Get threat heatmap data.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "heatmap_data": [
    {
      "category": "email",
      "count": 45,
      "severity": "high"
    },
    {
      "category": "url",
      "count": 32,
      "severity": "medium"
    }
  ]
}
```

### Notifications

#### GET /api/v1/notifications
Get user notifications.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 20)
- `unread_only`: Filter by unread status (default: false)

**Response (200):**
```json
{
  "notifications": [
    {
      "id": 1,
      "type": "scan_complete",
      "title": "Scan Complete",
      "message": "Your scan scan_119 has completed",
      "is_read": false,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 15,
  "unread_count": 5
}
```

#### PUT /api/v1/notifications/{notification_id}/read
Mark notification as read.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Notification marked as read"
}
```

### Users

#### GET /api/v1/users/me
Get current user profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "investor",
  "organization": "Example Corp",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /api/v1/users/me
Update current user profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "full_name": "John Updated",
  "organization": "New Organization"
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Updated",
  "role": "investor",
  "organization": "New Organization"
}
```

#### GET /api/v1/users (Admin Only)
List all users (admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 50)
- `role`: Filter by role (optional)

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "username": "johndoe",
      "full_name": "John Doe",
      "role": "investor",
      "is_active": true
    }
  ],
  "total": 100
}
```

### Reports

#### POST /api/v1/reports/generate
Generate a report.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "report_type": "monthly_summary|threat_analysis|audit",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**Response (202):**
```json
{
  "report_id": "report_456",
  "status": "generating",
  "message": "Report generation initiated"
}
```

#### GET /api/v1/reports/{report_id}
Download generated report.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
- Content-Type: application/pdf
- Binary PDF file

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `202 Accepted`: Request accepted for processing
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or invalid
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limits

- Authentication endpoints: 10 requests per minute
- Scan endpoints: 30 requests per minute
- Other endpoints: 100 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Webhooks (Future)

Webhook notifications can be configured for scan completion events.

**Webhook Payload:**
```json
{
  "event": "scan.completed",
  "scan_id": "scan_123",
  "trust_score": 35.0,
  "risk_level": "high",
  "timestamp": "2024-01-15T10:30:00Z"
}
```
