"""Gestión de base de datos y sesiones para el framework TurboAPI."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from ..core.config import TurboConfig


class TurboDatabase:
    """Gestor de base de datos y sesiones para TurboAPI."""

    def __init__(self, config: TurboConfig) -> None:
        """
        Inicializa el gestor de base de datos.

        Args:
            config: Configuración de la aplicación
        """
        self.config = config
        self.engine: Engine | None = None
        self.session_factory: sessionmaker[Session] | None = None
        self._initialized = False

    def initialize(self, database_url: str) -> None:
        """
        Inicializa la conexión a la base de datos.

        Args:
            database_url: URL de conexión a la base de datos
        """
        if self._initialized:
            return

        # Crear el motor de base de datos
        self.engine = create_engine(
            database_url,
            echo=self.config.debug if hasattr(self.config, "debug") else False,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        # Crear la factory de sesiones
        self.session_factory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
        )

        self._initialized = True

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Obtiene una sesión de base de datos con manejo automático de transacciones.

        Yields:
            Sesión de SQLAlchemy

        Raises:
            RuntimeError: Si la base de datos no ha sido inicializada
        """
        if not self._initialized or self.session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session_dependency(self) -> Generator[Session, None, None]:
        """
        Obtiene una sesión de base de datos para inyección de dependencias.

        Yields:
            Sesión de SQLAlchemy

        Raises:
            RuntimeError: Si la base de datos no ha sido inicializada
        """
        if not self._initialized or self.session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        session = self.session_factory()
        try:
            yield session
        finally:
            session.close()

    def create_tables(self, metadata: Any | None = None) -> None:
        """
        Crea todas las tablas definidas en los modelos.

        Args:
            metadata: Metadatos de SQLAlchemy con las tablas a crear

        Raises:
            RuntimeError: Si la base de datos no ha sido inicializada
        """
        if not self._initialized or self.engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        if metadata is None:
            # Importar aquí para evitar imports circulares
            from sqlalchemy import MetaData

            metadata = MetaData()

        metadata.create_all(self.engine)

    def drop_tables(self, metadata: Any | None = None) -> None:
        """
        Elimina todas las tablas de la base de datos.

        Args:
            metadata: Metadatos de SQLAlchemy con las tablas a eliminar

        Raises:
            RuntimeError: Si la base de datos no ha sido inicializada
        """
        if not self._initialized or self.engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        if metadata is None:
            # Importar aquí para evitar imports circulares
            from sqlalchemy import MetaData

            metadata = MetaData()

        metadata.drop_all(self.engine)

    def is_initialized(self) -> bool:
        """
        Verifica si la base de datos ha sido inicializada.

        Returns:
            True si está inicializada, False en caso contrario
        """
        return self._initialized
