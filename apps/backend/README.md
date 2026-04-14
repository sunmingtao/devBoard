# DevBoard Backend

Spring Boot REST API for the DevBoard task management system.

## 🚀 Quick Start

### Prerequisites
- Java 21+
- Maven 3.9+ (or use included Maven wrapper)
- MySQL 8+ (production) or H2 (development)

### Development Setup
```bash
cd apps/backend

# Run with development profile (H2)
./mvnw spring-boot:run -Dspring-boot.run.profiles=dev

# Or build and run JAR
./mvnw clean package
java -jar target/devboard-0.0.1-SNAPSHOT.jar --spring.profiles.active=dev
```

API base URL: `http://localhost:8080`

## 🧪 Testing & Coverage

```bash
cd apps/backend
./mvnw test
./generate-coverage.sh
```

Coverage report output:
- `target/site/jacoco/index.html`

## 📚 API Docs

- Swagger UI: `http://localhost:8080/swagger-ui.html`
- H2 Console (dev): `http://localhost:8080/h2-console`
  - JDBC URL: `jdbc:h2:mem:devboard_dev`
  - Username: `sa`
  - Password: *(empty)*

## 🏗️ Stack

- Spring Boot 3.3
- Spring Security
- Spring Data JPA
- JWT (jjwt)
- H2 / MySQL
- Redis (Spring Data Redis)
- JaCoCo
- SpringDoc OpenAPI

## 🔐 Auth & Roles

- JWT-based authentication
- Access roles:
  - `USER`
  - `ADMIN`

Development default credentials:
- `admin` / `admin123`
- `user` / `user123`

## 🔧 Configuration

### Profiles
- `dev`: H2 + local dev settings
- `test`: test-oriented settings
- `prod`: MySQL + production settings

### Environment Variables (common)

The backend now supports both `DATABASE_*` and legacy `DB_*` variable names.
`DATABASE_*` takes precedence when both are set.

```bash
# Preferred names
DATABASE_URL=jdbc:mysql://localhost:3306/devboard?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC
DATABASE_USERNAME=devboard_user
DATABASE_PASSWORD=your_secure_password

# Legacy names (still supported)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=devboard
DB_USERNAME=devboard_user
DB_PASSWORD=your_secure_password
JWT_SECRET=your_256_bit_secret_key_here
JWT_EXPIRATION=86400000
SERVER_PORT=8080
```

## 🐳 Docker

```bash
cd apps/backend
docker build -t devboard-backend .
docker run -p 8080:8080 \
  -e SPRING_PROFILES_ACTIVE=prod \
  -e DB_HOST=your_db_host \
  devboard-backend
```

### RDS connection troubleshooting (`Access denied for user ...`)

If startup fails with `java.sql.SQLException: Access denied for user ...`, this is usually a MySQL auth issue (credentials or grants), not a security-group reachability issue.

1. Confirm your task/service is using the expected DB variables (`DATABASE_USERNAME` / `DATABASE_PASSWORD` or `DB_USERNAME` / `DB_PASSWORD`).
2. Verify the user exists on RDS and can connect from `%` (or your app subnet CIDR host pattern):
   ```sql
   SELECT user, host FROM mysql.user WHERE user = 'devboard_user';
   SHOW GRANTS FOR 'devboard_user'@'%';
   ```
3. If needed, recreate grants:
   ```sql
   CREATE USER IF NOT EXISTS 'devboard_user'@'%' IDENTIFIED BY '***';
   GRANT ALL PRIVILEGES ON devboard.* TO 'devboard_user'@'%';
   FLUSH PRIVILEGES;
   ```
4. Security groups are likely fine if you see `Access denied`; SG/NACL issues typically surface as timeout/refused errors.

## 📋 Core API Endpoints

### Authentication
- `POST /api/auth/login`
- `POST /api/auth/register`

### Tasks
- `GET /api/tasks`
- `POST /api/tasks`
- `GET /api/tasks/{id}`
- `PUT /api/tasks/{id}`
- `DELETE /api/tasks/{id}`

### Comments
- `GET /api/tasks/{taskId}/comments`
- `POST /api/tasks/{taskId}/comments`
- `DELETE /api/comments/{id}`
