# SEBI Sentinel AI - Architecture Documentation

## System Architecture

### High-Level Overview

SEBI Sentinel AI follows a microservices-inspired architecture with clear separation between frontend, backend, and AI processing components. The system is designed for scalability, security, and performance.

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                        │
│                      (React + TypeScript)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (Nginx)                      │
│              (Load Balancing, SSL Termination)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend Server                      │
│         (Authentication, API Endpoints, Business Logic)        │
└──────┬──────────────────────────────────────────┬───────────┘
       │                                          │
       ▼                                          ▼
┌──────────────────┐                   ┌──────────────────────┐
│   PostgreSQL      │                   │      MongoDB         │
│  (Relational DB)  │                   │   (Document Store)   │
│                  │                   │                      │
│  - Users         │                   │  - Scan Results      │
│  - Scans         │                   │  - Unstructured Data │
│  - Reports       │                   │  - AI Model Outputs  │
│  - Notifications │                   │                      │
└──────────────────┘                   └──────────────────────┘
       │                                          │
       └──────────────┬───────────────────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │      Redis       │
            │   (Cache Layer)  │
            │                 │
            │ - Session Data  │
            │ - Rate Limits   │
            │ - Query Cache   │
            └─────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Detection Models                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Email Phish  │  │ URL Scanner  │  │ PDF Verify   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │Image Deepfake│  │Video Deepfake│  │Audio Analysis│    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │Social Media  │  │Trust Engine  │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer

**Technology Stack:**
- React 18 with TypeScript
- Tailwind CSS for styling
- Framer Motion for animations
- React Router v6 for navigation
- React Query for data fetching
- Radix UI for accessible components

**Key Components:**
- **Landing Page**: Hero section, features, statistics
- **Authentication**: Login, Signup, Password Reset
- **Dashboard**: Threat analytics, recent scans, quick stats
- **Upload Center**: Drag-and-drop file upload, URL scanning
- **Scan Result**: Trust score display, evidence cards, recommendations
- **Scan History**: Searchable history with filters
- **Analytics**: Charts, graphs, threat heatmap
- **Admin Panel**: User management, system statistics

### Backend Layer

**Technology Stack:**
- FastAPI with async/await
- SQLAlchemy with async support
- Motor for async MongoDB
- redis-py for Redis operations
- Pydantic for data validation
- JWT for authentication

**API Modules:**
- **Auth Module**: Signup, login, password reset, token refresh
- **Scans Module**: File upload, URL scanning, result retrieval
- **Dashboard Module**: Statistics, recent scans, threat data
- **Notifications Module**: User notifications, alerts
- **Users Module**: Profile management, user listing (admin)
- **Reports Module**: Report generation, PDF export

### Database Layer

**PostgreSQL (Relational Data):**
- Users table (authentication, profiles)
- Scans table (scan metadata, results)
- ThreatReports table (detailed threat analysis)
- Notifications table (user notifications)
- AuditLog table (system audit trail)

**MongoDB (Unstructured Data):**
- AI model outputs (detailed analysis results)
- Scan evidence (images, text extracts)
- User preferences
- Temporary scan data

**Redis (Cache Layer):**
- Session storage
- Rate limiting counters
- Query result caching
- Background task queues

### AI Detection Layer

**Email Phishing Detector:**
- Header analysis (SPF, DKIM, DMARC)
- Sender domain verification
- Subject line analysis (urgency, caps)
- Body text analysis (grammar, keywords)
- Link analysis (suspicious URLs, typosquatting)
- Attachment analysis (file types, names)

**URL Scanner:**
- SSL/TLS certificate verification
- HTTPS enforcement check
- Domain age calculation
- WHOIS data analysis
- Typosquatting detection
- Blacklist checking
- Suspicious TLD detection

**PDF Verifier:**
- Metadata extraction and validation
- OCR for text extraction
- Logo detection and verification
- Layout analysis
- Signature verification
- QR code detection and analysis
- Font consistency check

**Image Deepfake Detector:**
- EXIF metadata analysis
- Blur detection
- Edge analysis
- Noise pattern analysis
- Color distribution analysis
- Face detection and analysis
- Compression artifact detection
- Error Level Analysis (ELA)

**Video Deepfake Detector:**
- Temporal consistency analysis
- Blink detection
- Lip sync analysis
- Face consistency tracking
- Compression artifact analysis
- Lighting consistency
- Motion pattern analysis

**Audio Analyzer:**
- Spectral analysis
- Pitch detection and analysis
- Noise floor analysis
- Rhythm pattern analysis
- Timbre analysis
- Silence pattern detection
- Quality metrics

**Social Media Scanner:**
- Scam keyword detection
- Pump-and-dump pattern detection
- Urgency indicator analysis
- Link analysis
- Platform detection
- Sentiment analysis
- Grammar and style analysis

**Trust Engine:**
- Risk score aggregation
- Trust score calculation (0-100)
- Risk level determination
- Confidence calculation
- Evidence generation
- Recommendation generation

**Explainable AI:**
- Suspicious area identification
- Content highlighting
- Feature importance calculation
- Decision path explanation
- Visual explanation generation

## Security Architecture

### Authentication Flow
1. User submits credentials
2. Backend validates against PostgreSQL
3. JWT token generated with user claims
4. Token stored in localStorage (frontend)
5. Token sent with each API request
6. Middleware validates token on protected routes

### Authorization
- Role-based access control (investor, broker, admin)
- Protected routes require valid JWT
- Admin-only endpoints for sensitive operations

### Data Protection
- Passwords hashed with bcrypt
- Sensitive data encrypted at rest
- HTTPS enforced in production
- Input validation on all endpoints
- SQL injection prevention via ORM
- XSS protection via content sanitization

### Rate Limiting
- Token bucket algorithm
- Per-endpoint rate limits
- IP-based throttling
- Redis-backed distributed limits

## Deployment Architecture

### Development Environment
- Local PostgreSQL, MongoDB, Redis
- Backend running on port 8000
- Frontend running on port 3000
- Hot reload enabled

### Production Environment
- Docker containers for all services
- Nginx as reverse proxy
- SSL/TLS termination
- Load balancing (multiple instances)
- Auto-scaling based on load
- Database replication
- Redis cluster for caching

## Data Flow

### Scan Request Flow
1. User uploads file/URL via frontend
2. Frontend sends to backend API
3. Backend validates and stores file
4. Background task created
5. Appropriate AI model invoked
6. Results stored in MongoDB
7. Metadata stored in PostgreSQL
8. Frontend polls for results
9. Results displayed with explanations

### Authentication Flow
1. User submits login credentials
2. Backend validates against PostgreSQL
3. JWT token generated
4. Token returned to frontend
5. Token stored in localStorage
6. Subsequent requests include token
7. Middleware validates token
8. Request processed if valid

## Performance Considerations

### Caching Strategy
- Redis for frequently accessed data
- Query result caching
- Session storage in Redis
- Static file caching via Nginx

### Async Processing
- FastAPI async/await for I/O operations
- Background tasks for AI processing
- Async database operations
- Non-blocking file I/O

### Scalability
- Stateless API design
- Horizontal scaling via Docker
- Database connection pooling
- Redis for distributed caching
- Load balancing ready

## Monitoring and Logging

### Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR
- Audit trail for sensitive operations
- Error tracking and alerting

### Monitoring
- Application metrics (response time, error rate)
- Database metrics (query performance, connections)
- System metrics (CPU, memory, disk)
- Custom business metrics (scans per day, threat detection rate)

## Backup and Recovery

### Database Backups
- PostgreSQL daily backups
- MongoDB snapshots
- Redis persistence
- Automated backup verification

### Disaster Recovery
- Multi-region deployment option
- Database replication
- Failover procedures
- Data restoration procedures
