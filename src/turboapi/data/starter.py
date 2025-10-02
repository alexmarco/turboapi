"""Starter de datos para el framework TurboAPI."""

from typing import Any

from ..core.application import TurboApplication
from ..core.di import ComponentProvider
from .database import TurboDatabase
from .migrator import TurboMigrator


class DataStarter:
    """Starter que configura la capa de datos para TurboAPI."""

    def __init__(
        self,
        application: TurboApplication,
        database_url: str,
        migrations_dir: str | None = None,
    ) -> None:
        """
        Inicializa el starter de datos.

        Args:
            application: Aplicación TurboAPI
            database_url: URL de conexión a la base de datos
            migrations_dir: Directorio de migraciones (opcional)
        """
        self.application = application
        self.database_url = database_url
        self.migrations_dir = migrations_dir or "migrations"

        self.database: TurboDatabase | None = None
        self.migrator: TurboMigrator | None = None

    def configure(self) -> None:
        """Configura la capa de datos y registra los componentes en el contenedor DI."""
        # Crear instancias de base de datos y migrador
        self.database = TurboDatabase(self.application.config)
        self.migrator = TurboMigrator(self.application.config, self.database_url)

        # Inicializar componentes
        self.database.initialize(self.database_url)
        self.migrator.initialize(self.migrations_dir)

        # Registrar en el contenedor DI
        container = self.application.container

        # Registrar TurboDatabase como singleton
        container.register(
            "TurboDatabase", ComponentProvider(lambda: self.database, singleton=True)
        )

        # Registrar TurboMigrator como singleton
        container.register(
            "TurboMigrator", ComponentProvider(lambda: self.migrator, singleton=True)
        )

        # Registrar función para obtener sesión de base de datos
        container.register(
            "database_session",
            ComponentProvider(self.database.get_session_dependency, singleton=False),
        )

        # Registrar repositorios encontrados
        self._register_repositories()

    def _register_repositories(self) -> None:
        """Registra todos los repositorios encontrados en el contenedor DI."""
        scanner = self.application.scanner
        container = self.application.container

        repositories = scanner.find_repositories()

        for repository_class in repositories:
            # Crear una función factory específica para cada repositorio
            def make_factory(repo_class: type) -> Any:
                def create_repository() -> Any:
                    session = container.resolve("database_session")
                    return repo_class(session)

                return create_repository

            container.register(
                repository_class.__name__,
                ComponentProvider(make_factory(repository_class), singleton=False),
            )

    def create_tables(self, metadata: Any | None = None) -> None:
        """
        Crea todas las tablas en la base de datos.

        Args:
            metadata: Metadatos de SQLAlchemy con las tablas a crear
        """
        if self.database is None:
            raise RuntimeError("DataStarter not configured. Call configure() first.")

        self.database.create_tables(metadata)

    def drop_tables(self, metadata: Any | None = None) -> None:
        """
        Elimina todas las tablas de la base de datos.

        Args:
            metadata: Metadatos de SQLAlchemy con las tablas a eliminar
        """
        if self.database is None:
            raise RuntimeError("DataStarter not configured. Call configure() first.")

        self.database.drop_tables(metadata)

    def create_migration(self, message: str, autogenerate: bool = True) -> str | None:
        """
        Crea una nueva migración.

        Args:
            message: Mensaje descriptivo de la migración
            autogenerate: Si generar automáticamente basado en cambios de modelos

        Returns:
            ID de la revisión creada
        """
        if self.migrator is None:
            raise RuntimeError("DataStarter not configured. Call configure() first.")

        return self.migrator.create_revision(message, autogenerate=autogenerate)

    def upgrade_database(self, revision: str = "head") -> None:
        """
        Aplica migraciones a la base de datos.

        Args:
            revision: Revisión objetivo
        """
        if self.migrator is None:
            raise RuntimeError("DataStarter not configured. Call configure() first.")

        self.migrator.upgrade(revision)

    def downgrade_database(self, revision: str) -> None:
        """
        Revierte migraciones de la base de datos.

        Args:
            revision: Revisión objetivo
        """
        if self.migrator is None:
            raise RuntimeError("DataStarter not configured. Call configure() first.")

        self.migrator.downgrade(revision)

    def get_current_revision(self) -> str | None:
        """
        Obtiene la revisión actual de la base de datos.

        Returns:
            Revisión actual
        """
        if self.migrator is None:
            raise RuntimeError("DataStarter not configured. Call configure() first.")

        return self.migrator.current()
