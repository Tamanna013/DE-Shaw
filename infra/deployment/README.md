# TestLens Deployment & Runbook

This directory contains the deployment automation and operational runbook for the TestLens v1 single-host (or managed container service) architecture. Kubernetes migration is officially slated for the v2 roadmap.

## Versioning & Promotion Flow

We rely on **Manual CHANGELOG-driven Semantic Versioning**.
*Justification*: While tools like `python-semantic-release` are excellent for libraries, SaaS application releases often require coordinated marketing announcements, DB migration audits, and manual QA sign-offs on staging before hitting production. A manual tag (e.g., `git tag v1.2.0`) signals explicit human intent to release.

**Promotion Flow**:
1. **Merge to Main**: Triggers automated integration tests and smoke tests.
2. **Auto-Deploy to Staging**: Main branch changes are auto-deployed to the Staging environment (`staging.env`) via webhook.
3. **Manual Approval Gate**: QA/SDET team performs manual verification on Staging.
4. **Tag Release**: A developer runs `git tag v1.2.0 && git push --tags`.
5. **CI Release Job**: The tag triggers `.github/workflows/release.yml`, building and pushing immutable images to `ghcr.io/testlens/*:v1.2.0`.
6. **Deploy to Prod**: An operator executes `./deploy.sh v1.2.0 prod` on the target environment.

## Disaster Recovery Targets

For the v1 architecture, we define the following explicit disaster recovery targets:
- **RTO (Recovery Time Objective): < 15 minutes**. If a bad release breaks production, executing `./rollback.sh v1.1.9 prod` will pull the previous known-good images and restart the Docker Compose stack. Image pulls and container restarts typically complete within 2-3 minutes.
- **RPO (Recovery Point Objective): 1 hour**. Automated PostgreSQL snapshots (via WAL archiving to S3, using a tool like pgBackRest) run hourly. In the event of catastrophic data corruption, at most 1 hour of failure-analysis data would be lost.

## Automated Safe Deployments

The `deploy.sh` script is idempotent and implements the following safety gates:
1. **Pre-Deploy Migrations**: It runs `alembic upgrade head` *before* restarting any services. If migrations fail, the deployment halts immediately, and no containers are restarted.
2. **Healthcheck Verification**: After restarting the compose stack with the new image tags, `deploy.sh` polls the `/healthz` endpoints of every service.
3. **Auto-Rollback**: If any service fails to return HTTP 200 within the 60-second timeout, `deploy.sh` automatically invokes `rollback.sh` to revert to the previous images, minimizing downtime.

## Rollback Policy (Important Data Note)

The `rollback.sh` script **DOES NOT automatically downgrade database migrations**.
*Justification*: Blindly downgrading a database schema (e.g., dropping columns) usually results in permanent data loss. If a deployment fails *after* a migration successfully applied, rolling back the application code is usually safe (assuming the migration was backward compatible). If the migration itself caused data corruption, the on-call engineer must manually assess the situation, formulate a data-recovery plan, and manually execute `alembic downgrade`. This is a deliberate, documented manual gate.
