# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [No Liberado]

### Añadido

- Sistema completo de observabilidad con OpenTelemetry
- Logging estructurado con `structlog` y configuración avanzada
- Sistema de métricas unificado con OpenTelemetry y exportación a Prometheus
- Trazado distribuido integrado con OpenTelemetry
- Health checks y endpoints de diagnóstico con modelos Pydantic documentados
- Integración de métricas del sistema con `SystemMetricsInstrumentor`
- Arquitectura de addons para APM (New Relic, DataDog, Elastic APM)
- Sistema de addons con carga dinámica y configuración unificada
- Patrón Starter para configuración automática de componentes
- Modelos Pydantic con documentación completa para OpenAPI
- Endpoints de diagnóstico con métricas del sistema y proceso
- Sistema de seguridad completo con JWT, middleware y decoradores
- FastAPI middleware para CORS, rate limiting y seguridad
- Dependencias de FastAPI para autenticación y autorización
- Decoradores de seguridad para protección de endpoints
- Sistema de gestión de tokens JWT con refresh tokens
- Interfaces de seguridad y estructuras de datos
- Sistema de caché asíncrono con contexto de caché
- Framework TurboAPI con arquitectura modular
- Sistema de migraciones de base de datos con Alembic
- Configuración de proyecto con `pyproject.toml` y `uv`
- Quality gates obligatorios con Ruff, MyPy y pytest
- Documentación técnica completa (DDT) y roadmap de desarrollo
- Reglas de trabajo con Git y Python
- 495 tests unitarios con cobertura completa

### Cambiado

- Refactorización de variables globales a inyección de dependencias
- Actualización de tipos de Python a sintaxis moderna (`X | None` en lugar de `Optional[X]`)
- Reorganización de la arquitectura de observabilidad
- Separación de APM providers del core a addons
- Mejora de la documentación de modelos Pydantic para OpenAPI
- Actualización de reglas de calidad de código
- Alineación de documentación técnica con PRD

### Corregido

- Errores de MyPy en todo el código base
- Errores de Ruff (formateo y linting)
- Problemas de tipado estático
- Incompatibilidades de tipos en FastAPI
- Errores de importación y dependencias
- Problemas de configuración de bcrypt
- Conflictos de instrumentación de OpenTelemetry

### Eliminado

- Variables globales en módulos de observabilidad
- Dependencias directas de APM providers en el core
- Tipos obsoletos de Python (`Optional`, `Union`, `List`, `Dict`, etc.)
- Archivos de configuración duplicados
- Código legacy y no utilizado

## [1.0.0] - 2024-01-XX

### Añadido

- Framework TurboAPI inicial
- Sistema de caché asíncrono
- Arquitectura base del proyecto
- Configuración inicial de desarrollo

---

*Este changelog se genera automáticamente basado en los commits del proyecto siguiendo la convención de commits convencionales.*
