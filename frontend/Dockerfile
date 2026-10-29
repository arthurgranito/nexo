FROM node:22-alpine AS deps
WORKDIR /src
COPY package*.json ./
RUN npm ci
FROM node:22-alpine AS builder
WORKDIR /src
ARG API_PROXY_TARGET=http://api:8000
ARG NEXT_PUBLIC_SUPABASE_URL=
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY=
ARG NEXT_PUBLIC_API_URL=
ARG NEXT_PUBLIC_DEV_AUTH=true
ENV API_PROXY_TARGET=$API_PROXY_TARGET
ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_DEV_AUTH=$NEXT_PUBLIC_DEV_AUTH
COPY --from=deps /src/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build
FROM node:22-alpine AS runner
WORKDIR /src
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0
RUN addgroup -S nexo && adduser -S nexo -G nexo
COPY --from=builder --chown=nexo:nexo /src/.next/standalone ./
COPY --from=builder --chown=nexo:nexo /src/.next/static ./.next/static
USER nexo
EXPOSE 3000
CMD ["node", "server.js"]
