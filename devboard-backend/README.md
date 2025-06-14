# DevBoard Backend

Spring Boot REST API for the DevBoard task management system.

## 🚀 Quick Start

### Prerequisites
- Java 21+
- Maven 3.9+
- MySQL 8+ (for production) or H2 (for development)

### Development Setup
```bash
# Clone and navigate to backend
cd devboard-backend

# Run with development profile (uses H2 database)
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# Or build and run JAR
mvn clean package
java -jar target/devboard-0.0.1-SNAPSHOT.jar --spring.profiles.active=dev
```

The API will be available at: `http://localhost:8080`

## 🧪 Testing & Coverage

### Run Unit Tests
```bash
# Run all tests
mvn test

# Run specific test class
mvn test -Dtest=TaskServiceTest
```

### Generate Coverage Report
```bash
# Generate JaCoCo coverage report
./generate-coverage.sh

# Or manually:
mvn clean test
open target/site/jacoco/index.html
```

**Current Test Coverage:**
- **Total Coverage**: 44% instruction coverage, 32% branch coverage
- **Service Layer**: High coverage on core business logic
  - AdminService: 100% line coverage
  - CommentService: 97% line coverage
  - UserService: 80% line coverage
- **41 Unit Tests** covering service layer functionality

## 📚 API Documentation

### Swagger UI
Access interactive API documentation at: `http://localhost:8080/swagger-ui.html`

### H2 Console (Development)
Access H2 database console at: `http://localhost:8080/h2-console`
- JDBC URL: `jdbc:h2:mem:devboard_dev`
- Username: `sa`
- Password: (empty)

## 🏗️ Architecture

### Technology Stack
- **Spring Boot 3.3** - Application framework
- **Spring Security** - Authentication & authorization
- **Spring Data JPA** - Data persistence
- **JWT** - Token-based authentication
- **H2/MySQL** - Database options
- **JaCoCo** - Code coverage reporting
- **Swagger/OpenAPI 3** - API documentation

### Project Structure
```
src/main/java/com/example/devboard/
├── controller/          # REST controllers
├── service/            # Business logic
├── entity/             # JPA entities
├── repository/         # Data access layer
├── dto/               # Data transfer objects
├── security/          # JWT & authentication
├── config/            # Spring configuration
├── exception/         # Global exception handling
└── common/            # Shared utilities
```

## 🔐 Security

### Authentication
- JWT-based authentication
- Token expiration: 24 hours
- Refresh token mechanism included

### Authorization Levels
- **USER**: Standard user permissions
- **ADMIN**: Full system access

### Default Credentials (Development)
- Admin: `admin` / `admin123`
- User: `user` / `user123`

## 🗄️ Database

### Development (H2)
- In-memory database
- Automatic schema creation
- Sample data initialization

### Production (MySQL)
```bash
# Set environment variables
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=devboard
export DB_USERNAME=devboard_user
export DB_PASSWORD=your_password

# Run with production profile
java -jar target/devboard-0.0.1-SNAPSHOT.jar --spring.profiles.active=prod
```

## 🔧 Configuration

### Application Profiles
- `dev` - Development (H2, debug logging)
- `test` - Testing (H2, minimal logging)
- `prod` - Production (MySQL, optimized)

### Environment Variables
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=devboard
DB_USERNAME=devboard_user
DB_PASSWORD=your_secure_password

# JWT Configuration
JWT_SECRET=your_256_bit_secret_key_here
JWT_EXPIRATION=86400000

# Server Configuration
SERVER_PORT=8080
```

## 🚀 Deployment

### Docker
```bash
# Build image
docker build -t devboard-backend .

# Run container
docker run -p 8080:8080 \
  -e SPRING_PROFILES_ACTIVE=prod \
  -e DB_HOST=your_db_host \
  devboard-backend
```

### Docker Compose
See `docker-compose.yml` in project root for full stack deployment.

## 📊 Monitoring & Logging

### Health Check
- Endpoint: `GET /actuator/health`
- Status: Application and database health

### Logging
- Development: Console output with debug level
- Production: File-based logging with info level
- Log location: `./backend.log`

## 🛠️ Development

### Code Quality
```bash
# Run tests with coverage
mvn clean test

# Build for production
mvn clean package -Pprod
```

### Adding New Features
1. Create entity classes in `entity/`
2. Add repository interfaces in `repository/`
3. Implement business logic in `service/`
4. Create REST endpoints in `controller/`
5. Add comprehensive unit tests
6. Update API documentation

### Testing Best Practices
- Unit tests for service layer business logic
- Integration tests for controller endpoints
- Mock external dependencies
- Maintain >80% coverage on service layer

## 📋 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Tasks
- `GET /api/tasks` - List tasks with filters
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Comments
- `GET /api/tasks/{taskId}/comments` - List task comments
- `POST /api/tasks/{taskId}/comments` - Add comment
- `DELETE /api/comments/{id}` - Delete comment

### Admin
- `GET /api/admin/users` - List all users
- `GET /api/admin/dashboard` - Dashboard statistics
- `PUT /api/admin/users/{id}/role` - Update user role

For complete API documentation, visit the Swagger UI when the application is running.