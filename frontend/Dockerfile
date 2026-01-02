# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configurations
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx-main.conf /etc/nginx/nginx.conf

# Disable the auto-tuning script by replacing it with a no-op
RUN mv /docker-entrypoint.d/30-tune-worker-processes.sh /docker-entrypoint.d/30-tune-worker-processes.sh.disabled 2>/dev/null || true

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]


