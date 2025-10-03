# Documento de Diseño Técnico (DDT)

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

## Sistema de Documentación

### Arquitectura de Documentación

El sistema de documentación está diseñado para ser modular, mantenible y fácil de navegar, siguiendo el principio de separación de responsabilidades.

#### Estructura de Documentación

```
docs/
├── 01-prd.md                    # Product Requirements Document
├── 02-ddt.md                    # Documento de Diseño Técnico
├── 03-roadmap.md                # Roadmap de desarrollo
├── 04-getting-started.md        # Guía de inicio rápido
├── 05-core-system.md            # Documentación del sistema core
├── 06-web-layer.md              # Documentación de la capa web
├── 07-data-layer.md             # Documentación de la capa de datos
├── 08-security-system.md        # Documentación del sistema de seguridad
├── 09-observability-system.md   # Documentación del sistema de observabilidad
├── 10-cli-tools.md              # Documentación de herramientas CLI
├── 11-cache-system.md           # Documentación del sistema de caché
├── 12-task-system.md            # Documentación del sistema de tareas
├── 13-addons-system.md          # Documentación del sistema de addons
├── 14-examples.md               # Ejemplos de uso
├── 15-api-reference.md          # Referencia de API
└── 16-troubleshooting.md        # Guía de solución de problemas
```

#### Principios de Documentación

1. **Modularidad**: Cada documento se enfoca en un aspecto específico del framework
2. **Navegabilidad**: Enlaces cruzados entre documentos para facilitar la navegación
3. **Mantenibilidad**: Estructura clara que permite agregar nuevos módulos sin afectar la organización
4. **Consistencia**: Formato uniforme y estructura similar en todos los documentos
5. **Actualización**: Documentación sincronizada con el código fuente

#### Responsabilidades por Documento

- **README.md**: Punto de entrada principal con información general y enlaces
- **01-prd.md**: Requisitos del producto y visión
- **02-ddt.md**: Decisiones técnicas y arquitectura
- **03-roadmap.md**: Plan de desarrollo y estado del proyecto
- **04-getting-started.md**: Guía de instalación y primer proyecto
- **05-XX-system.md**: Documentación detallada de cada sistema del framework
- **14-examples.md**: Ejemplos prácticos de uso
- **15-api-reference.md**: Referencia completa de la API
- **16-troubleshooting.md**: Solución de problemas comunes

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

#### Características del Sistema

- **Síncrono y Asíncrono**: Soporte completo para ambos paradigmas
- **Decoradores Inteligentes**: Decoradores que detectan automáticamente el tipo de función
- **Gestión de TTL**: Time-to-live configurable por entrada
- **Estadísticas**: Métricas de hit/miss y rendimiento
- **Thread-Safe**: Implementación segura para entornos concurrentes
- **Integración DI**: Registro automático en el contenedor de inyección de dependencias
- **Descubrimiento Automático**: Escaneo automático de funciones cacheables

#### Implementaciones Disponibles

1. **InMemoryCache**: Para desarrollo y testing
2. **AsyncInMemoryCache**: Para aplicaciones asíncronas
3. **Extensible**: Fácil integración con Redis, Memcached, etc.

### Sistema de Tareas en Segundo Plano

#### Arquitectura del Sistema de Tareas

El sistema de tareas proporciona capacidades para ejecutar trabajos de forma asíncrona sin dependencias externas.

#### Componentes Principales

1. **BaseTaskQueue (Interface)**: Define la API estándar para colas de tareas
2. **InMemoryTaskQueue**: Implementación en memoria sin dependencias externas
3. **@Task Decorator**: Decorador para marcar funciones como tareas ejecutables
4. **TaskStarter**: Integración con el sistema de inyección de dependencias
5. **ComponentScanner**: Descubrimiento automático de funciones marcadas con @Task

#### Características del Sistema

- **Sin Dependencias Externas**: Implementación en memoria para simplicidad
- **Decoradores**: Marcado simple de funciones como tareas
- **Integración DI**: Registro automático en el contenedor
- **Descubrimiento Automático**: Escaneo automático de tareas
- **Extensible**: Fácil migración a Celery, RQ, etc.

### Sistema de Seguridad y Autenticación

#### Arquitectura del Sistema de Seguridad

El sistema de seguridad proporciona autenticación, autorización y protección integral para aplicaciones TurboAPI.

#### Componentes Principales

1. **Interfaces de Seguridad**:
   - `User`: Modelo de usuario con roles y permisos
   - `Role`: Modelo de rol con permisos asociados
   - `Permission`: Modelo de permiso con recurso y acción
   - `AuthResult`: Resultado de operaciones de autenticación

2. **Sistema JWT**:
   - `JWTTokenManager`: Gestión de tokens JWT y refresh tokens
   - `PasswordHandler`: Hashing y verificación de contraseñas con bcrypt
   - `JWTAuthProvider`: Proveedor de autenticación JWT

3. **Sistema RBAC**:
   - `InMemoryRBACManager`: Gestión de roles y permisos en memoria
   - Asignación de roles a usuarios
   - Asignación de permisos a roles
   - Verificación de permisos

4. **Gestión de Sesiones**:
   - `InMemorySessionManager`: Gestión de sesiones en memoria
   - `SessionInfo`: Información de sesión con metadatos
   - Revocación de sesiones individuales y por usuario

5. **Decoradores de Seguridad**:
   - `@Authenticate`: Requiere autenticación
   - `@RequireRole`: Requiere roles específicos
   - `@RequirePermission`: Requiere permisos específicos

6. **Middleware de Seguridad**:
   - `SecurityMiddleware`: Headers de seguridad, CORS, rate limiting
   - `CORSSecurityMiddleware`: Configuración CORS avanzada
   - `RateLimitMiddleware`: Limitación de velocidad por IP

7. **Dependencias FastAPI**:
   - `get_current_user`: Obtención del usuario actual
   - Integración nativa con el ecosistema FastAPI

8. **CLI de Seguridad**:
   - Comandos para gestión de usuarios, roles y permisos
   - Comandos para gestión de sesiones
   - Comandos de verificación y diagnóstico

#### Características del Sistema

- **Autenticación JWT**: Tokens seguros con refresh tokens
- **Autorización RBAC**: Sistema completo de roles y permisos
- **Gestión de Sesiones**: Control granular de sesiones activas
- **Middleware de Seguridad**: Protección integral de aplicaciones
- **CLI de Administración**: Herramientas de línea de comandos
- **Integración OAuth2**: Soporte para proveedores externos (como addons)
- **Sin Dependencias Externas**: Implementación en memoria para simplicidad
- **Extensible**: Fácil migración a sistemas externos

### Sistema de Observabilidad

#### Arquitectura del Sistema de Observabilidad

El sistema de observabilidad proporciona logging, métricas, tracing y health checks para aplicaciones TurboAPI.

#### Componentes Principales

1. **Sistema de Logging**:
   - `TurboLogging`: Logger estructurado con `structlog`
   - `LoggingConfig`: Configuración de niveles y formato
   - `StructuredLogger`: Logger con campos estructurados

2. **Sistema de Métricas**:
   - `OpenTelemetryCollector`: Recolector basado en OpenTelemetry
   - `MetricConfig`: Configuración de métricas
   - Integración con Prometheus para exportación
   - Métricas del sistema con `SystemMetricsInstrumentor`

3. **Sistema de Tracing**:
   - `OpenTelemetryTracer`: Tracer basado en OpenTelemetry
   - `TracingConfig`: Configuración de tracing
   - Integración con Jaeger para visualización
   - Context managers para spans

4. **Sistema de Health Checks**:
   - `HealthChecker`: Verificador de salud de la aplicación
   - `BaseHealthCheck`: Clase base para health checks personalizados
   - Endpoints de diagnóstico con modelos Pydantic

5. **Sistema de Diagnósticos**:
   - `DiagnosticsRouter`: Router FastAPI para endpoints de diagnóstico
   - Información del sistema y proceso
   - Métricas de rendimiento
   - Información de dependencias

6. **APM (Application Performance Monitoring)**:
   - `OpenTelemetryAPMProvider`: Proveedor base con OpenTelemetry
   - Sistema de addons para integraciones externas
   - New Relic, DataDog, Elastic APM como addons separados

#### Características del Sistema

- **Logging Estructurado**: Logs con campos estructurados y niveles configurables
- **Métricas Unificadas**: Sistema unificado basado en OpenTelemetry
- **Tracing Distribuido**: Trazabilidad completa de requests
- **Health Checks**: Endpoints de diagnóstico y verificación de salud
- **APM Integrado**: Monitoreo de rendimiento con addons externos
- **Sin Variables Globales**: Uso de inyección de dependencias
- **Modelos Pydantic**: Respuestas estructuradas para OpenAPI
- **Integración OpenTelemetry**: Estándar de la industria para observabilidad

### Sistema de Addons

#### Arquitectura del Sistema de Addons

El sistema de addons permite extender el framework con funcionalidades adicionales sin afectar el núcleo.

#### Componentes Principales

1. **Infraestructura Base**:
   - `AddonStarter`: Protocolo para starters de addons
   - `AddonRegistry`: Registro de addons disponibles
   - `load_addon`: Función para cargar addons dinámicamente

2. **Paquete Independiente**:
   - `turboapi-addons`: Paquete Python independiente
   - `pyproject.toml` separado para gestión de dependencias
   - Dependencias opcionales para cada tipo de addon

3. **Addons APM**:
   - `BaseAPMAddon`: Clase base para addons APM
   - `NewRelicAPMAddon`: Integración con New Relic
   - `DataDogAPMAddon`: Integración con DataDog
   - `ElasticAPMAddon`: Integración con Elastic APM

4. **Addons OAuth2**:
   - `BaseOAuthAddon`: Clase base para addons OAuth2
   - `GoogleOAuthAddon`: Integración con Google OAuth2
   - `GitHubOAuthAddon`: Integración con GitHub OAuth2
   - `MicrosoftOAuthAddon`: Integración con Microsoft OAuth2

#### Características del Sistema

- **Separación del Core**: Addons independientes del framework principal
- **Carga Dinámica**: Carga automática basada en configuración
- **Dependencias Opcionales**: Solo instalar lo que se necesita
- **Patrón Starter**: Integración con el sistema de starters
- **Configuración Unificada**: Configuración a través de `pyproject.toml`
- **Extensible**: Fácil creación de nuevos addons

#### Estructura del Paquete de Addons

```
turboapi-addons/
├── pyproject.toml              # Configuración del paquete
├── README.md                   # Documentación de addons
├── turboapi_addons/
│   ├── __init__.py            # Infraestructura base
│   ├── base.py                # Clases base para addons
│   ├── apm/                   # Addons APM
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── newrelic.py
│   │   ├── datadog.py
│   │   └── elastic.py
│   └── oauth/                 # Addons OAuth2
│       ├── __init__.py
│       ├── base.py
│       ├── google.py
│       ├── github.py
│       └── microsoft.py
└── tests/                     # Tests de addons
    └── test_oauth_addons.py
```

#### Instalación de Addons

```bash
# Instalar addons base
pip install turboapi-addons

# Instalar addons específicos
pip install turboapi-addons[apm-newrelic]
pip install turboapi-addons[oauth-google]

# Instalar todos los addons
pip install turboapi-addons[all]
```

## Estado de Implementación

### ✅ Completado

1. **Sistema Core**: DI, configuración, descubrimiento de componentes
2. **Capa Web**: Integración con FastAPI, decoradores, enrutamiento
3. **Capa de Datos**: SQLAlchemy, Alembic, patrón repositorio
4. **Sistema de Caché**: Implementaciones síncronas y asíncronas
5. **Sistema de Tareas**: Tareas en segundo plano con decoradores
6. **Sistema de Seguridad**: JWT, RBAC, middleware, CLI
7. **Sistema de Observabilidad**: Logging, métricas, tracing, health checks
8. **Sistema de Addons**: Arquitectura modular con paquete independiente
9. **CLI del Framework**: Comandos para gestión de proyectos
10. **Sistema de Documentación**: Estructura modular y mantenible

### 🚧 En Progreso

1. **Optimizaciones de Rendimiento**: Profiling, optimizaciones de caché
2. **Herramientas de Desarrollo**: Hot reload, debugging integrado

### 📋 Pendiente

1. **Integraciones Cloud**: AWS, GCP, Azure
2. **Herramientas de Deployment**: Docker, Kubernetes
3. **Ecosistema de Plugins**: Marketplace de addons

## Decisiones Técnicas Clave

### 1. Gestión de Dependencias con `uv`

**Decisión**: Usar `uv` como gestor de dependencias principal.

**Justificación**:

- Velocidad superior a pip y poetry
- Compatibilidad con estándares Python
- Gestión de entornos virtuales integrada
- Soporte para `pyproject.toml`

### 2. Calidad de Código con Ruff y MyPy

**Decisión**: Usar Ruff para linting/formateo y MyPy para tipado estático.

**Justificación**:

- Ruff es extremadamente rápido (100x más que flake8)
- MyPy proporciona verificación de tipos robusta
- Integración perfecta con `pyproject.toml`
- Reducción de configuración manual

### 3. Arquitectura Modular con Addons

**Decisión**: Separar funcionalidades opcionales en addons independientes.

**Justificación**:

- Mantener el núcleo ligero y enfocado
- Permitir instalación selectiva de funcionalidades
- Facilitar el mantenimiento y actualizaciones
- Seguir el principio de responsabilidad única

### 4. Sistema de Documentación Modular

**Decisión**: Organizar la documentación en módulos específicos en directorio `/docs`.

**Justificación**:

- Mantener el README principal conciso y enfocado
- Facilitar la navegación y búsqueda de información
- Permitir actualizaciones independientes por módulo
- Mejorar la mantenibilidad a largo plazo
- Seguir las mejores prácticas de documentación de proyectos open source

### 5. Observabilidad con OpenTelemetry

**Decisión**: Basar el sistema de observabilidad en OpenTelemetry.

**Justificación**:

- Estándar de la industria para observabilidad
- Integración con múltiples herramientas (Prometheus, Jaeger, Grafana)
- API unificada para métricas, logs y traces
- Extensibilidad y compatibilidad futura

---

## Changelog de Versiones

### v1.1 (2025-10-03)

- **NUEVO**: Sistema de documentación modular en directorio `/docs`
- **ACTUALIZADO**: Arquitectura de documentación con principios y responsabilidades
- **ACTUALIZADO**: Estructura de documentos específicos por sistema
- **ACTUALIZADO**: Decisiones técnicas para sistema de documentación

### v1.0 (2025-10-02)

- Versión inicial del DDT
- Definición de arquitectura técnica
- Decisiones de tecnología y implementación
