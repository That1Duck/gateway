# --- Build stage ---
FROM node:20-alpine AS builder
WORKDIR /app

COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN npm ci

COPY . .

ENV NUXT_PUBLIC_API_BASE=/api/api/v1
ENV NUXT_API_ORIGIN=http://gateway:8000

# Сборка SSR (Nitro preset node)
RUN npm run build

# --- Runtime stage ---
FROM node:20-alpine AS runner
WORKDIR /app

COPY --from=builder /app/.output ./.output

# Те же ENV в рантайме (можно переопределить из compose)
ENV NUXT_PUBLIC_API_BASE=/api/api/v1
ENV NUXT_API_ORIGIN=http://gateway:8000
ENV PORT=3000
EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
