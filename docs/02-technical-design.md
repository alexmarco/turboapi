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

## Próximas Funcionalidades (Épicas 7-10)

### Sistema de Seguridad y Autenticación (Epic 7)

**Arquitectura de Seguridad:**
- **BaseAuthProvider**: Interface para proveedores de autenticación
- **JWTManager**: Gestión de tokens JWT con refresh tokens
- **RBACManager**: Control de acceso basado en roles
- **SecurityMiddleware**: Middleware de seguridad para FastAPI
- **OAuth2Integration**: Integración con proveedores externos

**Características de Seguridad:**
- Autenticación JWT con refresh tokens
- Sistema RBAC completo
- Headers de seguridad automáticos
- Rate limiting integrado
- Auditoría de eventos de seguridad

### Observabilidad y Monitoreo (Epic 8)

**Stack de Observabilidad:**
- **StructuredLogger**: Logging estructurado con niveles configurables
- **MetricsCollector**: Métricas con Prometheus/StatsD
- **TracingManager**: Trazabilidad distribuida con OpenTelemetry
- **HealthChecker**: Health checks y diagnósticos
- **APMIntegration**: Integración con herramientas APM

**Capacidades de Monitoreo:**
- Dashboard web en tiempo real
- Alertas automáticas
- Profiling de rendimiento
- Métricas de aplicación
- Trazabilidad de requests

### Optimización y Rendimiento (Epic 9)

**Herramientas de Performance:**
- **ProfilerManager**: Profiling integrado
- **CacheOptimizer**: Optimizaciones avanzadas de caché
- **ConnectionPool**: Pool de conexiones optimizado
- **CompressionManager**: Compresión automática
- **LoadTester**: Herramientas de load testing

**Objetivos de Rendimiento:**
- Latencia < 10ms para operaciones básicas
- Throughput > 10,000 requests/segundo
- Uso eficiente de memoria
- Escalabilidad horizontal

### Herramientas de Desarrollo (Epic 10)

**DevTools Avanzadas:**
- **HotReloader**: Hot reload inteligente
- **DebuggerIntegration**: Debugging visual
- **DocGenerator**: Documentación automática
- **IDEPlugins**: Plugins para VS Code/PyCharm
- **DeploymentTools**: Deployment automatizado

**Experiencia de Desarrollo:**
- Reducción del 50% en tiempo de desarrollo
- Debugging interactivo
- Generación automática de código
- Integración completa con Docker/Kubernetes
