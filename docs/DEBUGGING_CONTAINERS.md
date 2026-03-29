# Container Debugging Guide

## 🐛 The Problem
When frontend apps are containerized, debugging becomes difficult because:
- JavaScript is minified and bundled
- Source maps are often missing
- Hot reload doesn't work
- Dev tools lose connection to original source files

## 🛠️ Debugging Solutions

### Option 1: Development Container Mode (Recommended)

**Use the development container for debugging:**

```bash
# Start in development mode with hot reload
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Frontend now runs on http://localhost:5173 (Vite dev server)
# - Source maps enabled
- Hot reload working
- Unminified code
- Direct source file debugging
```

**Benefits:**
- ✅ Original source files visible in browser DevTools
- ✅ Hot reload - changes appear instantly
- ✅ Breakpoints work in original Vue/JS files
- ✅ Full debugging experience like local development

### Option 2: Production Build with Source Maps

**Keep production container but enable debugging:**

```bash
# Rebuild frontend with source maps enabled
docker compose up --build frontend

# Frontend on http://localhost:3000 now has:
# - Source maps (.map files)
# - Unminified code (optional)
# - Original file names in DevTools
```

**Benefits:**
- ✅ Production-like environment
- ✅ Source maps show original code
- ✅ Breakpoints work (with source maps)
- ❌ No hot reload

### Option 3: Hybrid Development Setup

**Run frontend locally, backend in containers:**

```bash
# Start only backend services
docker compose up backend mysql

# Run frontend locally
cd devboard-frontend
npm run dev

# Frontend: http://localhost:5173 (local Vite)
# Backend: http://localhost:8080 (containerized)
```

**Benefits:**
- ✅ Full frontend debugging experience
- ✅ Hot reload and all dev tools
- ✅ Backend still containerized (consistent environment)
- ❌ Frontend not in container (environment differences)

## 🔍 Browser DevTools Techniques

### 1. Source Maps Navigation
When source maps are enabled:
```
DevTools → Sources → webpack:// → src/
- You'll see your original .vue files
- Set breakpoints directly in source code
- Variables show real names (not minified)
```

### 2. Network Tab Debugging
```
DevTools → Network → XHR/Fetch
- Monitor API calls to backend
- Check request/response formats
- Verify authentication headers
```

### 3. Console Debugging
```javascript
// Add debugging logs in your Vue components
console.log('API Response:', response.data)
console.log('User State:', user.value)

// Use debugger statements
debugger; // Pauses execution here
```

### 4. Vue DevTools Extension
Install Vue DevTools browser extension:
- Shows component tree
- Inspects reactive data
- Time-travel debugging
- Works even in containers with source maps

## 🚀 Quick Debug Commands

### Check if source maps are working:
```bash
# Look for .map files in built container
docker exec devboard-frontend ls -la /usr/share/nginx/html/assets/

# Should see files like:
# index-ABC123.js
# index-ABC123.js.map  ← Source map file
```

### View container logs:
```bash
# Frontend container logs
docker compose logs -f frontend

# Backend container logs  
docker compose logs -f backend

# All services
docker compose logs -f
```

### Inspect running container:
```bash
# Get shell access to frontend container
docker exec -it devboard-frontend sh

# Check nginx configuration
cat /etc/nginx/conf.d/default.conf

# Check served files
ls -la /usr/share/nginx/html/
```

## 📋 Debugging Workflow

### For Development (Daily Work):
1. Use development container mode: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up`
2. Access http://localhost:5173
3. Full debugging experience with hot reload

### For Production Testing:
1. Use production container with source maps: `docker compose up --build`
2. Access http://localhost:3000  
3. Use source maps for debugging
4. Test production-like environment

### For API Issues:
1. Check backend logs: `docker compose logs backend`
2. Use browser Network tab to inspect API calls
3. Test APIs directly: `curl http://localhost:8080/api/...`

## 🎯 Best Practices

### 1. Environment-Specific Builds
```javascript
// vite.config.js
export default defineConfig({
  build: {
    sourcemap: process.env.NODE_ENV !== 'production',
    minify: process.env.NODE_ENV === 'production'
  }
})
```

### 2. Debug-Friendly Docker Setup
```dockerfile
# Add labels for easier container management
LABEL debug.enabled="true"
LABEL debug.port="5173"

# Conditional source map copying
COPY --from=build-stage /app/dist /usr/share/nginx/html
# Copy source maps if they exist
COPY --from=build-stage /app/dist/*.map /usr/share/nginx/html/ || true
```

### 3. Logging Strategy
```javascript
// Use consistent logging
const logger = {
  debug: (msg, data) => console.log(`🐛 ${msg}`, data),
  error: (msg, error) => console.error(`❌ ${msg}`, error),
  api: (url, response) => console.log(`📡 API ${url}:`, response)
}

// Usage in components
logger.api('/tasks', response.data)
```

## 🔧 Quick Setup

To enable debugging right now:

```bash
# 1. Enable source maps (already done)
# Edit vite.config.js - sourcemap: true

# 2. Start development mode
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# 3. Access debuggable frontend
open http://localhost:5173

# 4. Open DevTools → Sources → webpack://
# You'll see your original Vue files!
```

## 🎉 Result
- Original source files visible in DevTools
- Breakpoints work in .vue files  
- Hot reload for instant updates
- Full debugging experience even in containers!