# DevBoard Deployment Environments

This document explains how to run DevBoard in different environments using Docker Compose.

## 🏗️ Environment Overview

| Environment | Spring Profile | Database | Frontend | Use Case |
|-------------|---------------|----------|----------|----------|
| **Development** | `dev` | H2 (in-memory) | Vite dev server | Local development |
| **MySQL Testing** | `mysql` | MySQL container | Production build | Container testing |
| **Production** | `prod` | MySQL (external/container) | Nginx production | Production deployment |

## 🚀 Quick Start Commands

### Development Environment
```bash
# Full development setup with hot reload
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Access:
# - Frontend: http://localhost:5173 (Vite dev server)
# - Backend: http://localhost:8080
# - H2 Console: http://localhost:8080/h2-console
```

### MySQL Testing Environment (Current Default)
```bash
# Production-like build with MySQL
docker compose up

# Access:
# - Frontend: http://localhost:3000 (Nginx)
# - Backend: http://localhost:8080
# - MySQL: localhost:3307
```

### Production Environment
```bash
# Production deployment
docker compose -f docker-compose.yml -f docker-compose.prod.yml up

# IMPORTANT: Set environment variables first!
export JWT_SECRET="your-256-bit-secret-key"
export DATABASE_PASSWORD="secure-production-password"
export CORS_ALLOWED_ORIGINS="https://yourdomain.com"

# Access:
# - Frontend: http://localhost:3000 (Nginx, optimized)
# - Backend: http://localhost:8080
# - MySQL: localhost:3307
```

## 🔧 Environment Details

### Development (`dev` profile)
**Features:**
- 🔥 Hot reload for frontend changes
- 🗄️ H2 in-memory database (data lost on restart)
- 🐛 Debug logging enabled
- 🔓 Permissive CORS settings
- ⏰ 24-hour JWT expiration
- 📊 H2 web console available

**Configuration:**
- **Frontend**: Vite dev server (port 5173)
- **Backend**: Spring Boot dev profile
- **Database**: H2 embedded (no external dependency)

### MySQL Testing (`mysql` profile)
**Features:**
- 🏗️ Production-like container setup
- 🗄️ MySQL persistent database
- 📦 Optimized frontend build (77MB image)
- 🔒 Container networking
- ⏰ 1-hour JWT expiration

**Configuration:**
- **Frontend**: Nginx serving optimized build (port 3000)
- **Backend**: Spring Boot with MySQL
- **Database**: MySQL 8.0 container (port 3307)

### Production (`prod` profile)
**Features:**
- 🚀 Production-optimized builds
- 🔒 Security hardened
- 📊 Resource limits and monitoring
- 🔐 Environment-based secrets
- ⚡ Performance optimized
- 🛡️ Restricted CORS

**Configuration:**
- **Frontend**: Nginx with gzip, security headers
- **Backend**: Production logging, strict validation
- **Database**: Production MySQL with tuned parameters

## 📋 Environment Variables

### Required for Production
```bash
# JWT Secret (256-bit minimum)
JWT_SECRET="your-super-secure-256-bit-secret-key-here"

# Database Password
DATABASE_PASSWORD="secure-production-password"

# CORS Origins
CORS_ALLOWED_ORIGINS="https://yourdomain.com,https://api.yourdomain.com"

# Optional MySQL Root Password
MYSQL_ROOT_PASSWORD="secure-root-password"
```

### Optional Configuration
```bash
# Logging
LOG_LEVEL=INFO                    # DEBUG, INFO, WARN, ERROR
ENABLE_DEBUG_LOGS=false

# JWT Expiration
JWT_EXPIRATION_MS=3600000         # 1 hour = 3600000ms

# Database Connection Pool
DB_POOL_MAX_SIZE=20
DB_POOL_MIN_IDLE=5
```

## 🔄 Switching Environments

### From Development to Production
```bash
# Stop development
docker compose -f docker-compose.yml -f docker-compose.dev.yml down

# Start production
export JWT_SECRET="your-production-secret"
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### From MySQL Testing to Development
```bash
# Stop current
docker compose down

# Start development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 🏥 Health Checks

### Development
```bash
# Backend health
curl http://localhost:8080/actuator/health

# H2 Console
open http://localhost:8080/h2-console
```

### Production
```bash
# Application health
curl http://localhost:8080/actuator/health

# Frontend health
curl http://localhost:3000

# Container health
docker compose ps
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using ports
   lsof -i :3000,5173,8080,3307
   ```

2. **Database Connection Issues**
   ```bash
   # Check MySQL logs
   docker compose logs mysql
   ```

3. **Frontend Build Issues**
   ```bash
   # Rebuild frontend
   docker compose build frontend --no-cache
   ```

4. **Environment Variable Issues**
   ```bash
   # Verify environment variables
   docker compose config
   ```

## 📁 File Structure

```
├── docker-compose.yml          # Base configuration (MySQL testing)
├── docker-compose.dev.yml      # Development overrides
├── docker-compose.prod.yml     # Production overrides
├── devboard-backend/
│   ├── src/main/resources/
│   │   ├── application.yml      # Base Spring config
│   │   ├── application-dev.yml  # Development profile
│   │   ├── application-mysql.yml # MySQL profile
│   │   └── application-prod.yml # Production profile
└── devboard-frontend/
    ├── .env.development         # Development variables
    ├── .env.production          # Production variables
    └── .env.local.example       # Local override template
```

This setup provides a clear separation of concerns and makes it easy to deploy to different environments! 🎯