---
Version: 1.1
Date: 2025-10-03
Autor: Alejandro Marco Ramos
---

# PRD: Framework Python Orientado a la DX

## 1. Introducción y Visión del Producto

### 1.1 Problema

Los desarrolladores de Python a menudo enfrentan una configuración compleja y una falta de estandarización al iniciar nuevos proyectos, lo que resulta en una curva de aprendizaje elevada y en una Experiencia de Desarrollador (DX) deficiente. Esto se traduce en un aumento del código repetitivo (boilerplate) y en dificultades para mantener una arquitectura modular y escalable.

### 1.2. Visión del Producto

Crear un framework de desarrollo en Python, inspirado en los principios de Spring Boot y Django, que priorice la Experiencia de Desarrollador (DX). El objetivo es ofrecer una herramienta "opinada" que simplifique la configuración, promueva las buenas prácticas de arquitectura y maximice la productividad desde el primer día.

## 2. Principios Fundamentales

* Convención sobre Configuración: El framework minimizará la necesidad de configuración manual, proporcionando valores predeterminados sensatos para que el desarrollador pueda enfocarse en la lógica de negocio.

* Modularidad Impuesta: Se guiará al desarrollador hacia una arquitectura basada en módulos autocontenidos ("apps") para fomentar la escalabilidad y la organización del código.

* Descubrimiento Automático: El sistema escaneará y registrará componentes clave de forma automática, reduciendo la configuración explícita.

* Abstracción y Extensibilidad: El framework se construirá sobre interfaces claras, permitiendo a los usuarios extender o reemplazar las implementaciones por defecto según sus necesidades.

## 3. Requisitos

### 3.1. REQ1: Núcleo del Framework y Gestión de Proyectos

* REQ 1.1 - CLI de Proyecto: El sistema debe proveer una herramienta de línea de comandos (CLI) para gestionar el ciclo de vida completo del proyecto:
  * Crear un nuevo proyecto (`framework new <nombre>`).
  * Crear una nueva aplicación modular dentro de un proyecto (`framework new-app <nombre>`).
  * Ejecutar el servidor de desarrollo (`framework run`).

* REQ 1.2 - Configuración Centralizada: El framework deberá cargar la configuración del proyecto desde un único fichero application.yaml o .env.

* REQ 1.3 - Contenedor de Inyección de Dependencias (DI): El sistema debe gestionar un contenedor de DI global que inyecte automáticamente las dependencias declaradas en los componentes de las installed_apps.

### 3.2. REQ2: Capa de Acceso a Datos

* REQ 2.1 - ORM por Defecto: Se debe integrar SQLModel como ORM predeterminado, permitiendo el uso de SQLAlchemy puro para casos avanzados.

* REQ 2.2 - Sistema de Migraciones: El CLI debe integrar Alembic para gestionar las migraciones de la base de datos, descubriendo automáticamente los modelos de todas las installed_apps.

* REQ 2.3 - Patrón Repositorio: Se debe proporcionar una interfaz BaseRepository que estandarice el acceso a los datos.

### 3.3. REQ3: Módulos Centrales (Starters)

* REQ 3.1 - Starter Web: Módulo que integre FastAPI y proporcione decoradores para controladores REST.

* REQ 3.2 - Starter de Datos: Módulo que configure SQLAlchemy, Alembic y el patrón repositorio.

* REQ 3.3 - Starter de Tareas: Módulo para ejecutar tareas en segundo plano de forma asíncrona.

* REQ 3.4 - Starter de Caché: Módulo que proporcione un sistema de caché configurable (memoria, Redis).

### 3.4. REQ4: Sistema de Seguridad y Autenticación

* REQ 4.1 - Autenticación JWT: Sistema completo de autenticación con tokens JWT y refresh tokens.

* REQ 4.2 - Autorización RBAC: Sistema de roles y permisos (Role-Based Access Control).

* REQ 4.3 - Middleware de Seguridad: Headers de seguridad, CORS, rate limiting.

* REQ 4.4 - Integración OAuth2: Soporte para proveedores OAuth2 (Google, GitHub, etc.).

### 3.5. REQ5: Sistema de Observabilidad

* REQ 5.1 - Logging Estructurado: Sistema de logging con niveles configurables y formato estructurado.

* REQ 5.2 - Métricas: Sistema unificado de métricas con exportación a Prometheus.

* REQ 5.3 - Trazabilidad: Trazabilidad distribuida integrada.

* REQ 5.4 - Health Checks: Endpoints de diagnóstico y health checks.

### 3.6. REQ6: Sistema de Documentación

* REQ 6.1 - Documentación Modular: El framework debe proporcionar documentación organizada en módulos específicos para facilitar la comprensión y mantenimiento.

* REQ 6.2 - Estructura de Documentación: La documentación debe estar organizada en:
  * Documento principal (README.md) con información general y enlaces
  * Documentos específicos por módulo en directorio `/docs`
  * Documentación técnica detallada (DDT)
  * Roadmap de desarrollo actualizado
  * Guías de usuario y ejemplos de uso

* REQ 6.3 - Mantenibilidad: La documentación debe ser fácil de mantener y actualizar, con estructura clara que permita agregar nuevos módulos sin afectar la organización general.

## 4. Arquitectura del Sistema

### 4.1. Componentes Principales

* **Core Framework**: Motor de inyección de dependencias, configuración y descubrimiento de componentes.
* **Web Layer**: Integración con FastAPI, decoradores y enrutamiento.
* **Data Layer**: ORM, migraciones y patrón repositorio.
* **Security Layer**: Autenticación, autorización y middleware de seguridad.
* **Observability Layer**: Logging, métricas, tracing y health checks.
* **CLI Tools**: Herramientas de línea de comandos para gestión del proyecto.

### 4.2. Patrones Arquitectónicos

* **Dependency Injection**: Contenedor DI para gestión de dependencias.
* **Component Discovery**: Escaneo automático de componentes en aplicaciones.
* **Repository Pattern**: Abstracción del acceso a datos.
* **Starter Pattern**: Módulos configurables para funcionalidades específicas.

## 5. Criterios de Éxito

### 5.1. Métricas Técnicas

* Tiempo de setup de proyecto: < 5 minutos
* Cobertura de tests: > 90%
* Tiempo de build: < 30 segundos
* Latencia de API: < 100ms para operaciones básicas

### 5.2. Métricas de Experiencia de Desarrollador

* Curva de aprendizaje: < 2 horas para primer proyecto funcional
* Reducción de boilerplate: > 70% comparado con FastAPI puro
* Satisfacción del desarrollador: > 4.5/5 en encuestas

## 6. Restricciones y Limitaciones

* Compatibilidad: Python 3.11+
* Dependencias: Minimizar dependencias externas
* Performance: No degradar rendimiento vs FastAPI puro
* Compatibilidad: Mantener compatibilidad con ecosistema Python existente

## 7. Roadmap de Implementación

### Fase 1: Núcleo (Completada)

- Sistema de DI y configuración
* CLI básico
* Descubrimiento de componentes

### Fase 2: Capas Fundamentales (Completada)

- Capa web con FastAPI
* Capa de datos con SQLAlchemy
* Sistema de caché
* Sistema de tareas

### Fase 3: Seguridad y Observabilidad (Completada)

- Autenticación JWT
* Sistema RBAC
* Logging, métricas y tracing
* Health checks

### Fase 4: Documentación y Optimización (En progreso)

- Reestructuración de documentación
* Optimizaciones de rendimiento
* Herramientas de desarrollo avanzadas

### Fase 5: Ecosistema (Futuro)

- Addons y plugins
* Integraciones con servicios cloud
* Herramientas de deployment

---

## Changelog de Versiones

### v1.1 (2025-10-03)

- **NUEVO**: Requisito REQ6 para sistema de documentación modular
* **ACTUALIZADO**: Estructura de documentación en directorio `/docs`
* **ACTUALIZADO**: Roadmap de implementación con fases completadas

### v1.0 (2025-10-02)

- Versión inicial del PRD
* Definición de requisitos fundamentales
* Arquitectura base del sistema
