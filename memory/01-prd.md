---
Version: 1.0
Date: 2025-10-02
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

* REQ 3.1 - Ejecutor de Tareas en Segundo Plano: El sistema debe incluir un módulo para ejecutar tareas asíncronas sin requerir dependencias externas complejas.

* REQ 3.2 - Sistema de Caché: Se debe ofrecer un sistema de caché con soporte para funciones síncronas y asíncronas, configurable mediante decoradores.

### 3.4. REQ4: Seguridad

* REQ 4.1 - Autenticación y Autorización: El framework debe incluir módulos para autenticación (JWT, OAuth2) y un sistema de Control de Acceso Basado en Roles (RBAC).

* REQ 4.2 - Seguridad por Defecto: Se deben habilitar por defecto headers de seguridad, políticas CORS y protección contra ataques comunes.

### 3.5. REQ 2: Observabilidad

* REQ 5.1 - Logging y Métricas: El sistema debe generar logs estructurados y exponer métricas compatibles con Prometheus de forma automática.

* REQ 5.2 - Trazabilidad: Debe integrarse con OpenTelemetry para permitir la trazabilidad distribuida en arquitecturas de microservicios.

* REQ 5.3 - Health Checks: Debe proporcionar un endpoint de health check para monitorear el estado de la aplicación.

### 3.6. REQ 3: Experiencia de Desarrollador (DX)

* REQ 6.1 - Hot Reload: El servidor de desarrollo debe reiniciarse automáticamente al detectar cambios en el código.

* REQ 6.2 - Generación de Documentación: El framework debe ser capaz de generar documentación de API de forma automática a partir del código.

* REQ 6.3 - Integración con Ecosistema: Se deben facilitar plantillas y guías para la integración con Docker, Kubernetes y sistemas de CI/CD.

## 4. Casos de Uso Clave

### Caso de Uso 1: Creación de un CRUD API en minutos

* Usuario: Un desarrollador.

* Acción: Utiliza el CLI para crear un nuevo proyecto y una nueva "app".

* Resultado: En pocos minutos, define un modelo con SQLModel, un @Controller y un @Service. El framework gestiona automáticamente las rutas, la conexión a la base de datos y la inyección de dependencias, exponiendo una API RESTful funcional.

### Caso de Uso 2: Añadir una tarea en segundo plano

* Usuario: Un desarrollador necesita procesar una tarea pesada sin bloquear la respuesta de la API.

* Acción: Define una función y la decora como una tarea asíncrona usando el starter correspondiente.

* Resultado: La tarea se ejecuta en segundo plano de manera fiable, sin necesidad de configurar un sistema de colas complejo como Celery o RQ.

## 5. Restricciones y Asunciones

Restricción 1: La primera versión del framework se centrará exclusivamente en el ecosistema asíncrono de Python (ASGI).

Restricción 2: Las implementaciones por defecto de caché y tareas en segundo plano serán soluciones "en memoria" para simplificar el arranque, recomendando soluciones externas para producción.

Asunción 1: Los desarrolladores que adopten el framework están dispuestos a seguir la arquitectura modular propuesta.

Asunción 2: El framework no buscará reemplazar a Django o FastAPI, sino ocupar un nicho intermedio enfocado en la DX y la arquitectura estructurada.
