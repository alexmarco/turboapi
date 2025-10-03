"""Gestor de tareas para el CLI."""

import json
import uuid
from pathlib import Path

import typer

from turboapi.core.application import TurboApplication
from turboapi.interfaces import Task
from turboapi.interfaces import TaskStatus
from turboapi.tasks.starter import TaskStarter


class TaskManager:
    """Gestor de tareas para el CLI."""

    def __init__(self) -> None:
        """Inicializa el gestor de tareas."""
        self.pyproject_path = self._find_pyproject_toml()
        if not self.pyproject_path:
            raise RuntimeError("No se encontró pyproject.toml en el directorio actual o superiores")

        self.application = TurboApplication(self.pyproject_path)
        self.application.initialize()

        # Configurar el sistema de tareas
        task_starter = TaskStarter(self.application)
        task_starter.configure()

        self.queue = task_starter.get_queue()
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

    def list_tasks(self) -> None:
        """Lista todas las tareas disponibles."""
        typer.echo("Buscando tareas disponibles...")

        # Descubrir tareas
        discovered_tasks = self.scanner.find_tasks()

        if not discovered_tasks:
            typer.echo("No se encontraron tareas.")
            return

        typer.echo(f"\n[OK] Se encontraron {len(discovered_tasks)} tareas:")
        typer.echo("-" * 50)

        for task_func in discovered_tasks:
            name = getattr(task_func, "_task_name", task_func.__name__)
            description = getattr(task_func, "_task_description", "")
            retry_count = getattr(task_func, "_task_retry_count", 0)
            timeout = getattr(task_func, "_task_timeout", None)

            typer.echo(f"• {name}")
            if description:
                typer.echo(f"  Descripción: {description}")
            if retry_count > 0:
                typer.echo(f"  Reintentos: {retry_count}")
            if timeout:
                typer.echo(f"  Timeout: {timeout}s")
            typer.echo()

    def run_task(self, task_name: str, task_args: str = "") -> None:
        """Ejecuta una tarea específica."""
        typer.echo(f"Ejecutando tarea: {task_name}")

        # Buscar la tarea
        discovered_tasks = self.scanner.find_tasks()
        task_func = None

        for func in discovered_tasks:
            func_name = getattr(func, "_task_name", func.__name__)
            if func_name == task_name:
                task_func = func
                break

        if not task_func:
            typer.echo(f"[ERROR] Tarea '{task_name}' no encontrada", err=True)
            return

        # Parsear argumentos si se proporcionan
        args = ()
        kwargs = {}

        if task_args:
            try:
                parsed_args = json.loads(task_args)
                if isinstance(parsed_args, list):
                    args = tuple(parsed_args)
                elif isinstance(parsed_args, dict):
                    kwargs = parsed_args
                else:
                    typer.echo(
                        "[ERROR] Los argumentos deben ser una lista o un objeto JSON", err=True
                    )
                    return
            except json.JSONDecodeError as e:
                typer.echo(f"[ERROR] Error al parsear argumentos JSON: {e}", err=True)
                return

        # Crear la tarea
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            name=task_name,
            func=task_func,
            args=args,
            kwargs=kwargs,
            status=TaskStatus.PENDING,
        )

        # Añadir a la cola
        self.queue.enqueue(task)
        typer.echo(f"[OK] Tarea '{task_name}' añadida a la cola con ID: {task_id}")

        # Ejecutar inmediatamente (para simplicidad en esta versión)
        self._execute_task_immediately(task)

    def _execute_task_immediately(self, task: Task) -> None:
        """Ejecuta una tarea inmediatamente (versión simplificada)."""
        try:
            # Actualizar estado a running
            self.queue.update_task_status(task.id, TaskStatus.RUNNING)
            typer.echo(f"[INFO] Ejecutando tarea '{task.name}'...")

            # Ejecutar la función
            result = task.func(*task.args, **task.kwargs)

            # Actualizar estado a completed
            self.queue.update_task_status(task.id, TaskStatus.COMPLETED, result=result)
            typer.echo(f"[OK] Tarea '{task.name}' completada exitosamente")

            if result is not None:
                typer.echo(f"Resultado: {result}")

        except Exception as e:
            # Actualizar estado a failed
            self.queue.update_task_status(task.id, TaskStatus.FAILED, error=str(e))
            typer.echo(f"[ERROR] Tarea '{task.name}' falló: {e}", err=True)

    def show_status(self) -> None:
        """Muestra el estado de todas las tareas en la cola."""
        typer.echo("Estado de las tareas:")

        all_tasks = self.queue.get_all_tasks()

        if not all_tasks:
            typer.echo("No hay tareas en la cola.")
            return

        typer.echo(f"\n[OK] {len(all_tasks)} tareas en la cola:")
        typer.echo("-" * 70)

        for task in all_tasks:
            status_color = {
                TaskStatus.PENDING: "yellow",
                TaskStatus.RUNNING: "blue",
                TaskStatus.COMPLETED: "green",
                TaskStatus.FAILED: "red",
            }.get(task.status, "white")

            typer.echo(f"• {task.name} (ID: {task.id[:8]}...)")
            typer.echo("  Estado: ", nl=False)
            typer.secho(task.status.value.upper(), fg=status_color)
            typer.echo(f"  Creado: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

            if task.started_at:
                typer.echo(f"  Iniciado: {task.started_at.strftime('%Y-%m-%d %H:%M:%S')}")

            if task.completed_at:
                typer.echo(f"  Completado: {task.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")

            if task.result is not None:
                typer.echo(f"  Resultado: {task.result}")

            if task.error:
                typer.echo(f"  Error: {task.error}")

            typer.echo()
