# Multi-Stage Build React application
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json ./
# Run clean dependency install
RUN npm install

COPY . .

# Set env to load fallback Zod validations at build compile
ENV VITE_API_URL=http://localhost:8000/api/v1
ENV VITE_APP_ENV=production

RUN npm run build

# Server runner stage using lightweight nginx
FROM nginx:1.27-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
# Copy standard custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
