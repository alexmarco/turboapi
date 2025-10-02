"""Generador de proyectos TurboAPI."""

from pathlib import Path

import typer


class ProjectGenerator:
    """Generador de proyectos TurboAPI."""

    def __init__(self) -> None:
        """Inicializa el generador."""
        self.templates_dir = Path(__file__).parent / "project_templates"

    def create_project(
        self, project_name: str, template: str = "basic", target_dir: Path | None = None
    ) -> None:
        """
        Crea un nuevo proyecto TurboAPI.

        Args:
            project_name: Nombre del proyecto
            template: Plantilla a usar
            target_dir: Directorio donde crear el proyecto
        """
        if target_dir is None:
            target_dir = Path.cwd() / project_name

        # Verificar que el directorio no existe
        if target_dir.exists():
            raise typer.BadParameter(f"El directorio '{target_dir}' ya existe")

        # Crear el directorio del proyecto
        target_dir.mkdir(parents=True, exist_ok=True)

        # Generar la estructura del proyecto
        self._generate_project_structure(target_dir, project_name, template)

        typer.echo(f"[OK] Proyecto '{project_name}' creado exitosamente en '{target_dir}'")

    def _generate_project_structure(
        self, target_dir: Path, project_name: str, template: str
    ) -> None:
        """
        Genera la estructura del proyecto.

        Args:
            target_dir: Directorio del proyecto
            project_name: Nombre del proyecto
            template: Plantilla a usar
        """
        # Crear directorios principales
        (target_dir / "apps").mkdir()
        (target_dir / "tests").mkdir()
        (target_dir / "docs").mkdir()

        # Generar archivos según la plantilla
        if template == "basic":
            self._generate_basic_template(target_dir, project_name)
        elif template == "advanced":
            self._generate_advanced_template(target_dir, project_name)
        else:
            raise typer.BadParameter(f"Plantilla '{template}' no reconocida")

    def _generate_basic_template(self, target_dir: Path, project_name: str) -> None:
        """
        Genera la plantilla básica.

        Args:
            target_dir: Directorio del proyecto
            project_name: Nombre del proyecto
        """
        # pyproject.toml
        pyproject_content = f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "Proyecto TurboAPI"
dependencies = [
    "turboapi",
    "uvicorn",
]

[tool.turboapi]
installed_apps = [
    # Agregar aquí las aplicaciones del proyecto
]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "C4", "SIM"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
"""

        with open(target_dir / "pyproject.toml", "w", encoding="utf-8") as f:
            f.write(pyproject_content)

        # README.md
        readme_content = f"""# {project_name}

Proyecto TurboAPI.

## Instalación

```bash
uv sync
```

## Ejecución

```bash
framework run
```

## Estructura del Proyecto

- `apps/`: Aplicaciones del proyecto
- `tests/`: Pruebas
- `docs/`: Documentación
"""

        with open(target_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)

        # main.py
        main_content = '''"""Punto de entrada de la aplicación."""

from turboapi import TurboAPI

app = TurboAPI()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
'''

        with open(target_dir / "main.py", "w", encoding="utf-8") as f:
            f.write(main_content)

        # .gitignore
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# TurboAPI
migrations/
alembic.ini
"""

        with open(target_dir / ".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore_content)

    def _generate_advanced_template(self, target_dir: Path, project_name: str) -> None:
        """
        Genera la plantilla avanzada.

        Args:
            target_dir: Directorio del proyecto
            project_name: Nombre del proyecto
        """
        # Generar plantilla básica primero
        self._generate_basic_template(target_dir, project_name)

        # Agregar archivos adicionales para plantilla avanzada
        (target_dir / "config").mkdir()
        (target_dir / "scripts").mkdir()

        # config/settings.py
        settings_content = '''"""Configuración de la aplicación."""

from turboapi.core.config import TurboConfig

config = TurboConfig()
'''

        with open(target_dir / "config" / "settings.py", "w", encoding="utf-8") as f:
            f.write(settings_content)

        # config/__init__.py
        with open(target_dir / "config" / "__init__.py", "w", encoding="utf-8") as f:
            f.write('"""Módulo de configuración."""\n')

        # scripts/start.py
        start_content = '''"""Script de inicio."""

import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
'''

        with open(target_dir / "scripts" / "start.py", "w", encoding="utf-8") as f:
            f.write(start_content)

        # scripts/__init__.py
        with open(target_dir / "scripts" / "__init__.py", "w", encoding="utf-8") as f:
            f.write('"""Scripts del proyecto."""\n')
