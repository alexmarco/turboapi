"""Security management CLI for TurboAPI."""

import asyncio
from datetime import datetime
from typing import Annotated

import typer

from turboapi.security.interfaces import Permission
from turboapi.security.interfaces import Role
from turboapi.security.interfaces import User
from turboapi.security.rbac import InMemoryRBACManager
from turboapi.security.session import InMemorySessionManager

app = typer.Typer(
    name="security",
    help="Security management commands for users, roles, and permissions",
)


@app.command()
def create_user(
    username: Annotated[str, typer.Option(help="Username for the new user")],
    email: Annotated[str, typer.Option(help="Email for the new user")],
    password: Annotated[str, typer.Option(help="Password for the new user")],
    is_active: Annotated[
        bool, typer.Option("--is-active/--no-is-active", help="Whether the user is active")
    ] = True,
    is_verified: Annotated[
        bool, typer.Option("--is-verified/--no-is-verified", help="Whether the user is verified")
    ] = False,
) -> None:
    """Create a new user."""
    user = User(
        id=f"user_{username}",
        username=username,
        email=email,
        is_active=is_active,
        is_verified=is_verified,
        roles=[],
        permissions=[],
        created_at=datetime.now(),
    )

    # In a real implementation, this would save to a database
    typer.echo(f"[OK] User '{username}' created successfully")
    typer.echo(f"   ID: {user.id}")
    typer.echo(f"   Email: {user.email}")
    typer.echo(f"   Active: {user.is_active}")
    typer.echo(f"   Verified: {user.is_verified}")


@app.command()
def create_role(
    name: Annotated[str, typer.Option(help="Name of the role")],
    description: Annotated[str, typer.Option(help="Description of the role")],
    is_system_role: Annotated[
        bool,
        typer.Option("--is-system-role/--no-is-system-role", help="Whether this is a system role"),
    ] = False,
) -> None:
    """Create a new role."""
    role = Role(
        name=name,
        description=description,
        permissions=[],
        is_system_role=is_system_role,
        created_at=datetime.now(),
    )

    # In a real implementation, this would save to a database
    typer.echo(f"[OK] Role '{name}' created successfully")
    typer.echo(f"   Description: {role.description}")
    typer.echo(f"   System Role: {role.is_system_role}")


@app.command()
def create_permission(
    name: Annotated[str, typer.Option(help="Name of the permission")],
    resource: Annotated[str, typer.Option(help="Resource this permission applies to")],
    action: Annotated[str, typer.Option(help="Action this permission allows")],
    description: Annotated[str, typer.Option(help="Description of the permission")] = "",
) -> None:
    """Create a new permission."""
    permission = Permission(
        name=name,
        description=description,
        resource=resource,
        action=action,
        created_at=datetime.now(),
    )

    # In a real implementation, this would save to a database
    typer.echo(f"[OK] Permission '{name}' created successfully")
    typer.echo(f"   Resource: {permission.resource}")
    typer.echo(f"   Action: {permission.action}")
    typer.echo(f"   Description: {permission.description}")


@app.command()
def assign_role(
    user_id: Annotated[str, typer.Option(help="ID of the user")],
    role_name: Annotated[str, typer.Option(help="Name of the role to assign")],
) -> None:
    """Assign a role to a user."""

    async def _assign_role() -> None:
        rbac_manager = InMemoryRBACManager()
        success = await rbac_manager.assign_role(user_id, role_name)

        if success:
            typer.echo(f"[OK] Role '{role_name}' assigned to user '{user_id}' successfully")
        else:
            typer.echo(f"[ERROR] Failed to assign role '{role_name}' to user '{user_id}'")
            typer.echo("   Make sure both the user and role exist")

    asyncio.run(_assign_role())


@app.command()
def revoke_role(
    user_id: Annotated[str, typer.Option(help="ID of the user")],
    role_name: Annotated[str, typer.Option(help="Name of the role to revoke")],
) -> None:
    """Revoke a role from a user."""

    async def _revoke_role() -> None:
        rbac_manager = InMemoryRBACManager()
        success = await rbac_manager.revoke_role(user_id, role_name)

        if success:
            typer.echo(f"[OK] Role '{role_name}' revoked from user '{user_id}' successfully")
        else:
            typer.echo(f"[ERROR] Failed to revoke role '{role_name}' from user '{user_id}'")
            typer.echo("   Make sure the user has this role assigned")

    asyncio.run(_revoke_role())


@app.command()
def assign_permission_to_role(
    role_name: Annotated[str, typer.Option(help="Name of the role")],
    permission_key: Annotated[str, typer.Option(help="Permission key (resource:action)")],
) -> None:
    """Assign a permission to a role."""

    async def _assign_permission() -> None:
        rbac_manager = InMemoryRBACManager()
        success = await rbac_manager.assign_permission_to_role(role_name, permission_key)

        if success:
            typer.echo(
                f"[OK] Permission '{permission_key}' assigned to role '{role_name}' successfully"
            )
        else:
            typer.echo(
                f"[ERROR] Failed to assign permission '{permission_key}' to role '{role_name}'"
            )
            typer.echo("   Make sure both the role and permission exist")

    asyncio.run(_assign_permission())


@app.command()
def revoke_permission_from_role(
    role_name: Annotated[str, typer.Option(help="Name of the role")],
    permission_key: Annotated[str, typer.Option(help="Permission key (resource:action)")],
) -> None:
    """Revoke a permission from a role."""

    async def _revoke_permission() -> None:
        rbac_manager = InMemoryRBACManager()
        success = await rbac_manager.revoke_permission_from_role(role_name, permission_key)

        if success:
            typer.echo(
                f"[OK] Permission '{permission_key}' revoked from role '{role_name}' successfully"
            )
        else:
            typer.echo(
                f"[ERROR] Failed to revoke permission '{permission_key}' from role '{role_name}'"
            )
            typer.echo("   Make sure the role has this permission assigned")

    asyncio.run(_revoke_permission())


@app.command()
def list_users() -> None:
    """List all users."""
    # In a real implementation, this would fetch from a database
    typer.echo("[INFO] Users:")
    typer.echo("   (No users found - implement database integration)")
    typer.echo("   Use 'create-user' command to create users")


@app.command()
def list_roles() -> None:
    """List all roles."""

    async def _list_roles() -> None:
        rbac_manager = InMemoryRBACManager()
        roles = await rbac_manager.get_all_roles()

        if roles:
            typer.echo("[INFO] Roles:")
            for role in roles:
                typer.echo(f"   • {role.name}: {role.description}")
                typer.echo(f"     System Role: {role.is_system_role}")
                typer.echo(f"     Created: {role.created_at}")
                typer.echo()
        else:
            typer.echo("[INFO] No roles found")
            typer.echo("   Use 'create-role' command to create roles")

    asyncio.run(_list_roles())


@app.command()
def list_permissions() -> None:
    """List all permissions."""

    async def _list_permissions() -> None:
        rbac_manager = InMemoryRBACManager()
        permissions = await rbac_manager.get_all_permissions()

        if permissions:
            typer.echo("[INFO] Permissions:")
            for permission in permissions:
                typer.echo(f"   • {permission.name}: {permission.resource}:{permission.action}")
                typer.echo(f"     Description: {permission.description}")
                typer.echo(f"     Created: {permission.created_at}")
                typer.echo()
        else:
            typer.echo("[INFO] No permissions found")
            typer.echo("   Use 'create-permission' command to create permissions")

    asyncio.run(_list_permissions())


@app.command()
def show_user_roles(
    user_id: Annotated[str, typer.Option(help="ID of the user")],
) -> None:
    """Show roles assigned to a user."""

    async def _show_user_roles() -> None:
        rbac_manager = InMemoryRBACManager()
        roles = await rbac_manager.get_user_roles(user_id)

        if roles:
            typer.echo(f"[INFO] Roles for user '{user_id}':")
            for role in roles:
                typer.echo(f"   • {role.name}: {role.description}")
        else:
            typer.echo(f"[INFO] No roles assigned to user '{user_id}'")

    asyncio.run(_show_user_roles())


@app.command()
def show_user_permissions(
    user_id: Annotated[str, typer.Option(help="ID of the user")],
) -> None:
    """Show permissions assigned to a user (direct + from roles)."""

    async def _show_user_permissions() -> None:
        rbac_manager = InMemoryRBACManager()
        permissions = await rbac_manager.get_user_permissions(user_id)

        if permissions:
            typer.echo(f"[INFO] Permissions for user '{user_id}':")
            for permission in permissions:
                typer.echo(f"   • {permission.name}: {permission.resource}:{permission.action}")
                typer.echo(f"     Description: {permission.description}")
        else:
            typer.echo(f"[INFO] No permissions assigned to user '{user_id}'")

    asyncio.run(_show_user_permissions())


@app.command()
def check_permission(
    user_id: Annotated[str, typer.Option(help="ID of the user")],
    resource: Annotated[str, typer.Option(help="Resource to check")],
    action: Annotated[str, typer.Option(help="Action to check")],
) -> None:
    """Check if a user has a specific permission."""

    async def _check_permission() -> None:
        rbac_manager = InMemoryRBACManager()

        # Create a mock user for the check
        user = User(
            id=user_id,
            username="mock_user",
            email="mock@example.com",
            is_active=True,
            is_verified=True,
            roles=[],
            permissions=[],
            created_at=datetime.now(),
        )

        has_permission = await rbac_manager.check_permission(user, resource, action)

        if has_permission:
            typer.echo(f"[OK] User '{user_id}' has permission '{resource}:{action}'")
        else:
            typer.echo(f"[ERROR] User '{user_id}' does NOT have permission '{resource}:{action}'")

    asyncio.run(_check_permission())


@app.command()
def list_sessions() -> None:
    """List all active sessions."""

    async def _list_sessions() -> None:
        session_manager = InMemorySessionManager()
        sessions = await session_manager.get_all_sessions()

        if sessions:
            typer.echo("[INFO] Active Sessions:")
            for session in sessions:
                typer.echo(f"   • Session ID: {session.session_id}")
                typer.echo(f"     User ID: {session.user_id}")
                typer.echo(f"     Created: {session.created_at}")
                typer.echo(f"     Last Activity: {session.last_activity}")
                typer.echo(f"     Expires: {session.expires_at}")
                typer.echo()
        else:
            typer.echo("[INFO] No active sessions found")

    asyncio.run(_list_sessions())


@app.command()
def revoke_session(
    session_id: Annotated[str, typer.Option(help="ID of the session to revoke")],
) -> None:
    """Revoke a specific session."""

    async def _revoke_session() -> None:
        session_manager = InMemorySessionManager()
        success = await session_manager.revoke_session(session_id)

        if success:
            typer.echo(f"[OK] Session '{session_id}' revoked successfully")
        else:
            typer.echo(f"[ERROR] Failed to revoke session '{session_id}'")
            typer.echo("   Session may not exist or already expired")

    asyncio.run(_revoke_session())


@app.command()
def revoke_user_sessions(
    user_id: Annotated[str, typer.Option(help="ID of the user")],
) -> None:
    """Revoke all sessions for a specific user."""

    async def _revoke_user_sessions() -> None:
        session_manager = InMemorySessionManager()
        success = await session_manager.revoke_user_sessions(user_id)

        if success:
            typer.echo(f"[OK] All sessions for user '{user_id}' revoked successfully")
        else:
            typer.echo(f"[ERROR] Failed to revoke sessions for user '{user_id}'")
            typer.echo("   User may not have any active sessions")

    asyncio.run(_revoke_user_sessions())


if __name__ == "__main__":
    app()
