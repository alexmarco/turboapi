"""Generador de aplicaciones TurboAPI."""

from pathlib import Path

import typer


class AppGenerator:
    """Generador de aplicaciones TurboAPI."""

    def __init__(self) -> None:
        """Inicializa el generador."""
        self.templates_dir = Path(__file__).parent / "app_templates"

    def create_app(self, app_name: str, target_dir: Path | None = None) -> None:
        """
        Crea una nueva aplicación TurboAPI.

        Args:
            app_name: Nombre de la aplicación
            target_dir: Directorio donde crear la aplicación
        """
        if target_dir is None:
            target_dir = Path.cwd() / "apps" / app_name
        else:
            target_dir = Path(target_dir) / app_name

        # Verificar que el directorio no existe
        if target_dir.exists():
            raise typer.BadParameter(f"El directorio '{target_dir}' ya existe")

        # Crear el directorio de la aplicación
        target_dir.mkdir(parents=True, exist_ok=True)

        # Generar la estructura de la aplicación
        self._generate_app_structure(target_dir, app_name)

        typer.echo(f"[OK] Aplicación '{app_name}' creada exitosamente en '{target_dir}'")

    def _generate_app_structure(self, target_dir: Path, app_name: str) -> None:
        """
        Genera la estructura de la aplicación.

        Args:
            target_dir: Directorio de la aplicación
            app_name: Nombre de la aplicación
        """
        # Crear archivo __init__.py
        with open(target_dir / "__init__.py", "w", encoding="utf-8") as f:
            f.write(f'"""Aplicación {app_name}."""\n')

        # Crear archivo models.py
        models_content = f'''"""Modelos de la aplicación {app_name}."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ExampleModel(Base):
    """Modelo de ejemplo para {app_name}."""
    
    __tablename__ = "{app_name}_example"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ExampleModel(id={{self.id}}, name={{self.name}})>"
'''

        with open(target_dir / "models.py", "w", encoding="utf-8") as f:
            f.write(models_content)

        # Crear archivo repositories.py
        repositories_content = f'''"""Repositorios de la aplicación {app_name}."""

from turboapi.data.repository import SQLRepository
from .models import ExampleModel


class ExampleRepository(SQLRepository[ExampleModel]):
    """Repositorio para el modelo ExampleModel."""
    
    def __init__(self, session):
        super().__init__(session, ExampleModel)
    
    def find_by_name(self, name: str) -> ExampleModel | None:
        """Busca un modelo por nombre."""
        return self.session.query(ExampleModel).filter(ExampleModel.name == name).first()
    
    def find_active(self) -> list[ExampleModel]:
        """Busca todos los modelos activos."""
        return self.session.query(ExampleModel).filter(ExampleModel.is_active).all()
'''

        with open(target_dir / "repositories.py", "w", encoding="utf-8") as f:
            f.write(repositories_content)

        # Crear archivo controllers.py
        controllers_content = f'''"""Controladores de la aplicación {app_name}."""

from typing import Any
from turboapi.web.decorators import Controller, Get, Post, Put, Delete
from .repositories import ExampleRepository


@Controller("/{app_name}")
class ExampleController:
    """Controlador de ejemplo para {app_name}."""
    
    def __init__(self, repository: ExampleRepository) -> None:
        self.repository = repository
    
    @Get("/")
    def list_examples(self) -> dict[str, Any]:
        """Lista todos los ejemplos."""
        examples = self.repository.find_all()
        return {{
            "data": [{{"id": ex.id, "name": ex.name, "description": ex.description}} for ex in examples],
            "count": len(examples)
        }}
    
    @Get("/{{example_id}}")
    def get_example(self, example_id: int) -> dict[str, Any]:
        """Obtiene un ejemplo por ID."""
        example = self.repository.find_by_id(example_id)
        if not example:
            return {{"error": "Example not found"}}, 404
        
        return {{
            "id": example.id,
            "name": example.name,
            "description": example.description,
            "is_active": example.is_active,
            "created_at": example.created_at.isoformat(),
            "updated_at": example.updated_at.isoformat()
        }}
    
    @Post("/")
    def create_example(self, data: dict[str, Any]) -> dict[str, Any]:
        """Crea un nuevo ejemplo."""
        example = self.repository.create({{
            "name": data.get("name"),
            "description": data.get("description"),
            "is_active": data.get("is_active", True)
        }})
        
        return {{
            "id": example.id,
            "name": example.name,
            "description": example.description,
            "is_active": example.is_active
        }}, 201
    
    @Put("/{{example_id}}")
    def update_example(self, example_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Actualiza un ejemplo existente."""
        example = self.repository.find_by_id(example_id)
        if not example:
            return {{"error": "Example not found"}}, 404
        
        updated_data = {{}}
        if "name" in data:
            updated_data["name"] = data["name"]
        if "description" in data:
            updated_data["description"] = data["description"]
        if "is_active" in data:
            updated_data["is_active"] = data["is_active"]
        
        updated_example = self.repository.update(example_id, updated_data)
        
        return {{
            "id": updated_example.id,
            "name": updated_example.name,
            "description": updated_example.description,
            "is_active": updated_example.is_active
        }}
    
    @Delete("/{{example_id}}")
    def delete_example(self, example_id: int) -> dict[str, Any]:
        """Elimina un ejemplo."""
        example = self.repository.find_by_id(example_id)
        if not example:
            return {{"error": "Example not found"}}, 404
        
        self.repository.delete(example_id)
        return {{"message": "Example deleted successfully"}}
'''

        with open(target_dir / "controllers.py", "w", encoding="utf-8") as f:
            f.write(controllers_content)

        # Crear archivo services.py
        services_content = f'''"""Servicios de la aplicación {app_name}."""

from typing import Any
from .repositories import ExampleRepository


class ExampleService:
    """Servicio de ejemplo para {app_name}."""
    
    def __init__(self, repository: ExampleRepository) -> None:
        self.repository = repository
    
    def get_example_with_validation(self, example_id: int) -> dict[str, Any] | None:
        """Obtiene un ejemplo con validaciones adicionales."""
        example = self.repository.find_by_id(example_id)
        if not example:
            return None
        
        if not example.is_active:
            return None
        
        return {{
            "id": example.id,
            "name": example.name,
            "description": example.description,
            "is_active": example.is_active
        }}
    
    def create_example_with_validation(self, data: dict[str, Any]) -> dict[str, Any] | None:
        """Crea un ejemplo con validaciones."""
        if not data.get("name"):
            return None
        
        # Verificar si ya existe un ejemplo con el mismo nombre
        existing = self.repository.find_by_name(data["name"])
        if existing:
            return None
        
        example = self.repository.create(data)
        return {{
            "id": example.id,
            "name": example.name,
            "description": example.description,
            "is_active": example.is_active
        }}
'''

        with open(target_dir / "services.py", "w", encoding="utf-8") as f:
            f.write(services_content)

        # Crear directorio tests
        tests_dir = target_dir / "tests"
        tests_dir.mkdir()

        # Crear __init__.py en tests
        with open(tests_dir / "__init__.py", "w", encoding="utf-8") as f:
            f.write('"""Pruebas para la aplicación."""\n')

        # Crear test_models.py
        test_models_content = f'''"""Pruebas para los modelos de {app_name}."""

import pytest
from datetime import datetime
from ..models import ExampleModel


class TestExampleModel:
    """Pruebas para el modelo ExampleModel."""
    
    def test_model_creation(self) -> None:
        """Prueba la creación de un modelo."""
        model = ExampleModel(
            name="Test Model",
            description="Test Description",
            is_active=True
        )
        
        assert model.name == "Test Model"
        assert model.description == "Test Description"
        assert model.is_active is True
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)
    
    def test_model_repr(self) -> None:
        """Prueba la representación del modelo."""
        model = ExampleModel(id=1, name="Test Model")
        repr_str = repr(model)
        
        assert "ExampleModel" in repr_str
        assert "id=1" in repr_str
        assert "name=Test Model" in repr_str
'''

        with open(tests_dir / "test_models.py", "w", encoding="utf-8") as f:
            f.write(test_models_content)

        # Crear README.md para la aplicación
        readme_content = f"""# {app_name}

Aplicación TurboAPI generada automáticamente.

## Estructura

- `models.py`: Modelos de datos (SQLAlchemy)
- `repositories.py`: Repositorios para acceso a datos
- `controllers.py`: Controladores REST API
- `services.py`: Lógica de negocio
- `tests/`: Pruebas unitarias

## Uso

Esta aplicación incluye un ejemplo completo con:

- Modelo `ExampleModel` con campos básicos
- Repositorio `ExampleRepository` con métodos CRUD
- Controlador `ExampleController` con endpoints REST
- Servicio `ExampleService` con lógica de negocio
- Pruebas unitarias básicas

## Endpoints

- `GET /{app_name}/`: Lista todos los ejemplos
- `GET /{app_name}/{{id}}`: Obtiene un ejemplo por ID
- `POST /{app_name}/`: Crea un nuevo ejemplo
- `PUT /{app_name}/{{id}}`: Actualiza un ejemplo
- `DELETE /{app_name}/{{id}}`: Elimina un ejemplo

## Configuración

Para usar esta aplicación, agrégalo a `installed_apps` en tu `pyproject.toml`:

```toml
[tool.turboapi]
installed_apps = [
    "{app_name}",
    # ... otras aplicaciones
]
```
"""

        with open(target_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
