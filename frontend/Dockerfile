FROM node:22-slim AS builder
WORKDIR /app

# Install rsvg-convert for SVG→PNG icon generation
RUN apt-get update && apt-get install -y librsvg2-bin && rm -rf /var/lib/apt/lists/*

COPY package.json ./
RUN npm install

COPY . .

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

# Generate PNG icons from SVG
RUN mkdir -p public/icons \
    && rsvg-convert -w 192 -h 192 public/logo.svg -o public/icons/icon-192.png \
    && rsvg-convert -w 512 -h 512 public/logo.svg -o public/icons/icon-512.png

RUN npm run build

FROM node:22-slim AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
ENV HOST=0.0.0.0
ENV PORT=4367
EXPOSE 4367
CMD ["node", "dist/server/entry.mjs"]
