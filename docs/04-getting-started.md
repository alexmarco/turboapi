# Getting Started with TurboAPI

This guide will help you get up and running with TurboAPI in minutes.

## Prerequisites

- Python 3.11 or higher
- `uv` package manager (recommended) or `pip`

## Installation

### Using uv (Recommended)

```bash
# Install TurboAPI
uv add turboapi

# Or create a new project with TurboAPI
uv init my-turboapi-project
cd my-turboapi-project
uv add turboapi
```

### Using pip

```bash
# Install TurboAPI
pip install turboapi
```

## Create Your First Project

### 1. Generate Project Structure

```bash
# Create a new TurboAPI project
framework new my-first-project
cd my-first-project
```

This creates a project structure like:

```txt
my-first-project/
├── pyproject.toml          # Project configuration
├── .env.example           # Environment variables template
├── apps/                  # Your applications
│   ├── __init__.py
│   └── home/              # Default home app
│       ├── __init__.py
│       ├── api.py         # API endpoints
│       ├── models.py      # Data models
│       └── services.py    # Business logic
└── main.py                # Application entry point
```

### 2. Create Your First App

```bash
# Create a new application
framework new-app users
```

This adds a new `users` app to your project with the same structure as the `home` app.

### 3. Configure Your Project

Edit `pyproject.toml` to register your apps:

```toml
[tool.turboapi]
installed_apps = [
    "apps.home",
    "apps.users",
]
```

## Your First API Endpoint

### 1. Create a Controller

Edit `apps/home/api.py`:

```python
from turboapi.web import Controller, Get, Post
from turboapi.security import Authenticate, RequireRole
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

@Controller("/api/v1")
class HomeController:
    
    @Get("/")
    async def home(self) -> dict:
        return {"message": "Welcome to TurboAPI!"}
    
    @Get("/users")
    @Authenticate()
    async def list_users(self) -> dict:
        return {"users": []}
    
    @Post("/users")
    @Authenticate()
    @RequireRole("admin")
    async def create_user(self, user_data: UserCreate) -> dict:
        return {"message": "User created", "user": user_data.dict()}
```

### 2. Run Your Application

```bash
# Start the development server
framework run
```

Your API will be available at `http://localhost:8000`

### 3. Test Your Endpoints

```bash
# Test the home endpoint
curl http://localhost:8000/api/v1/

# Test protected endpoints (requires authentication)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/users
```

## Next Steps

### Explore the Documentation

- **[Core System](05-core-system.md)** - Learn about dependency injection and configuration
- **[Web Layer](06-web-layer.md)** - Master controllers and routing
- **[Security System](08-security-system.md)** - Implement authentication and authorization
- **[Data Layer](07-data-layer.md)** - Work with databases and repositories
- **[Examples](14-examples.md)** - See practical examples and patterns

### Common Patterns

#### Dependency Injection

```python
from turboapi.core import Injectable
from turboapi.interfaces import BaseRepository

@Injectable()
class UserService:
    def __init__(self, user_repo: BaseRepository):
        self.user_repo = user_repo
    
    async def get_user(self, user_id: str):
        return await self.user_repo.get_by_id(user_id)
```

#### Repository Pattern

```python
from turboapi.data import Repository
from turboapi.interfaces import BaseRepository

@Repository()
class UserRepository(BaseRepository):
    async def get_by_email(self, email: str):
        # Implementation here
        pass
```

#### Caching

```python
from turboapi.cache import SmartCache

@SmartCache(ttl=300)  # Cache for 5 minutes
async def expensive_operation(self, param: str) -> dict:
    # This will be cached automatically
    return {"result": "expensive computation"}
```

#### Background Tasks

```python
from turboapi.tasks import Task

@Task()
async def send_email_task(email: str, subject: str, body: str):
    # This will run in the background
    # Implementation here
    pass
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure your apps are registered in `pyproject.toml`
2. **Port Already in Use**: Change the port in your configuration or stop other services
3. **Database Connection**: Ensure your database is running and accessible

### Getting Help

- Check the **[Troubleshooting Guide](16-troubleshooting.md)**
- Review the **[API Reference](15-api-reference.md)**
- Look at **[Examples](14-examples.md)** for common patterns
- Open an [issue](https://github.com/alexmarco/turboapi/issues) for bugs

## What's Next?

Now that you have a basic TurboAPI project running:

1. **Add Authentication** - Implement JWT authentication
2. **Create Models** - Define your data models
3. **Add Business Logic** - Create services and repositories
4. **Implement Security** - Add role-based access control
5. **Add Observability** - Enable logging, metrics, and tracing

Happy coding with TurboAPI! 🚀
