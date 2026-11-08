# ---------- Build
FROM node:24-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .
RUN npx ng build --configuration production

# ---------- Runtime
FROM nginx:1.29-alpine

COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist/browser /usr/share/nginx/html

# Indirizzo dell'API dietro al proxy (nome del servizio in docker-compose)
ENV API_UPSTREAM=http://api:8000

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=5 \
    CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
