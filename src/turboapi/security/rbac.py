"""RBAC (Role-Based Access Control) implementation."""

from .interfaces import BaseRBACManager
from .interfaces import Permission
from .interfaces import Role
from .interfaces import User


class InMemoryRBACManager(BaseRBACManager):
    """
    In-memory implementation of RBAC manager.

    This implementation stores roles, permissions, and user assignments
    in memory. Suitable for development and testing environments.
    """

    def __init__(self) -> None:
        """Initialize the RBAC manager."""
        self._roles: dict[str, Role] = {}
        self._permissions: dict[str, Permission] = {}
        self._user_roles: dict[str, set[str]] = {}
        self._role_permissions: dict[str, set[str]] = {}
        self._user_permissions: dict[str, set[str]] = {}

    async def check_permission(self, user: User, resource: str, action: str) -> bool:
        """
        Check if a user has permission to perform an action on a resource.

        Parameters
        ----------
        user : User
            User to check.
        resource : str
            Resource to access.
        action : str
            Action to perform.

        Returns
        -------
        bool
            True if the user has the permission.
        """
        user_permissions = await self.get_user_permissions(user.id)

        for permission in user_permissions:
            if permission.resource == resource and permission.action == action:
                return True

        return False

    async def check_role(self, user: User, role_name: str) -> bool:
        """
        Check if a user has a specific role.

        Parameters
        ----------
        user : User
            User to check.
        role_name : str
            Name of the role.

        Returns
        -------
        bool
            True if the user has the role.
        """
        user_roles = self._user_roles.get(user.id, set())
        return role_name in user_roles

    async def assign_role(self, user_id: str, role_name: str) -> bool:
        """
        Assign a role to a user.

        Parameters
        ----------
        user_id : str
            User ID.
        role_name : str
            Name of the role to assign.

        Returns
        -------
        bool
            True if the assignment was successful.
        """
        if role_name not in self._roles:
            return False

        if user_id not in self._user_roles:
            self._user_roles[user_id] = set()

        self._user_roles[user_id].add(role_name)
        return True

    async def revoke_role(self, user_id: str, role_name: str) -> bool:
        """
        Revoke a role from a user.

        Parameters
        ----------
        user_id : str
            User ID.
        role_name : str
            Name of the role to revoke.

        Returns
        -------
        bool
            True if the revocation was successful.
        """
        if user_id not in self._user_roles:
            return False

        if role_name not in self._user_roles[user_id]:
            return False

        self._user_roles[user_id].discard(role_name)
        return True

    async def create_role(self, role: Role) -> bool:
        """
        Create a new role in the system.

        Parameters
        ----------
        role : Role
            Role to create.

        Returns
        -------
        bool
            True if the creation was successful.
        """
        if role.name in self._roles:
            return False

        self._roles[role.name] = role
        self._role_permissions[role.name] = set()
        return True

    async def create_permission(self, permission: Permission) -> bool:
        """
        Create a new permission in the system.

        Parameters
        ----------
        permission : Permission
            Permission to create.

        Returns
        -------
        bool
            True if the creation was successful.
        """
        permission_key = f"{permission.resource}:{permission.action}"
        if permission_key in self._permissions:
            return False

        self._permissions[permission_key] = permission
        return True

    async def get_user_roles(self, user_id: str) -> list[Role]:
        """
        Get all roles of a user.

        Parameters
        ----------
        user_id : str
            User ID.

        Returns
        -------
        list[Role]
            List of user roles.
        """
        user_role_names = self._user_roles.get(user_id, set())
        return [self._roles[name] for name in user_role_names if name in self._roles]

    async def get_user_permissions(self, user_id: str) -> list[Permission]:
        """
        Get all permissions of a user (direct + from roles).

        Parameters
        ----------
        user_id : str
            User ID.

        Returns
        -------
        list[Permission]
            List of user permissions.
        """
        permissions = []
        seen_keys = set()

        # Direct user permissions
        user_permission_keys = self._user_permissions.get(user_id, set())
        for key in user_permission_keys:
            if key in self._permissions and key not in seen_keys:
                permissions.append(self._permissions[key])
                seen_keys.add(key)

        # Permissions from roles
        user_role_names = self._user_roles.get(user_id, set())
        for role_name in user_role_names:
            role_permission_keys = self._role_permissions.get(role_name, set())
            for key in role_permission_keys:
                if key in self._permissions and key not in seen_keys:
                    permissions.append(self._permissions[key])
                    seen_keys.add(key)

        return permissions

    async def assign_permission_to_role(self, role_name: str, permission_key: str) -> bool:
        """
        Assign a permission to a role.

        Parameters
        ----------
        role_name : str
            Name of the role.
        permission_key : str
            Permission key (resource:action).

        Returns
        -------
        bool
            True if the assignment was successful.
        """
        if role_name not in self._roles or permission_key not in self._permissions:
            return False

        if role_name not in self._role_permissions:
            self._role_permissions[role_name] = set()

        self._role_permissions[role_name].add(permission_key)
        return True

    async def revoke_permission_from_role(self, role_name: str, permission_key: str) -> bool:
        """
        Revoke a permission from a role.

        Parameters
        ----------
        role_name : str
            Name of the role.
        permission_key : str
            Permission key (resource:action).

        Returns
        -------
        bool
            True if the revocation was successful.
        """
        if role_name not in self._role_permissions:
            return False

        self._role_permissions[role_name].discard(permission_key)
        return True

    async def assign_permission_to_user(self, user_id: str, permission_key: str) -> bool:
        """
        Assign a permission directly to a user.

        Parameters
        ----------
        user_id : str
            User ID.
        permission_key : str
            Permission key (resource:action).

        Returns
        -------
        bool
            True if the assignment was successful.
        """
        if permission_key not in self._permissions:
            return False

        if user_id not in self._user_permissions:
            self._user_permissions[user_id] = set()

        self._user_permissions[user_id].add(permission_key)
        return True

    async def revoke_permission_from_user(self, user_id: str, permission_key: str) -> bool:
        """
        Revoke a permission directly from a user.

        Parameters
        ----------
        user_id : str
            User ID.
        permission_key : str
            Permission key (resource:action).

        Returns
        -------
        bool
            True if the revocation was successful.
        """
        if user_id not in self._user_permissions:
            return False

        self._user_permissions[user_id].discard(permission_key)
        return True

    async def get_all_roles(self) -> list[Role]:
        """
        Get all roles in the system.

        Returns
        -------
        list[Role]
            List of all roles.
        """
        return list(self._roles.values())

    async def get_all_permissions(self) -> list[Permission]:
        """
        Get all permissions in the system.

        Returns
        -------
        list[Permission]
            List of all permissions.
        """
        return list(self._permissions.values())

    async def delete_role(self, role_name: str) -> bool:
        """
        Delete a role from the system.

        Parameters
        ----------
        role_name : str
            Name of the role to delete.

        Returns
        -------
        bool
            True if the deletion was successful.
        """
        if role_name not in self._roles:
            return False

        # Remove role from all users
        for user_id in self._user_roles:
            self._user_roles[user_id].discard(role_name)

        # Remove role and its permissions
        del self._roles[role_name]
        if role_name in self._role_permissions:
            del self._role_permissions[role_name]

        return True

    async def delete_permission(self, permission_key: str) -> bool:
        """
        Delete a permission from the system.

        Parameters
        ----------
        permission_key : str
            Permission key (resource:action) to delete.

        Returns
        -------
        bool
            True if the deletion was successful.
        """
        if permission_key not in self._permissions:
            return False

        # Remove permission from all roles
        for role_name in self._role_permissions:
            self._role_permissions[role_name].discard(permission_key)

        # Remove permission from all users
        for user_id in self._user_permissions:
            self._user_permissions[user_id].discard(permission_key)

        # Remove permission
        del self._permissions[permission_key]
        return True
