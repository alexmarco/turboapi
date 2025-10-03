"""CLI principal de TurboAPI."""

import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer

from .templates import AppGenerator
from .templates import ProjectGenerator


def _find_app_module() -> str | None:
    """
    Busca automáticamente el módulo de la aplicación.

    Busca en archivos comunes como main.py, app.py, server.py
    y verifica que contengan una instancia de aplicación.

    Returns:
        El módulo de la aplicación en formato 'archivo:variable' o None si no se encuentra.
    """
    common_files = ["main.py", "app.py", "server.py", "run.py"]
    common_vars = ["app", "application", "turbo_app", "main_app"]

    for file_name in common_files:
        file_path = Path(file_name)
        if file_path.exists():
            # Leer el contenido del archivo para buscar variables de aplicación
            try:
                content = file_path.read_text(encoding="utf-8")
                for var_name in common_vars:
                    # Buscar patrones como "app = TurboApplication()" o "app: TurboApplication"
                    if (
                        f"{var_name} = " in content
                        or f"{var_name}: " in content
                        or f"{var_name}=" in content
                    ):
                        module_name = file_path.stem  # nombre sin extensión
                        return f"{module_name}:{var_name}"
            except Exception:
                continue

    return None


app = typer.Typer(
    name="framework",
    help="TurboAPI Framework CLI",
    no_args_is_help=True,
)


@app.command()
def new(
    project_name: Annotated[str, typer.Argument(help="Nombre del proyecto")],
    template: Annotated[str, typer.Option("--template", "-t", help="Plantilla a usar")] = "basic",
    path: Annotated[str, typer.Option("--path", "-p", help="Ruta donde crear el proyecto")] = ".",
) -> None:
    """Crea un nuevo proyecto TurboAPI."""
    typer.echo(f"Creando proyecto '{project_name}' con plantilla '{template}'...")

    try:
        generator = ProjectGenerator()
        target_dir = Path(path) / project_name if path != "." else Path(project_name)
        generator.create_project(project_name, template, target_dir)
    except typer.BadParameter as e:
        typer.echo(f"[ERROR] {e}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"[ERROR] Error al crear el proyecto: {e}", err=True)
        raise typer.Exit(1) from e


@app.command()
def new_app(
    app_name: Annotated[str, typer.Argument(help="Nombre de la aplicación")],
    path: Annotated[
        str, typer.Option("--path", "-p", help="Ruta donde crear la aplicación")
    ] = "apps",
) -> None:
    """Crea una nueva aplicación en el proyecto."""
    typer.echo(f"Creando aplicación '{app_name}' en '{path}'...")

    try:
        generator = AppGenerator()
        target_dir = Path(path)
        generator.create_app(app_name, target_dir)
    except typer.BadParameter as e:
        typer.echo(f"[ERROR] {e}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"[ERROR] Error al crear la aplicación: {e}", err=True)
        raise typer.Exit(1) from e


@app.command()
def run(
    host: Annotated[
        str, typer.Option("--host", "-h", help="Host para ejecutar el servidor")
    ] = "127.0.0.1",
    port: Annotated[
        int, typer.Option("--port", "-p", help="Puerto para ejecutar el servidor")
    ] = 8000,
    reload: Annotated[bool, typer.Option("--reload", help="Activar recarga automática")] = False,
    app_module: Annotated[
        str, typer.Option("--app", help="Módulo de la aplicación (ej: main:app)")
    ] = "",
) -> None:
    """Ejecuta el servidor de desarrollo."""
    # Buscar el módulo de la aplicación si no se especifica
    if not app_module:
        found_module = _find_app_module()
        if not found_module:
            typer.echo(
                "[ERROR] No se encontró un módulo de aplicación. "
                "Crea un archivo main.py o app.py con una instancia de TurboApplication, "
                "o especifica el módulo con --app",
                err=True,
            )
            raise typer.Exit(1)
        app_module = found_module

    typer.echo(f"Ejecutando servidor en {host}:{port}...")
    typer.echo(f"Módulo de aplicación: {app_module}")
    typer.echo(f"Recarga automática: {'activada' if reload else 'desactivada'}")

    # Construir comando uvicorn
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        app_module,
        "--host",
        host,
        "--port",
        str(port),
    ]

    if reload:
        cmd.append("--reload")

    try:
        # Ejecutar uvicorn
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        typer.echo(f"[ERROR] Error al ejecutar el servidor: {e}", err=True)
        raise typer.Exit(1) from e
    except KeyboardInterrupt:
        typer.echo("\n[INFO] Servidor detenido por el usuario")
        raise typer.Exit(0) from None


@app.command()
def db(
    command: Annotated[str, typer.Argument(help="Comando de base de datos")],
    message: Annotated[str, typer.Option("--message", "-m", help="Mensaje para migraciones")] = "",
) -> None:
    """Comandos de gestión de base de datos."""
    typer.echo(f"Ejecutando comando de BD: {command}")
    # TODO: Implementar lógica de comandos de base de datos
    typer.echo("✅ Comando de BD ejecutado!")


@app.command()
def task(
    action: Annotated[str, typer.Argument(help="Acción a realizar (list, run, status)")],
    task_name: Annotated[str, typer.Option("--name", "-n", help="Nombre de la tarea")] = "",
    task_args: Annotated[str, typer.Option("--args", help="Argumentos para la tarea (JSON)")] = "",
) -> None:
    """Gestiona las tareas en segundo plano."""
    try:
        from .tasks import TaskManager

        manager = TaskManager()

        if action == "list":
            manager.list_tasks()
        elif action == "run":
            if not task_name:
                typer.echo("[ERROR] Se requiere --name para ejecutar una tarea", err=True)
                raise typer.Exit(1)
            manager.run_task(task_name, task_args)
        elif action == "status":
            manager.show_status()
        else:
            typer.echo(f"[ERROR] Acción desconocida: {action}", err=True)
            typer.echo("Acciones disponibles: list, run, status", err=True)
            raise typer.Exit(1)

    except ImportError:
        typer.echo("[ERROR] Sistema de tareas no disponible", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"[ERROR] Error al gestionar tareas: {e}", err=True)
        raise typer.Exit(1) from e


@app.command()
def cache(
    action: Annotated[str, typer.Argument(help="Acción a realizar (list, clear, stats)")],
    key: Annotated[str, typer.Option("--key", "-k", help="Clave específica del caché")] = "",
) -> None:
    """Gestiona el sistema de caché."""
    try:
        from .cache import CacheManager

        manager = CacheManager()

        if action == "list":
            manager.list_cached_functions()
        elif action == "clear":
            if key:
                manager.clear_key(key)
            else:
                manager.clear_all()
        elif action == "stats":
            manager.show_stats()
        else:
            typer.echo(f"[ERROR] Acción desconocida: {action}", err=True)
            typer.echo("Acciones disponibles: list, clear, stats", err=True)
            raise typer.Exit(1)

    except ImportError:
        typer.echo("[ERROR] Sistema de caché no disponible", err=True)
        raise typer.Exit(1) from None
    except Exception as e:
        typer.echo(f"[ERROR] Error al gestionar caché: {e}", err=True)
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
