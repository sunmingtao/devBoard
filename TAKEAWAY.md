# Key Takeaways & Tips

## Development Tools & Tricks

### H2 Console for Database Debugging
**What**: H2 database comes with a built-in web console for database management.

**Why it's useful**:
- Browse database schema (tables, columns, indexes)
- Execute SQL queries directly in the browser
- Inspect data without writing code
- Debug data persistence issues
- Test SQL queries before implementing in code

**How to use**:
1. Add to `application.yml`:
   ```yaml
   spring:
     h2:
       console:
         enabled: true
         path: /h2-console
   ```
2. Start your Spring Boot application
3. Navigate to `http://localhost:8080/h2-console`
4. Connect using:
   - JDBC URL: `jdbc:h2:mem:devboard`
   - Username: `sa`
   - Password: (leave empty)

**Pro tip**: Perfect for development debugging - you can see exactly what JPA is creating and storing!

---

## Spring Boot Tips

### Spring Initializr via Command Line
Instead of using the web UI, you can create a Spring Boot project with a single curl command:
```bash
curl https://start.spring.io/starter.zip \
  -d dependencies=web,data-jpa,lombok,mysql \
  -d type=maven-project \
  -d language=java \
  -d bootVersion=3.3.0 \
  -d javaVersion=21 \
  -o project.zip && unzip project.zip
```

### DataSource Auto-Configuration
**Issue**: Spring Data JPA requires a datasource configuration, even if you're not ready to use a database yet.

**Solution**: Add H2 for development to avoid configuration errors:
```xml
<dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>runtime</scope>
</dependency>
```

### YAML vs Properties Configuration
**Trend**: Modern Spring Boot projects prefer YAML over properties files.

**Why YAML**:
- Less verbose (no repetitive prefixes)
- Better readability with hierarchical structure
- Cleaner syntax for lists and complex configurations
- Industry standard for newer projects

**Example comparison**:
```properties
# application.properties
spring.datasource.url=jdbc:h2:mem:devboard
spring.jpa.hibernate.ddl-auto=create-drop
```

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:h2:mem:devboard
  jpa:
    hibernate:
      ddl-auto: create-drop
```

---

## Vue 3 & Vite Tips

### Creating Vue 3 Project with Vite
**Best Practice**: Use a stable version of Vite instead of @latest to avoid compatibility issues.

```bash
# Recommended: Use Vite 5.x for stability
npm create vite@5 project-name -- --template vue

# Alternative templates:
# --template vue-ts       # Vue 3 + TypeScript
# --template react        # React
# --template vanilla      # Vanilla JS
```

**Common Issue**: Latest Vite versions may have esbuild installation errors with newer Node.js versions.

**Solution**: Specify a stable version:
```bash
npm create vite@5 devboard-frontend -- --template vue
cd devboard-frontend
npm install
npm run dev
```

### Vite Project Structure
```
devboard-frontend/
├── src/
│   ├── App.vue         # Root component
│   ├── main.js         # Entry point
│   ├── components/     # Vue components
│   └── assets/         # Static assets
├── public/             # Public static files
├── index.html          # HTML entry point
├── vite.config.js      # Vite configuration
└── package.json        # Dependencies
```

### Understanding Vite: No Bundling in Development
**Key Insight**: Vite doesn't bundle during development - this is its main innovation!

**Traditional Build Tools (Webpack)**:
```
Bundle everything → Serve bundle → Browser
(Slow startup, requires rebuilding on changes)
```

**Vite's Approach**:
```
Serve source files directly → Browser requests ES modules → Transform on-demand
(Instant startup, only process what's needed)
```

**How Vite Uses Tools**:
- **Development**: Native ES modules + esbuild (for deps pre-bundling & TS/JSX)
- **Production**: Rollup (for optimized bundling) + esbuild (for minification)

**Benefits**:
- Instant server start (no bundling wait)
- Lightning-fast HMR (only update changed modules)
- On-demand compilation (only process requested files)

---

## Docker & Database Tips

### Setting Up MySQL with Docker
**Why Docker**: No need to install MySQL locally, easy setup, reproducible environment.

```bash
# Create docker-compose.yml with MySQL 8.0 configuration
# Start MySQL container
docker-compose up -d

# Check if running
docker ps

# Stop container
docker-compose down
```

**Docker Compose Configuration**:
```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    container_name: devboard-mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: devboard
      MYSQL_USER: devboard_user
      MYSQL_PASSWORD: devboard_pass
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
```

### Spring Boot Database Profiles
**Best Practice**: Use Spring profiles to switch between databases easily.

```bash
# Run with H2 (default)
./mvnw spring-boot:run

# Run with MySQL
./mvnw spring-boot:run -Dspring.profiles.active=mysql
```

**Profile Structure**:
- `application.yml` - Default configuration (H2)
- `application-dev.yml` - Development with H2
- `application-mysql.yml` - MySQL configuration

### Useful Docker Commands
```bash
# View container logs
docker logs devboard-mysql

# Access MySQL inside container
docker exec -it devboard-mysql mysql -u root -prootpassword

# Stop all containers
docker stop $(docker ps -aq)

# Remove unused volumes
docker volume prune
```

---

## Git & GitHub Tips

### Creating Issues via GitHub CLI
```bash
gh issue create --title "Title" --body "Description"
gh issue comment 1 --body "Comment"
gh issue close 1
```

### Kill Process on Specific Port (macOS/Linux)
```bash
lsof -ti:8080 | xargs kill -9
```

---

*This file contains useful tips and learnings discovered during the DevBoard project development.*