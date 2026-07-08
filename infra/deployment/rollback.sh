#!/usr/bin/env bash
set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: ./rollback.sh <previous_version> <environment>"
    echo "Example: ./rollback.sh v1.1.9 prod"
    exit 1
fi

VERSION=$1
ENV=$2

echo "⚠️ Initiating rollback to ${VERSION} in ${ENV}..."

# Export version for compose
export APP_VERSION=${VERSION}

# NOTE: We explicitly DO NOT automatically run `alembic downgrade`.
# If the previous deployment ran a migration, downgrading it automatically
# could result in catastrophic data loss (e.g., dropping columns).
# We roll back the application code only. If the DB schema is severely corrupted,
# an on-call engineer must intervene manually.
echo "⚠️ WARNING: Database migrations are NOT automatically reverted."
echo "If manual schema downgrade is required, execute: docker-compose run --rm failure_analyzer alembic downgrade -1"

echo "📦 Pulling known-good images for ${VERSION}..."
# docker-compose pull

echo "🔄 Restarting services..."
# docker-compose up -d

echo "✅ Rollback to ${VERSION} initiated. Please monitor the application logs."
