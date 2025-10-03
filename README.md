# TurboAPI

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Check](https://img.shields.io/badge/type%20check-mypy-blue.svg)](https://mypy.readthedocs.io/)

> ⚠️ **WARNING: ALPHA STATUS** ⚠️
>
> **This framework is under active development and is NOT recommended for production use.**
>
> - API may change without notice
> - No stability guarantees
> - Missing critical production features
> - Use at your own risk

A modern web framework for Python inspired by FastAPI and Django, designed for high-performance enterprise applications with a focus on Developer Experience (DX).

## 🚀 Quick Start

### Installation

```bash
# Install TurboAPI
pip install turboapi

# Or with uv (recommended)
uv add turboapi
```

### Create Your First Project

```bash
# Create a new project
framework new my-project
cd my-project

# Create your first app
framework new-app users

# Run the development server
framework run
```

### Basic Example

```python
# apps/users/api.py
from turboapi.web import Controller, Get, Post
from turboapi.security import Authenticate, RequireRole

@Controller("/users")
class UserController:
    
    @Get("/")
    async def list_users(self) -> dict:
        return {"users": []}
    
    @Post("/")
    @Authenticate()
    @RequireRole("admin")
    async def create_user(self, user_data: dict) -> dict:
        return {"message": "User created", "user": user_data}
```

## 📚 Documentation

Our documentation is organized in modular sections for easy navigation:

### 📋 Project Documentation

- **[Product Requirements Document (PRD)](docs/01-prd.md)** - Product vision and requirements
- **[Technical Design Document (DDT)](docs/02-ddt.md)** - Technical architecture and decisions
- **[Development Roadmap](docs/03-roadmap.md)** - Development plan and progress

### 🚀 Getting Started

- **[Quick Start Guide](docs/04-getting-started.md)** - Installation and first project
- **[Examples](docs/14-examples.md)** - Practical usage examples
- **[API Reference](docs/15-api-reference.md)** - Complete API documentation

### 🔧 System Documentation

- **[Core System](docs/05-core-system.md)** - Dependency injection and configuration
- **[Web Layer](docs/06-web-layer.md)** - FastAPI integration and routing
- **[Data Layer](docs/07-data-layer.md)** - Database and repository pattern
- **[Security System](docs/08-security-system.md)** - Authentication and authorization
- **[Observability System](docs/09-observability-system.md)** - Logging, metrics, and tracing
- **[Cache System](docs/11-cache-system.md)** - Caching strategies and decorators
- **[Task System](docs/12-task-system.md)** - Background task processing
- **[Addons System](docs/13-addons-system.md)** - Extending the framework

### 🛠️ Development Tools

- **[CLI Tools](docs/10-cli-tools.md)** - Command-line interface
- **[Troubleshooting](docs/16-troubleshooting.md)** - Common issues and solutions

## ✨ Key Features

### 🏗️ Framework Core

- **🔧 Dependency Injection** - Robust and flexible DI container
- **⚙️ Centralized Configuration** - Based on `pyproject.toml`
- **🔍 Automatic Discovery** - Intelligent component scanning
- **🌐 Web Decorators** - Controllers and endpoints with FastAPI
- **💾 Data Layer** - SQLAlchemy with Alembic migrations
- **⚡ Task System** - Background task queue
- **🗄️ Cache System** - Synchronous, asynchronous and hybrid caching
- **🖥️ CLI Tools** - Project and application generation

### 🔐 Security System

- **🔑 JWT Authentication** - Access and refresh tokens
- **🛡️ Security Middleware** - CORS, rate limiting, security headers
- **🎭 RBAC Authorization** - Role-based access control
- **🔒 Session Management** - Granular session control
- **🔌 OAuth2 Addons** - Google, GitHub, Microsoft integration

### 📊 Observability System

- **📝 Structured Logging** - With `structlog` and advanced configuration
- **📈 Unified Metrics** - OpenTelemetry with Prometheus export
- **🔍 Distributed Tracing** - Complete OpenTelemetry integration
- **❤️ Health Checks** - Diagnostic endpoints with Pydantic models
- **🔌 APM Addons** - New Relic, DataDog, Elastic APM as separate addons

### 🔌 Extensibility

- **📦 Addon System** - Modular extensions for APM and OAuth2
- **🎯 Plugin Architecture** - Easy integration of third-party services
- **⚙️ Configuration Driven** - Enable features through configuration

## 🏗️ Architecture

TurboAPI follows a modular architecture with clear separation of concerns:

```
src/turboapi/
├── core/           # DI, configuration, discovery
├── web/            # FastAPI integration, routing
├── data/           # Database, migrations, repositories
├── security/       # Authentication, authorization, middleware
├── observability/  # Logging, metrics, tracing, health checks
├── cache/          # Caching system and decorators
├── tasks/          # Background task processing
└── cli/            # Command-line tools
```

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/turboapi

# Run specific test categories
uv run pytest tests/test_security/
uv run pytest tests/test_observability/
```

## 🚀 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/alexmarco/turboapi.git
cd turboapi

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff format .
uv run ruff check . --fix
uv run mypy .
```

### Quality Gates

Before committing, ensure all quality gates pass:

```bash
# 1. Format code
uv run ruff format .

# 2. Fix linting issues
uv run ruff check . --fix

# 3. Type checking
uv run mypy .

# 4. Run tests
uv run pytest
```

## 📊 Project Status

### ✅ Completed Systems (9/11)

- Core Framework (DI, Configuration, Discovery)
- Web Layer (FastAPI Integration, Routing)
- Data Layer (SQLAlchemy, Migrations, Repositories)
- CLI Tools (Project Generation, Commands)
- Task System (Background Processing)
- Cache System (Synchronous, Asynchronous, Hybrid)
- Security System (JWT, RBAC, Middleware, OAuth2)
- Observability System (Logging, Metrics, Tracing, Health Checks)
- Documentation System (Modular Documentation)

### 🚧 In Progress

- Performance Optimizations
- Advanced Development Tools

### 📋 Planned

- Cloud Integrations (AWS, GCP, Azure)
- Deployment Tools (Docker, Kubernetes)
- Plugin Ecosystem

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run quality gates
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - For the excellent web framework foundation
- [Django](https://www.djangoproject.com/) - For architectural inspiration
- [Spring Boot](https://spring.io/projects/spring-boot) - For the developer experience philosophy
- [OpenTelemetry](https://opentelemetry.io/) - For the observability standards

## 📞 Support

- 📖 [Documentation](docs/) - Comprehensive guides and references
- 🐛 [Issues](https://github.com/alexmarco/turboapi/issues) - Report bugs and request features
- 💬 [Discussions](https://github.com/alexmarco/turboapi/discussions) - Community discussions
- 📧 [Contact](mailto:alexmarco@example.com) - Direct contact for questions

---

<<<<<<< HEAD
<div align="center">

**⚠️ RECUERDA: Este framework está en estado ALPHA y NO es recomendado para producción ⚠️**

[![GitHub](https://img.shields.io/badge/GitHub-alexmarco-181717?style=flat&logo=github)](https://github.com/alexmarco)
[![Email](https://img.shields.io/badge/Email-alejandro.marco.ramos@gmail.com-D14836?style=flat&logo=gmail)](mailto:alejandro.marco.ramos@gmail.com)

</div>
=======
**Made with ❤️ for the Python community**
>>>>>>> master
