"""Tests for RBAC (Role-Based Access Control) system."""

from datetime import datetime

import pytest

from turboapi.security.interfaces import Permission
from turboapi.security.interfaces import Role
from turboapi.security.interfaces import User
from turboapi.security.rbac import InMemoryRBACManager


class TestInMemoryRBACManager:
    """Test cases for InMemoryRBACManager."""

    @pytest.fixture
    def rbac_manager(self) -> InMemoryRBACManager:
        """Create an RBAC manager instance."""
        return InMemoryRBACManager()

    @pytest.fixture
    def sample_user(self) -> User:
        """Create a sample user."""
        return User(
            id="user1",
            username="testuser",
            email="test@example.com",
            is_active=True,
            is_verified=True,
            roles=[],
            permissions=[],
            created_at=datetime.now(),
        )

    @pytest.fixture
    def sample_role(self) -> Role:
        """Create a sample role."""
        return Role(
            name="admin",
            description="Administrator role",
            permissions=[],
            is_system_role=False,
            created_at=datetime.now(),
        )

    @pytest.fixture
    def sample_permission(self) -> Permission:
        """Create a sample permission."""
        return Permission(
            name="read_users",
            description="Read users permission",
            resource="users",
            action="read",
            created_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_create_role(self, rbac_manager: InMemoryRBACManager, sample_role: Role) -> None:
        """Test role creation."""
        result = await rbac_manager.create_role(sample_role)
        assert result is True

        # Try to create the same role again
        result = await rbac_manager.create_role(sample_role)
        assert result is False

    @pytest.mark.asyncio
    async def test_create_permission(
        self, rbac_manager: InMemoryRBACManager, sample_permission: Permission
    ) -> None:
        """Test permission creation."""
        result = await rbac_manager.create_permission(sample_permission)
        assert result is True

        # Try to create the same permission again
        result = await rbac_manager.create_permission(sample_permission)
        assert result is False

    @pytest.mark.asyncio
    async def test_assign_role_to_user(
        self, rbac_manager: InMemoryRBACManager, sample_user: User, sample_role: Role
    ) -> None:
        """Test role assignment to user."""
        # Create role first
        await rbac_manager.create_role(sample_role)

        # Assign role to user
        result = await rbac_manager.assign_role(sample_user.id, sample_role.name)
        assert result is True

        # Try to assign non-existent role
        result = await rbac_manager.assign_role(sample_user.id, "nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_revoke_role_from_user(
        self, rbac_manager: InMemoryRBACManager, sample_user: User, sample_role: Role
    ) -> None:
        """Test role revocation from user."""
        # Create role and assign it
        await rbac_manager.create_role(sample_role)
        await rbac_manager.assign_role(sample_user.id, sample_role.name)

        # Revoke role
        result = await rbac_manager.revoke_role(sample_user.id, sample_role.name)
        assert result is True

        # Try to revoke non-existent role
        result = await rbac_manager.revoke_role(sample_user.id, "nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_check_role(
        self, rbac_manager: InMemoryRBACManager, sample_user: User, sample_role: Role
    ) -> None:
        """Test role checking."""
        # Create role and assign it
        await rbac_manager.create_role(sample_role)
        await rbac_manager.assign_role(sample_user.id, sample_role.name)

        # Check if user has the role
        result = await rbac_manager.check_role(sample_user, sample_role.name)
        assert result is True

        # Check if user has a different role
        result = await rbac_manager.check_role(sample_user, "user")
        assert result is False

    @pytest.mark.asyncio
    async def test_assign_permission_to_role(
        self, rbac_manager: InMemoryRBACManager, sample_role: Role, sample_permission: Permission
    ) -> None:
        """Test permission assignment to role."""
        # Create role and permission
        await rbac_manager.create_role(sample_role)
        await rbac_manager.create_permission(sample_permission)

        # Assign permission to role
        permission_key = f"{sample_permission.resource}:{sample_permission.action}"
        result = await rbac_manager.assign_permission_to_role(sample_role.name, permission_key)
        assert result is True

        # Try to assign non-existent permission
        result = await rbac_manager.assign_permission_to_role(
            sample_role.name, "nonexistent:action"
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_check_permission(
        self,
        rbac_manager: InMemoryRBACManager,
        sample_user: User,
        sample_role: Role,
        sample_permission: Permission,
    ) -> None:
        """Test permission checking."""
        # Create role and permission
        await rbac_manager.create_role(sample_role)
        await rbac_manager.create_permission(sample_permission)

        # Assign role to user and permission to role
        await rbac_manager.assign_role(sample_user.id, sample_role.name)
        permission_key = f"{sample_permission.resource}:{sample_permission.action}"
        await rbac_manager.assign_permission_to_role(sample_role.name, permission_key)

        # Check if user has the permission
        result = await rbac_manager.check_permission(
            sample_user, sample_permission.resource, sample_permission.action
        )
        assert result is True

        # Check if user has a different permission
        result = await rbac_manager.check_permission(sample_user, "posts", "write")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_user_roles(
        self, rbac_manager: InMemoryRBACManager, sample_user: User, sample_role: Role
    ) -> None:
        """Test getting user roles."""
        # Create role and assign it
        await rbac_manager.create_role(sample_role)
        await rbac_manager.assign_role(sample_user.id, sample_role.name)

        # Get user roles
        roles = await rbac_manager.get_user_roles(sample_user.id)
        assert len(roles) == 1
        assert roles[0].name == sample_role.name

    @pytest.mark.asyncio
    async def test_get_user_permissions(
        self,
        rbac_manager: InMemoryRBACManager,
        sample_user: User,
        sample_role: Role,
        sample_permission: Permission,
    ) -> None:
        """Test getting user permissions."""
        # Create role and permission
        await rbac_manager.create_role(sample_role)
        await rbac_manager.create_permission(sample_permission)

        # Assign role to user and permission to role
        await rbac_manager.assign_role(sample_user.id, sample_role.name)
        permission_key = f"{sample_permission.resource}:{sample_permission.action}"
        await rbac_manager.assign_permission_to_role(sample_role.name, permission_key)

        # Get user permissions
        permissions = await rbac_manager.get_user_permissions(sample_user.id)
        assert len(permissions) == 1
        assert permissions[0].name == sample_permission.name

    @pytest.mark.asyncio
    async def test_assign_permission_directly_to_user(
        self, rbac_manager: InMemoryRBACManager, sample_user: User, sample_permission: Permission
    ) -> None:
        """Test direct permission assignment to user."""
        # Create permission
        await rbac_manager.create_permission(sample_permission)

        # Assign permission directly to user
        permission_key = f"{sample_permission.resource}:{sample_permission.action}"
        result = await rbac_manager.assign_permission_to_user(sample_user.id, permission_key)
        assert result is True

        # Check if user has the permission
        result = await rbac_manager.check_permission(
            sample_user, sample_permission.resource, sample_permission.action
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_get_all_roles(
        self, rbac_manager: InMemoryRBACManager, sample_role: Role
    ) -> None:
        """Test getting all roles."""
        # Create role
        await rbac_manager.create_role(sample_role)

        # Get all roles
        roles = await rbac_manager.get_all_roles()
        assert len(roles) == 1
        assert roles[0].name == sample_role.name

    @pytest.mark.asyncio
    async def test_get_all_permissions(
        self, rbac_manager: InMemoryRBACManager, sample_permission: Permission
    ) -> None:
        """Test getting all permissions."""
        # Create permission
        await rbac_manager.create_permission(sample_permission)

        # Get all permissions
        permissions = await rbac_manager.get_all_permissions()
        assert len(permissions) == 1
        assert permissions[0].name == sample_permission.name

    @pytest.mark.asyncio
    async def test_delete_role(
        self, rbac_manager: InMemoryRBACManager, sample_user: User, sample_role: Role
    ) -> None:
        """Test role deletion."""
        # Create role and assign it
        await rbac_manager.create_role(sample_role)
        await rbac_manager.assign_role(sample_user.id, sample_role.name)

        # Delete role
        result = await rbac_manager.delete_role(sample_role.name)
        assert result is True

        # Check if user still has the role
        result = await rbac_manager.check_role(sample_user, sample_role.name)
        assert result is False

        # Try to delete non-existent role
        result = await rbac_manager.delete_role("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_permission(
        self, rbac_manager: InMemoryRBACManager, sample_role: Role, sample_permission: Permission
    ) -> None:
        """Test permission deletion."""
        # Create role and permission
        await rbac_manager.create_role(sample_role)
        await rbac_manager.create_permission(sample_permission)

        # Assign permission to role
        permission_key = f"{sample_permission.resource}:{sample_permission.action}"
        await rbac_manager.assign_permission_to_role(sample_role.name, permission_key)

        # Delete permission
        result = await rbac_manager.delete_permission(permission_key)
        assert result is True

        # Try to delete non-existent permission
        result = await rbac_manager.delete_permission("nonexistent:action")
        assert result is False

    @pytest.mark.asyncio
    async def test_complex_rbac_scenario(self, rbac_manager: InMemoryRBACManager) -> None:
        """Test a complex RBAC scenario with multiple users, roles, and permissions."""
        # Create users
        admin_user = User(
            id="admin",
            username="admin",
            email="admin@example.com",
            is_active=True,
            is_verified=True,
            roles=[],
            permissions=[],
            created_at=datetime.now(),
        )
        editor_user = User(
            id="editor",
            username="editor",
            email="editor@example.com",
            is_active=True,
            is_verified=True,
            roles=[],
            permissions=[],
            created_at=datetime.now(),
        )
        viewer_user = User(
            id="viewer",
            username="viewer",
            email="viewer@example.com",
            is_active=True,
            is_verified=True,
            roles=[],
            permissions=[],
            created_at=datetime.now(),
        )

        # Create roles
        admin_role = Role(
            name="admin",
            description="Administrator",
            permissions=[],
            is_system_role=False,
            created_at=datetime.now(),
        )
        editor_role = Role(
            name="editor",
            description="Editor",
            permissions=[],
            is_system_role=False,
            created_at=datetime.now(),
        )
        viewer_role = Role(
            name="viewer",
            description="Viewer",
            permissions=[],
            is_system_role=False,
            created_at=datetime.now(),
        )

        # Create permissions
        read_users = Permission(
            name="read_users",
            description="Read users",
            resource="users",
            action="read",
            created_at=datetime.now(),
        )
        write_users = Permission(
            name="write_users",
            description="Write users",
            resource="users",
            action="write",
            created_at=datetime.now(),
        )
        delete_users = Permission(
            name="delete_users",
            description="Delete users",
            resource="users",
            action="delete",
            created_at=datetime.now(),
        )
        read_posts = Permission(
            name="read_posts",
            description="Read posts",
            resource="posts",
            action="read",
            created_at=datetime.now(),
        )
        write_posts = Permission(
            name="write_posts",
            description="Write posts",
            resource="posts",
            action="write",
            created_at=datetime.now(),
        )

        # Create roles and permissions
        await rbac_manager.create_role(admin_role)
        await rbac_manager.create_role(editor_role)
        await rbac_manager.create_role(viewer_role)

        await rbac_manager.create_permission(read_users)
        await rbac_manager.create_permission(write_users)
        await rbac_manager.create_permission(delete_users)
        await rbac_manager.create_permission(read_posts)
        await rbac_manager.create_permission(write_posts)

        # Assign permissions to roles
        await rbac_manager.assign_permission_to_role("admin", "users:read")
        await rbac_manager.assign_permission_to_role("admin", "users:write")
        await rbac_manager.assign_permission_to_role("admin", "users:delete")
        await rbac_manager.assign_permission_to_role("admin", "posts:read")
        await rbac_manager.assign_permission_to_role("admin", "posts:write")

        await rbac_manager.assign_permission_to_role("editor", "users:read")
        await rbac_manager.assign_permission_to_role("editor", "posts:read")
        await rbac_manager.assign_permission_to_role("editor", "posts:write")

        await rbac_manager.assign_permission_to_role("viewer", "users:read")
        await rbac_manager.assign_permission_to_role("viewer", "posts:read")

        # Assign roles to users
        await rbac_manager.assign_role("admin", "admin")
        await rbac_manager.assign_role("editor", "editor")
        await rbac_manager.assign_role("viewer", "viewer")

        # Test permissions
        # Admin should have all permissions
        assert await rbac_manager.check_permission(admin_user, "users", "read") is True
        assert await rbac_manager.check_permission(admin_user, "users", "write") is True
        assert await rbac_manager.check_permission(admin_user, "users", "delete") is True
        assert await rbac_manager.check_permission(admin_user, "posts", "read") is True
        assert await rbac_manager.check_permission(admin_user, "posts", "write") is True

        # Editor should have limited permissions
        assert await rbac_manager.check_permission(editor_user, "users", "read") is True
        assert await rbac_manager.check_permission(editor_user, "users", "write") is False
        assert await rbac_manager.check_permission(editor_user, "users", "delete") is False
        assert await rbac_manager.check_permission(editor_user, "posts", "read") is True
        assert await rbac_manager.check_permission(editor_user, "posts", "write") is True

        # Viewer should have read-only permissions
        assert await rbac_manager.check_permission(viewer_user, "users", "read") is True
        assert await rbac_manager.check_permission(viewer_user, "users", "write") is False
        assert await rbac_manager.check_permission(viewer_user, "users", "delete") is False
        assert await rbac_manager.check_permission(viewer_user, "posts", "read") is True
        assert await rbac_manager.check_permission(viewer_user, "posts", "write") is False
