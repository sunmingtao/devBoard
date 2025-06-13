# Frontend Dockerfile for Vue3 Application
# Two-stage build: Build with Node.js, serve with Nginx

# =====================================
# Stage 1: BUILD STAGE
# =====================================
# Use Node.js 18 Alpine (lightweight Linux)
FROM node:18-alpine AS build-stage

# Set working directory inside container
WORKDIR /app

# Copy package files first (for better Docker layer caching)
# This way, dependencies are only reinstalled if package.json changes
COPY package*.json ./

# Install dependencies (including devDependencies for build tools like Vite)
# npm ci is faster and more reliable for production than npm install
RUN npm ci

# Copy all source code
COPY . .

# Build the application for production
# This creates the dist/ directory with optimized static files
RUN npm run build

# =====================================
# Stage 2: PRODUCTION STAGE  
# =====================================
# Use lightweight Nginx Alpine image for serving static files
FROM nginx:alpine AS production-stage

# Remove default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy built Vue application from build stage
# Copy from /app/dist (Vite output) to Nginx html directory
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Create custom Nginx configuration for Vue Router (SPA)
# This ensures that all routes are handled by index.html
COPY --from=build-stage /app/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (standard HTTP port)
EXPOSE 80

# Start Nginx server
# daemon off ensures Nginx runs in foreground (required for Docker)
CMD ["nginx", "-g", "daemon off;"]