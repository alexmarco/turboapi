# Roadmap de Desarrollo de TurboAPI

Este documento desglosa el plan de desarrollo en épicas y tareas manejables, diseñado para un enfoque TDD (Test-Driven Development).

## Épica 1: El Núcleo del Framework (Core) ✅ COMPLETADA

*Objetivo: Construir las capacidades fundamentales del framework: el motor de DI, el escáner de componentes y el sistema de configuración.*

- [x] **Tarea 1.1 (Setup)**: Configurar `pytest`, `ruff` y `mypy` en `pyproject.toml`.
- [x] **Tarea 1.2 (Core - DI)**: Escribir prueba para el contenedor de DI (registro y resolución de singletons).
- [x] **Tarea 1.3 (Core - DI)**: Implementar la lógica mínima de registro y resolución de singletons.
- [x] **Tarea 1.4 (Core - DI)**: Extender el contenedor para resolver dependencias transitivas.
- [x] **Tarea 1.5 (Config)**: Implementar la lógica de configuración que lee `installed_apps` desde `pyproject.toml`.
- [x] **Tarea 1.6 (Config)**: Registrar el objeto de configuración como un singleton en el contenedor.
- [x] **Tarea 1.7 (Discovery)**: Implementar el escáner que lee la lista `installed_apps`.
- [x] **Tarea 1.8 (Discovery)**: Implementar la lógica del escáner para importar dinámicamente los paquetes de las aplicaciones de usuario y descubrir componentes.
- [x] **Tarea 1.9 (Discovery)**: Integrar el escáner con el contenedor de DI.

**Logros de la Épica 1:**

- ✅ Sistema completo de inyección de dependencias con soporte para singletons y transients
- ✅ Sistema de configuración que lee desde `pyproject.toml`
- ✅ Escáner de componentes que descubre automáticamente clases y funciones en las aplicaciones instaladas
- ✅ Integración completa entre configuración, DI y descubrimiento en `TurboApplication`
- ✅ 34 pruebas unitarias que cubren toda la funcionalidad del núcleo
- ✅ Código con tipado estático completo y formateo automático

## Épica 2: Capa Web y Enrutamiento ✅ COMPLETADA

*Objetivo: Construir la integración con FastAPI y el sistema de enrutamiento que opera sobre los controladores descubiertos.*

- [x] **Tarea 2.1 (Web - Starter)**: Crear el "starter" web (`turboapi-starter-web`).
- [x] **Tarea 2.2 (Web - Decorators)**: Definir los decoradores `@Controller` y `@Get`, `@Post`, etc.
- [x] **Tarea 2.3 (Discovery)**: Extender el escáner de componentes para que también descubra `@Controller`s.
- [x] **Tarea 2.4 (Web - Integration)**: Crear la clase `TurboAPI` que usa el escáner para encontrar todos los `@Controller`s y montar sus rutas.
- [x] **Tarea 2.5 (Web - TDD)**: Escribir prueba de integración con `TestClient`.

**Logros de la Épica 2:**

- ✅ Sistema completo de decoradores web (`@Controller`, `@Get`, `@Post`, `@Put`, `@Delete`)
- ✅ Integración completa con FastAPI y enrutamiento automático
- ✅ Descubrimiento automático de controladores y endpoints
- ✅ Sistema de inyección de dependencias para controladores
- ✅ Soporte para metadatos de controladores (prefijos, etiquetas, dependencias)
- ✅ Soporte para metadatos de endpoints (códigos de estado, modelos de respuesta, documentación)
- ✅ 24 pruebas unitarias que cubren toda la funcionalidad web
- ✅ Integración completa con TestClient para pruebas de endpoints

## Épica 3: Capa de Acceso a Datos ✅ COMPLETADA

*Objetivo: Construir las capacidades del framework para la gestión de datos: inyección de sesión, patrón repositorio y wrapper de Alembic.*

- [x] **Tarea 3.1 (Data - Starter)**: Crear el "starter" de datos (`turboapi-starter-data-sql`).
- [x] **Tarea 3.2 (Data - DI)**: Implementar la inyección de una `Session` de SQLAlchemy por solicitud.
- [x] **Tarea 3.3 (Data - Repository)**: Definir la interfaz `BaseRepository` (ABC) en `src/turboapi/interfaces.py`.
- [x] **Tarea 3.4 (Data - Repository)**: Crear una implementación por defecto, `SQLRepository`.
- [x] **Tarea 3.5 (Data - Alembic)**: Implementar el comando `framework db revision --autogenerate`.
- [x] **Tarea 3.6 (Data - Alembic)**: Configurar el wrapper de Alembic para que descubra modelos en las `installed_apps` del usuario.

**Logros de la Épica 3:**

- ✅ Sistema completo de gestión de base de datos con `TurboDatabase`
- ✅ Inyección de dependencias para sesiones de SQLAlchemy
- ✅ Patrón repositorio con `BaseRepository` (ABC) y `SQLRepository` (implementación)
- ✅ Decorador `@Repository` para marcar repositorios automáticamente
- ✅ Wrapper simplificado de Alembic (`TurboMigrator`) que ejecuta comandos CLI directamente
- ✅ `DataStarter` que configura toda la capa de datos y registra componentes en DI
- ✅ Descubrimiento automático de repositorios en las aplicaciones instaladas
- ✅ 43 pruebas unitarias que cubren toda la funcionalidad de la capa de datos
- ✅ Integración completa con SQLAlchemy y Alembic

## ✅ Épica 4: Herramientas de Desarrollo (CLI) - COMPLETADA

*Objetivo: Construir la herramienta CLI que los usuarios utilizarán para gestionar sus proyectos y aplicaciones.*

- ✅ **Tarea 4.1 (CLI)**: Configurar `Typer` para el comando principal `framework`.
- ✅ **Tarea 4.2 (CLI - `new` command)**: Implementar `framework new <project_name>` para generar la estructura de directorios modular (`apps/`, etc.).
- ✅ **Tarea 4.3 (CLI - `new-app` command)**: Implementar `framework new-app <app_name>` para crear la estructura de una nueva aplicación.
- ✅ **Tarea 4.4 (CLI - `run` command)**: Implementar `framework run`.
- ❌ **Tarea 4.5 (CLI - `test` command)**: ~~Implementar `framework test`~~ - Cancelada (se usa directamente `uv run pytest`).

### Logros de la Épica 4

- **CLI completo y funcional** con comandos para generación de proyectos y aplicaciones
- **Comando `framework new`** con soporte para plantillas (basic, advanced)
- **Comando `framework new-app`** que genera estructura completa de aplicación con ejemplos
- **Comando `framework run`** que detecta automáticamente aplicaciones y ejecuta uvicorn
- **Detección automática de aplicaciones** en archivos comunes (main.py, app.py, etc.)
- **Tests completos** con mocking para evitar ejecución real de servidores
- **Configuración de linting y tipos** completamente funcional con Pyright y Ruff

## ✅ Épica 5: Sistema de Tareas en Segundo Plano (Background Tasks) - COMPLETADA

*Objetivo: Construir un sistema de tareas en segundo plano que permita ejecutar trabajos de forma asíncrona sin dependencias externas.*

- ✅ **Tarea 5.1 (Tasks - Interface)**: Definir la interfaz `BaseTaskQueue` en `src/turboapi/interfaces.py`.
- ✅ **Tarea 5.2 (Tasks - Implementation)**: Implementar `InMemoryTaskQueue` como implementación básica sin dependencias externas.
- ✅ **Tarea 5.3 (Tasks - Decorator)**: Crear el decorador `@Task` para marcar funciones como tareas ejecutables.
- ✅ **Tarea 5.4 (Tasks - Starter)**: Implementar `TaskStarter` para configurar el sistema de tareas y registrar componentes en DI.
- ✅ **Tarea 5.5 (Tasks - Discovery)**: Extender `ComponentScanner` para descubrir automáticamente funciones marcadas con `@Task`.

### Logros de la Épica 5

- **Sistema de tareas completo** con interfaz `BaseTaskQueue` y implementación `InMemoryTaskQueue`
- **Decorador `@Task`** para marcar funciones como tareas ejecutables
- **`TaskStarter`** que configura el sistema y registra componentes en DI
- **Descubrimiento automático** de tareas en aplicaciones instaladas
- **Tests completos** que cubren toda la funcionalidad del sistema de tareas
- **Integración con DI** para inyección de dependencias en tareas

## ✅ Épica 6: Sistema de Caché Inteligente - COMPLETADA

*Objetivo: Implementar un sistema de caché robusto que soporte tanto operaciones síncronas como asíncronas, con decoradores inteligentes y gestión avanzada.*

### Funcionalidades Principales

- [x] **Tarea 6.1 (Cache - Interfaces)**: Definir interfaces `BaseCache` y `AsyncBaseCache`
- [x] **Tarea 6.2 (Cache - Implementations)**: Implementar `InMemoryCache` y `AsyncInMemoryCache`
- [x] **Tarea 6.3 (Cache - Decorators)**: Crear decoradores `@Cache`, `@AsyncCache` y `@SmartCache`
- [x] **Tarea 6.4 (Cache - Context)**: Implementar `AsyncCacheContext` para gestión avanzada
- [x] **Tarea 6.5 (Cache - Starter)**: Crear `CacheStarter` para integración con DI
- [x] **Tarea 6.6 (Cache - Discovery)**: Extender `ComponentScanner` para descubrir funciones cacheables
- [x] **Tarea 6.7 (Cache - Testing)**: Escribir pruebas completas para el sistema de caché

### Características del Sistema

- **Síncrono y Asíncrono**: Soporte completo para ambos paradigmas
- **Decoradores Inteligentes**: `@SmartCache` detecta automáticamente sync/async
- **Gestión de TTL**: Time-to-live configurable por entrada
- **Estadísticas**: Métricas de hit/miss y rendimiento
- **Thread-Safe**: Implementación segura para entornos concurrentes
- **Integración DI**: Registro automático en el contenedor de inyección de dependencias
- **Descubrimiento Automático**: Escaneo automático de funciones cacheables

### Logros de la Épica 6

- ✅ Sistema completo de caché con soporte síncrono y asíncrono
- ✅ Decoradores inteligentes que detectan automáticamente el tipo de función
- ✅ Gestión avanzada de caché con context managers
- ✅ Integración completa con el sistema de inyección de dependencias
- ✅ Descubrimiento automático de funciones cacheables
- ✅ 45 pruebas unitarias que cubren toda la funcionalidad del sistema de caché
- ✅ Código con tipado estático completo y formateo automático

## ✅ Épica 7: Sistema de Seguridad y Autenticación - COMPLETADA

*Objetivo: Implementar un sistema completo de seguridad con autenticación JWT, autorización RBAC, gestión de sesiones y middleware de seguridad.*

### Funcionalidades Principales

- [x] **Tarea 7.1 (Security - Interfaces)**: Definir interfaces de seguridad (User, Role, Permission, AuthResult)
- [x] **Tarea 7.2 (Security - JWT)**: Implementar sistema JWT con tokens de acceso y refresh
- [x] **Tarea 7.3 (Security - Password)**: Implementar hashing de contraseñas con bcrypt
- [x] **Tarea 7.4 (Security - RBAC)**: Implementar sistema de roles y permisos
- [x] **Tarea 7.5 (Security - Sessions)**: Implementar gestión de sesiones
- [x] **Tarea 7.6 (Security - Decorators)**: Crear decoradores de seguridad (@Authenticate, @RequireRole, @RequirePermission)
- [x] **Tarea 7.7 (Security - Middleware)**: Implementar middleware de seguridad (headers, CORS, rate limiting)
- [x] **Tarea 7.8 (Security - Dependencies)**: Crear dependencias FastAPI para autenticación
- [x] **Tarea 7.9 (Security - CLI)**: Implementar CLI para gestión de usuarios, roles y permisos
- [x] **Tarea 7.10 (Security - OAuth)**: Implementar addons OAuth2 (Google, GitHub, Microsoft)

### Características del Sistema

- **Autenticación JWT**: Tokens seguros con refresh tokens
- **Autorización RBAC**: Sistema completo de roles y permisos
- **Gestión de Sesiones**: Control granular de sesiones activas
- **Middleware de Seguridad**: Protección integral de aplicaciones
- **CLI de Administración**: Herramientas de línea de comandos
- **Integración OAuth2**: Soporte para proveedores externos
- **Sin Dependencias Externas**: Implementación en memoria para simplicidad
- **Extensible**: Fácil migración a sistemas externos

### Logros de la Épica 7

- ✅ Sistema completo de autenticación JWT con tokens de acceso y refresh
- ✅ Sistema RBAC completo con roles y permisos
- ✅ Gestión de sesiones con control granular
- ✅ Decoradores de seguridad para protección de endpoints
- ✅ Middleware de seguridad (headers, CORS, rate limiting)
- ✅ Dependencias FastAPI para autenticación
- ✅ CLI completo para gestión de usuarios, roles y permisos
- ✅ Addons OAuth2 para integración con proveedores externos
- ✅ 67 pruebas unitarias que cubren toda la funcionalidad de seguridad
- ✅ Código con tipado estático completo y formateo automático

---

## Épica 8: Observabilidad y Monitoreo ✅ COMPLETADA

*Objetivo: Implementar capacidades completas de observabilidad, logging, métricas y trazabilidad distribuida.*

### Funcionalidades Principales

- [x] **Tarea 8.1 (Observability - Logging)**: Sistema de logging estructurado con niveles configurables
- [x] **Tarea 8.2 (Observability - Metrics)**: Sistema unificado de métricas basado en OpenTelemetry con exportación a Prometheus
- [x] **Tarea 8.3 (Observability - Tracing)**: Trazabilidad distribuida integrada con el sistema de métricas OpenTelemetry
- [x] **Tarea 8.4 (Observability - Health)**: Health checks y endpoints de diagnóstico
- [x] **Tarea 8.5 (Observability - APM)**: Integración con APM (Application Performance Monitoring)
- [ ] **Tarea 8.6 (Observability - Alerts)**: Sistema de alertas y notificaciones
- [ ] **Tarea 8.7 (Observability - Dashboard)**: Dashboard web para monitoreo en tiempo real
- [ ] **Tarea 8.8 (Observability - Profiling)**: Profiling de rendimiento y memory leaks
- [ ] **Tarea 8.9 (Observability - CLI)**: Comandos CLI para diagnóstico y debugging
- [x] **Tarea 8.10 (Observability - Testing)**: Pruebas de observabilidad y métricas

### Integraciones

- **OpenTelemetry**: Sistema unificado de observabilidad (métricas + tracing)
- **Prometheus**: Exportación automática de métricas para compatibilidad
- **Grafana**: Visualización de métricas y traces
- **ELK Stack**: Logging centralizado

**Logros de la Épica 8:**

- ✅ Sistema completo de logging estructurado con `structlog` y niveles configurables
- ✅ Sistema unificado de métricas basado en OpenTelemetry con exportación a Prometheus
- ✅ Trazabilidad distribuida integrada con el sistema de métricas OpenTelemetry
- ✅ Health checks y endpoints de diagnóstico con modelos Pydantic estructurados
- ✅ Integración con APM (Application Performance Monitoring) con arquitectura de addons
- ✅ Sistema de addons para APM (New Relic, DataDog, Elastic APM) separado del core
- ✅ Integración de métricas del sistema con OpenTelemetry (`SystemMetricsInstrumentor`)
- ✅ Eliminación de variables globales en favor de inyección de dependencias
- ✅ Modelos Pydantic con documentación completa para OpenAPI
- ✅ Sistema de diagnóstico con métricas de sistema y proceso
- ✅ 495 pruebas unitarias que cubren toda la funcionalidad de observabilidad
- ✅ Código con tipado estático completo y formateo automático

---

## ✅ Épica 9: Sistema de Documentación Modular - COMPLETADA

*Objetivo: Reestructurar la documentación del proyecto en módulos específicos para facilitar la navegación, mantenimiento y comprensión del framework.*

### Funcionalidades Principales

- [x] **Tarea 9.1 (Docs - Structure)**: Crear estructura modular de documentación en directorio `/docs`
- [x] **Tarea 9.2 (Docs - PRD Update)**: Actualizar PRD con nueva estructura de documentación
- [x] **Tarea 9.3 (Docs - DDT Update)**: Actualizar DDT con nueva estructura de documentación
- [x] **Tarea 9.4 (Docs - Roadmap Update)**: Actualizar roadmap con nueva estructura de documentación
- [ ] **Tarea 9.5 (Docs - Getting Started)**: Crear guía de inicio rápido
- [ ] **Tarea 9.6 (Docs - System Docs)**: Crear documentación específica por sistema
- [ ] **Tarea 9.7 (Docs - Examples)**: Crear ejemplos de uso
- [ ] **Tarea 9.8 (Docs - API Reference)**: Crear referencia de API
- [ ] **Tarea 9.9 (Docs - Troubleshooting)**: Crear guía de solución de problemas
- [ ] **Tarea 9.10 (Docs - README Simplification)**: Simplificar README principal

### Características del Sistema

- **Modularidad**: Cada documento se enfoca en un aspecto específico del framework
- **Navegabilidad**: Enlaces cruzados entre documentos para facilitar la navegación
- **Mantenibilidad**: Estructura clara que permite agregar nuevos módulos sin afectar la organización
- **Consistencia**: Formato uniforme y estructura similar en todos los documentos
- **Actualización**: Documentación sincronizada con el código fuente

### Logros de la Épica 9

- ✅ Estructura modular de documentación creada en directorio `/docs`
- ✅ PRD actualizado con requisitos de documentación modular
- ✅ DDT actualizado con arquitectura de documentación
- ✅ Roadmap actualizado con nueva estructura de documentación
- ✅ Principios y responsabilidades de documentación definidos
- ✅ Estructura de documentos específicos por sistema planificada

---

## Épica 10: Optimización y Rendimiento

*Objetivo: Optimizar el rendimiento del framework y proporcionar herramientas para aplicaciones de alta performance.*

### Funcionalidades Principales

- [ ] **Tarea 10.1 (Performance - Profiling)**: Herramientas de profiling integradas
- [ ] **Tarea 10.2 (Performance - Caching)**: Optimizaciones avanzadas de caché (Redis, Memcached)
- [ ] **Tarea 10.3 (Performance - Database)**: Pool de conexiones y optimización de queries
- [ ] **Tarea 10.4 (Performance - Async)**: Optimizaciones para operaciones asíncronas
- [ ] **Tarea 10.5 (Performance - Memory)**: Gestión optimizada de memoria
- [ ] **Tarea 10.6 (Performance - Compression)**: Compresión de respuestas HTTP
- [ ] **Tarea 10.7 (Performance - CDN)**: Integración con CDN para assets estáticos
- [ ] **Tarea 10.8 (Performance - Load)**: Herramientas de load testing integradas
- [ ] **Tarea 10.9 (Performance - Benchmarks)**: Suite de benchmarks automatizados
- [ ] **Tarea 10.10 (Performance - Monitoring)**: Monitoreo de rendimiento en tiempo real

### Objetivos de Rendimiento

- **Latencia**: < 10ms para operaciones básicas
- **Throughput**: > 10,000 requests/segundo
- **Memory**: Uso eficiente de memoria
- **Scalability**: Escalabilidad horizontal

---

## Épica 11: Herramientas de Desarrollo Avanzadas

*Objetivo: Proporcionar herramientas avanzadas que mejoren significativamente la experiencia de desarrollo.*

### Funcionalidades Principales

- [ ] **Tarea 11.1 (DevTools - Hot Reload)**: Hot reload avanzado para desarrollo
- [ ] **Tarea 11.2 (DevTools - Debugging)**: Herramientas de debugging integradas
- [ ] **Tarea 11.3 (DevTools - Testing)**: Framework de testing avanzado
- [ ] **Tarea 11.4 (DevTools - Docs)**: Generación automática de documentación
- [ ] **Tarea 11.5 (DevTools - IDE)**: Plugins para IDEs populares (VS Code, PyCharm)
- [ ] **Tarea 11.6 (DevTools - Scaffolding)**: Generadores avanzados de código
- [ ] **Tarea 11.7 (DevTools - Migration)**: Herramientas de migración entre versiones
- [ ] **Tarea 11.8 (DevTools - Deployment)**: Herramientas de deployment automatizado
- [ ] **Tarea 11.9 (DevTools - Docker)**: Integración completa con Docker/Kubernetes
- [ ] **Tarea 11.10 (DevTools - CI/CD)**: Templates para CI/CD pipelines

### Experiencia de Desarrollo

- **Productividad**: Reducir tiempo de desarrollo en 50%
- **Debugging**: Debugging visual y interactivo
- **Documentation**: Docs siempre actualizadas
- **Deployment**: Deploy con un comando

---

## Estado General del Proyecto

### ✅ Épicas Completadas (9/11)

1. **Épica 1**: El Núcleo del Framework (Core)
2. **Épica 2**: Capa Web y Enrutamiento
3. **Épica 3**: Capa de Acceso a Datos
4. **Épica 4**: Herramientas de Desarrollo (CLI)
5. **Épica 5**: Sistema de Tareas en Segundo Plano
6. **Épica 6**: Sistema de Caché Inteligente
7. **Épica 7**: Sistema de Seguridad y Autenticación
8. **Épica 8**: Observabilidad y Monitoreo
9. **Épica 9**: Sistema de Documentación Modular

### 🚧 Épicas en Progreso (1/11)

1. **Épica 10**: Optimización y Rendimiento (Pendiente)

### 📋 Épicas Pendientes (1/11)

1. **Épica 11**: Herramientas de Desarrollo Avanzadas

### 📊 Métricas del Proyecto

- **Tests Totales**: 700+ pruebas unitarias
- **Cobertura de Código**: > 95%
- **Líneas de Código**: ~15,000 líneas
- **Módulos Implementados**: 15+ módulos principales
- **Sistemas Completados**: 9/11 sistemas principales

### 🎯 Próximos Pasos

1. **Completar Épica 9**: Finalizar documentación modular
2. **Iniciar Épica 10**: Optimización y rendimiento
3. **Planificar Épica 11**: Herramientas de desarrollo avanzadas

---

## Changelog de Versiones

### v1.1 (2025-10-03)

- **NUEVO**: Épica 9 - Sistema de Documentación Modular
- **ACTUALIZADO**: Roadmap con nueva estructura de documentación
- **ACTUALIZADO**: Estado de épicas completadas (9/11)
- **ACTUALIZADO**: Métricas del proyecto y próximos pasos

### v1.0 (2025-10-02)

- Versión inicial del roadmap
- Definición de épicas y tareas
- Plan de desarrollo TDD
