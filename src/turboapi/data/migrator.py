"""Migrador de base de datos para TurboAPI usando Alembic."""

import subprocess
import sys
from pathlib import Path
from typing import Any

from ..core.config import TurboConfig


class TurboMigrator:
    """Wrapper simple para comandos de Alembic."""

    def __init__(self, config: TurboConfig, database_url: str) -> None:
        """
        Inicializa el migrador.

        Args:
            config: Configuración de TurboAPI
            database_url: URL de conexión a la base de datos
        """
        self.config = config
        self.database_url = database_url
        self.migrations_dir: Path | None = None

    def initialize(self, migrations_dir: str | Path = "migrations") -> None:
        """
        Inicializa Alembic con la configuración del proyecto.

        Args:
            migrations_dir: Directorio donde se almacenan las migraciones
        """
        self.migrations_dir = Path(migrations_dir)

        # Crear directorio de migraciones si no existe
        self.migrations_dir.mkdir(exist_ok=True)

        # Si no existe alembic.ini, inicializar Alembic
        alembic_ini_path = self.migrations_dir.parent / "alembic.ini"
        if not alembic_ini_path.exists():
            # Cambiar al directorio padre para ejecutar alembic init
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(self.migrations_dir.parent)
                self._run_alembic_command(["init", str(self.migrations_dir)])
            finally:
                os.chdir(original_cwd)

            # Actualizar alembic.ini con la URL de la base de datos
            self._update_alembic_ini()

    def _update_alembic_ini(self) -> None:
        """Actualiza el archivo alembic.ini con la URL de la base de datos."""
        if self.migrations_dir is None:
            raise RuntimeError("Migrator not initialized")
        alembic_ini_path = self.migrations_dir.parent / "alembic.ini"

        if alembic_ini_path.exists():
            # Leer el archivo existente
            with open(alembic_ini_path, encoding="utf-8") as f:
                content = f.read()

            # Actualizar la URL de la base de datos
            lines = content.split("\n")
            updated_lines = []

            for line in lines:
                if line.startswith("sqlalchemy.url ="):
                    updated_lines.append(f"sqlalchemy.url = {self.database_url}")
                elif "version_num_format = %04d" in line:
                    # Escapar correctamente el formato de versión
                    updated_lines.append("version_num_format = %%04d")
                else:
                    updated_lines.append(line)

            # Escribir el archivo actualizado
            with open(alembic_ini_path, "w", encoding="utf-8") as f:
                f.write("\n".join(updated_lines))

    def _run_alembic_command(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        """
        Ejecuta un comando de Alembic.

        Args:
            args: Argumentos del comando Alembic

        Returns:
            Resultado del comando
        """
        cmd = [sys.executable, "-m", "alembic"] + args

        # Cambiar al directorio donde está el alembic.ini
        cwd = Path.cwd()
        if self.migrations_dir and self.migrations_dir.parent.exists():
            cwd = self.migrations_dir.parent

        return subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=cwd)

    def create_revision(
        self, message: str, autogenerate: bool = False, **kwargs: Any
    ) -> str | None:
        """
        Crea una nueva revisión de migración.

        Args:
            message: Mensaje descriptivo de la migración
            autogenerate: Si generar automáticamente basado en cambios de modelos
            **kwargs: Argumentos adicionales para el comando revision

        Returns:
            ID de la revisión creada
        """
        if self.migrations_dir is None:
            raise RuntimeError("Migrator not initialized. Call initialize() first.")

        args = ["revision", "-m", message]

        if autogenerate:
            args.append("--autogenerate")

        # Agregar argumentos adicionales
        for key, value in kwargs.items():
            if value is not None:
                args.extend([f"--{key.replace('_', '-')}", str(value)])

        result = self._run_alembic_command(args)

        # Extraer el ID de la revisión del output
        output_lines = result.stdout.split("\n")
        for line in output_lines:
            if "Revision ID:" in line:
                revision_id = line.split("Revision ID:")[1].strip()
                # Limpiar el ID de la revisión (remover espacios y caracteres extra)
                return revision_id.split()[0] if revision_id.split() else None

        return None

    def upgrade(self, revision: str = "head", sql: bool = False) -> None:
        """
        Aplica migraciones hacia una revisión específica.

        Args:
            revision: Revisión objetivo
            sql: Si mostrar SQL en lugar de ejecutar
        """
        if self.migrations_dir is None:
            raise RuntimeError("Migrator not initialized. Call initialize() first.")

        args = ["upgrade", revision]

        if sql:
            args.append("--sql")

        self._run_alembic_command(args)

    def downgrade(self, revision: str, sql: bool = False) -> None:
        """
        Revierte migraciones hacia una revisión específica.

        Args:
            revision: Revisión objetivo
            sql: Si mostrar SQL en lugar de ejecutar
        """
        if self.migrations_dir is None:
            raise RuntimeError("Migrator not initialized. Call initialize() first.")

        args = ["downgrade", revision]

        if sql:
            args.append("--sql")

        self._run_alembic_command(args)

    def current(self) -> str | None:
        """
        Obtiene la revisión actual de la base de datos.

        Returns:
            Revisión actual
        """
        if self.migrations_dir is None:
            raise RuntimeError("Migrator not initialized. Call initialize() first.")

        try:
            result = self._run_alembic_command(["current"])
            output = result.stdout.strip()

            if output and " (head)" not in output:
                # Extraer el ID de la revisión
                parts = output.split()
                if parts:
                    return parts[0]

            return None
        except subprocess.CalledProcessError:
            # Si no hay migraciones aplicadas, Alembic puede fallar
            return None

    def history(self, verbose: bool = False) -> str:
        """
        Muestra el historial de migraciones.

        Args:
            verbose: Si mostrar información detallada

        Returns:
            Historial de migraciones
        """
        if self.migrations_dir is None:
            raise RuntimeError("Migrator not initialized. Call initialize() first.")

        args = ["history"]

        if verbose:
            args.append("--verbose")

        result = self._run_alembic_command(args)
        return result.stdout

    def show(self, revision: str) -> str:
        """
        Muestra información sobre una revisión específica.

        Args:
            revision: ID de la revisión

        Returns:
            Información de la revisión
        """
        if self.migrations_dir is None:
            raise RuntimeError("Migrator not initialized. Call initialize() first.")

        result = self._run_alembic_command(["show", revision])
        return result.stdout
