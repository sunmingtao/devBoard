# Frontend Dockerfile for Vue3 Application
# Optimized multi-stage build: Build with Node.js, serve with Nginx

# =====================================
# Stage 1: BUILD STAGE
# =====================================
# Use Node.js 18 Alpine (lightweight Linux) - ~170MB vs ~900MB for regular node
FROM node:18-alpine AS build-stage

# Set working directory inside container
WORKDIR /app

# Add build arguments for environment-specific optimization
ARG NODE_ENV=production
ARG VITE_APP_ENVIRONMENT=production

# Install only necessary build dependencies
RUN apk add --no-cache git

# Copy package files first (for better Docker layer caching)
# This way, dependencies are only reinstalled if package.json changes
COPY package*.json ./

# Install dependencies including devDependencies for build
# Use npm install to get all dependencies needed for build
RUN npm cache clean --force && \
    npm install --include=dev --no-audit --no-fund

# Copy source code (exclude unnecessary files via .dockerignore)
COPY . .

# Build the application for production with environment optimization
# Environment variables are available during build
ENV NODE_ENV=${NODE_ENV}
ENV VITE_APP_ENVIRONMENT=${VITE_APP_ENVIRONMENT}

# Production build with optimizations
RUN npm run build && \
    # Clean up source files and dependencies after build
    rm -rf src/ public/ node_modules/ && \
    # Verify build output exists
    ls -la dist/

# =====================================
# Stage 2: PRODUCTION STAGE  
# =====================================
# Use nginx:alpine - smallest Nginx image (~22MB)
FROM nginx:alpine AS production-stage

# Install dumb-init for proper signal handling (optional but recommended)
RUN apk add --no-cache dumb-init

# Remove default Nginx content and config
RUN rm -rf /usr/share/nginx/html/* /etc/nginx/conf.d/default.conf

# Copy built Vue application from build stage (only dist folder)
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy optimized Nginx configuration
COPY --from=build-stage /app/nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user for security (nginx user already exists, just modify permissions)
# The nginx:alpine image already has nginx user, so we just need to set permissions

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Switch to non-root user
USER nginx

# Expose port 80 (standard HTTP port)
EXPOSE 80

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Start Nginx with dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]
CMD ["nginx", "-g", "daemon off;"]