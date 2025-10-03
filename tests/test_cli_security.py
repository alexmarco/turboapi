"""Tests for security CLI commands."""

import pytest
from typer.testing import CliRunner

from turboapi.cli.security import app


class TestSecurityCLI:
    """Test cases for security CLI commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner for testing."""
        return CliRunner()

    def test_create_user(self, runner: CliRunner) -> None:
        """Test user creation command."""
        result = runner.invoke(
            app,
            [
                "create-user",
                "--username",
                "testuser",
                "--email",
                "test@example.com",
                "--password",
                "password123",
                "--is-active",
                "--no-is-verified",
            ],
        )

        assert result.exit_code == 0
        assert "[OK] User 'testuser' created successfully" in result.stdout
        assert "ID: user_testuser" in result.stdout
        assert "Email: test@example.com" in result.stdout
        assert "Active: True" in result.stdout
        assert "Verified: False" in result.stdout

    def test_create_role(self, runner: CliRunner) -> None:
        """Test role creation command."""
        result = runner.invoke(
            app,
            [
                "create-role",
                "--name",
                "admin",
                "--description",
                "Administrator role",
                "--no-is-system-role",
            ],
        )

        assert result.exit_code == 0
        assert "[OK] Role 'admin' created successfully" in result.stdout
        assert "Description: Administrator role" in result.stdout
        assert "System Role: False" in result.stdout

    def test_create_permission(self, runner: CliRunner) -> None:
        """Test permission creation command."""
        result = runner.invoke(
            app,
            [
                "create-permission",
                "--name",
                "read_users",
                "--resource",
                "users",
                "--action",
                "read",
                "--description",
                "Read users permission",
            ],
        )

        assert result.exit_code == 0
        assert "[OK] Permission 'read_users' created successfully" in result.stdout
        assert "Resource: users" in result.stdout
        assert "Action: read" in result.stdout
        assert "Description: Read users permission" in result.stdout

    def test_assign_role_help(self, runner: CliRunner) -> None:
        """Test role assignment command help."""
        result = runner.invoke(
            app,
            [
                "assign-role",
                "--help",
            ],
        )

        assert result.exit_code == 0
        assert "Assign a role to a user" in result.stdout

    def test_revoke_role_help(self, runner: CliRunner) -> None:
        """Test role revocation command help."""
        result = runner.invoke(
            app,
            [
                "revoke-role",
                "--help",
            ],
        )

        assert result.exit_code == 0
        assert "Revoke a role from a user" in result.stdout

    def test_assign_permission_to_role_help(self, runner: CliRunner) -> None:
        """Test permission assignment to role command help."""
        result = runner.invoke(
            app,
            [
                "assign-permission-to-role",
                "--help",
            ],
        )

        assert result.exit_code == 0
        assert "Assign a permission to a role" in result.stdout

    def test_revoke_permission_from_role_help(self, runner: CliRunner) -> None:
        """Test permission revocation from role command help."""
        result = runner.invoke(
            app,
            [
                "revoke-permission-from-role",
                "--help",
            ],
        )

        assert result.exit_code == 0
        assert "Revoke a permission from a role" in result.stdout

    def test_list_users(self, runner: CliRunner) -> None:
        """Test list users command."""
        result = runner.invoke(app, ["list-users"])

        assert result.exit_code == 0
        assert "[INFO] Users:" in result.stdout
        assert "No users found" in result.stdout

    def test_list_roles_help(self, runner: CliRunner) -> None:
        """Test list roles command help."""
        result = runner.invoke(
            app,
            [
                "list-roles",
                "--help",
            ],
        )

        assert result.exit_code == 0
        assert "List all roles" in result.stdout

    def test_list_permissions_help(self, runner: CliRunner) -> None:
        """Test list permissions command help."""
        result = runner.invoke(
            app,
            [
                "list-permissions",
                "--help",
            ],
        )

        assert result.exit_code == 0
        assert "List all permissions" in result.stdout

    def test_show_user_roles_help(self, runner: CliRunner) -> None:
        """Test show user roles command help."""
        result = runner.invoke(
            app,
            [
                "show-user-roles",
                "--help",
            ],
        )

        assert result.exit_code == 0
        assert "Show roles assigned to a user" in result.stdout

    def test_show_user_permissions_help(self, runner: CliRunner) -> None:
        """Test show user permissions command help."""
        result = runner.invoke(
            app,
            [
                "show-user-permissions",
                "--help",
            ],
        )

        assert result.exit_code == 0
        assert "Show permissions assigned to a user" in result.stdout

    def test_check_permission_help(self, runner: CliRunner) -> None:
        """Test check permission command help."""
        result = runner.invoke(
            app,
            [
                "check-permission",
                "--help",
            ],
        )

        assert result.exit_code == 0
        assert "Check if a user has a specific permission" in result.stdout

    def test_list_sessions_help(self, runner: CliRunner) -> None:
        """Test list sessions command help."""
        result = runner.invoke(
            app,
            [
                "list-sessions",
                "--help",
            ],
        )

        assert result.exit_code == 0
        assert "List all active sessions" in result.stdout

    def test_revoke_session_help(self, runner: CliRunner) -> None:
        """Test revoke session command help."""
        result = runner.invoke(
            app,
            [
                "revoke-session",
                "--help",
            ],
        )

        assert result.exit_code == 0
        assert "Revoke a specific session" in result.stdout

    def test_revoke_user_sessions_help(self, runner: CliRunner) -> None:
        """Test revoke user sessions command help."""
        result = runner.invoke(
            app,
            [
                "revoke-user-sessions",
                "--help",
            ],
        )

        assert result.exit_code == 0
        assert "Revoke all sessions for a specific user" in result.stdout

    def test_security_cli_help(self, runner: CliRunner) -> None:
        """Test security CLI help."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Security management commands" in result.stdout
        assert "create-user" in result.stdout
        assert "create-role" in result.stdout
        assert "create-permission" in result.stdout
        assert "assign-role" in result.stdout
        assert "revoke-role" in result.stdout
        assert "list-users" in result.stdout
        assert "list-roles" in result.stdout
        assert "list-permissions" in result.stdout
