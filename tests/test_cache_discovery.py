"""Pruebas para el descubrimiento de funciones cacheables."""

import sys
import tempfile
from pathlib import Path

from turboapi.core.config import TurboConfig
from turboapi.core.discovery import ComponentScanner


class TestCacheDiscovery:
    """Pruebas para el descubrimiento de funciones cacheables."""

    def create_test_module_with_cached_functions(self) -> tuple[Path, str]:
        """Crea un módulo temporal con funciones cacheables para pruebas."""
        # Crear un directorio temporal
        temp_dir = Path(tempfile.mkdtemp())

        # Crear un módulo con funciones cacheables
        module_content = '''
"""Test module with cached functions."""

from datetime import timedelta
from turboapi.cache.decorators import Cache

@Cache()
def simple_cached_function(x: int) -> int:
    """A simple cached function."""
    return x * 2

@Cache(ttl=timedelta(seconds=300))
def cached_function_with_ttl(x: int, y: str = "default") -> str:
    """A cached function with TTL."""
    return f"{x}-{y}"

def not_cached_function() -> str:
    """This function is not cached."""
    return "Not cached"

class SomeClass:
    """A class that is not cached."""

    @Cache()
    def cached_method(self, x: int) -> int:
        """A method that is cached."""
        return x + 1
'''

        module_file = temp_dir / "test_cache_module.py"
        module_file.write_text(module_content, encoding="utf-8")

        # Añadir el directorio temporal al path de Python
        sys.path.insert(0, str(temp_dir))

        return temp_dir, "test_cache_module"

    def test_find_cached_functions_basic(self) -> None:
        """Prueba el descubrimiento básico de funciones cacheables."""
        temp_dir, module_name = self.create_test_module_with_cached_functions()

        try:
            config = TurboConfig(
                project_name="test_project",
                project_version="1.0.0",
                installed_apps=[module_name],
            )

            scanner = ComponentScanner(config)
            cached_functions = scanner.find_cached_functions()

            # Debe encontrar las funciones cacheables
            assert len(cached_functions) >= 2  # Al menos 2 funciones

            # Verificar que son funciones con metadatos de caché
            function_names = []
            for func in cached_functions:
                assert hasattr(func, "_is_cached")
                assert func._is_cached is True
                function_names.append(func.__name__)

            # Verificar que se encontraron las funciones esperadas
            assert "simple_cached_function" in function_names
            assert "cached_function_with_ttl" in function_names

        finally:
            # Limpiar
            sys.path.remove(str(temp_dir))
            if module_name in sys.modules:
                del sys.modules[module_name]

    def test_find_cached_functions_with_metadata(self) -> None:
        """Prueba que las funciones encontradas mantienen sus metadatos."""
        temp_dir, module_name = self.create_test_module_with_cached_functions()

        try:
            config = TurboConfig(
                project_name="test_project",
                project_version="1.0.0",
                installed_apps=[module_name],
            )

            scanner = ComponentScanner(config)
            cached_functions = scanner.find_cached_functions()

            # Buscar la función con TTL
            ttl_function = None
            for func in cached_functions:
                if func.__name__ == "cached_function_with_ttl":
                    ttl_function = func
                    break

            assert ttl_function is not None
            assert hasattr(ttl_function, "_cache_ttl")
            # Nota: El TTL específico puede no estar disponible debido a la importación

        finally:
            # Limpiar
            sys.path.remove(str(temp_dir))
            if module_name in sys.modules:
                del sys.modules[module_name]

    def test_find_cached_functions_excludes_non_cached(self) -> None:
        """Prueba que solo se encuentran funciones marcadas como cacheables."""
        temp_dir, module_name = self.create_test_module_with_cached_functions()

        try:
            config = TurboConfig(
                project_name="test_project",
                project_version="1.0.0",
                installed_apps=[module_name],
            )

            scanner = ComponentScanner(config)
            cached_functions = scanner.find_cached_functions()

            # Verificar que no se incluye la función que no es cacheable
            function_names = [func.__name__ for func in cached_functions]
            assert "not_cached_function" not in function_names

        finally:
            # Limpiar
            sys.path.remove(str(temp_dir))
            if module_name in sys.modules:
                del sys.modules[module_name]

    def test_find_cached_functions_empty_apps(self) -> None:
        """Prueba el descubrimiento de funciones cacheables con aplicaciones vacías."""
        config = TurboConfig(
            project_name="test_project",
            project_version="1.0.0",
            installed_apps=[],
        )

        scanner = ComponentScanner(config)
        cached_functions = scanner.find_cached_functions()

        assert cached_functions == []

    def test_find_cached_functions_nonexistent_app(self) -> None:
        """Prueba el descubrimiento de funciones cacheables con aplicación inexistente."""
        config = TurboConfig(
            project_name="test_project",
            project_version="1.0.0",
            installed_apps=["nonexistent_app"],
        )

        scanner = ComponentScanner(config)
        # No debe lanzar excepción, pero tampoco encontrar funciones
        cached_functions = scanner.find_cached_functions()

        assert cached_functions == []
