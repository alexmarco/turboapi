"""Tests for session management system."""

from datetime import datetime
from datetime import timedelta

import pytest

from turboapi.security.interfaces import User
from turboapi.security.session import InMemorySessionManager
from turboapi.security.session import SessionData


class TestSessionData:
    """Test cases for SessionData."""

    def test_session_data_creation(self) -> None:
        """Test session data creation."""
        now = datetime.now()
        session_data = SessionData(
            session_id="test_session",
            user_id="user1",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            last_activity=now,
            ip_address="127.0.0.1",
            user_agent="Test Agent",
        )

        assert session_data.session_id == "test_session"
        assert session_data.user_id == "user1"
        assert session_data.ip_address == "127.0.0.1"
        assert session_data.user_agent == "Test Agent"
        assert session_data.is_active() is True

    def test_session_expiration(self) -> None:
        """Test session expiration logic."""
        now = datetime.now()
        expired_session = SessionData(
            session_id="expired",
            user_id="user1",
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            last_activity=now - timedelta(hours=1),
        )

        assert expired_session.is_expired() is True
        assert expired_session.is_active() is False

    def test_session_activity_update(self) -> None:
        """Test session activity update."""
        now = datetime.now()
        session_data = SessionData(
            session_id="test",
            user_id="user1",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            last_activity=now,
        )

        original_activity = session_data.last_activity
        import time

        time.sleep(0.001)  # Small delay to ensure time difference
        session_data.update_activity()

        assert session_data.last_activity > original_activity

    def test_session_extension(self) -> None:
        """Test session expiration extension."""
        now = datetime.now()
        session_data = SessionData(
            session_id="test",
            user_id="user1",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            last_activity=now,
        )

        original_expiry = session_data.expires_at
        session_data.extend_expiration(timedelta(hours=2))

        assert session_data.expires_at == original_expiry + timedelta(hours=2)

    def test_session_to_dict(self) -> None:
        """Test session data serialization."""
        now = datetime.now()
        session_data = SessionData(
            session_id="test",
            user_id="user1",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            last_activity=now,
            ip_address="127.0.0.1",
            user_agent="Test Agent",
            extra_data={"key": "value"},
        )

        data_dict = session_data.to_dict()

        assert data_dict["session_id"] == "test"
        assert data_dict["user_id"] == "user1"
        assert data_dict["ip_address"] == "127.0.0.1"
        assert data_dict["user_agent"] == "Test Agent"
        assert data_dict["extra_data"] == {"key": "value"}
        assert "created_at" in data_dict
        assert "expires_at" in data_dict
        assert "last_activity" in data_dict


class TestInMemorySessionManager:
    """Test cases for InMemorySessionManager."""

    @pytest.fixture
    def session_manager(self) -> InMemorySessionManager:
        """Create a session manager instance."""
        return InMemorySessionManager()

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

    @pytest.mark.asyncio
    async def test_create_session(
        self, session_manager: InMemorySessionManager, sample_user: User
    ) -> None:
        """Test session creation."""
        session = await session_manager.create_session(
            sample_user,
            ip_address="127.0.0.1",
            user_agent="Test Agent",
        )

        assert session.user_id == sample_user.id
        assert session.ip_address == "127.0.0.1"
        assert session.user_agent == "Test Agent"
        assert session.is_active() is True
        assert len(session.session_id) > 0

    @pytest.mark.asyncio
    async def test_get_session(
        self, session_manager: InMemorySessionManager, sample_user: User
    ) -> None:
        """Test session retrieval."""
        # Create session
        created_session = await session_manager.create_session(sample_user)

        # Retrieve session
        retrieved_session = await session_manager.get_session(created_session.session_id)

        assert retrieved_session is not None
        assert retrieved_session.session_id == created_session.session_id
        assert retrieved_session.user_id == sample_user.id

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, session_manager: InMemorySessionManager) -> None:
        """Test retrieval of non-existent session."""
        session = await session_manager.get_session("nonexistent")
        assert session is None

    @pytest.mark.asyncio
    async def test_validate_session(
        self, session_manager: InMemorySessionManager, sample_user: User
    ) -> None:
        """Test session validation."""
        # Create session
        session = await session_manager.create_session(sample_user)

        # Validate session
        is_valid = await session_manager.validate_session(session.session_id)
        assert is_valid is True

        # Validate non-existent session
        is_valid = await session_manager.validate_session("nonexistent")
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_refresh_session(
        self, session_manager: InMemorySessionManager, sample_user: User
    ) -> None:
        """Test session refresh."""
        # Create session
        session = await session_manager.create_session(sample_user)
        original_expiry = session.expires_at

        # Refresh session
        result = await session_manager.refresh_session(session.session_id)
        assert result is True

        # Check if session was extended
        refreshed_session = await session_manager.get_session(session.session_id)
        assert refreshed_session is not None
        assert refreshed_session.expires_at > original_expiry

    @pytest.mark.asyncio
    async def test_refresh_nonexistent_session(
        self, session_manager: InMemorySessionManager
    ) -> None:
        """Test refresh of non-existent session."""
        result = await session_manager.refresh_session("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_revoke_session(
        self, session_manager: InMemorySessionManager, sample_user: User
    ) -> None:
        """Test session revocation."""
        # Create session
        session = await session_manager.create_session(sample_user)

        # Revoke session
        result = await session_manager.revoke_session(session.session_id)
        assert result is True

        # Check if session is gone
        retrieved_session = await session_manager.get_session(session.session_id)
        assert retrieved_session is None

    @pytest.mark.asyncio
    async def test_revoke_nonexistent_session(
        self, session_manager: InMemorySessionManager
    ) -> None:
        """Test revocation of non-existent session."""
        result = await session_manager.revoke_session("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_revoke_user_sessions(
        self, session_manager: InMemorySessionManager, sample_user: User
    ) -> None:
        """Test revocation of all user sessions."""
        # Create multiple sessions for the same user
        session1 = await session_manager.create_session(sample_user)
        session2 = await session_manager.create_session(sample_user)

        # Create session for different user
        other_user = User(
            id="user2",
            username="otheruser",
            email="other@example.com",
            is_active=True,
            is_verified=True,
            roles=[],
            permissions=[],
            created_at=datetime.now(),
        )
        other_session = await session_manager.create_session(other_user)

        # Revoke all sessions for user1
        revoked_count = await session_manager.revoke_user_sessions(sample_user.id)
        assert revoked_count == 2

        # Check that user1 sessions are gone
        assert await session_manager.get_session(session1.session_id) is None
        assert await session_manager.get_session(session2.session_id) is None

        # Check that other user's session still exists
        assert await session_manager.get_session(other_session.session_id) is not None

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(
        self, session_manager: InMemorySessionManager, sample_user: User
    ) -> None:
        """Test cleanup of expired sessions."""
        # Create a session with short duration
        short_session = await session_manager.create_session(
            sample_user, duration=timedelta(milliseconds=1)
        )

        # Create a normal session
        normal_session = await session_manager.create_session(sample_user)

        # Wait for short session to expire
        import time

        time.sleep(0.01)

        # Cleanup expired sessions
        cleaned_count = await session_manager.cleanup_expired_sessions()
        assert cleaned_count == 1

        # Check that expired session is gone
        assert await session_manager.get_session(short_session.session_id) is None

        # Check that normal session still exists
        assert await session_manager.get_session(normal_session.session_id) is not None

    @pytest.mark.asyncio
    async def test_get_user_sessions(
        self, session_manager: InMemorySessionManager, sample_user: User
    ) -> None:
        """Test getting all sessions for a user."""
        # Create multiple sessions for the same user
        session1 = await session_manager.create_session(sample_user)
        session2 = await session_manager.create_session(sample_user)

        # Create session for different user
        other_user = User(
            id="user2",
            username="otheruser",
            email="other@example.com",
            is_active=True,
            is_verified=True,
            roles=[],
            permissions=[],
            created_at=datetime.now(),
        )
        await session_manager.create_session(other_user)

        # Get sessions for user1
        user_sessions = await session_manager.get_user_sessions(sample_user.id)
        assert len(user_sessions) == 2

        session_ids = {session.session_id for session in user_sessions}
        assert session1.session_id in session_ids
        assert session2.session_id in session_ids

    @pytest.mark.asyncio
    async def test_get_all_sessions(
        self, session_manager: InMemorySessionManager, sample_user: User
    ) -> None:
        """Test getting all active sessions."""
        # Create multiple sessions
        session1 = await session_manager.create_session(sample_user)

        other_user = User(
            id="user2",
            username="otheruser",
            email="other@example.com",
            is_active=True,
            is_verified=True,
            roles=[],
            permissions=[],
            created_at=datetime.now(),
        )
        session2 = await session_manager.create_session(other_user)

        # Get all sessions
        all_sessions = await session_manager.get_all_sessions()
        assert len(all_sessions) == 2

        session_ids = {session.session_id for session in all_sessions}
        assert session1.session_id in session_ids
        assert session2.session_id in session_ids

    @pytest.mark.asyncio
    async def test_get_session_count(
        self, session_manager: InMemorySessionManager, sample_user: User
    ) -> None:
        """Test getting session count."""
        # Initially no sessions
        count = await session_manager.get_session_count()
        assert count == 0

        # Create sessions
        await session_manager.create_session(sample_user)
        await session_manager.create_session(sample_user)

        # Check count
        count = await session_manager.get_session_count()
        assert count == 2

    @pytest.mark.asyncio
    async def test_get_user_session_count(
        self, session_manager: InMemorySessionManager, sample_user: User
    ) -> None:
        """Test getting session count for a specific user."""
        # Create sessions for user1
        await session_manager.create_session(sample_user)
        await session_manager.create_session(sample_user)

        # Create session for different user
        other_user = User(
            id="user2",
            username="otheruser",
            email="other@example.com",
            is_active=True,
            is_verified=True,
            roles=[],
            permissions=[],
            created_at=datetime.now(),
        )
        await session_manager.create_session(other_user)

        # Check user1 session count
        count = await session_manager.get_user_session_count(sample_user.id)
        assert count == 2

        # Check user2 session count
        count = await session_manager.get_user_session_count(other_user.id)
        assert count == 1

    @pytest.mark.asyncio
    async def test_custom_session_duration(self, sample_user: User) -> None:
        """Test session creation with custom duration."""
        custom_duration = timedelta(hours=2)
        session_manager = InMemorySessionManager(default_duration=custom_duration)

        session = await session_manager.create_session(sample_user)

        # Check that session expires after custom duration
        expected_expiry = session.created_at + custom_duration
        assert abs((session.expires_at - expected_expiry).total_seconds()) < 1

    @pytest.mark.asyncio
    async def test_session_activity_tracking(
        self, session_manager: InMemorySessionManager, sample_user: User
    ) -> None:
        """Test session activity tracking."""
        # Create session
        session = await session_manager.create_session(sample_user)
        original_activity = session.last_activity

        # Small delay to ensure time difference
        import time

        time.sleep(0.001)

        # Refresh session (should update activity)
        await session_manager.refresh_session(session.session_id)

        # Get updated session
        updated_session = await session_manager.get_session(session.session_id)
        assert updated_session is not None
        assert updated_session.last_activity > original_activity
