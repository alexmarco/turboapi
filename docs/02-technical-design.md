# Documento de Diseño Técnico

Este documento detalla las decisiones tecnológicas clave para la implementación del framework, basadas en el Plan Arquitectónico.

## Pila Tecnológica Principal

- **Lenguaje**: Python 3.11+
- **Framework Web Base**: FastAPI y Starlette. Se aprovechará su ecosistema ASGI, el enrutamiento, la validación con Pydantic y la inyección de dependencias a nivel de solicitud.
- **Gestión de Proyecto**: `uv` para la gestión de dependencias y entornos virtuales.
- **Fichero de Proyecto**: `pyproject.toml` como única fuente de verdad para la configuración del proyecto, dependencias y herramientas.
- **Calidad de Código**:
  - **Linting y Formateo**: `Ruff` para un análisis de código estático y formateo extremadamente rápidos.
  - **Comprobación de Tipado**: `Mypy` para garantizar que el tipado estático sea correcto.
- **Testing**: `pytest` como framework de pruebas, incluyendo `pytest-asyncio` para el código asíncrono.

## Arquitectura Interna del Framework (`src/turboapi`)

El código fuente del propio framework se organizará por funcionalidades clave para facilitar su mantenimiento y desarrollo.

```txt
src/turboapi/
├── __init__.py
├── core/                 # Lógica principal: DI, escáner de componentes, configuración.
│   ├── __init__.py
│   ├── di.py
│   └── discovery.py
├── web/                  # Integración con FastAPI: decoradores, montaje de rutas.
│   ├── __init__.py
│   └── routing.py
├── data/                 # Lógica de BBDD: wrapper de Alembic, inyección de sesión.
│   └── __init__.py
├── cli/                  # Comandos del CLI (Typer).
│   ├── __init__.py
│   └── main.py
└──- interfaces.py         # Definición de las ABCs (BaseRepository, BaseCache, etc.).
```

## Arquitectura del Proyecto de Usuario (Generada)

El CLI del framework (`framework new`) generará la siguiente estructura de directorios para los proyectos de usuario, promoviendo una arquitectura modular basada en aplicaciones.

```txt
/
├── pyproject.toml
├── .env.example
└── apps/
    ├── __init__.py
    └── home/
        ├── __init__.py
        ├── api.py
        ├── models.py
        └── services.py
```

## Configuración de Aplicaciones del Usuario (`pyproject.toml`)

El motor de descubrimiento del framework leerá esta sección para saber qué aplicaciones escanear.

```toml
[tool.turboapi]
installed_apps = [
    "apps.home",
]
```

## Detalles de Implementación de Componentes

1. **Contenedor de Inyección de Dependencias (DI)**:
    - Ubicado en `src/turboapi/core/di.py`.
    - Leerá la configuración `installed_apps` y coordinará con el módulo de descubrimiento.

2. **Motor de Descubrimiento**:
    - Ubicado en `src/turboapi/core/discovery.py`.
    - Será responsable de importar dinámicamente los paquetes de las aplicaciones del usuario y encontrar los componentes decorados.

3. **CLI del Framework**:
    - Ubicado en `src/turboapi/cli/`.
    - Implementará los comandos `new`, `new-app`, `run`, etc., que operan sobre la estructura del proyecto del usuario.

## Sistema de Caché

### Arquitectura del Sistema de Caché

El sistema de caché de TurboAPI proporciona una capa de almacenamiento temporal para mejorar el rendimiento de las aplicaciones.

#### Componentes Principales

1. **BaseCache (Interface)**: Define la API estándar para implementaciones de caché síncronas
2. **AsyncBaseCache (Interface)**: Define la API estándar para implementaciones de caché asíncronas
3. **InMemoryCache**: Implementación síncrona en memoria sin dependencias externas
4. **AsyncInMemoryCache**: Implementación asíncrona en memoria con `asyncio.Lock`
5. **CacheEntry**: Representa una entrada de caché con metadatos (TTL, estadísticas)
6. **BaseCacheDecorator**: Clase base común para decoradores de caché
7. **@Cache Decorator**: Decorador para funciones síncronas con caché automático
8. **@AsyncCache Decorator**: Decorador para funciones asíncronas con caché automático
9. **@SmartCache Decorator**: Decorador híbrido que detecta automáticamente sync/async
10. **AsyncCacheContext**: Context manager para gestión avanzada de caché asíncrono
11. **CacheStarter**: Integración con el sistema de inyección de dependencias
12. **ComponentScanner**: Descubrimiento automático de funciones cacheables

#### Funcionalidades Implementadas

**Caché Síncrono:**

- ✅ Caché en memoria con TTL configurable
- ✅ Normalización de argumentos para claves consistentes
- ✅ Estadísticas de rendimiento (hits, misses, hit rate)
- ✅ Limpieza automática de entradas expiradas
- ✅ Decorador `@Cache` para funciones síncronas
- ✅ CLI para gestión del caché
- ✅ Integración con sistema de inyección de dependencias

**Caché Asíncrono:**

- ✅ Implementación completamente asíncrona (`AsyncInMemoryCache`)
- ✅ Decorador `@AsyncCache` para funciones `async def`
- ✅ Manejo de operaciones concurrentes con `asyncio.Lock`
- ✅ Prevención de ejecuciones duplicadas con pending operations
- ✅ Integración con contextos asyncio (gather, tasks, semáforos)
- ✅ Context managers para gestión avanzada (`AsyncCacheContext`)
- ✅ Separación arquitectónica completa entre sync y async

**Funcionalidades Avanzadas:**

- ✅ Decorador híbrido `@SmartCache` con detección automática
- ✅ Refactorización con `BaseCacheDecorator` para eliminar duplicación
- ✅ Soporte para funciones personalizadas de generación de claves
- ✅ Manejo robusto de excepciones y timeouts
- ✅ Compatibilidad completa con `pytest-asyncio`

---

## Sistema de Seguridad y Autenticación

### Arquitectura de Seguridad (REQ 4.x)

El framework implementa un sistema de seguridad robusto que cumple con estándares empresariales y facilita la implementación de autenticación y autorización.

#### Componentes de Seguridad

**1. Interfaces Base (`src/turboapi/security/interfaces.py`)**

```python
class BaseAuthProvider(ABC):
    """Interface para proveedores de autenticación."""
    @abstractmethod
    async def authenticate(self, credentials: dict) -> AuthResult: ...
    @abstractmethod
    async def validate_token(self, token: str) -> TokenPayload: ...

class BaseTokenManager(ABC):
    """Interface para gestión de tokens."""
    @abstractmethod
    def generate_token(self, payload: dict) -> str: ...
    @abstractmethod
    def verify_token(self, token: str) -> dict: ...

class BaseRBACManager(ABC):
    """Interface para control de acceso basado en roles."""
    @abstractmethod
    async def check_permission(self, user: User, resource: str, action: str) -> bool: ...
```

**2. Gestión de Autenticación (`src/turboapi/security/auth.py`)**

- **JWTAuthProvider**: Implementación JWT con refresh tokens
- **OAuth2Provider**: Integración con proveedores externos (Google, GitHub, etc.)
- **SessionManager**: Gestión de sesiones seguras con almacenamiento configurable

**3. Control de Acceso (`src/turboapi/security/rbac.py`)**

- **RBACManager**: Sistema completo de roles, permisos y recursos
- **PermissionRegistry**: Registro automático de permisos desde decoradores
- **RoleHierarchy**: Soporte para jerarquías de roles

**4. Middleware de Seguridad (`src/turboapi/security/middleware.py`)**

- **AuthenticationMiddleware**: Verificación automática de tokens
- **SecurityHeadersMiddleware**: Headers de seguridad automáticos
- **RateLimitMiddleware**: Rate limiting configurable
- **CORSMiddleware**: Configuración CORS segura

#### Decoradores de Seguridad

```python
# Autenticación requerida
@Controller("/api/secure")
class SecureController:
    @Get("/data")
    @RequireAuth()
    async def get_data(self) -> dict: ...

    # Control de acceso basado en roles
    @Post("/admin")
    @RequireRole("admin")
    async def admin_action(self) -> dict: ...

    # Control granular de permisos
    @Delete("/resource/{id}")
    @RequirePermission("resource:delete")
    async def delete_resource(self, id: int) -> dict: ...
```

#### Configuración de Seguridad (`pyproject.toml`)

```toml
[tool.turboapi.security]
# JWT Configuration
jwt_secret = "${JWT_SECRET}"
jwt_algorithm = "HS256"
jwt_expiration = 3600
refresh_token_expiration = 86400

# Session Configuration
session_backend = "memory"  # memory, redis, database
session_expire = 1800

# Security Headers
security_headers = true
cors_origins = ["http://localhost:3000"]
rate_limit = {requests = 100, window = 60}

# OAuth2 Providers
[tool.turboapi.security.oauth2]
google = {client_id = "${GOOGLE_CLIENT_ID}", client_secret = "${GOOGLE_CLIENT_SECRET}"}
github = {client_id = "${GITHUB_CLIENT_ID}", client_secret = "${GITHUB_CLIENT_SECRET}"}
```

#### Auditoría y Compliance

**1. Logging de Seguridad (`src/turboapi/security/audit.py`)**

- **SecurityLogger**: Logging estructurado de eventos de seguridad
- **AuditTrail**: Trazabilidad completa de acciones de usuarios
- **ComplianceReporter**: Reportes para GDPR, CCPA

**2. Validación y Sanitización**

- **InputValidator**: Validación estricta de inputs con Pydantic
- **XSSProtection**: Protección automática contra XSS
- **SQLInjectionProtection**: Protección contra inyección SQL

#### Casos de Uso de Seguridad

**Caso de Uso 1: Autenticación JWT**

```python
# 1. Login endpoint
@Post("/auth/login")
async def login(credentials: LoginRequest, auth: JWTAuthProvider) -> TokenResponse:
    result = await auth.authenticate(credentials.dict())
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=3600
    )

# 2. Endpoint protegido
@Get("/profile")
@RequireAuth()
async def get_profile(current_user: User) -> UserProfile:
    return UserProfile.from_user(current_user)
```

**Caso de Uso 2: Control de Acceso RBAC**

```python
# Definición de roles
@dataclass
class Role:
    name: str
    permissions: list[str]

# Configuración en el controlador
@Controller("/api/admin")
@RequireRole("admin")
class AdminController:
    @Get("/users")
    @RequirePermission("user:list")
    async def list_users(self) -> list[User]: ...
```

---

## Sistema de Observabilidad y Monitoreo

### Arquitectura de Observabilidad (REQ 5.x)

El framework integra capacidades completas de observabilidad siguiendo estándares de la industria para facilitar el monitoreo y diagnóstico de aplicaciones.

#### Stack de Observabilidad

**1. Logging Estructurado (`src/turboapi/observability/logging.py`)**

```python
class StructuredLogger:
    """Logger estructurado con contexto automático."""
    def info(self, message: str, **context): ...
    def error(self, message: str, error: Exception, **context): ...
    
    # Integración automática con request context
    @contextmanager
    def request_context(self, request_id: str, user_id: str = None): ...
```

**2. Métricas y Monitoreo (`src/turboapi/observability/metrics.py`)**

- **PrometheusCollector**: Métricas compatibles con Prometheus
- **MetricsRegistry**: Registro automático de métricas de aplicación
- **CustomMetrics**: API para métricas personalizadas del usuario

**3. Trazabilidad Distribuida (`src/turboapi/observability/tracing.py`)**

- **OpenTelemetryIntegration**: Integración completa con OpenTelemetry
- **TraceManager**: Gestión automática de traces y spans
- **ContextPropagation**: Propagación de contexto entre servicios

#### Health Checks y Diagnósticos

**1. Health Check System (`src/turboapi/observability/health.py`)**

```python
@HealthCheck("database")
async def check_database() -> HealthStatus:
    """Verifica conectividad de base de datos."""
    ...

@HealthCheck("cache")
async def check_cache() -> HealthStatus:
    """Verifica estado del sistema de caché."""
    ...

# Endpoint automático: GET /health
# Respuesta: {"status": "healthy", "checks": {...}}
```

**2. Métricas Automáticas**

- Request/Response time
- Error rates por endpoint
- Cache hit/miss ratios
- Database connection pool status
- Memory usage y garbage collection

#### Configuración de Observabilidad (`pyproject.toml`)

```toml
[tool.turboapi.observability]
# Logging
log_level = "INFO"
log_format = "json"  # json, text
log_destination = "stdout"  # stdout, file, syslog

# Metrics
metrics_enabled = true
metrics_endpoint = "/metrics"
prometheus_registry = true

# Tracing
tracing_enabled = true
tracing_endpoint = "http://jaeger:14268/api/traces"
trace_sample_rate = 0.1

# Health Checks
health_endpoint = "/health"
health_checks_interval = 30
```

#### Integración con Herramientas Externas

**1. Prometheus + Grafana**

- Dashboards predefinidos para métricas del framework
- Alertas automáticas para errores críticos
- Visualización de performance trends

**2. ELK Stack / OpenSearch**

- Configuración automática para logging centralizado
- Índices optimizados para búsquedas de logs
- Dashboards de Kibana predefinidos

**3. APM Tools**

- New Relic integration
- DataDog integration
- Elastic APM integration

---

## Herramientas de Experiencia de Desarrollador

### Arquitectura de DevTools (REQ 6.x)

El framework proporciona herramientas avanzadas que maximizan la productividad del desarrollador y simplifican el ciclo de desarrollo.

#### Hot Reload y Desarrollo

**1. Smart Hot Reload (`src/turboapi/devtools/reload.py`)**

- Detección inteligente de cambios en código
- Reload selectivo por módulos afectados
- Preservación de estado durante reload
- Integración con debugger

**2. Development Server (`src/turboapi/devtools/server.py`)**

```python
# Comando: framework dev
# Características:
# - Hot reload automático
# - Logging mejorado para desarrollo
# - Debug mode con stacktraces detallados
# - Live reload de configuración
```

#### Generación Automática de Documentación

**1. API Documentation (`src/turboapi/devtools/docs.py`)**

- Generación automática de OpenAPI/Swagger
- Documentación interactiva con FastAPI
- Ejemplos automáticos desde tests
- Versionado de API documentation

**2. Code Documentation**

- Extracción automática de docstrings
- Generación de documentación de arquitectura
- Diagramas automáticos de dependencias

#### Integración con Ecosistema

**1. Docker Integration (`src/turboapi/devtools/docker.py`)**

```dockerfile
# Dockerfile generado automáticamente
FROM python:3.11-slim
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
CMD ["framework", "run", "--host", "0.0.0.0"]
```

**2. Kubernetes Templates**

- Manifests automáticos para deployment
- ConfigMaps para configuración
- Services y Ingress predefinidos

**3. CI/CD Templates**

```yaml
# .github/workflows/turboapi.yml (generado)
name: TurboAPI CI/CD
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv sync
      - run: uv run pytest
      - run: uv run ruff check .
      - run: uv run mypy .
```

#### Herramientas de Desarrollo

**1. Debug Tools**

- Integration con VS Code debugger
- PyCharm plugin development
- Interactive debugging console

**2. Testing Utilities**

- Test fixtures automáticos
- Mock generators para servicios
- Performance testing helpers

**3. Migration Tools**

- Framework version migration scripts
- Automated refactoring tools
- Deprecation warnings system

---

## Estado de Implementación

### ✅ Funcionalidades Completadas (Épicas 1-6.1)

**Núcleo del Framework:**

- ✅ **Sistema de DI**: Container robusto con inyección automática
- ✅ **Configuración**: Gestión centralizada via `pyproject.toml`
- ✅ **Descubrimiento**: Escaneo automático de componentes
- ✅ **Web Framework**: Integración FastAPI con decoradores
- ✅ **Capa de Datos**: SQLAlchemy + Alembic con migraciones
- ✅ **Sistema de Tareas**: Queue de tareas con decoradores
- ✅ **Sistema de Caché**: Implementación completa sync/async/híbrido
- ✅ **CLI**: Herramientas de generación y gestión

### 🎯 Funcionalidades Diseñadas (REQ 4.x, 5.x, 6.x - Listas para Implementación)

**✅ Sistema de Seguridad:** Arquitectura completa definida, interfaces especificadas, configuración documentada
**✅ Sistema de Observabilidad:** Stack completo diseñado, integración OpenTelemetry planificada
**✅ Herramientas DevTools:** Hot reload, documentación automática, integración ecosistema

### 🚀 Próximas Épicas de Optimización

**Epic 9: Performance Optimization**

- ProfilerManager, CacheOptimizer, ConnectionPool, LoadTester

**Epic 10: Advanced DevTools**

- IDEPlugins, DeploymentTools, MigrationTools, TestingFramework
