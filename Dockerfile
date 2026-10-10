FROM node:22-slim AS node

FROM python:3.13-slim

# Reflex builds the frontend with a JavaScript toolchain; take Node.js and npm
# from the official image instead of downloading Bun at build time.
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx
ENV REFLEX_USE_NPM=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install the frontend packages now so startup is fast.
RUN reflex export --frontend-only --no-zip && rm -rf .web/build *.db

ENV PORT=8000
EXPOSE 8000

# Frontend and backend share one port. The frontend is built at startup so it
# picks up the public URL (RENDER_EXTERNAL_URL or API_URL).
CMD ["sh", "-c", "reflex run --env prod --single-port --backend-port ${PORT}"]
