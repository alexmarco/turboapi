"""Pruebas para el CLI principal de TurboAPI."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from turboapi.cli.main import app

runner = CliRunner()


class TestCLIMain:
    """Pruebas para el CLI principal."""

    def test_cli_help(self) -> None:
        """Prueba que el CLI muestra la ayuda correctamente."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "TurboAPI Framework CLI" in result.output
        assert "new" in result.output
        assert "new-app" in result.output
        assert "run" in result.output
        assert "db" in result.output

    def test_cli_no_args_shows_help(self) -> None:
        """Prueba que el CLI muestra ayuda cuando no se pasan argumentos."""
        result = runner.invoke(app, [])

        assert result.exit_code == 2  # Typer devuelve 2 cuando no hay argumentos
        assert "TurboAPI Framework CLI" in result.output

    def test_new_command_help(self) -> None:
        """Prueba que el comando new muestra ayuda correctamente."""
        result = runner.invoke(app, ["new", "--help"])

        assert result.exit_code == 0
        assert "Crea un nuevo proyecto TurboAPI" in result.output
        assert "project_name" in result.output
        assert "--template" in result.output

    def test_new_command_basic(self) -> None:
        """Prueba el comando new básico."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            result = runner.invoke(app, ["new", "test_project", "--path", str(temp_path)])

            assert result.exit_code == 0
            assert "Creando proyecto 'test_project' con plantilla 'basic'..." in result.output
            assert "[OK] Proyecto 'test_project' creado exitosamente" in result.output
            assert (temp_path / "test_project").exists()

    def test_new_command_with_template(self) -> None:
        """Prueba el comando new con plantilla personalizada."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            result = runner.invoke(
                app,
                [
                    "new",
                    "test_project_advanced",
                    "--template",
                    "advanced",
                    "--path",
                    str(temp_path),
                ],
            )

            assert result.exit_code == 0
            assert (
                "Creando proyecto 'test_project_advanced' con plantilla 'advanced'..."
                in result.output
            )
            assert "[OK] Proyecto 'test_project_advanced' creado exitosamente" in result.output
            assert (temp_path / "test_project_advanced").exists()

    def test_new_app_command_help(self) -> None:
        """Prueba que el comando new-app muestra ayuda correctamente."""
        result = runner.invoke(app, ["new-app", "--help"])

        assert result.exit_code == 0
        assert "Crea una nueva aplicación en el proyecto" in result.output
        assert "app_name" in result.output
        assert "--path" in result.output

    def test_new_app_command_basic(self) -> None:
        """Prueba el comando new-app básico."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            result = runner.invoke(app, ["new-app", "test_app", "--path", str(temp_path / "apps")])

            assert result.exit_code == 0
            assert "Creando aplicación 'test_app' en" in result.output
            assert "[OK] Aplicación 'test_app' creada exitosamente" in result.output
            assert (temp_path / "apps" / "test_app").exists()

    def test_new_app_command_with_path(self) -> None:
        """Prueba el comando new-app con ruta personalizada."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            result = runner.invoke(
                app, ["new-app", "test_app", "--path", str(temp_path / "custom_path")]
            )

            assert result.exit_code == 0
            assert "Creando aplicación 'test_app' en" in result.output
            assert "[OK] Aplicación 'test_app' creada exitosamente" in result.output
            assert (temp_path / "custom_path" / "test_app").exists()

    def test_run_command_help(self) -> None:
        """Prueba que el comando run muestra ayuda correctamente."""
        result = runner.invoke(app, ["run", "--help"])

        assert result.exit_code == 0
        assert "Ejecuta el servidor de desarrollo" in result.output
        assert "--host" in result.output
        assert "--port" in result.output
        assert "--reload" in result.output
        assert "--app" in result.output

    def test_run_command_basic_no_app_found(self) -> None:
        """Prueba el comando run cuando no se encuentra una aplicación."""
        result = runner.invoke(app, ["run"])

        assert result.exit_code == 1
        assert "[ERROR] No se encontró un módulo de aplicación" in result.output

    @patch("turboapi.cli.main.subprocess.run")
    def test_run_command_with_app_specified(self, mock_subprocess) -> None:
        """Prueba el comando run con aplicación especificada."""
        # Configurar el mock para simular éxito
        mock_subprocess.return_value.returncode = 0

        result = runner.invoke(app, ["run", "--app", "main:app"])

        # Verificar que no hay errores
        assert result.exit_code == 0

        # Verificar que se muestran los mensajes correctos
        assert "Ejecutando servidor en 127.0.0.1:8000..." in result.output
        assert "Módulo de aplicación: main:app" in result.output
        assert "Recarga automática: desactivada" in result.output

        # Verificar que se llamó a subprocess.run con los argumentos correctos
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]  # Primer argumento posicional
        assert "uvicorn" in call_args
        assert "main:app" in call_args
        assert "--host" in call_args
        assert "127.0.0.1" in call_args

    @patch("turboapi.cli.main.subprocess.run")
    def test_run_command_with_options(self, mock_subprocess) -> None:
        """Prueba el comando run con opciones personalizadas."""
        # Configurar el mock para simular éxito
        mock_subprocess.return_value.returncode = 0

        result = runner.invoke(
            app, ["run", "--app", "main:app", "--host", "0.0.0.0", "--port", "9000", "--reload"]
        )

        # Verificar que no hay errores
        assert result.exit_code == 0

        # Verificar que se muestran los mensajes correctos
        assert "Ejecutando servidor en 0.0.0.0:9000..." in result.output
        assert "Módulo de aplicación: main:app" in result.output
        assert "Recarga automática: activada" in result.output

        # Verificar que se llamó a subprocess.run con los argumentos correctos
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]  # Primer argumento posicional
        assert "uvicorn" in call_args
        assert "main:app" in call_args
        assert "--host" in call_args
        assert "0.0.0.0" in call_args
        assert "--port" in call_args
        assert "9000" in call_args
        assert "--reload" in call_args

    def test_db_command_help(self) -> None:
        """Prueba que el comando db muestra ayuda correctamente."""
        result = runner.invoke(app, ["db", "--help"])

        assert result.exit_code == 0
        assert "Comandos de gestión de base de datos" in result.output
        assert "command" in result.output
        assert "--message" in result.output

    def test_db_command_basic(self) -> None:
        """Prueba el comando db básico."""
        result = runner.invoke(app, ["db", "migrate"])

        assert result.exit_code == 0
        assert "Ejecutando comando de BD: migrate" in result.output
        assert "✅ Comando de BD ejecutado!" in result.output

    def test_db_command_with_message(self) -> None:
        """Prueba el comando db con mensaje."""
        result = runner.invoke(app, ["db", "revision", "--message", "test migration"])

        assert result.exit_code == 0
        assert "Ejecutando comando de BD: revision" in result.output
        assert "✅ Comando de BD ejecutado!" in result.output
