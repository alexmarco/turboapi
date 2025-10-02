"""Pruebas para el sistema de repositorios."""

import pytest
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from turboapi.data.decorators import Repository
from turboapi.data.repository import BaseRepository
from turboapi.data.repository import SQLRepository

Base = declarative_base()


def create_test_session() -> Session:
    """Crea una sesión de prueba conectada a una base de datos en memoria."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


class RepositoryTestEntity(Base):
    """Entidad de prueba para las pruebas de repositorios."""

    __tablename__ = "test_entities"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)


class ConcreteRepository(BaseRepository[RepositoryTestEntity, int]):
    """Implementación concreta de BaseRepository para pruebas."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.model_class = RepositoryTestEntity

    def create(self, entity: RepositoryTestEntity) -> RepositoryTestEntity:
        """Crea una nueva entidad."""
        self.session.add(entity)
        self.session.flush()
        return entity

    def get_by_id(self, entity_id: int) -> RepositoryTestEntity | None:
        """Obtiene una entidad por ID."""
        return self.session.get(RepositoryTestEntity, entity_id)

    def get_all(self) -> list[RepositoryTestEntity]:
        """Obtiene todas las entidades."""
        return list(self.session.query(RepositoryTestEntity).all())

    def update(self, entity: RepositoryTestEntity) -> RepositoryTestEntity:
        """Actualiza una entidad."""
        self.session.merge(entity)
        return entity

    def delete(self, entity_id: int) -> bool:
        """Elimina una entidad por ID."""
        entity = self.get_by_id(entity_id)
        if entity is None:
            return False
        self.session.delete(entity)
        return True

    def count(self) -> int:
        """Cuenta las entidades."""
        return self.session.query(RepositoryTestEntity).count()


@Repository(entity_type=RepositoryTestEntity, id_type=int)
class DecoratedRepository(SQLRepository[RepositoryTestEntity, int]):
    """Repositorio decorado con @Repository."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, RepositoryTestEntity)


class TestBaseRepository:
    """Pruebas para la clase base BaseRepository."""

    def test_repository_initialization(self) -> None:
        """Prueba la inicialización del repositorio."""
        # Crear una sesión mock
        session = create_test_session()

        repository = ConcreteRepository(session)

        assert repository.session is session

    def test_repository_is_abstract(self) -> None:
        """Prueba que BaseRepository es abstracta."""
        with pytest.raises(TypeError):
            BaseRepository(Session())


class TestSQLRepository:
    """Pruebas para la clase SQLRepository."""

    def test_sql_repository_initialization(self) -> None:
        """Prueba la inicialización del repositorio SQL."""
        session = create_test_session()
        repository = SQLRepository(session, RepositoryTestEntity)

        assert repository.session is session
        assert repository.model_class is RepositoryTestEntity

    def test_create_entity(self) -> None:
        """Prueba la creación de entidades."""
        session = create_test_session()
        repository = SQLRepository(session, RepositoryTestEntity)

        entity = RepositoryTestEntity(name="Test Entity", email="test@example.com")
        created_entity = repository.create(entity)

        assert created_entity is entity
        assert created_entity.id is not None

    def test_get_by_id(self) -> None:
        """Prueba la obtención de entidades por ID."""
        session = create_test_session()
        repository = SQLRepository(session, RepositoryTestEntity)

        # Crear una entidad
        entity = RepositoryTestEntity(name="Test Entity", email="test@example.com")
        repository.create(entity)
        entity_id = entity.id

        # Obtener la entidad por ID
        retrieved_entity = repository.get_by_id(entity_id)

        assert retrieved_entity is not None
        assert retrieved_entity.id == entity_id
        assert retrieved_entity.name == "Test Entity"

    def test_get_by_id_not_found(self) -> None:
        """Prueba la obtención de entidades por ID cuando no existe."""
        session = create_test_session()
        repository = SQLRepository(session, RepositoryTestEntity)

        retrieved_entity = repository.get_by_id(999)

        assert retrieved_entity is None

    def test_get_all(self) -> None:
        """Prueba la obtención de todas las entidades."""
        session = create_test_session()
        repository = SQLRepository(session, RepositoryTestEntity)

        # Crear varias entidades
        entity1 = RepositoryTestEntity(name="Entity 1", email="entity1@example.com")
        entity2 = RepositoryTestEntity(name="Entity 2", email="entity2@example.com")

        repository.create(entity1)
        repository.create(entity2)

        # Obtener todas las entidades
        all_entities = repository.get_all()

        assert len(all_entities) == 2
        assert entity1 in all_entities
        assert entity2 in all_entities

    def test_update_entity(self) -> None:
        """Prueba la actualización de entidades."""
        session = create_test_session()
        repository = SQLRepository(session, RepositoryTestEntity)

        # Crear una entidad
        entity = RepositoryTestEntity(name="Original Name", email="original@example.com")
        repository.create(entity)

        # Actualizar la entidad
        entity.name = "Updated Name"
        entity.email = "updated@example.com"
        updated_entity = repository.update(entity)

        assert updated_entity is entity
        assert updated_entity.name == "Updated Name"
        assert updated_entity.email == "updated@example.com"

    def test_delete_entity(self) -> None:
        """Prueba la eliminación de entidades."""
        session = create_test_session()
        repository = SQLRepository(session, RepositoryTestEntity)

        # Crear una entidad
        entity = RepositoryTestEntity(name="Test Entity", email="test@example.com")
        repository.create(entity)
        entity_id = entity.id

        # Eliminar la entidad
        result = repository.delete(entity_id)

        assert result is True

        # Hacer commit para confirmar la eliminación
        session.commit()

        # Verificar que la entidad fue eliminada
        deleted_entity = repository.get_by_id(entity_id)
        assert deleted_entity is None

    def test_delete_entity_not_found(self) -> None:
        """Prueba la eliminación de entidades que no existen."""
        session = create_test_session()
        repository = SQLRepository(session, RepositoryTestEntity)

        result = repository.delete(999)

        assert result is False

    def test_count_entities(self) -> None:
        """Prueba el conteo de entidades."""
        session = create_test_session()
        repository = SQLRepository(session, RepositoryTestEntity)

        # Inicialmente no hay entidades
        assert repository.count() == 0

        # Crear algunas entidades
        entity1 = RepositoryTestEntity(name="Entity 1", email="entity1@example.com")
        entity2 = RepositoryTestEntity(name="Entity 2", email="entity2@example.com")

        repository.create(entity1)
        repository.create(entity2)

        # Verificar el conteo
        assert repository.count() == 2

    def test_find_by_criteria(self) -> None:
        """Prueba la búsqueda por criterios específicos."""
        session = create_test_session()
        repository = SQLRepository(session, RepositoryTestEntity)

        # Crear entidades con diferentes valores
        entity1 = RepositoryTestEntity(name="John", email="john@example.com")
        entity2 = RepositoryTestEntity(name="Jane", email="jane@example.com")
        entity3 = RepositoryTestEntity(name="John", email="john.doe@example.com")

        repository.create(entity1)
        repository.create(entity2)
        repository.create(entity3)

        # Buscar por nombre
        john_entities = repository.find_by(name="John")
        assert len(john_entities) == 2
        assert entity1 in john_entities
        assert entity3 in john_entities

        # Buscar por email
        jane_entities = repository.find_by(email="jane@example.com")
        assert len(jane_entities) == 1
        assert entity2 in jane_entities

    def test_find_one_by_criteria(self) -> None:
        """Prueba la búsqueda de una entidad por criterios específicos."""
        session = create_test_session()
        repository = SQLRepository(session, RepositoryTestEntity)

        # Crear entidades
        entity1 = RepositoryTestEntity(name="John", email="john@example.com")
        entity2 = RepositoryTestEntity(name="Jane", email="jane@example.com")

        repository.create(entity1)
        repository.create(entity2)

        # Buscar una entidad específica
        jane_entity = repository.find_one_by(name="Jane")
        assert jane_entity is not None
        assert jane_entity.name == "Jane"
        assert jane_entity.email == "jane@example.com"

        # Buscar una entidad que no existe
        non_existent = repository.find_one_by(name="NonExistent")
        assert non_existent is None


class TestRepositoryDecorator:
    """Pruebas para el decorador @Repository."""

    def test_repository_decorator(self) -> None:
        """Prueba que el decorador @Repository marca correctamente las clases."""
        assert hasattr(DecoratedRepository, "_is_repository")
        assert getattr(DecoratedRepository, "_is_repository", False) is True
        assert getattr(DecoratedRepository, "_entity_type", None) is RepositoryTestEntity
        assert getattr(DecoratedRepository, "_id_type", None) is int

    def test_decorated_repository_functionality(self) -> None:
        """Prueba que un repositorio decorado funciona correctamente."""
        session = create_test_session()
        repository = DecoratedRepository(session)

        # Crear una entidad
        entity = RepositoryTestEntity(name="Test Entity", email="test@example.com")
        created_entity = repository.create(entity)

        assert created_entity is entity
        assert created_entity.id is not None

        # Obtener la entidad
        retrieved_entity = repository.get_by_id(created_entity.id)
        assert retrieved_entity is not None
        assert retrieved_entity.name == "Test Entity"
