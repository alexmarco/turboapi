# TurboAPI Examples

This document provides practical examples of common patterns and use cases with TurboAPI.

## Table of Contents

- [Basic API Controller](#basic-api-controller)
- [Authentication and Authorization](#authentication-and-authorization)
- [Database Operations](#database-operations)
- [Caching Strategies](#caching-strategies)
- [Background Tasks](#background-tasks)
- [Observability](#observability)
- [Error Handling](#error-handling)
- [Testing Examples](#testing-examples)

## Basic API Controller

### Simple Controller with CRUD Operations

```python
# apps/users/api.py
from turboapi.web import Controller, Get, Post, Put, Delete
from turboapi.security import Authenticate, RequireRole
from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "user"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: str

@Controller("/api/v1/users")
class UserController:
    
    def __init__(self, user_service: "UserService"):
        self.user_service = user_service
    
    @Get("/")
    @Authenticate()
    async def list_users(self) -> List[UserResponse]:
        """List all users"""
        users = await self.user_service.get_all_users()
        return [UserResponse(**user.dict()) for user in users]
    
    @Get("/{user_id}")
    @Authenticate()
    async def get_user(self, user_id: str) -> UserResponse:
        """Get user by ID"""
        user = await self.user_service.get_user(user_id)
        return UserResponse(**user.dict())
    
    @Post("/")
    @Authenticate()
    @RequireRole("admin")
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        user = await self.user_service.create_user(user_data.dict())
        return UserResponse(**user.dict())
    
    @Put("/{user_id}")
    @Authenticate()
    @RequireRole("admin")
    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """Update user"""
        user = await self.user_service.update_user(user_id, user_data.dict(exclude_unset=True))
        return UserResponse(**user.dict())
    
    @Delete("/{user_id}")
    @Authenticate()
    @RequireRole("admin")
    async def delete_user(self, user_id: str) -> dict:
        """Delete user"""
        await self.user_service.delete_user(user_id)
        return {"message": "User deleted successfully"}
```

## Authentication and Authorization

### JWT Authentication with Role-Based Access

```python
# apps/auth/api.py
from turboapi.web import Controller, Post
from turboapi.security import Authenticate, RequireRole
from turboapi.security import JWTAuthProvider, PasswordHandler
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

@Controller("/api/v1/auth")
class AuthController:
    
    def __init__(self, auth_provider: JWTAuthProvider):
        self.auth_provider = auth_provider
    
    @Post("/login")
    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """Authenticate user and return tokens"""
        result = await self.auth_provider.authenticate_with_credentials(
            login_data.username, 
            login_data.password
        )
        
        if not result.success:
            raise HTTPException(status_code=401, detail=result.error_message)
        
        return LoginResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            expires_in=1800  # 30 minutes
        )
    
    @Post("/refresh")
    async def refresh_token(self, refresh_token: str) -> LoginResponse:
        """Refresh access token"""
        result = await self.auth_provider.authenticate_with_refresh_token(refresh_token)
        
        if not result.success:
            raise HTTPException(status_code=401, detail=result.error_message)
        
        return LoginResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            expires_in=1800
        )

# Protected endpoint example
@Controller("/api/v1/admin")
class AdminController:
    
    @Get("/users")
    @Authenticate()
    @RequireRole("admin")
    async def admin_users(self, current_user: User) -> dict:
        """Admin-only endpoint"""
        return {"message": f"Welcome admin {current_user.username}"}
    
    @Get("/stats")
    @Authenticate()
    @RequireRole("admin")
    async def admin_stats(self) -> dict:
        """Admin statistics"""
        return {"total_users": 1000, "active_sessions": 50}
```

## Database Operations

### Repository Pattern with SQLAlchemy

```python
# apps/users/models.py
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# apps/users/repositories.py
from turboapi.data import Repository
from turboapi.interfaces import BaseRepository
from .models import User

@Repository()
class UserRepository(BaseRepository):
    
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email"""
        return await self.session.query(User).filter(User.email == email).first()
    
    async def get_by_role(self, role: str) -> List[User]:
        """Get users by role"""
        return await self.session.query(User).filter(User.role == role).all()
    
    async def get_active_users(self) -> List[User]:
        """Get all active users"""
        return await self.session.query(User).filter(User.is_active == True).all()

# apps/users/services.py
from turboapi.core import Injectable
from .repositories import UserRepository
from .models import User

@Injectable()
class UserService:
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def create_user(self, user_data: dict) -> User:
        """Create a new user"""
        user = User(**user_data)
        return await self.user_repo.create(user)
    
    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email"""
        return await self.user_repo.get_by_email(email)
    
    async def get_admin_users(self) -> List[User]:
        """Get all admin users"""
        return await self.user_repo.get_by_role("admin")
    
    async def deactivate_user(self, user_id: str) -> User:
        """Deactivate user"""
        user = await self.user_repo.get_by_id(user_id)
        user.is_active = False
        return await self.user_repo.update(user)
```

## Caching Strategies

### Smart Caching with TTL

```python
# apps/products/services.py
from turboapi.core import Injectable
from turboapi.cache import SmartCache
from .repositories import ProductRepository

@Injectable()
class ProductService:
    
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo
    
    @SmartCache(ttl=300)  # Cache for 5 minutes
    async def get_product(self, product_id: str) -> dict:
        """Get product with caching"""
        product = await self.product_repo.get_by_id(product_id)
        return product.dict()
    
    @SmartCache(ttl=600, key_prefix="products_list")  # Cache for 10 minutes
    async def list_products(self, category: str = None) -> List[dict]:
        """List products with caching"""
        if category:
            products = await self.product_repo.get_by_category(category)
        else:
            products = await self.product_repo.get_all()
        
        return [product.dict() for product in products]
    
    async def update_product(self, product_id: str, data: dict) -> dict:
        """Update product and invalidate cache"""
        product = await self.product_repo.update(product_id, data)
        
        # Invalidate related cache entries
        await self.invalidate_product_cache(product_id)
        
        return product.dict()
    
    async def invalidate_product_cache(self, product_id: str):
        """Invalidate cache for specific product"""
        # Implementation would depend on your cache strategy
        pass

# Advanced caching with context manager
from turboapi.cache import AsyncCacheContext

async def complex_operation_with_caching():
    async with AsyncCacheContext() as cache:
        # Check cache first
        cached_result = await cache.get("complex_key")
        if cached_result:
            return cached_result
        
        # Perform expensive operation
        result = await expensive_database_operation()
        
        # Cache the result
        await cache.set("complex_key", result, ttl=3600)
        
        return result
```

## Background Tasks

### Async Task Processing

```python
# apps/notifications/tasks.py
from turboapi.tasks import Task
from turboapi.core import Injectable
from .services import EmailService, NotificationService

@Injectable()
class NotificationTasks:
    
    def __init__(self, email_service: EmailService, notification_service: NotificationService):
        self.email_service = email_service
        self.notification_service = notification_service
    
    @Task()
    async def send_welcome_email(self, user_email: str, user_name: str):
        """Send welcome email to new user"""
        subject = "Welcome to our platform!"
        body = f"Hello {user_name}, welcome to our platform!"
        
        await self.email_service.send_email(user_email, subject, body)
    
    @Task()
    async def send_password_reset_email(self, user_email: str, reset_token: str):
        """Send password reset email"""
        subject = "Password Reset Request"
        body = f"Click here to reset your password: /reset?token={reset_token}"
        
        await self.email_service.send_email(user_email, subject, body)
    
    @Task()
    async def process_bulk_notifications(self, notification_data: List[dict]):
        """Process bulk notifications"""
        for data in notification_data:
            await self.notification_service.send_notification(data)
    
    @Task()
    async def cleanup_expired_sessions(self):
        """Clean up expired user sessions"""
        expired_sessions = await self.notification_service.get_expired_sessions()
        for session in expired_sessions:
            await self.notification_service.delete_session(session.id)

# Triggering tasks from controllers
@Controller("/api/v1/users")
class UserController:
    
    def __init__(self, user_service: UserService, notification_tasks: NotificationTasks):
        self.user_service = user_service
        self.notification_tasks = notification_tasks
    
    @Post("/")
    async def create_user(self, user_data: UserCreate) -> dict:
        """Create user and send welcome email"""
        user = await self.user_service.create_user(user_data.dict())
        
        # Queue welcome email task
        await self.notification_tasks.send_welcome_email(
            user.email, 
            user.name
        )
        
        return {"message": "User created", "user": user.dict()}
```

## Observability

### Structured Logging and Metrics

```python
# apps/orders/services.py
from turboapi.core import Injectable
from turboapi.observability import get_logger, trace_function
from .repositories import OrderRepository

@Injectable()
class OrderService:
    
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo
        self.logger = get_logger(__name__)
    
    @trace_function("order_creation")
    async def create_order(self, order_data: dict) -> dict:
        """Create order with tracing and logging"""
        self.logger.info("Creating new order", extra={
            "user_id": order_data.get("user_id"),
            "amount": order_data.get("total_amount")
        })
        
        try:
            order = await self.order_repo.create(order_data)
            
            self.logger.info("Order created successfully", extra={
                "order_id": order.id,
                "user_id": order.user_id
            })
            
            return order.dict()
            
        except Exception as e:
            self.logger.error("Failed to create order", extra={
                "error": str(e),
                "user_id": order_data.get("user_id")
            })
            raise
    
    async def process_payment(self, order_id: str, payment_data: dict) -> dict:
        """Process payment with metrics"""
        # This would integrate with your metrics system
        # Example: increment payment_attempts counter
        
        result = await self.process_payment_gateway(payment_data)
        
        if result.success:
            # Example: increment successful_payments counter
            await self.order_repo.update_payment_status(order_id, "completed")
        else:
            # Example: increment failed_payments counter
            await self.order_repo.update_payment_status(order_id, "failed")
        
        return result.dict()
```

## Error Handling

### Custom Exception Handling

```python
# apps/common/exceptions.py
from turboapi.exceptions import TurboAPIException

class UserNotFoundError(TurboAPIException):
    """Raised when user is not found"""
    status_code = 404
    detail = "User not found"

class InsufficientPermissionsError(TurboAPIException):
    """Raised when user lacks required permissions"""
    status_code = 403
    detail = "Insufficient permissions"

class ValidationError(TurboAPIException):
    """Raised when data validation fails"""
    status_code = 400
    detail = "Validation error"

# apps/users/services.py
from turboapi.core import Injectable
from .exceptions import UserNotFoundError, ValidationError

@Injectable()
class UserService:
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def get_user(self, user_id: str) -> dict:
        """Get user with proper error handling"""
        user = await self.user_repo.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        return user.dict()
    
    async def update_user(self, user_id: str, data: dict) -> dict:
        """Update user with validation"""
        # Validate required fields
        if not data:
            raise ValidationError("Update data cannot be empty")
        
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        updated_user = await self.user_repo.update(user_id, data)
        return updated_user.dict()

# Global exception handler (in main.py or app setup)
from fastapi import Request
from fastapi.responses import JSONResponse

async def global_exception_handler(request: Request, exc: TurboAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "type": exc.__class__.__name__,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## Testing Examples

### Unit Testing with Dependency Injection

```python
# tests/test_user_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from apps.users.services import UserService
from apps.users.repositories import UserRepository

@pytest.fixture
def mock_user_repo():
    return AsyncMock(spec=UserRepository)

@pytest.fixture
def user_service(mock_user_repo):
    return UserService(user_repo=mock_user_repo)

@pytest.mark.asyncio
async def test_create_user(user_service, mock_user_repo):
    """Test user creation"""
    # Arrange
    user_data = {"name": "John Doe", "email": "john@example.com"}
    expected_user = MagicMock()
    expected_user.dict.return_value = {"id": "123", **user_data}
    mock_user_repo.create.return_value = expected_user
    
    # Act
    result = await user_service.create_user(user_data)
    
    # Assert
    assert result["name"] == "John Doe"
    assert result["email"] == "john@example.com"
    mock_user_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_not_found(user_service, mock_user_repo):
    """Test user not found scenario"""
    # Arrange
    mock_user_repo.get_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(UserNotFoundError):
        await user_service.get_user("nonexistent_id")

# Integration testing
@pytest.mark.asyncio
async def test_user_controller_integration():
    """Test user controller with real dependencies"""
    # This would use the actual DI container in test mode
    app = create_test_app()
    
    async with TestClient(app) as client:
        response = await client.get("/api/v1/users/123")
        assert response.status_code == 404  # User not found
```

These examples demonstrate common patterns and best practices when building applications with TurboAPI. Each example shows how to leverage the framework's features effectively while maintaining clean, testable code.
