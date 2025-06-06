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

### ESLint & Prettier Setup for Vue 3
**Purpose**: Ensure consistent code style and catch potential errors across the team.

**Installation**:
```bash
npm install --save-dev eslint prettier @eslint/js eslint-plugin-vue eslint-config-prettier eslint-plugin-prettier
```

**Key Configuration Files**:
- `eslint.config.js` - ESLint v9 flat config format
- `.prettierrc` - Prettier formatting rules
- `.prettierignore` - Files to ignore during formatting

**Package.json Scripts**:
```json
{
  "scripts": {
    "lint": "eslint . --ext .vue,.js,.jsx,.ts,.tsx",
    "lint:fix": "eslint . --ext .vue,.js,.jsx,.ts,.tsx --fix", 
    "format": "prettier --write src/",
    "format:check": "prettier --check src/"
  }
}
```

**Usage**:
```bash
npm run lint        # Check for linting errors
npm run lint:fix    # Auto-fix linting errors
npm run format      # Format all files in src/
npm run format:check # Check if files are formatted
```

**ESLint v9 Note**: Uses new flat config format (`eslint.config.js`) instead of legacy `.eslintrc.js`.

### Vue Router 4 Setup
**Purpose**: Enable client-side routing for Single Page Application (SPA) navigation.

**Installation**:
```bash
npm install vue-router@4
```

**Basic Router Configuration** (`src/router/index.js`):
```javascript
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'DevBoard - Home' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Update page title based on route
router.beforeEach((to) => {
  document.title = to.meta.title || 'DevBoard'
})

export default router
```

**Integration in main.js**:
```javascript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router)
app.mount('#app')
```

**Key Features Implemented**:
- **Navigation Component**: Responsive navbar with active link highlighting
- **Route-based Page Titles**: Automatic title updates via router guards
- **Nested Layouts**: Navigation + router-view structure
- **Mobile-friendly**: Responsive navigation with hamburger menu

**Project Structure**:
```
src/
├── router/
│   └── index.js          # Router configuration
├── views/                # Page components
│   ├── Home.vue         # Homepage with hero section
│   ├── About.vue        # About page with tech stack
│   └── TaskBoard.vue    # Kanban board view
└── components/
    ├── Navigation.vue   # Responsive navigation bar
    ├── ApiTest.vue      # API connection testing
    └── Counter.vue      # Composition API demo
```

### Vue 3 Composition API Examples
**Purpose**: Demonstrate modern Vue 3 reactive programming patterns.

**Key Concepts Demonstrated**:

**1. `ref` vs `reactive`**:
```javascript
import { ref, reactive, computed, watch } from 'vue'

// ref for primitive values
const count = ref(0)
console.log(count.value) // Access with .value

// reactive for objects
const state = reactive({
  count: 0,
  history: []
})
console.log(state.count) // Direct access, no .value
```

**2. Computed Properties**:
```javascript
const doubleCount = computed(() => state.count * 2)
const total = computed(() => ref1.value + state.count)
```

**3. Watchers**:
```javascript
watch(count, (newValue, oldValue) => {
  console.log(`Changed from ${oldValue} to ${newValue}`)
})
```

**4. Lifecycle Hooks**:
```javascript
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  console.log('Component mounted')
})
```

**When to Use What**:
- **`ref`**: Primitive values (strings, numbers, booleans)
- **`reactive`**: Objects and arrays
- **`computed`**: Derived values that update automatically
- **`watch`**: Side effects when data changes

### Axios HTTP Client Setup
**Purpose**: Make HTTP requests from Vue frontend to Spring Boot backend.

**Installation**:
```bash
npm install axios
```

**API Service Structure** (`src/services/`):
```javascript
// api.js - Base axios configuration
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8080/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

// taskService.js - Specific API methods
export const taskService = {
  getAllTasks: () => api.get('/tasks'),
  createTask: (task) => api.post('/tasks', task),
  updateTask: (id, task) => api.put(`/tasks/${id}`, task),
  deleteTask: (id) => api.delete(`/tasks/${id}`)
}
```

**CORS Configuration** (Backend - Spring Boot 3.x Recommended):
```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
  @Override
  public void addCorsMappings(CorsRegistry registry) {
    registry.addMapping("/api/**")
            .allowedOrigins("http://localhost:5173", "http://localhost:5174")
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
            .allowCredentials(true);
  }
}
```

**Alternative (Filter-based - Less Reliable)**:
```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
  // May not work reliably in Spring Boot 3.x
}
```

**Sample Data Initialization** (Backend):
```java
@Component
public class DataInitializer implements CommandLineRunner {
  public void run(String... args) {
    // Create sample tasks on application startup
  }
}
```

**Error Handling Best Practices**:
- Request/response interceptors for logging
- Graceful fallback to sample data
- User-friendly error messages
- Loading states for better UX

### Common CORS Issues & Solutions

**Problem**: `Cross-Origin Request Blocked` error even though backend is running.

**Root Cause**: Vite auto-increments ports when default port (5173) is busy.
- Vite tries 5173 → 5174 → 5175 → etc.
- CORS config only allows specific ports
- Browser blocks requests from unallowed origins

**Solution 1: Add Port Range** (Recommended for development):
```java
configuration.setAllowedOrigins(Arrays.asList(
    "http://localhost:5173",  // Vite default
    "http://localhost:5174",  // Auto-increment 1  
    "http://localhost:5175"   // Auto-increment 2
));
```

**Solution 2: Force Specific Port**:
```json
// package.json
"scripts": {
  "dev": "vite --port 5173"
}
```

**Solution 3: Pattern Matching** (Development only):
```java
configuration.setAllowedOriginPatterns(Arrays.asList("http://localhost:*"));
```

**Debug Tips**:
- Check actual frontend port in browser address bar
- Look for CORS errors in browser console (F12)
- Verify backend CORS configuration matches frontend port
- **⚠️ ALWAYS RESTART BACKEND** after CORS configuration changes

**Common Issues & Solutions**:

1. **Forgetting to restart** Spring Boot server after configuration changes
   - Java configuration is loaded once at startup
   - CORS settings are not hot-reloadable
   - Changes require full application restart

2. **Wrong CORS configuration approach** for Spring Boot 3.x
   - **❌ Filter-based**: `CorsConfigurationSource` bean may not register properly
   - **✅ MVC-based**: `WebMvcConfigurer.addCorsMappings()` is more reliable
   - Filter-based works at servlet level, MVC-based works at Spring MVC level

3. **Spring Boot 3.x CORS Changes**
   - WebMvcConfigurer approach is recommended over filter-based
   - Better integration with Spring MVC request processing pipeline
   - More explicit and reliable configuration

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