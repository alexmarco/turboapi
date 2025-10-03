"""Session management system for secure user sessions."""

import secrets
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from datetime import timedelta
from typing import Any

from .interfaces import User


class SessionData:
    """
    Session data container.

    Parameters
    ----------
    session_id : str
        Unique session identifier.
    user_id : str
        User ID associated with the session.
    created_at : datetime
        Session creation timestamp.
    expires_at : datetime
        Session expiration timestamp.
    last_activity : datetime
        Last activity timestamp.
    ip_address : str, optional
        IP address of the client.
    user_agent : str, optional
        User agent string of the client.
    extra_data : dict[str, Any], optional
        Additional session data.
    """

    def __init__(
        self,
        session_id: str,
        user_id: str,
        created_at: datetime,
        expires_at: datetime,
        last_activity: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
        extra_data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize session data."""
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = created_at
        self.expires_at = expires_at
        self.last_activity = last_activity
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.extra_data = extra_data or {}

    def is_expired(self) -> bool:
        """
        Check if the session is expired.

        Returns
        -------
        bool
            True if the session is expired.
        """
        return datetime.now() > self.expires_at

    def is_active(self) -> bool:
        """
        Check if the session is active (not expired).

        Returns
        -------
        bool
            True if the session is active.
        """
        return not self.is_expired()

    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.now()

    def extend_expiration(self, duration: timedelta) -> None:
        """
        Extend the session expiration time.

        Parameters
        ----------
        duration : timedelta
            Duration to extend the session.
        """
        self.expires_at += duration

    def to_dict(self) -> dict[str, Any]:
        """
        Convert session data to dictionary.

        Returns
        -------
        dict[str, Any]
            Session data as dictionary.
        """
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "extra_data": self.extra_data,
        }


class BaseSessionManager(ABC):
    """
    Base interface for session managers.

    Defines methods for managing user sessions including creation,
    validation, and cleanup.
    """

    @abstractmethod
    async def create_session(
        self,
        user: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
        duration: timedelta | None = None,
    ) -> SessionData:
        """
        Create a new session for a user.

        Parameters
        ----------
        user : User
            User to create session for.
        ip_address : str, optional
            IP address of the client.
        user_agent : str, optional
            User agent string of the client.
        duration : timedelta, optional
            Session duration. Defaults to 24 hours.

        Returns
        -------
        SessionData
            Created session data.
        """
        ...

    @abstractmethod
    async def get_session(self, session_id: str) -> SessionData | None:
        """
        Get session data by session ID.

        Parameters
        ----------
        session_id : str
            Session ID to retrieve.

        Returns
        -------
        SessionData | None
            Session data if found and active, None otherwise.
        """
        ...

    @abstractmethod
    async def validate_session(self, session_id: str) -> bool:
        """
        Validate if a session is active and not expired.

        Parameters
        ----------
        session_id : str
            Session ID to validate.

        Returns
        -------
        bool
            True if the session is valid.
        """
        ...

    @abstractmethod
    async def refresh_session(self, session_id: str, duration: timedelta | None = None) -> bool:
        """
        Refresh a session by extending its expiration time.

        Parameters
        ----------
        session_id : str
            Session ID to refresh.
        duration : timedelta, optional
            Duration to extend. Defaults to 24 hours.

        Returns
        -------
        bool
            True if the session was refreshed successfully.
        """
        ...

    @abstractmethod
    async def revoke_session(self, session_id: str) -> bool:
        """
        Revoke a session.

        Parameters
        ----------
        session_id : str
            Session ID to revoke.

        Returns
        -------
        bool
            True if the session was revoked successfully.
        """
        ...

    @abstractmethod
    async def revoke_user_sessions(self, user_id: str) -> int:
        """
        Revoke all sessions for a user.

        Parameters
        ----------
        user_id : str
            User ID to revoke sessions for.

        Returns
        -------
        int
            Number of sessions revoked.
        """
        ...

    @abstractmethod
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.

        Returns
        -------
        int
            Number of sessions cleaned up.
        """
        ...

    @abstractmethod
    async def get_user_sessions(self, user_id: str) -> list[SessionData]:
        """
        Get all active sessions for a user.

        Parameters
        ----------
        user_id : str
            User ID to get sessions for.

        Returns
        -------
        list[SessionData]
            List of active sessions for the user.
        """
        ...


class InMemorySessionManager(BaseSessionManager):
    """
    In-memory implementation of session manager.

    This implementation stores sessions in memory. Suitable for
    development and testing environments.
    """

    def __init__(self, default_duration: timedelta | None = None) -> None:
        """
        Initialize the session manager.

        Parameters
        ----------
        default_duration : timedelta, optional
            Default session duration. Defaults to 24 hours.
        """
        self._sessions: dict[str, SessionData] = {}
        self._default_duration = default_duration or timedelta(hours=24)

    def _generate_session_id(self) -> str:
        """
        Generate a secure session ID.

        Returns
        -------
        str
            Secure session ID.
        """
        return secrets.token_urlsafe(32)

    async def create_session(
        self,
        user: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
        duration: timedelta | None = None,
    ) -> SessionData:
        """
        Create a new session for a user.

        Parameters
        ----------
        user : User
            User to create session for.
        ip_address : str, optional
            IP address of the client.
        user_agent : str, optional
            User agent string of the client.
        duration : timedelta, optional
            Session duration. Defaults to configured default.

        Returns
        -------
        SessionData
            Created session data.
        """
        session_id = self._generate_session_id()
        now = datetime.now()
        session_duration = duration or self._default_duration

        session_data = SessionData(
            session_id=session_id,
            user_id=user.id,
            created_at=now,
            expires_at=now + session_duration,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self._sessions[session_id] = session_data
        return session_data

    async def get_session(self, session_id: str) -> SessionData | None:
        """
        Get session data by session ID.

        Parameters
        ----------
        session_id : str
            Session ID to retrieve.

        Returns
        -------
        SessionData | None
            Session data if found and active, None otherwise.
        """
        session = self._sessions.get(session_id)
        if session is None or session.is_expired():
            if session and session.is_expired():
                del self._sessions[session_id]
            return None

        return session

    async def validate_session(self, session_id: str) -> bool:
        """
        Validate if a session is active and not expired.

        Parameters
        ----------
        session_id : str
            Session ID to validate.

        Returns
        -------
        bool
            True if the session is valid.
        """
        session = await self.get_session(session_id)
        return session is not None

    async def refresh_session(self, session_id: str, duration: timedelta | None = None) -> bool:
        """
        Refresh a session by extending its expiration time.

        Parameters
        ----------
        session_id : str
            Session ID to refresh.
        duration : timedelta, optional
            Duration to extend. Defaults to configured default.

        Returns
        -------
        bool
            True if the session was refreshed successfully.
        """
        session = self._sessions.get(session_id)
        if session is None or session.is_expired():
            return False

        session.update_activity()
        extend_duration = duration or self._default_duration
        session.extend_expiration(extend_duration)
        return True

    async def revoke_session(self, session_id: str) -> bool:
        """
        Revoke a session.

        Parameters
        ----------
        session_id : str
            Session ID to revoke.

        Returns
        -------
        bool
            True if the session was revoked successfully.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    async def revoke_user_sessions(self, user_id: str) -> int:
        """
        Revoke all sessions for a user.

        Parameters
        ----------
        user_id : str
            User ID to revoke sessions for.

        Returns
        -------
        int
            Number of sessions revoked.
        """
        sessions_to_remove = [
            session_id
            for session_id, session in self._sessions.items()
            if session.user_id == user_id
        ]

        for session_id in sessions_to_remove:
            del self._sessions[session_id]

        return len(sessions_to_remove)

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.

        Returns
        -------
        int
            Number of sessions cleaned up.
        """
        expired_sessions = [
            session_id for session_id, session in self._sessions.items() if session.is_expired()
        ]

        for session_id in expired_sessions:
            del self._sessions[session_id]

        return len(expired_sessions)

    async def get_user_sessions(self, user_id: str) -> list[SessionData]:
        """
        Get all active sessions for a user.

        Parameters
        ----------
        user_id : str
            User ID to get sessions for.

        Returns
        -------
        list[SessionData]
            List of active sessions for the user.
        """
        active_sessions = []
        for session in self._sessions.values():
            if session.user_id == user_id and session.is_active():
                active_sessions.append(session)

        return active_sessions

    async def get_all_sessions(self) -> list[SessionData]:
        """
        Get all active sessions.

        Returns
        -------
        list[SessionData]
            List of all active sessions.
        """
        return [session for session in self._sessions.values() if session.is_active()]

    async def get_session_count(self) -> int:
        """
        Get the total number of active sessions.

        Returns
        -------
        int
            Number of active sessions.
        """
        return len([s for s in self._sessions.values() if s.is_active()])

    async def get_user_session_count(self, user_id: str) -> int:
        """
        Get the number of active sessions for a user.

        Parameters
        ----------
        user_id : str
            User ID to count sessions for.

        Returns
        -------
        int
            Number of active sessions for the user.
        """
        return len(await self.get_user_sessions(user_id))
