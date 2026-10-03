# My Own Bytes

A small Flask webhook server and Plaid data runner.

## License

This project is available under the [Revenue-Based Sponsorship License](LICENSE).
Use is free for individuals and organizations with less than USD 300,000 in
annual revenue. Above that threshold, the license requires a regressive
sponsorship payment based on the user's total annual revenue. This custom
license is source-available and is not an OSI-approved open-source license.

The license applies only to this project's code. Third-party packages retain
their own licenses; when redistributing them, retain the package license and
notice files included with those packages.

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```sh
uv sync
```

Create a `.env` file:

```dotenv
TEST_PLAID_CLIENT=your-client-id
TEST_PLAID_SECRET=your-sandbox-secret
TEST_PLAID_HOST=https://sandbox.plaid.com/
TEST_PLAID_ENV=sandbox
TEST_DB_URI=sqlite:///test.db

FLASK_PLAID_CLIENT=your-client-id
FLASK_PLAID_SECRET=your-production-secret
FLASK_PLAID_HOST=https://production.plaid.com/
FLASK_PLAID_ENV=production
FLASK_DB_URI=sqlite:///myownbytes.db
```

## Webhook server

```sh
# Production-style listener on 0.0.0.0:5000
uv run wh-run

# Flask development server with debug enabled
uv run wh-dev

# Flask server in testing mode
uv run wh-test
```

Plaid webhooks are received at `POST /webhooks`.

## Plaid runner

The runner uses the configured Plaid credentials and an existing access token:

```sh
# Run commands with test credentials
uv run plaid --app 'myownbytes.plaidrunner.py:make_app("test")' runner COMMAND [OPTIONS]

# Run commands with production credentials
uv run plaid runner COMMAND [OPTIONS]
```

Commands:

```sh
# Trigger a sandbox webhook
... fire-wh ACCESS_TOKEN WEBHOOK_TYPE WEBHOOK_CODE

# Add or update an item's webhook URL
... update-wh ACCESS_TOKEN https://example.com/webhooks

# Retrieve Plaid data
... get-item ACCESS_TOKEN
... get-accounts ACCESS_TOKEN
... get-liabilities ACCESS_TOKEN
... get-balances ACCESS_TOKEN
... sync-txns ACCESS_TOKEN
```

Add `-a` to `get-item`, `get-accounts`, `get-liabilities`, `get-balances`, or `sync-txns` to save the result to the database:

```sh
# Retrieve sandbox item data from plaid and store to test.db database
uv run plaid --app 'myownbytes.plaidrunner:make_app("test")' runner get-item -a ACCESS_TOKEN

# Retrieve production data
uv run plaid runner get-item -a ACCESS_TOKEN
uv run plaid runner sync-txns -a ACCESS_TOKEN
```

Run `--help` on any command for details:

```sh
uv run plaid runner --help

uv run plaid runner fire-wh --help
```
