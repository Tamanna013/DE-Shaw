# Stage 1: Build
FROM node:20-alpine as builder
WORKDIR /app

# Install dependencies first for layer caching
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
# Copy custom nginx config if we had one for routing SPA
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static output from builder
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
