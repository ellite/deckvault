FROM node:22-slim AS builder
WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

# Generate PNG icons from SVG
RUN node generate-icons.mjs

RUN npm run build

FROM node:22-slim AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
ENV HOST=0.0.0.0
ENV PORT=4367
EXPOSE 4367
CMD ["node", "dist/server/entry.mjs"]
