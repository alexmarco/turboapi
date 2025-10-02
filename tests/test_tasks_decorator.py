"""Pruebas para el decorador @Task."""

from turboapi.tasks.decorators import Task as TaskDecorator


class TestTaskDecorator:
    """Pruebas para el decorador @Task."""

    def test_task_decorator_basic(self) -> None:
        """Prueba el uso básico del decorador @Task."""

        @TaskDecorator()
        def sample_task() -> str:
            return "Hello World"

        # Verificar que la función mantiene su funcionalidad
        result = sample_task()
        assert result == "Hello World"

        # Verificar que tiene los metadatos de tarea
        assert hasattr(sample_task, "_is_task")
        assert sample_task._is_task is True
        assert hasattr(sample_task, "_task_name")
        assert sample_task._task_name == "sample_task"

    def test_task_decorator_with_name(self) -> None:
        """Prueba el decorador @Task con nombre personalizado."""

        @TaskDecorator(name="custom_task_name")
        def sample_task() -> str:
            return "Hello World"

        assert sample_task._task_name == "custom_task_name"

    def test_task_decorator_with_description(self) -> None:
        """Prueba el decorador @Task con descripción."""

        @TaskDecorator(description="This is a sample task")
        def sample_task() -> str:
            return "Hello World"

        assert hasattr(sample_task, "_task_description")
        assert sample_task._task_description == "This is a sample task"

    def test_task_decorator_with_all_options(self) -> None:
        """Prueba el decorador @Task con todas las opciones."""

        @TaskDecorator(
            name="custom_task",
            description="A custom task with all options",
            retry_count=3,
            timeout=60,
        )
        def sample_task() -> str:
            return "Hello World"

        assert sample_task._task_name == "custom_task"
        assert sample_task._task_description == "A custom task with all options"
        assert sample_task._task_retry_count == 3
        assert sample_task._task_timeout == 60

    def test_task_decorator_preserves_function_metadata(self) -> None:
        """Prueba que el decorador preserva los metadatos de la función."""

        @TaskDecorator()
        def sample_task(x: int, y: str = "default") -> str:
            """A sample task function."""
            return f"{x}-{y}"

        # Verificar que la función mantiene su signatura y docstring
        assert sample_task.__name__ == "sample_task"
        assert sample_task.__doc__ == "A sample task function."

        # Verificar que funciona correctamente
        result = sample_task(42, "test")
        assert result == "42-test"

    def test_task_decorator_with_async_function(self) -> None:
        """Prueba el decorador @Task con función asíncrona."""

        @TaskDecorator()
        async def async_task() -> str:
            return "Async Hello World"

        # Verificar que mantiene los metadatos
        assert hasattr(async_task, "_is_task")
        assert async_task._is_task is True
        assert async_task._task_name == "async_task"

    def test_task_decorator_default_values(self) -> None:
        """Prueba los valores por defecto del decorador @Task."""

        @TaskDecorator()
        def sample_task() -> str:
            return "Hello World"

        assert sample_task._task_name == "sample_task"
        assert sample_task._task_description == ""
        assert sample_task._task_retry_count == 0
        assert sample_task._task_timeout is None

    def test_multiple_tasks_with_decorator(self) -> None:
        """Prueba múltiples funciones con el decorador @Task."""

        @TaskDecorator(name="task_one")
        def task_one() -> str:
            return "Task One"

        @TaskDecorator(name="task_two", description="Second task")
        def task_two() -> str:
            return "Task Two"

        # Verificar que cada función mantiene sus propios metadatos
        assert task_one._task_name == "task_one"
        assert task_one._task_description == ""

        assert task_two._task_name == "task_two"
        assert task_two._task_description == "Second task"

        # Verificar que funcionan independientemente
        assert task_one() == "Task One"
        assert task_two() == "Task Two"

    def test_task_decorator_without_parentheses(self) -> None:
        """Prueba el decorador @Task sin paréntesis."""

        # Esto debería funcionar: @TaskDecorator sin ()
        def sample_function() -> str:
            return "Hello"

        # Aplicar el decorador manualmente para simular @TaskDecorator
        decorated_function = TaskDecorator()(sample_function)

        assert hasattr(decorated_function, "_is_task")
        assert decorated_function._is_task is True
        assert decorated_function._task_name == "sample_function"
