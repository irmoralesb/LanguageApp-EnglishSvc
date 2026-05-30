# English Service - production image for on-premises (Ubuntu + docker-compose) and Azure Web App for Containers.
#
# Build:  docker build -t <dockerhub-user>/languageapp-english:latest .
# Run:    provide ENGLISH_DATABASE_URL, ENGLISH_DATABASE_MIGRATION_URL, SECRET_TOKEN_KEY, AUTH_ALGORITHM,
#         TOKEN_TIME_DELTA_IN_MINUTES, TOKEN_URL, SERVICE_ID, SERVICE_NAME (and optional LLM_*) via env or compose/App Settings.
#
# Listens on port 80 by default (Azure App Service forwards to 80). Override with WEBSITES_PORT or PORT.
# On startup the container runs Alembic migrations, then launches Uvicorn.

FROM python:3.12-slim

WORKDIR /app

# Temporary workaround: allow SHA1 so Microsoft's apt repo signature is accepted (Debian policy as of 2026-02-01).
RUN mkdir -p /etc/crypto-policies/back-ends \
    && printf '%s\n' '[hash_algorithms]' 'sha1 = "always"' '[asymmetric_algorithms]' 'rsa1024 = "always"' \
       > /etc/crypto-policies/back-ends/sequoia.config

# Install system deps and Microsoft ODBC Driver 18 for SQL Server (required by pyodbc/aioodbc).
# python:3.12-slim is Debian Bookworm (12).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates gnupg \
    && curl -sSL -o /tmp/packages-microsoft-prod.deb \
        "https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb" \
    && dpkg -i /tmp/packages-microsoft-prod.deb \
    && rm /tmp/packages-microsoft-prod.deb \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 unixodbc-dev libgssapi-krb5-2 \
    && apt-get purge -y curl gnupg \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code.
COPY . .

EXPOSE 80

# Run DB migrations, then serve. Trust the reverse-proxy headers so /docs and redirects use the correct scheme/host.
CMD ["sh", "-c", "alembic upgrade head && port=${WEBSITES_PORT:-${PORT:-80}} && echo \"Listening on port $port\" && exec uvicorn main:app --host 0.0.0.0 --port $port --proxy-headers --forwarded-allow-ips='*'"]
