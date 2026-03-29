# Container Deployment Guide for DevBoard

## 📚 Container Basics (Start Here!)

### What are Containers?
Think of containers like **lightweight virtual machines**, but much more efficient. Instead of running a full operating system, containers share the host OS kernel but isolate the application and its dependencies.

**Real-world analogy**: Containers are like shipping containers 📦
- **Standardized**: Same container works on any ship, truck, or port
- **Isolated**: Contents don't affect other containers
- **Portable**: Move from development → testing → production seamlessly
- **Lightweight**: Much lighter than shipping a whole truck for each package

### Docker vs Traditional Deployment

**Traditional Deployment:**
```
Your Computer                    Production Server
├── Java 21                     ├── Java 17 ❌ (Version mismatch!)
├── Node.js 18                  ├── Node.js 16 ❌ (Different version!)
├── MySQL 8.0                   ├── PostgreSQL 13 ❌ (Wrong database!)
└── Your App                    └── "It works on my machine!" 😫
```

**Container Deployment:**
```
Your Computer                    Production Server
├── Docker                      ├── Docker
└── Container 📦                └── Same Container 📦 ✅
    ├── Java 21                     ├── Java 21
    ├── Your App                    ├── Your App  
    ├── All Dependencies            ├── All Dependencies
    └── Exact Environment           └── Exact Environment
```

### Key Docker Concepts

#### 1. **Image** 🖼️
- A **blueprint** or **template** for creating containers
- Contains your application + all dependencies + operating system
- **Immutable** (never changes once built)
- Like a **class** in programming - defines what a container should look like

#### 2. **Container** 📦
- A **running instance** of an image
- Like an **object** created from a class
- Can start, stop, restart, delete
- **Isolated** from other containers and host system

#### 3. **Dockerfile** 📄
- **Text file** with instructions on how to build an image
- Like a **recipe** for creating your application environment
```dockerfile
FROM java:21                    # Start with Java 21
COPY myapp.jar /app/            # Copy your app
CMD ["java", "-jar", "/app/myapp.jar"]  # Run your app
```

#### 4. **Docker Compose** 🎼
- **Tool for running multi-container applications**
- Define multiple services (database + backend + frontend) in one file
- Like a **conductor** orchestrating multiple musicians (containers)

## 🎯 Our DevBoard Container Strategy

### Current Architecture
```
┌─────────────────┐
│   Your Computer │
├─────────────────┤
│ Java 21         │
│ Node.js 18      │  
│ MySQL 8.0       │
│ DevBoard App    │
└─────────────────┘
```

### Target Container Architecture
```
┌──────────────────────────────────────────┐
│              Docker Host                 │
├──────────────┬──────────────┬────────────┤
│   Frontend   │   Backend    │  Database  │
│  Container   │  Container   │ Container  │
├──────────────┼──────────────┼────────────┤
│ Nginx        │ Java 21      │ MySQL 8.0  │
│ Vue.js build │ Spring Boot  │ Data files │
│ Port 3000    │ Port 8080    │ Port 3306  │
└──────────────┴──────────────┴────────────┘
         ↕              ↕             ↕
      HTTP           REST API     Database
    requests        requests     connections
```

### Benefits for DevBoard

1. **Consistent Development**: Everyone on the team gets identical environment
2. **Easy Setup**: New developers run one command: `docker-compose up`
3. **Production Ready**: Same containers work in development and production
4. **Isolation**: Database changes don't affect your host machine
5. **Version Control**: Docker configs are versioned with your code

## 📋 Week 5 Modified Plan

### Day 1: Docker Basics + Backend Containerization
- Learn Docker fundamentals
- Create Dockerfile for Spring Boot application
- Build and run backend container
- Connect to external MySQL (not containerized yet)

### Day 2: Unified API Response + Global Exception Handling
- Standardize all API responses
- Add comprehensive error handling
- Test everything works in containers

### Day 3: Database Containerization + Docker Compose
- Create MySQL container
- Learn docker-compose basics
- Connect backend container to database container
- Understand container networking

### Day 4: Frontend Containerization
- Create Vue.js production build
- Containerize with Nginx
- Add frontend to docker-compose
- Full container orchestration

### Day 5: Environment Configuration + Optimization
- Development vs Production configurations
- Environment variables and secrets
- Image size optimization
- Build performance improvements

### Day 6-7: Production Readiness + Documentation
- Health checks and monitoring
- Backup and data persistence
- Deployment scripts
- Complete documentation

## 🛠️ Prerequisites Check

Before we start, let's verify you have Docker installed:

### Installing Docker
1. **Download Docker Desktop** from https://www.docker.com/products/docker-desktop
2. **Install and start** Docker Desktop
3. **Verify installation**:
```bash
docker --version
docker-compose --version
```

Expected output:
```
Docker version 24.x.x
Docker Compose version v2.x.x
```

### Basic Docker Commands You'll Learn

```bash
# Image Management
docker build -t myapp .              # Build image from Dockerfile
docker images                        # List all images
docker rmi myapp                     # Remove image

# Container Management  
docker run -p 8080:8080 myapp       # Run container with port mapping
docker ps                           # List running containers
docker ps -a                        # List all containers
docker stop container_name          # Stop container
docker rm container_name            # Remove container

# Docker Compose (Multi-container)
docker-compose up                   # Start all services
docker-compose up --build          # Rebuild and start
docker-compose down                 # Stop and remove all containers
docker-compose logs backend        # View logs for specific service
```

## 🚀 Ready to Start?

Once Docker is installed and verified, we'll begin with Day 1: Creating your first Spring Boot container!

### What We'll Build Today (Day 1)
1. **Dockerfile** for Spring Boot application
2. **Build process** to create backend image
3. **Run backend container** connected to your existing MySQL
4. **Test** that containerized backend works with frontend

Are you ready to start? Let me know when Docker is installed and we'll create your first container! 🐳

---

## 🎉 Week 5 Day 1 - COMPLETED!

### What We Accomplished Today

✅ **Docker Basics Learned**
- Understanding containers vs traditional deployment
- Key concepts: Images, Containers, Dockerfile, Docker Compose
- Basic Docker commands for image and container management

✅ **Backend Containerization**
- Created `Dockerfile` for Spring Boot application
- Built JAR file: `./mvnw clean package -DskipTests`
- Built Docker image: `docker build -t devboard-backend:latest .`
- Successfully ran backend container: `docker run -d -p 8080:8080 --name devboard-backend-container devboard-backend:latest`

✅ **Container Testing**
- Verified container is running: `docker ps`
- Checked application logs: `docker logs devboard-backend-container`
- Tested API endpoints:
  - `/api/hello` ✅ Working
  - `/api/auth/login` ✅ Working (using H2 in-memory DB)
- Frontend can still connect to containerized backend

### Key Insights Gained

1. **Container Isolation**: Our Spring Boot app runs in complete isolation with its own Java 21 environment
2. **Port Mapping**: `-p 8080:8080` maps container port to host port
3. **Development Profile**: Container uses H2 in-memory database (dev profile) instead of external MySQL
4. **Log Monitoring**: `docker logs` command is essential for debugging containerized applications
5. **CORS Configuration**: Our existing CORS setup automatically works with the containerized backend

### Current Architecture

```
┌─────────────────────────────────────────┐
│            Development Setup            │
├──────────────┬──────────────────────────┤
│   Frontend   │      Backend Container   │
│  (Node.js)   │     (devboard-backend)   │
├──────────────┼──────────────────────────┤
│ Vue.js       │ Java 21 + Spring Boot   │
│ Port 5176    │ Port 8080                │
│ Host Machine │ Docker Container         │
└──────────────┴──────────────────────────┘
       ↕                    ↕
    Browser           HTTP Requests
    Access            (localhost:8080)
```

### Commands We Used Today

```bash
# 1. Build the JAR file
./mvnw clean package -DskipTests

# 2. Build Docker image
docker build -t devboard-backend:latest .

# 3. Run container with port mapping
docker run -d -p 8080:8080 --name devboard-backend-container devboard-backend:latest

# 4. Monitor and manage containers
docker ps                                    # List running containers
docker logs devboard-backend-container       # View application logs
docker stop devboard-backend-container       # Stop container
docker rm devboard-backend-container         # Remove container
```

### 🔄 What's Next: Day 2

Tomorrow we'll focus on:
- Unified API response structure
- Global exception handling
- Making sure everything works seamlessly in our containerized environment

---

## 🔧 Advanced Topic: Connecting to External MySQL

### The Network Isolation Challenge

When we first tried to run the container with MySQL profile:
```bash
docker run -d -p 8080:8080 --name devboard-backend-container \
  -e SPRING_PROFILES_ACTIVE=mysql \
  devboard-backend:latest
```

**It failed!** 🚫 Error: `Communications link failure`

**Why?** Container tried to connect to `localhost:3307`, but inside a container, `localhost` refers to the container itself, NOT your host machine!

### Understanding Docker Networking

```
┌─────────────────────────────────────────┐
│            HOST MACHINE                 │
├─────────────────┬───────────────────────┤
│   MySQL Server  │   Docker Container    │
│   Port 3307     │   (Backend App)       │
├─────────────────┼───────────────────────┤
│ localhost:3307  │ localhost = container │
│ ✅ Accessible   │ ❌ Can't reach host   │
└─────────────────┴───────────────────────┘
```

### Solution: Docker Host Networking

**host.docker.internal** - Special DNS name that resolves to the host machine (Mac/Windows)

```bash
# ✅ This works!
docker run -d -p 8080:8080 --name devboard-backend-container \
  -e SPRING_PROFILES_ACTIVE=mysql \
  -e SPRING_DATASOURCE_URL="jdbc:mysql://host.docker.internal:3307/devboard?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC" \
  devboard-backend:latest
```

### Container + MySQL Connection Methods

#### Method 1: Environment Variables (Simple)
```bash
docker run -d -p 8080:8080 \
  --name devboard-backend-container \
  -e SPRING_PROFILES_ACTIVE=mysql \
  -e SPRING_DATASOURCE_URL="jdbc:mysql://host.docker.internal:3307/devboard?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC" \
  devboard-backend:latest
```

**Pros:**
- Quick and easy
- No config file changes needed
- Good for development

**Cons:**
- Long command
- host.docker.internal doesn't work on Linux

#### Method 2: Custom Docker Network
```bash
# Create network
docker network create devboard-network

# Run MySQL container
docker run -d --name mysql-container \
  --network devboard-network \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=devboard \
  mysql:8.0

# Run backend container
docker run -d --name backend-container \
  --network devboard-network \
  -e SPRING_PROFILES_ACTIVE=mysql \
  -e SPRING_DATASOURCE_URL="jdbc:mysql://mysql-container:3306/devboard" \
  devboard-backend:latest
```

**Pros:**
- Containers communicate by name
- More secure (isolated network)
- Works on all platforms

**Cons:**
- More complex setup
- Need to manage multiple containers

#### Method 3: Docker Compose (Production Ready)
```yaml
# docker-compose.yml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: devboard
      MYSQL_USER: devboard_user
      MYSQL_PASSWORD: devboard_pass
    ports:
      - "3307:3306"
    
  backend:
    image: devboard-backend:latest
    ports:
      - "8080:8080"
    environment:
      SPRING_PROFILES_ACTIVE: mysql
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/devboard
    depends_on:
      - mysql
```

**Pros:**
- One command starts everything: `docker-compose up`
- Declarative configuration
- Handles dependencies
- Easy to share

**Cons:**
- Need to learn docker-compose syntax
- Another tool to manage

### Key Docker Networking Concepts

1. **Container Isolation**: Containers have their own network namespace
2. **Port Mapping**: `-p 8080:8080` maps host port → container port
3. **DNS Resolution**:
   - `localhost` inside container = the container itself
   - `host.docker.internal` = host machine (Mac/Windows)
   - Container names = other containers on same network
4. **Environment Variables**: Override Spring config without rebuilding image

### Debugging Connection Issues

```bash
# Check if container is running
docker ps

# View container logs
docker logs devboard-backend-container

# Inspect container details
docker inspect devboard-backend-container

# Test connectivity from inside container
docker exec devboard-backend-container ping host.docker.internal
```

### 🎓 Lessons Learned

1. **Always consider networking** when containerizing applications
2. **Environment variables** are powerful for configuration
3. **host.docker.internal** is your friend on Mac/Windows
4. **Docker Compose** will make multi-container apps much easier (Day 3!)
5. **Logs are essential** - always check them when debugging

---

## 🚀 Week 5 Day 3 - Docker Compose Multi-Container Setup

### What We Accomplished Today

✅ **Complete docker-compose.yml Configuration**
- MySQL 8.0 database container with health checks
- Spring Boot backend container with automatic build
- Custom Docker network for container communication
- Environment-based configuration
- Container dependencies (backend waits for MySQL)

✅ **Docker Networking Setup**
```yaml
networks:
  devboard-network:
    driver: bridge
```
- Containers communicate by service name (mysql, backend)
- Isolated network for security
- No need for host.docker.internal

✅ **Container Configuration**
```yaml
backend:
  environment:
    SPRING_PROFILES_ACTIVE: mysql
    SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/devboard?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC
```
- Backend connects to MySQL using service name
- MySQL profile activated automatically
- Database credentials passed via environment

✅ **.dockerignore for Optimized Builds**
- Excludes unnecessary files from Docker context
- Faster builds and smaller images
- Only includes essential runtime files

### How to Run Everything

```bash
# Start all services
docker compose up --build

# Start in background
docker compose up -d --build

# View logs
docker compose logs -f backend
docker compose logs -f mysql

# Stop everything
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

### Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              Docker Host                        │
├─────────────────────┬───────────────────────────┤
│   MySQL Container   │    Backend Container      │
│   (devboard-mysql)  │    (devboard-backend)     │
├─────────────────────┼───────────────────────────┤
│ Port: 3307→3306     │ Port: 8080→8080          │
│ User: devboard_user │ Profile: mysql           │
│ Pass: devboard_pass │ Connects to: mysql:3306  │
│ DB: devboard        │ Built from: Dockerfile   │
└─────────────────────┴───────────────────────────┘
         ↑                        ↓
         └────── Network: devboard-network ──────┘
```

### Testing the Setup

```bash
# 1. Start containers
docker compose up --build

# 2. Test backend health
curl http://localhost:8080/api/hello | python3 -m json.tool

# 3. Test database connection
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | python3 -m json.tool

# 4. Check MySQL directly
docker exec -it devboard-mysql mysql -u devboard_user -pdevboard_pass -e "USE devboard; SHOW TABLES;"
```

### Key Learnings

1. **Service Names as Hostnames**: In Docker networks, service names (like `mysql`) automatically resolve to container IPs
2. **Health Checks Matter**: Using `depends_on` with `condition: service_healthy` ensures MySQL is ready before backend starts
3. **Environment Over Hardcoding**: All configuration via environment variables for flexibility
4. **Single Command Deployment**: `docker compose up` brings up entire stack

---

## 🎉 Week 5 Day 4 - Frontend Dockerization COMPLETED!

### What We Accomplished Today

✅ **Vue3 Frontend Containerization**
- Created multi-stage `Dockerfile` for Vue3 application
- **Build Stage**: Node.js 18 Alpine for building Vue3 app
- **Runtime Stage**: Nginx Alpine for serving static files
- Optimized build process with proper dependency management

✅ **Nginx Configuration for Single Page Apps**
- Custom `nginx.conf` for Vue Router support
- Proper fallback to `index.html` for all routes
- Static asset caching and security headers
- GZIP compression for better performance

✅ **Docker Build Optimization**
- Created comprehensive `.dockerignore` file
- Used Docker layer caching for faster builds
- Separated build and runtime environments
- Reduced final image size (only Nginx + static files)

✅ **Complete Multi-Container Orchestration**
- Added frontend service to `docker-compose.yml`
- Frontend, Backend, and Database all containerized
- Container dependency management (frontend → backend → mysql)
- Custom Docker network for secure communication

### Current Full-Stack Container Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Docker Host                           │
├───────────────┬─────────────────┬─────────────────────┤
│   Frontend    │     Backend     │      Database       │
│  Container    │   Container     │     Container       │
├───────────────┼─────────────────┼─────────────────────┤
│ Nginx Alpine  │ OpenJDK 21 Slim│ MySQL 8.0           │
│ Vue3 Build    │ Spring Boot     │ Persistent Data     │
│ Port 3000→80  │ Port 8080→8080  │ Port 3307→3306      │
│ Static Files  │ REST API        │ devboard Database   │
└───────────────┴─────────────────┴─────────────────────┘
        ↕               ↕                 ↕
    Web Browser    HTTP Requests    Database Queries
   (localhost:3000) (localhost:8080)  (mysql:3306)
        ↑               ↑                 ↑
        └─── devboard-network (isolated) ───┘
```

### How to Run the Complete Stack

```bash
# Start all services (builds images if needed)
docker compose up --build

# Start in background
docker compose up -d

# View status
docker compose ps

# View logs
docker compose logs frontend
docker compose logs backend
docker compose logs mysql

# Stop everything
docker compose down

# Complete cleanup (removes volumes)
docker compose down -v
```

### Testing the Full Stack

**Frontend Testing:**
```bash
# Test frontend is serving Vue app
curl http://localhost:3000

# Should return HTML with Vue.js application
```

**Backend Testing:**
```bash
# Test backend API
curl http://localhost:8080/api/hello | python3 -m json.tool

# Should return JSON response from Spring Boot
```

**Database Testing:**
```bash
# Test database connectivity
docker exec devboard-mysql mysql -u devboard_user -pdevboard_pass -e "SHOW TABLES;"

# Should show users, tasks, comments tables
```

### Key Docker Concepts Learned

1. **Multi-Stage Builds**: Separate build environment from runtime
   - Build stage: Install dependencies, compile code
   - Runtime stage: Only production files needed

2. **Container Dependencies**: Use `depends_on` for startup order
   - Frontend waits for backend
   - Backend waits for database health check

3. **Port Mapping**: Different ports for each service
   - Frontend: `3000:80` (host:container)
   - Backend: `8080:8080`
   - MySQL: `3307:3306`

4. **Container Networking**: Services communicate by name
   - Frontend talks to backend via container network
   - Backend talks to MySQL via `mysql:3306`

5. **Build Context Optimization**: `.dockerignore` excludes unnecessary files
   - Faster builds
   - Smaller images
   - Better security

### Frontend-Specific Docker Insights

#### Why Two-Stage Build?

**Without Multi-Stage:**
```dockerfile
FROM node:18
WORKDIR /app
COPY . .
RUN npm install && npm run build
CMD ["npm", "start"]
```
**Problems:**
- Final image includes Node.js, npm, source code
- Large image size (~1GB+)
- More security vulnerabilities
- Slower deployment

**With Multi-Stage:**
```dockerfile
FROM node:18 AS build
# ... build the app

FROM nginx:alpine AS runtime  
# ... copy only built files
```
**Benefits:**
- Final image only has Nginx + static files (~50MB)
- No Node.js in production
- Faster deployment
- More secure

#### Nginx Configuration Essentials

For Vue Router (Single Page Apps), you need:
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```
**Why?** When user visits `/tasks/123`:
1. Nginx looks for `/tasks/123` file (doesn't exist)
2. Nginx looks for `/tasks/123/` directory (doesn't exist)
3. Nginx serves `/index.html` (Vue Router handles the route)

Without this, direct URL access to Vue routes would show 404 errors.

### Development vs Production Considerations

**Development (what we've built):**
- All containers on same machine
- Direct port mapping to localhost
- No HTTPS/SSL
- Development database credentials

**Production (future improvements):**
- Load balancers for scaling
- HTTPS/SSL certificates
- Environment-specific configurations
- Secure credential management
- Health checks and monitoring
- Persistent volume management

### Common Issues and Solutions

#### Issue: Frontend can't reach backend
**Symptoms:** API calls from frontend fail
**Cause:** CORS or network configuration
**Solution:** Ensure both services on same Docker network

#### Issue: "vite: not found" during build
**Symptoms:** Build stage fails
**Cause:** Only production dependencies installed
**Solution:** Use `npm ci` (not `npm ci --only=production`)

#### Issue: Vue Router routes return 404
**Symptoms:** Direct URL access fails
**Cause:** Missing Nginx fallback configuration
**Solution:** Add `try_files $uri $uri/ /index.html;` to nginx.conf

#### Issue: Build context too large
**Symptoms:** Slow Docker builds
**Cause:** Sending unnecessary files to Docker daemon
**Solution:** Add comprehensive `.dockerignore` file

### Performance Tips

1. **Layer Caching**: Copy `package.json` before source code
2. **Build Cache**: Use `--build-arg BUILDKIT_INLINE_CACHE=1`
3. **Image Size**: Use Alpine Linux variants
4. **Static Assets**: Enable GZIP compression in Nginx
5. **Development**: Use bind mounts for faster iteration

---

## 🐛 Container Debugging Solution

### The Problem
Once containerized, frontend debugging becomes difficult because:
- JavaScript is minified and bundled
- Source maps are missing
- Hot reload doesn't work
- Original source files aren't visible in DevTools

### The Solution: Development Mode Container

**Development Container Setup:**

1. **Development Dockerfile** (`Dockerfile.dev`):
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

2. **Development Override** (`docker-compose.dev.yml`):
```yaml
services:
  frontend:
    build:
      dockerfile: Dockerfile.dev
    volumes:
      - ./devboard-frontend/src:/app/src  # Hot reload
    ports:
      - "5173:5173"  # Vite dev server
    environment:
      - NODE_ENV=development
```

3. **Vite Configuration** (Source maps enabled):
```javascript
export default defineConfig({
  build: {
    sourcemap: true,  // Enable source maps
    minify: false,    // Disable minification for debugging
  }
})
```

### Usage

**For Development/Debugging:**
```bash
# Start development mode with hot reload
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Access debuggable frontend
open http://localhost:5173

# Features:
# ✅ Original source files visible in DevTools
# ✅ Hot reload - changes appear instantly  
# ✅ Breakpoints work in .vue files
# ✅ Unminified, readable code
```

**For Production Testing:**
```bash
# Start production mode with source maps
docker compose up --build

# Access production-like frontend
open http://localhost:3000

# Features:
# ✅ Source maps for debugging
# ✅ Production build optimization
# ❌ No hot reload
```

### Browser DevTools Experience

With development mode enabled:
1. **Sources Tab**: See original `.vue` files under `webpack://`
2. **Breakpoints**: Set breakpoints directly in source code
3. **Console**: Variables show real names (not minified)
4. **Network**: Monitor API calls to backend
5. **Vue DevTools**: Full component inspection

### Quick Debug Commands

```bash
# Check if source maps exist
docker exec devboard-frontend ls -la /app/dist/assets/*.map

# View container logs
docker compose logs -f frontend

# Get shell access to container  
docker exec -it devboard-frontend sh
```

### Result: Best of Both Worlds

- **Development**: Full debugging experience with hot reload (`localhost:5173`)
- **Production**: Production-like testing with source maps (`localhost:3000`)
- **Container Benefits**: Consistent environment across team
- **Debugging Power**: Original source files and breakpoints work

Now you can debug containerized applications as easily as local development! 🎉

---

*This guide will be updated as we progress through each day of Week 5.*