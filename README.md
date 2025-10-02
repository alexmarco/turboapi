# TurboAPI

Un framework web moderno para Python inspirado en FastAPI y Django.

## Desarrollo

### Configuración del entorno

```bash
# Instalar dependencias
uv sync

# Instalar dependencias de desarrollo
uv sync --group dev
```

### Comandos de calidad de código

Toda la configuración está centralizada en `pyproject.toml`. Ejecuta estos comandos en orden:

```bash
# 1. Linting con fixes automáticos
uv run ruff check . --fix

# 2. Formateo de código
uv run ruff format .

# 3. Verificación de tipos (solo src/, excluye tests/)
uv run mypy .

# 4. Ejecutar pruebas
uv run pytest
```

**Flujo completo:**

```bash
# Bash/Linux/macOS
uv run ruff check . --fix && uv run ruff format . && uv run mypy . && uv run pytest

# PowerShell/Windows
uv run ruff check . --fix; uv run ruff format .; uv run mypy .; uv run pytest
```

**Nota:** Usa directamente `uv run pytest` en lugar de `framework test` para mayor flexibilidad.

### Configuración del IDE

**Archivos de configuración:**

- `pyproject.toml` - Configuración de Ruff, Mypy y Pytest
- `pyrightconfig.json` - Configuración de Pyright (análisis de tipos en IDE)
- `.vscode/settings.json` - Configuración mínima del workspace

**Análisis de tipos:**

- **Pyright** (integrado en Cursor) lee automáticamente `pyrightconfig.json`
- Excluye la carpeta `tests/` automáticamente
- Analiza solo el código fuente en `src/`

**Linting:**

- **Ruff** configurado en `pyproject.toml`
- Ejecuta `uv run ruff check . --fix` para correcciones automáticas

### CLI del Framework

```bash
# Crear un nuevo proyecto
uv run framework new mi_proyecto

# Crear una nueva aplicación
uv run framework new-app mi_app

# Ejecutar servidor de desarrollo
uv run framework run --reload

# Ejecutar servidor con configuración personalizada
uv run framework run --host 0.0.0.0 --port 9000 --app main:app

# Gestionar tareas en segundo plano
uv run framework task list                    # Listar tareas disponibles
uv run framework task run --name mi_tarea    # Ejecutar una tarea
uv run framework task status                 # Ver estado de tareas

# Gestionar sistema de caché
uv run framework cache list                  # Listar funciones cacheables
uv run framework cache clear                 # Limpiar todo el caché
uv run framework cache clear --key mi_clave  # Limpiar clave específica
uv run framework cache stats                 # Ver estadísticas del caché

# 🚀 El sistema de caché soporta tanto funciones síncronas como asíncronas
# Usa @Cache, @AsyncCache o @SmartCache según tus necesidades

# Ver ayuda
uv run framework --help
```

### Estructura del proyecto

- `src/turboapi/` - Código fuente del framework
- `tests/` - Pruebas unitarias
- `docs/` - Documentación

## Características

- ✅ Inyección de dependencias
- ✅ Configuración basada en `pyproject.toml`
- ✅ Descubrimiento automático de componentes
- ✅ Decoradores para controladores y endpoints
- ✅ Capa de acceso a datos con SQLAlchemy
- ✅ Migraciones con Alembic
- ✅ Sistema de tareas en segundo plano
- ✅ Sistema de caché avanzado (síncrono y asíncrono)
- ✅ CLI para generación de proyectos y aplicaciones
