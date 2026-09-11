# Образ nginx: збірка React + сам nginx. Збирається з кореня репозиторію
# (context: . у docker-compose.yml), тому шляхи тут — від кореня.

# Етап 1: збираємо React у статичні файли (dist/)
FROM node:24-alpine AS build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

# Адреса API вшивається в бандл під час збірки.
# Відносний шлях — бо nginx проксить /api/ на Django з того самого домену.
ENV VITE_API_URL=/api/v1
RUN npm run build

# Етап 2: nginx віддає dist/ і проксить API на Django. Node у фінальному образі немає.
FROM nginx:1.28-alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
