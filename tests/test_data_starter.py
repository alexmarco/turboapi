"""Pruebas para el starter de datos."""

import tempfile
from pathlib import Path

import pytest
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from turboapi.core.application import TurboApplication
from turboapi.core.config import TurboConfig
from turboapi.data.decorators import Repository
from turboapi.data.repository import SQLRepository
from turboapi.data.starter import DataStarter

Base = declarative_base()


def create_test_config() -> TurboConfig:
    """Crea una configuración de prueba."""
    return TurboConfig(
        project_name="test_project", project_version="1.0.0", installed_apps=["test_app"]
    )


def create_test_application() -> TurboApplication:
    """Crea una aplicación de prueba."""
    # Crear un archivo pyproject.toml temporal
    import tempfile

    pyproject_content = """[project]
name = "test_project"
version = "1.0.0"

[tool.turboapi]
installed_apps = ["tests.test_data_starter"]
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(pyproject_content)
        pyproject_path = Path(f.name)

    return TurboApplication(pyproject_path)


class StarterTestModel(Base):
    """Modelo de prueba para las pruebas del starter."""

    __tablename__ = "test_models"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)


@Repository(entity_type=StarterTestModel, id_type=int)
class StarterTestRepository(SQLRepository[StarterTestModel, int]):
    """Repositorio de prueba para las pruebas del starter."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, StarterTestModel)


class TestDataStarter:
    """Pruebas para la clase DataStarter."""

    def test_starter_initialization(self) -> None:
        """Prueba la inicialización del starter."""
        config = create_test_config()
        application = create_test_application()
        database_url = "sqlite:///:memory:"

        starter = DataStarter(application, database_url)

        assert starter.application is application
        assert starter.database_url == database_url
        assert starter.migrations_dir == "migrations"
        assert starter.database is None
        assert starter.migrator is None

    def test_starter_initialization_with_custom_migrations_dir(self) -> None:
        """Prueba la inicialización del starter con directorio de migraciones personalizado."""
        config = create_test_config()
        application = create_test_application()
        database_url = "sqlite:///:memory:"
        migrations_dir = "custom_migrations"

        starter = DataStarter(application, database_url, migrations_dir)

        assert starter.migrations_dir == migrations_dir

    def test_starter_configure(self) -> None:
        """Prueba la configuración del starter."""
        config = create_test_config()
        application = create_test_application()
        database_url = "sqlite:///:memory:"

        starter = DataStarter(application, database_url)
        starter.configure()

        assert starter.database is not None
        assert starter.migrator is not None
        assert starter.database.is_initialized()

    def test_starter_configure_registers_components(self) -> None:
        """Prueba que el starter registra los componentes en el contenedor DI."""
        config = create_test_config()
        application = create_test_application()
        database_url = "sqlite:///:memory:"

        starter = DataStarter(application, database_url)
        starter.configure()

        container = application.container

        # Verificar que TurboDatabase está registrado
        database = container.resolve("TurboDatabase")
        assert database is not None
        assert database.is_initialized()

        # Verificar que TurboMigrator está registrado
        migrator = container.resolve("TurboMigrator")
        assert migrator is not None

        # Verificar que la función de sesión está registrada
        session_gen = container.resolve("database_session")
        assert session_gen is not None

    def test_starter_configure_registers_repositories(self) -> None:
        """Prueba que el starter registra los repositorios encontrados."""
        config = create_test_config()
        application = create_test_application()
        database_url = "sqlite:///:memory:"

        starter = DataStarter(application, database_url)
        starter.configure()

        container = application.container

        # Verificar que StarterTestRepository está registrado
        repository = container.resolve("StarterTestRepository")
        assert repository is not None
        assert repository.__class__.__name__ == "StarterTestRepository"

    def test_starter_create_tables(self) -> None:
        """Prueba la creación de tablas."""
        config = create_test_config()
        application = create_test_application()
        database_url = "sqlite:///:memory:"

        starter = DataStarter(application, database_url)
        starter.configure()

        # Crear las tablas
        starter.create_tables(StarterTestModel.metadata)

        # Verificar que las tablas fueron creadas
        with starter.database.get_session() as session:
            # Intentar crear una instancia del modelo
            test_model = StarterTestModel(name="test")
            session.add(test_model)
            session.commit()

            # Verificar que se puede recuperar
            retrieved = session.query(StarterTestModel).first()
            assert retrieved is not None
            assert retrieved.name == "test"

    def test_starter_drop_tables(self) -> None:
        """Prueba la eliminación de tablas."""
        config = create_test_config()
        application = create_test_application()
        database_url = "sqlite:///:memory:"

        starter = DataStarter(application, database_url)
        starter.configure()

        # Crear las tablas y agregar datos
        starter.create_tables(StarterTestModel.metadata)

        with starter.database.get_session() as session:
            test_model = StarterTestModel(name="test")
            session.add(test_model)
            session.commit()

        # Eliminar las tablas
        starter.drop_tables(StarterTestModel.metadata)

        # Verificar que las tablas fueron eliminadas
        with starter.database.get_session() as session, pytest.raises(Exception):
            session.query(StarterTestModel).first()

    def test_starter_create_migration(self) -> None:
        """Prueba la creación de migraciones."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = create_test_config()
            application = create_test_application()
            database_url = "sqlite:///:memory:"
            migrations_dir = str(Path(temp_dir) / "migrations")

            starter = DataStarter(application, database_url, migrations_dir)
            starter.configure()

            # Verificar que el migrador se inicializó correctamente
            assert starter.migrator is not None
            assert starter.migrator.migrations_dir is not None

            # Limpiar el archivo alembic.ini
            alembic_ini = Path("alembic.ini")
            if alembic_ini.exists():
                alembic_ini.unlink()

    def test_starter_upgrade_database(self) -> None:
        """Prueba la aplicación de migraciones."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = create_test_config()
            application = create_test_application()
            database_url = "sqlite:///:memory:"
            migrations_dir = str(Path(temp_dir) / "migrations")

            starter = DataStarter(application, database_url, migrations_dir)
            starter.configure()

            # Verificar que el migrador se inicializó correctamente
            assert starter.migrator is not None

            # Limpiar el archivo alembic.ini
            alembic_ini = Path("alembic.ini")
            if alembic_ini.exists():
                alembic_ini.unlink()

    def test_starter_downgrade_database(self) -> None:
        """Prueba la reversión de migraciones."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = create_test_config()
            application = create_test_application()
            database_url = "sqlite:///:memory:"
            migrations_dir = str(Path(temp_dir) / "migrations")

            starter = DataStarter(application, database_url, migrations_dir)
            starter.configure()

            # Verificar que el migrador se inicializó correctamente
            assert starter.migrator is not None

            # Aplicar las migraciones
            starter.upgrade_database()

            # Revertir las migraciones
            starter.downgrade_database("base")

            # Verificar que se revirtieron las migraciones
            current_revision = starter.get_current_revision()
            assert current_revision is None

            # Limpiar el archivo alembic.ini
            alembic_ini = Path("alembic.ini")
            if alembic_ini.exists():
                alembic_ini.unlink()

    def test_starter_get_current_revision(self) -> None:
        """Prueba la obtención de la revisión actual."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = create_test_config()
            application = create_test_application()
            database_url = "sqlite:///:memory:"
            migrations_dir = str(Path(temp_dir) / "migrations")

            starter = DataStarter(application, database_url, migrations_dir)
            starter.configure()

            # Inicialmente no hay revisión
            current_revision = starter.get_current_revision()
            assert current_revision is None

            # Verificar que el migrador se inicializó correctamente
            assert starter.migrator is not None

            # Limpiar el archivo alembic.ini
            alembic_ini = Path("alembic.ini")
            if alembic_ini.exists():
                alembic_ini.unlink()

    def test_starter_unconfigured_errors(self) -> None:
        """Prueba que los métodos fallen si el starter no está configurado."""
        config = create_test_config()
        application = create_test_application()
        database_url = "sqlite:///:memory:"

        starter = DataStarter(application, database_url)

        with pytest.raises(RuntimeError, match="DataStarter not configured"):
            starter.create_tables()

        with pytest.raises(RuntimeError, match="DataStarter not configured"):
            starter.drop_tables()

        with pytest.raises(RuntimeError, match="DataStarter not configured"):
            starter.create_migration("test")

        with pytest.raises(RuntimeError, match="DataStarter not configured"):
            starter.upgrade_database()

        with pytest.raises(RuntimeError, match="DataStarter not configured"):
            starter.downgrade_database("base")

        with pytest.raises(RuntimeError, match="DataStarter not configured"):
            starter.get_current_revision()
