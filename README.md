# TurboAPI

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Check](https://img.shields.io/badge/type%20check-mypy-blue.svg)](https://mypy.readthedocs.io/)

> ⚠️ **ADVERTENCIA: ESTADO ALPHA** ⚠️
> 
> **Este framework está en desarrollo activo y NO es recomendado para uso en producción.**
> 
> - La API puede cambiar sin previo aviso
> - No hay garantías de estabilidad
> - Faltan características críticas para producción
> - Use bajo su propio riesgo

Un framework web moderno para Python inspirado en FastAPI y Django, diseñado para aplicaciones empresariales de alto rendimiento.

## 🚀 Características Principales

### ✅ Núcleo del Framework (Completado)

- **🔧 Inyección de dependencias** - Container DI robusto y flexible
- **⚙️ Configuración centralizada** - Basada en `pyproject.toml`
- **🔍 Descubrimiento automático** - Escaneo de componentes inteligente
- **🌐 Decoradores web** - Controladores y endpoints con FastAPI
- **💾 Capa de datos** - SQLAlchemy con migraciones Alembic
- **⚡ Sistema de tareas** - Queue de tareas en segundo plano
- **🗄️ Sistema de caché completo** - Síncrono, asíncrono e híbrido
- **🖥️ CLI avanzado** - Generación de proyectos y aplicaciones

### 🔐 Sistema de Seguridad (Completado)

- **🔑 Autenticación JWT** - Tokens de acceso y refresh
- **🛡️ Middleware de seguridad** - CORS, rate limiting, headers de seguridad
- **🎭 Decoradores de autorización** - Protección de endpoints por roles y permisos
- **🔒 Dependencias de FastAPI** - Integración nativa con el ecosistema

### 📊 Sistema de Observabilidad (Completado)

- **📝 Logging estructurado** - Con `structlog` y configuración avanzada
- **📈 Métricas unificadas** - OpenTelemetry con exportación a Prometheus
- **🔍 Trazado distribuido** - Integración completa con OpenTelemetry
- **❤️ Health checks** - Endpoints de diagnóstico con modelos Pydantic
- **🔌 Addons APM** - New Relic, DataDog, Elastic APM como addons separados

## 📦 Instalación

### Requisitos

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recomendado) o pip

### Instalación desde GitHub

```bash
# Clonar el repositorio
git clone https://github.com/alexmarco/turboapi.git
cd turboapi

# Instalar dependencias
uv sync

# Instalar dependencias de desarrollo
uv sync --group dev
```

### Instalación como dependencia

```bash
# Desde GitHub (desarrollo)
uv add git+https://github.com/alexmarco/turboapi.git

# O con pip
pip install git+https://github.com/alexmarco/turboapi.git
```

## 🚀 Inicio Rápido

### 1. Crear un nuevo proyecto

```bash
# Crear proyecto
uv run framework new mi_proyecto
cd mi_proyecto

# Instalar dependencias
uv sync
```

### 2. Crear una aplicación

```bash
# Crear aplicación
uv run framework new-app mi_app
```

### 3. Configurar observabilidad

```python
# pyproject.toml
[tool.turboapi.observability]
apm_enabled = true
service_name = "mi_proyecto"
environment = "development"
version = "1.0.0"
sample_rate = 1.0

[tool.turboapi.observability.apm.newrelic]
license_key = "your-license-key"
app_name = "mi_proyecto"
```

### 4. Ejecutar el servidor

```bash
# Servidor de desarrollo
uv run framework run --reload

# Con configuración personalizada
uv run framework run --host 0.0.0.0 --port 9000
```

## 📚 Documentación

### Documentos Principales

- **[PRD (Product Requirements Document)](docs/01-prd.md)** - Requisitos del producto
- **[DDT (Documento de Diseño Técnico)](docs/02-ddt.md)** - Arquitectura técnica
- **[Roadmap](docs/03-roadmap.md)** - Plan de desarrollo
- **[CHANGELOG](CHANGELOG.md)** - Historial de cambios

### Ejemplos de Uso

#### Sistema de Caché

```python
from turboapi.cache import Cache, AsyncCache, SmartCache

# Caché síncrono
@Cache(ttl=300)
def get_user_data(user_id: int):
    return {"id": user_id, "name": "Usuario"}

# Caché asíncrono
@AsyncCache(ttl=600)
async def fetch_api_data(url: str):
    # Lógica asíncrona
    return await api_call(url)

# Caché inteligente (automático)
@SmartCache
def expensive_calculation(data: dict):
    return complex_processing(data)
```

#### Sistema de Seguridad

```python
from turboapi.security import Authenticate, RequireRole
from turboapi.security.dependencies import get_current_user

@Authenticate
@RequireRole("admin")
async def admin_endpoint(user: User = Depends(get_current_user)):
    return {"message": f"Hola {user.name}"}
```

#### Observabilidad

```python
from turboapi.observability import get_logger, get_metrics_collector

# Logging estructurado
logger = get_logger(__name__)
logger.info("Operación completada", user_id=123, action="login")

# Métricas
metrics = get_metrics_collector()
metrics.increment_counter("requests_total", {"endpoint": "/api/users"})
```

## 🛠️ Desarrollo

### Configuración del entorno

```bash
# Instalar dependencias
uv sync

# Instalar dependencias de desarrollo
uv sync --group dev
```

### Quality Gates Obligatorios

Antes de cada commit, ejecuta esta secuencia completa:

```bash
# 1. Formatear código
uv run ruff format .

# 2. Corregir errores de linting
uv run ruff check . --fix

# 3. Verificar tipado estático
uv run mypy .

# 4. Ejecutar pruebas
uv run pytest
```

### Comandos de desarrollo

```bash
# Ejecutar tests
uv run pytest

# Tests con cobertura
uv run pytest --cov=src --cov-report=html

# Linting
uv run ruff check .

# Formateo
uv run ruff format .

# Verificación de tipos
uv run mypy .

# CLI del framework
uv run framework --help
```

### Estructura del proyecto

```
turboapi/
├── src/turboapi/           # Código fuente del framework
│   ├── core/               # Núcleo del framework
│   ├── web/                # Componentes web
│   ├── data/               # Capa de datos
│   ├── cache/              # Sistema de caché
│   ├── security/           # Sistema de seguridad
│   ├── observability/      # Sistema de observabilidad
│   └── cli/                # CLI del framework
├── addons/                 # Addons del framework
│   └── apm/                # Addons de APM
├── tests/                  # Pruebas unitarias
├── docs/                   # Documentación
├── pyproject.toml          # Configuración del proyecto
└── README.md               # Este archivo
```

## 🧪 Testing

El proyecto incluye 495 tests unitarios que cubren:

- ✅ Sistema de caché (síncrono, asíncrono, híbrido)
- ✅ Sistema de seguridad (JWT, middleware, decoradores)
- ✅ Sistema de observabilidad (logging, métricas, tracing)
- ✅ Inyección de dependencias
- ✅ Configuración y CLI
- ✅ Integración con FastAPI

```bash
# Ejecutar todos los tests
uv run pytest

# Tests específicos
uv run pytest tests/test_observability_*.py

# Tests con verbose
uv run pytest -v

# Tests con cobertura
uv run pytest --cov=src --cov-report=term-missing
```

## 🔧 Configuración

### pyproject.toml

```toml
[project]
name = "mi-proyecto"
version = "0.1.0"
description = "Mi proyecto con TurboAPI"
requires-python = ">=3.11"
dependencies = [
    "turboapi",
    "fastapi",
    "uvicorn[standard]",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
]

[tool.turboapi]
installed_apps = ["mi_app"]

[tool.turboapi.observability]
apm_enabled = true
service_name = "mi-proyecto"
environment = "development"
version = "0.1.0"
sample_rate = 1.0

[tool.turboapi.observability.apm.newrelic]
license_key = "your-license-key"
app_name = "mi-proyecto"
```

## 🤝 Contribuir

### Flujo de trabajo

1. **Fork** el repositorio
2. **Crear** una rama feature: `git checkout -b feature/nueva-funcionalidad`
3. **Desarrollar** siguiendo las reglas de calidad
4. **Ejecutar** quality gates antes de commit
5. **Crear** Pull Request hacia `develop`

### Reglas de desarrollo

- ✅ **Quality Gates obligatorios** antes de cada commit
- ✅ **Commits convencionales** (feat, fix, docs, etc.)
- ✅ **Tipado estático** con MyPy
- ✅ **Formateo** con Ruff
- ✅ **Tests** para nueva funcionalidad
- ✅ **Documentación** actualizada

### Estándares de código

- **Python 3.11+** con tipos modernos (`str | None` en lugar de `Optional[str]`)
- **Ruff** para linting y formateo
- **MyPy** para verificación de tipos
- **Pytest** para testing
- **Conventional Commits** para mensajes de commit

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🆘 Soporte

### Estado del proyecto

- **Versión actual**: 1.0.0 (Alpha)
- **Estado**: En desarrollo activo
- **Uso en producción**: ❌ No recomendado

### Recursos

- 📖 [Documentación](docs/)
- 🐛 [Issues](https://github.com/alexmarco/turboapi/issues)
- 💬 [Discussions](https://github.com/alexmarco/turboapi/discussions)
- 📋 [Roadmap](docs/03-roadmap.md)

### Contacto

- **Autor**: Alejandro Marco Ramos
- **Email**: alejandro.marco.ramos@gmail.com
- **GitHub**: [@alexmarco](https://github.com/alexmarco)

---

<div align="center">

**⚠️ RECUERDA: Este framework está en estado ALPHA y NO es recomendado para producción ⚠️**

[![GitHub](https://img.shields.io/badge/GitHub-alexmarco-181717?style=flat&logo=github)](https://github.com/alexmarco)
[![Email](https://img.shields.io/badge/Email-alejandro.marco.ramos@gmail.com-D14836?style=flat&logo=gmail)](mailto:alejandro.marco.ramos@gmail.com)

</div>
