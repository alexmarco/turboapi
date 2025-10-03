# TurboAPI Addons

Addons and extensions for the TurboAPI framework.

## Installation

Install the base addons package:

```bash
pip install turboapi-addons
```

Install specific addon groups:

```bash
# APM addons
pip install turboapi-addons[apm-all]

# OAuth2 addons
pip install turboapi-addons[oauth-all]

# All addons
pip install turboapi-addons[all]
```

## Available Addons

### APM (Application Performance Monitoring)

- **New Relic**: `turboapi-addons[apm-newrelic]`
- **DataDog**: `turboapi-addons[apm-datadog]`
- **Elastic APM**: `turboapi-addons[apm-elastic]`

### OAuth2 Providers

- **Google**: `turboapi-addons[oauth-google]`
- **GitHub**: `turboapi-addons[oauth-github]`
- **Microsoft**: `turboapi-addons[oauth-microsoft]`

## Usage

### APM Addons

```python
from turboapi import TurboApplication
from turboapi_addons.apm.newrelic import NewRelicAPMAddon
from turboapi_addons.apm.datadog import DataDogAPMAddon

app = TurboApplication()

# Configure New Relic
newrelic_addon = NewRelicAPMAddon(app, {
    "license_key": "your-license-key",
    "app_name": "my-app"
})
await newrelic_addon.configure()

# Configure DataDog
datadog_addon = DataDogAPMAddon(app, {
    "service": "my-app",
    "env": "production"
})
await datadog_addon.configure()
```

### OAuth2 Addons

```python
from turboapi import TurboApplication
from turboapi_addons.oauth.google import GoogleOAuthAddon
from turboapi_addons.oauth.github import GitHubOAuthAddon

app = TurboApplication()

# Configure Google OAuth2
google_addon = GoogleOAuthAddon(app, {
    "client_id": "your-google-client-id",
    "client_secret": "your-google-client-secret",
    "redirect_uri": "http://localhost:8000/auth/google/callback"
})
await google_addon.configure()

# Configure GitHub OAuth2
github_addon = GitHubOAuthAddon(app, {
    "client_id": "your-github-client-id",
    "client_secret": "your-github-client-secret",
    "redirect_uri": "http://localhost:8000/auth/github/callback"
})
await github_addon.configure()
```

## Development

### Setup

```bash
git clone https://github.com/turboapi/turboapi-addons
cd turboapi-addons
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
ruff format .
ruff check . --fix
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## License

MIT License - see LICENSE file for details.
