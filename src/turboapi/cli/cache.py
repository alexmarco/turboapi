"""Gestor de caché para el CLI."""

from pathlib import Path

import typer

from turboapi.cache.starter import CacheStarter
from turboapi.core.application import TurboApplication


class CacheManager:
    """Gestor de caché para el CLI."""

    def __init__(self) -> None:
        """Inicializa el gestor de caché."""
        self.pyproject_path = self._find_pyproject_toml()
        if not self.pyproject_path:
            raise RuntimeError("No se encontró pyproject.toml en el directorio actual o superiores")

        self.application = TurboApplication(self.pyproject_path)
        self.application.initialize()

        # Configurar el sistema de caché
        cache_starter = CacheStarter(self.application)
        cache_starter.configure()

        self.cache = cache_starter.get_cache()
        self.scanner = self.application.get_scanner()

    def _find_pyproject_toml(self) -> Path | None:
        """Busca el archivo pyproject.toml en el directorio actual o superiores."""
        current_dir = Path.cwd()

        while current_dir != current_dir.parent:
            pyproject_path = current_dir / "pyproject.toml"
            if pyproject_path.exists():
                return pyproject_path
            current_dir = current_dir.parent

        return None

    def list_cached_functions(self) -> None:
        """Lista todas las funciones cacheables disponibles."""
        typer.echo("Buscando funciones cacheables...")

        # Descubrir funciones cacheables
        cached_functions = self.scanner.find_cached_functions()

        if not cached_functions:
            typer.echo("No se encontraron funciones cacheables.")
            return

        typer.echo(f"\n[OK] Se encontraron {len(cached_functions)} funciones cacheables:")
        typer.echo("-" * 60)

        for func in cached_functions:
            name = func.__name__
            doc = func.__doc__ or "Sin descripción"
            ttl = getattr(func, "_cache_ttl", None)

            typer.echo(f"• {name}")
            typer.echo(f"  Descripción: {doc.strip()}")
            if ttl:
                typer.echo(f"  TTL: {ttl}")
            typer.echo()

    def clear_key(self, key: str) -> None:
        """Limpia una clave específica del caché."""
        typer.echo(f"Limpiando clave del caché: {key}")

        if self.cache.delete(key):
            typer.echo(f"[OK] Clave '{key}' eliminada del caché")
        else:
            typer.echo(f"[INFO] Clave '{key}' no encontrada en el caché")

    def clear_all(self) -> None:
        """Limpia todo el caché."""
        typer.echo("Limpiando todo el caché...")

        # Obtener estadísticas antes de limpiar
        stats_before = self.cache.stats()
        entries_before = stats_before.get("total_entries", 0)

        self.cache.clear()

        typer.echo(f"[OK] Caché limpiado. Se eliminaron {entries_before} entradas")

    def show_stats(self) -> None:
        """Muestra estadísticas del caché."""
        typer.echo("Estadísticas del caché:")

        stats = self.cache.stats()

        typer.echo("\n[OK] Estadísticas del sistema de caché:")
        typer.echo("-" * 50)

        typer.echo(f"• Entradas totales: {stats.get('total_entries', 0)}")
        typer.echo(f"• Entradas válidas: {stats.get('valid_entries', 0)}")
        typer.echo(f"• Hits: {stats.get('hits', 0)}")
        typer.echo(f"• Misses: {stats.get('misses', 0)}")
        typer.echo(f"• Total de solicitudes: {stats.get('total_requests', 0)}")
        typer.echo(f"• Tasa de aciertos: {stats.get('hit_rate', 0.0):.2%}")

        # Mostrar claves actuales
        keys = self.cache.keys()
        if keys:
            typer.echo(f"\nClaves en caché ({len(keys)}):")
            for i, key in enumerate(keys[:10]):  # Mostrar solo las primeras 10
                typer.echo(f"  {i + 1}. {key}")
            if len(keys) > 10:
                typer.echo(f"  ... y {len(keys) - 10} más")
        else:
            typer.echo("\nNo hay claves en el caché.")
