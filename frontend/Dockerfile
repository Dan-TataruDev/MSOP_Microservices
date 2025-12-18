# Frontend Dockerfile
FROM node:18-alpine AS builder

# Install pnpm
RUN npm install -g pnpm@8.15.0

WORKDIR /app

# Copy package files for dependency resolution
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./

# Copy all package.json files
COPY apps/main/package.json ./apps/main/
COPY packages/api-client/package.json ./packages/api-client/
COPY packages/design-system/package.json ./packages/design-system/
COPY packages/types/package.json ./packages/types/
COPY packages/utils/package.json ./packages/utils/

# Install dependencies (this will install all workspace dependencies)
# Note: Using regular install instead of --frozen-lockfile for compatibility
# with shamefully-hoist setting. Lockfile will be updated if needed.
RUN pnpm install

# Copy source code
COPY apps/main ./apps/main
COPY packages ./packages

# Build workspace packages first (if they have build scripts)
RUN pnpm --filter "./packages/*" build --if-present || true

# Build the main app
# Using npx to find vite from hoisted node_modules
WORKDIR /app/apps/main
RUN npx vite build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/apps/main/dist /usr/share/nginx/html

# Create nginx configuration
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Gzip compression \
    gzip on; \
    gzip_vary on; \
    gzip_min_length 1024; \
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json; \
    \
    # Security headers \
    add_header X-Frame-Options "SAMEORIGIN" always; \
    add_header X-Content-Type-Options "nosniff" always; \
    add_header X-XSS-Protection "1; mode=block" always; \
    \
    # SPA routing \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # API proxy - Auth Service \
    location /api/auth { \
        proxy_pass http://auth-service:8001/api; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    \
    # API proxy - Guest Interaction Service \
    location /api/guest { \
        proxy_pass http://guest-interaction-service:8000/api; \
        proxy_http_version 1.1; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    \
    # API proxy - Booking Service \
    location /api/booking { \
        proxy_pass http://booking-reservation-service:8002/api; \
        proxy_http_version 1.1; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    \
    # API proxy - Other services (catch-all) \
    location /api { \
        proxy_pass http://auth-service:8001; \
        proxy_http_version 1.1; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    \
    # Static assets caching \
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
