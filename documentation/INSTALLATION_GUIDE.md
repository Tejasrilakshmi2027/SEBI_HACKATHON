# SEBI Sentinel AI - Installation Guide

This guide provides step-by-step instructions for setting up SEBI Sentinel AI on your local machine or production environment.

## Prerequisites

### Required Software
- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **PostgreSQL**: 15.x or higher
- **MongoDB**: 7.x or higher
- **Redis**: 7.x or higher
- **Docker**: 20.x or higher (optional, for containerized deployment)
- **Docker Compose**: 2.x or higher (optional)
- **Git**: Latest version

### System Requirements
- **CPU**: 4 cores minimum (8 cores recommended for AI processing)
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 50GB minimum (100GB recommended for file storage)
- **OS**: Linux (Ubuntu 22.04 recommended), macOS, or Windows with WSL2

## Installation Methods

### Method 1: Docker Compose (Recommended)

This is the easiest method for getting started quickly.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/your-org/sebi-sentinel-ai.git
cd SEBI_project
```

#### Step 2: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
POSTGRES_USER=sebi_user
POSTGRES_PASSWORD=sebi_password
POSTGRES_DB=sebi_db
DATABASE_URL=postgresql://sebi_user:sebi_password@postgres:5432/sebi_db

# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME=sebi_user
MONGO_INITDB_ROOT_PASSWORD=sebi_password
MONGODB_URL=mongodb://sebi_user:sebi_password@mongodb:27017

# Redis Configuration
REDIS_URL=redis://redis:6379

# Application Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=10485760

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

#### Step 3: Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- MongoDB database
- Redis cache
- FastAPI backend
- React frontend

#### Step 4: Initialize Database

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create initial admin user (optional)
docker-compose exec backend python scripts/create_admin.py
```

#### Step 5: Access the Application

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

#### Step 6: Stop Services

```bash
docker-compose down
```

To remove volumes (delete all data):

```bash
docker-compose down -v
```

### Method 2: Manual Installation

This method gives you more control over the setup.

#### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm postgresql mongodb-server redis-server
```

**macOS (with Homebrew):**
```bash
brew install python@3.11 node postgresql@15 mongodb-community redis
```

**Windows:**
- Install Python 3.11 from python.org
- Install Node.js from nodejs.org
- Install PostgreSQL from postgresql.org
- Install MongoDB from mongodb.com
- Install Redis from redis.io

#### Step 2: Clone the Repository

```bash
git clone https://github.com/your-org/sebi-sentinel-ai.git
cd SEBI_project
```

#### Step 3: Set Up PostgreSQL

```bash
# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql@15  # macOS

# Create database and user
sudo -u postgres psql
```

In PostgreSQL prompt:
```sql
CREATE USER sebi_user WITH PASSWORD 'sebi_password';
CREATE DATABASE sebi_db OWNER sebi_user;
GRANT ALL PRIVILEGES ON DATABASE sebi_db TO sebi_user;
\q
```

#### Step 4: Set Up MongoDB

```bash
# Start MongoDB service
sudo systemctl start mongod  # Linux
brew services start mongodb-community  # macOS

# Create admin user
mongosh
```

In MongoDB prompt:
```javascript
use admin
db.createUser({
  user: "sebi_user",
  pwd: "sebi_password",
  roles: [{ role: "readWriteAnyDatabase", db: "admin" }]
})
exit
```

#### Step 5: Set Up Redis

```bash
# Start Redis service
sudo systemctl start redis  # Linux
brew services start redis  # macOS
```

#### Step 6: Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://sebi_user:sebi_password@localhost:5432/sebi_db
MONGODB_URL=mongodb://sebi_user:sebi_password@localhost:27017
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
```

Run migrations:
```bash
alembic upgrade head
```

Start backend server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 7: Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_URL=http://localhost:8000
```

Start frontend development server:
```bash
npm run dev
```

#### Step 8: Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Verification

### Backend Verification

```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Should return: {"status": "healthy"}
```

### Frontend Verification

Open your browser and navigate to http://localhost:5173. You should see the landing page.

### Database Verification

**PostgreSQL:**
```bash
psql -U sebi_user -d sebi_db -c "SELECT version();"
```

**MongoDB:**
```bash
mongosh --eval "db.version()"
```

**Redis:**
```bash
redis-cli ping
# Should return: PONG
```

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Find process using port 8000
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows
```

### Database Connection Errors

1. Verify database services are running
2. Check credentials in `.env` file
3. Ensure firewall allows connections
4. Check database logs for errors

### Python Module Not Found

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Node Module Issues

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Docker Issues

```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check container logs
docker-compose logs backend
docker-compose logs frontend
```

## Production Setup

For production deployment, see the [Deployment Guide](DEPLOYMENT_GUIDE.md).

Key differences for production:
- Use strong, randomly generated secrets
- Enable HTTPS/SSL
- Configure proper CORS settings
- Set up proper logging
- Configure monitoring and alerting
- Use production-grade database configurations
- Enable rate limiting
- Set up backup and recovery procedures

## Next Steps

After installation:
1. Create an admin account
2. Configure AI model paths (if using custom models)
3. Set up monitoring
4. Configure email notifications
5. Review security settings

For more information, see:
- [Architecture Documentation](ARCHITECTURE.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
