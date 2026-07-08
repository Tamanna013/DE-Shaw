# TestLens CLI (`testlens-cli`)

A powerful CLI for interacting with the TestLens platform directly from your terminal or CI environment.

## Installation

```bash
pip install testlens-cli
```

## Features

- **Blazing Fast**: Startup time is consistently under 200ms because heavy modules like `rich` are lazy-loaded only when terminal rendering is needed.
- **Machine Parseable**: Every read command supports the `--json` flag to emit raw JSON, making it trivial to pipe TestLens data into `jq` or CI bash scripts.
- **Secure by Default**: Auth tokens are stored securely in your OS keychain via the `keyring` library, never lying around in plaintext dotfiles (unless running headless without a keychain, in which case it gracefully falls back to a warning and uses `~/.testlens/config.json` or the `TESTLENS_API_TOKEN` env var).

## Exit Codes

- `0`: Success
- `1`: General Error (Network, Validation)
- `2`: Authentication Error (Token expired or missing - allows CI scripts to explicitly branch logic to re-auth)

## Example Usage

```bash
# Authenticate
testlens login

# View recent failures for a repo
testlens failures list --repo testlens/backend

# Get machine-readable flaky leaderboard for CI alerting
testlens flaky list --repo testlens/backend --json > flaky.json
```
