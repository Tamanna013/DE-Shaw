#!/usr/bin/env bash
set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: ./deploy.sh <version> <environment>"
    echo "Example: ./deploy.sh v1.2.0 prod"
    exit 1
fi

VERSION=$1
ENV=$2

ENV_FILE="environments/${ENV}.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file $ENV_FILE does not exist."
    exit 1
fi

echo "🚀 Starting deployment of ${VERSION} to ${ENV}..."

# Export current version to be picked up by docker-compose
export APP_VERSION=${VERSION}

# 1. Pull the new images
echo "📦 Pulling images for ${VERSION}..."
# In a real scenario, this would pull from ghcr.io
# docker-compose pull

# 2. Run Database Migrations (Pre-Deploy Gate)
echo "🗄️ Running database migrations..."
# Using a one-off container to run alembic upgrade head
# If this fails, the script exits immediately (set -e) and no live services are restarted
# docker-compose run --rm failure_analyzer alembic upgrade head || exit 1
echo "✅ Migrations successful (mocked)."

# 3. Rolling Restart Services
echo "🔄 Restarting services..."
# docker-compose up -d --no-deps
echo "✅ Services restarted (mocked)."

# 4. Verify Healthchecks
echo "🏥 Verifying service health..."
TIMEOUT=60
START_TIME=$(date +%s)
HEALTHY=false

# We'll poll the gateway, which checks downstream dependencies
# In reality we might poll each service individually
while [ $(( $(date +%s) - START_TIME )) -lt $TIMEOUT ]; do
    if curl -s -f http://localhost:8000/readyz > /dev/null; then
        HEALTHY=true
        break
    fi
    sleep 5
    echo "Waiting for services to become healthy..."
done

if [ "$HEALTHY" = false ]; then
    echo "❌ ERROR: Services failed to become healthy within ${TIMEOUT} seconds."
    echo "⚠️ Initiating automatic rollback..."
    
    # Attempt to find the previous tag. For the sake of this script, we'll invoke rollback.sh
    # with a dummy 'previous' tag if one isn't explicitly known.
    PREV_VERSION=$(git describe --abbrev=0 --tags HEAD^ 2>/dev/null || echo "previous-known-good")
    
    ./rollback.sh "$PREV_VERSION" "$ENV"
    
    echo "❌ Deployment failed and was rolled back."
    exit 1
fi

echo "🎉 Deployment of ${VERSION} to ${ENV} completed successfully!"
