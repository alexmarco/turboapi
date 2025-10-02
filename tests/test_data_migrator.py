"""Pruebas para el wrapper de Alembic."""

import tempfile
from pathlib import Path

import pytest

from turboapi.core.config import TurboConfig
from turboapi.data.migrator import TurboMigrator


def create_test_config() -> TurboConfig:
    """Crea una configuración de prueba."""
    return TurboConfig(
        project_name="test_project", project_version="1.0.0", installed_apps=["test_app"]
    )


class TestTurboMigrator:
    """Pruebas para la clase TurboMigrator."""

    def test_migrator_initialization(self) -> None:
        """Prueba la inicialización del migrador."""
        config = create_test_config()
        database_url = "sqlite:///:memory:"
        migrator = TurboMigrator(config, database_url)

        assert migrator.config is config
        assert migrator.database_url == database_url
        assert migrator.migrations_dir is None

    def test_migrator_initialize(self) -> None:
        """Prueba la inicialización de Alembic."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = create_test_config()
            database_url = "sqlite:///:memory:"
            migrator = TurboMigrator(config, database_url)

            migrations_dir = Path(temp_dir) / "migrations"
            migrator.initialize(str(migrations_dir))

            assert migrator.migrations_dir is not None
            assert migrations_dir.exists()

            # Verificar que se creó el archivo alembic.ini
            alembic_ini = migrations_dir.parent / "alembic.ini"
            assert alembic_ini.exists()

            # Limpiar el archivo alembic.ini
            alembic_ini.unlink()

    def test_migrator_initialize_creates_alembic_ini(self) -> None:
        """Prueba que se crea el archivo alembic.ini con la configuración correcta."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = create_test_config()
            database_url = "sqlite:///test.db"
            migrator = TurboMigrator(config, database_url)

            migrations_dir = Path(temp_dir) / "migrations"
            migrator.initialize(str(migrations_dir))

            # Verificar que se creó el archivo alembic.ini
            alembic_ini = migrations_dir.parent / "alembic.ini"
            assert alembic_ini.exists()

            # Verificar el contenido del archivo
            with open(alembic_ini, encoding="utf-8") as f:
                content = f.read()

            assert f"script_location = {migrations_dir.as_posix()}" in content
            assert f"sqlalchemy.url = {database_url}" in content

            # Limpiar el archivo alembic.ini
            alembic_ini.unlink()

    def test_migrator_initialize_creates_migrations_directory(self) -> None:
        """Prueba que se crea el directorio de migraciones."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = create_test_config()
            database_url = "sqlite:///:memory:"
            migrator = TurboMigrator(config, database_url)

            migrations_dir = Path(temp_dir) / "migrations"
            migrator.initialize(str(migrations_dir))

            assert migrations_dir.exists()
            assert migrations_dir.is_dir()

    def test_migrator_uninitialized_errors(self) -> None:
        """Prueba que los métodos fallen si el migrador no está inicializado."""
        config = create_test_config()
        database_url = "sqlite:///:memory:"
        migrator = TurboMigrator(config, database_url)

        with pytest.raises(RuntimeError, match="Migrator not initialized"):
            migrator.create_revision("test message")

        with pytest.raises(RuntimeError, match="Migrator not initialized"):
            migrator.upgrade()

        with pytest.raises(RuntimeError, match="Migrator not initialized"):
            migrator.downgrade("base")

        with pytest.raises(RuntimeError, match="Migrator not initialized"):
            migrator.current()

        with pytest.raises(RuntimeError, match="Migrator not initialized"):
            migrator.history()

        with pytest.raises(RuntimeError, match="Migrator not initialized"):
            migrator.show("head")

    def test_migrator_initialization_with_existing_alembic_ini(self) -> None:
        """Prueba la inicialización cuando ya existe un archivo alembic.ini."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = create_test_config()
            database_url = "sqlite:///:memory:"
            migrator = TurboMigrator(config, database_url)

            migrations_dir = Path(temp_dir) / "migrations"
            migrator.initialize(str(migrations_dir))

            # Verificar que se creó el directorio de migraciones
            assert migrations_dir.exists()
            assert migrations_dir.is_dir()

    def test_migrator_database_url_configuration(self) -> None:
        """Prueba que la URL de la base de datos se configura correctamente."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = create_test_config()
            database_url = "sqlite:///test.db"
            migrator = TurboMigrator(config, database_url)

            migrations_dir = Path(temp_dir) / "migrations"
            migrator.initialize(str(migrations_dir))

            # Verificar que se inicializó correctamente
            assert migrator.migrations_dir is not None

            # Limpiar el archivo alembic.ini
            alembic_ini = Path("alembic.ini")
            if alembic_ini.exists():
                alembic_ini.unlink()

    def test_migrator_engine_creation(self) -> None:
        """Prueba que se crea el motor de base de datos correctamente."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = create_test_config()
            database_url = "sqlite:///:memory:"
            migrator = TurboMigrator(config, database_url)

            migrations_dir = Path(temp_dir) / "migrations"
            migrator.initialize(str(migrations_dir))

            assert migrator.migrations_dir is not None

            # Limpiar el archivo alembic.ini
            alembic_ini = Path("alembic.ini")
            if alembic_ini.exists():
                alembic_ini.unlink()
