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
- ✅ **Tarea 5.6 (Tasks - CLI)**: Crear comando `framework task` para gestionar tareas (listar, ejecutar, estado).

### Logros de la Épica 5

- **Sistema completo de tareas en segundo plano** sin dependencias externas
- **Interfaz `BaseTaskQueue`** con implementación `InMemoryTaskQueue` funcional
- **Decorador `@Task`** para marcar funciones como tareas ejecutables con metadatos
- **TaskStarter** que configura e integra el sistema de tareas con DI
- **Descubrimiento automático** de tareas en aplicaciones instaladas
- **Comando CLI `framework task`** con acciones: list, run, status
- **Cola FIFO** con estados de tarea (pending, running, completed, failed)
- **Ejecución inmediata** de tareas con manejo de errores y resultados
- **32 pruebas unitarias** que cubren toda la funcionalidad del sistema de tareas

## ✅ Épica 6: Sistema de Caché (Cache System) - COMPLETADA

*Objetivo: Construir un sistema de caché flexible que permita almacenar y recuperar datos de forma eficiente sin dependencias externas.*

- ✅ **Tarea 6.1 (Cache - Interface)**: Definir la interfaz `BaseCache` en `src/turboapi/interfaces.py`.
- ✅ **Tarea 6.2 (Cache - Implementation)**: Implementar `InMemoryCache` como implementación básica sin dependencias externas.
- ✅ **Tarea 6.3 (Cache - Decorator)**: Crear el decorador `@Cache` para funciones con caché automático.
- ✅ **Tarea 6.4 (Cache - Starter)**: Implementar `CacheStarter` para configurar el sistema de caché y registrar componentes en DI.
- ✅ **Tarea 6.5 (Cache - Discovery)**: Integrar descubrimiento de funciones cacheables en `ComponentScanner`.
- ✅ **Tarea 6.6 (Cache - CLI)**: Crear comando `framework cache` para gestionar caché (clear, stats, list).

### Logros de la Épica 6

- **Sistema completo de caché en memoria** sin dependencias externas
- **Interfaz `BaseCache`** con implementación `InMemoryCache` funcional
- **Decorador `@Cache`** para funciones con caché automático y TTL configurable
- **CacheStarter** que configura e integra el sistema de caché con DI
- **Descubrimiento automático** de funciones cacheables en aplicaciones instaladas
- **Comando CLI `framework cache`** con acciones: list, clear, stats
- **Normalización de argumentos** para claves de caché consistentes
- **Estadísticas de rendimiento** (hits, misses, hit rate)
- **Soporte para TTL** y expiración automática de entradas
- **Gestión de valores None** y diferentes tipos de datos
- **40 pruebas unitarias** que cubren toda la funcionalidad del sistema de caché

## ✅ Épica 6.1: Sistema de Caché Asíncrono (Async Cache System) - COMPLETADA

*Objetivo: Extender el sistema de caché para soportar funciones asíncronas y operaciones de caché no bloqueantes.*

- [x] **Tarea 6.1.1 (AsyncCache - Interface)**: Extender `BaseCache` con métodos asíncronos (`async get`, `async set`, etc.).
- [x] **Tarea 6.1.2 (AsyncCache - Implementation)**: Implementar `AsyncInMemoryCache` con operaciones no bloqueantes.
- [x] **Tarea 6.1.3 (AsyncCache - Decorator)**: Crear decorador `@AsyncCache` para funciones `async def`.
- [x] **Tarea 6.1.4 (AsyncCache - Integration)**: Integrar con contextos asyncio y loops de eventos.
- [x] **Tarea 6.1.5 (AsyncCache - Hybrid)**: Crear decorador híbrido que detecte automáticamente sync/async.
- [x] **Tarea 6.1.6 (AsyncCache - Testing)**: Pruebas completas con `pytest-asyncio`.
- [x] **Tarea 6.1.7 (AsyncCache - Documentation)**: Actualizar toda la documentación para reflejar que el soporte async está implementado.

### Logros de la Épica 6.1

**🎯 Funcionalidades Implementadas:**

- ✅ **AsyncBaseCache Interface**: API completa para caché asíncrono
- ✅ **AsyncInMemoryCache**: Implementación thread-safe con `asyncio.Lock`
- ✅ **@AsyncCache Decorator**: Caché automático para funciones `async def`
- ✅ **@SmartCache Decorator**: Detección automática sync/async
- ✅ **AsyncCacheContext**: Context managers para gestión avanzada
- ✅ **Integración asyncio**: Soporte completo para gather, tasks, semáforos
- ✅ **Refactorización**: `BaseCacheDecorator` elimina duplicación de código
- ✅ **Concurrent Operations**: Prevención de ejecuciones duplicadas
- ✅ **Testing Completo**: 80+ pruebas con `pytest-asyncio`

**🔧 Mejoras Arquitectónicas:**

- ✅ **Separación Sync/Async**: Arquitecturas completamente independientes
- ✅ **Eliminación de Limitaciones**: Soporte completo para funciones asíncronas
- ✅ **Documentación Actualizada**: README, diseño técnico y roadmap actualizados

### Consideraciones Técnicas

- **Compatibilidad**: Mantener compatibilidad con el sistema de caché síncrono existente
- **Detección automática**: El decorador debe detectar si la función es sync o async
- **Contexto asyncio**: Integración correcta con loops de eventos
- **Rendimiento**: Las operaciones async no deben bloquear el hilo principal

---
*Las épicas para Seguridad y Observabilidad se detallarán una vez que el núcleo esté maduro.*
