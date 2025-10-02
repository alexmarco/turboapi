"""Pruebas para la gestión de base de datos."""

import pytest
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base

from turboapi.core.config import TurboConfig
from turboapi.data.database import TurboDatabase

Base = declarative_base()


def create_test_config() -> TurboConfig:
    """Crea una configuración de prueba."""
    return TurboConfig(
        project_name="test_project", project_version="1.0.0", installed_apps=["test_app"]
    )


class DatabaseTestModel(Base):
    """Modelo de prueba para las pruebas de base de datos."""

    __tablename__ = "test_models"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)


class TestTurboDatabase:
    """Pruebas para la clase TurboDatabase."""

    def test_database_initialization(self) -> None:
        """Prueba la inicialización de la base de datos."""
        config = create_test_config()
        database = TurboDatabase(config)

        assert not database.is_initialized()
        assert database.engine is None
        assert database.session_factory is None

    def test_database_initialize(self) -> None:
        """Prueba la inicialización de la conexión a la base de datos."""
        config = create_test_config()
        database = TurboDatabase(config)

        # Usar SQLite en memoria para las pruebas
        database_url = "sqlite:///:memory:"
        database.initialize(database_url)

        assert database.is_initialized()
        assert database.engine is not None
        assert database.session_factory is not None

    def test_database_double_initialization(self) -> None:
        """Prueba que la inicialización múltiple no cause problemas."""
        config = create_test_config()
        database = TurboDatabase(config)

        database_url = "sqlite:///:memory:"
        database.initialize(database_url)
        first_engine = database.engine

        # Intentar inicializar nuevamente
        database.initialize(database_url)

        # Debe ser la misma instancia
        assert database.engine is first_engine

    def test_get_session_context_manager(self) -> None:
        """Prueba el contexto manager para obtener sesiones."""
        config = create_test_config()
        database = TurboDatabase(config)
        database.initialize("sqlite:///:memory:")

        with database.get_session() as session:
            assert isinstance(session, Session)
            # La sesión debe estar activa (is_active es True cuando está activa)
            assert session.is_active

    def test_get_session_dependency(self) -> None:
        """Prueba la función de dependencia para obtener sesiones."""
        config = create_test_config()
        database = TurboDatabase(config)
        database.initialize("sqlite:///:memory:")

        session_gen = database.get_session_dependency()
        session = next(session_gen)

        assert isinstance(session, Session)

        # Cerrar el generador
        try:
            next(session_gen)
        except StopIteration:
            pass

    def test_create_tables(self) -> None:
        """Prueba la creación de tablas."""
        config = create_test_config()
        database = TurboDatabase(config)
        database.initialize("sqlite:///:memory:")

        # Crear las tablas
        database.create_tables(Base.metadata)

        # Verificar que las tablas existen
        with database.get_session() as session:
            # Verificar que podemos crear una instancia del modelo
            test_model = DatabaseTestModel(name="test")
            session.add(test_model)
            session.commit()

            # Verificar que podemos recuperar el modelo
            retrieved = session.query(DatabaseTestModel).first()
            assert retrieved is not None
            assert retrieved.name == "test"

    def test_drop_tables(self) -> None:
        """Prueba la eliminación de tablas."""
        config = create_test_config()
        database = TurboDatabase(config)
        database.initialize("sqlite:///:memory:")

        # Crear las tablas y agregar datos
        database.create_tables(Base.metadata)

        with database.get_session() as session:
            test_model = DatabaseTestModel(name="test")
            session.add(test_model)
            session.commit()

        # Eliminar las tablas
        database.drop_tables(Base.metadata)

        # Verificar que las tablas fueron eliminadas
        with database.get_session() as session:
            # Esto debería fallar porque la tabla no existe
            with pytest.raises(Exception):
                session.query(DatabaseTestModel).first()

    def test_uninitialized_database_errors(self) -> None:
        """Prueba que los métodos fallen si la base de datos no está inicializada."""
        config = create_test_config()
        database = TurboDatabase(config)

        with pytest.raises(RuntimeError, match="Database not initialized"):
            with database.get_session():
                pass

        with pytest.raises(RuntimeError, match="Database not initialized"):
            next(database.get_session_dependency())

        with pytest.raises(RuntimeError, match="Database not initialized"):
            database.create_tables()

        with pytest.raises(RuntimeError, match="Database not initialized"):
            database.drop_tables()
