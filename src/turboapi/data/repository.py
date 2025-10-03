"""Sistema de repositorios para el framework TurboAPI."""

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from sqlalchemy.orm import Session

# TypeVar para el tipo de entidad
EntityType = TypeVar("EntityType")
# TypeVar para el tipo de ID
IdType = TypeVar("IdType")


class BaseRepository(ABC, Generic[EntityType, IdType]):
    """
    Interfaz base para repositorios.

    Define las operaciones CRUD básicas que todos los repositorios deben implementar.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            session: Sesión de SQLAlchemy
        """
        self.session = session

    @abstractmethod
    def create(self, entity: EntityType) -> EntityType:
        """
        Crea una nueva entidad en la base de datos.

        Args:
            entity: Entidad a crear

        Returns:
            Entidad creada con ID asignado
        """
        pass

    @abstractmethod
    def get_by_id(self, entity_id: IdType) -> EntityType | None:
        """
        Obtiene una entidad por su ID.

        Args:
            entity_id: ID de la entidad

        Returns:
            Entidad encontrada o None si no existe
        """
        pass

    @abstractmethod
    def get_all(self) -> list[EntityType]:
        """
        Obtiene todas las entidades.

        Returns:
            Lista de todas las entidades
        """
        pass

    @abstractmethod
    def update(self, entity: EntityType) -> EntityType:
        """
        Actualiza una entidad existente.

        Args:
            entity: Entidad a actualizar

        Returns:
            Entidad actualizada
        """
        pass

    @abstractmethod
    def delete(self, entity_id: IdType) -> bool:
        """
        Elimina una entidad por su ID.

        Args:
            entity_id: ID de la entidad a eliminar

        Returns:
            True si se eliminó correctamente, False si no se encontró
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Cuenta el número total de entidades.

        Returns:
            Número total de entidades
        """
        pass


class SQLRepository(BaseRepository[EntityType, IdType]):
    """
    Implementación base de repositorio usando SQLAlchemy.

    Proporciona una implementación genérica de las operaciones CRUD.
    """

    def __init__(self, session: Session, model_class: type[EntityType]) -> None:
        """
        Inicializa el repositorio SQL.

        Args:
            session: Sesión de SQLAlchemy
            model_class: Clase del modelo SQLAlchemy
        """
        super().__init__(session)
        self.model_class = model_class

    def create(self, entity: EntityType) -> EntityType:
        """
        Crea una nueva entidad en la base de datos.

        Args:
            entity: Entidad a crear

        Returns:
            Entidad creada con ID asignado
        """
        self.session.add(entity)
        self.session.flush()  # Para obtener el ID sin hacer commit
        return entity

    def get_by_id(self, entity_id: IdType) -> EntityType | None:
        """
        Obtiene una entidad por su ID.

        Args:
            entity_id: ID de la entidad

        Returns:
            Entidad encontrada o None si no existe
        """
        return self.session.get(self.model_class, entity_id)

    def get_all(self) -> list[EntityType]:
        """
        Obtiene todas las entidades.

        Returns:
            Lista de todas las entidades
        """
        return list(self.session.query(self.model_class).all())

    def update(self, entity: EntityType) -> EntityType:
        """
        Actualiza una entidad existente.

        Args:
            entity: Entidad a actualizar

        Returns:
            Entidad actualizada
        """
        self.session.merge(entity)
        return entity

    def delete(self, entity_id: IdType) -> bool:
        """
        Elimina una entidad por su ID.

        Args:
            entity_id: ID de la entidad a eliminar

        Returns:
            True si se eliminó correctamente, False si no se encontró
        """
        entity = self.get_by_id(entity_id)
        if entity is None:
            return False

        self.session.delete(entity)
        return True

    def count(self) -> int:
        """
        Cuenta el número total de entidades.

        Returns:
            Número total de entidades
        """
        return self.session.query(self.model_class).count()

    def find_by(self, **filters: Any) -> list[EntityType]:
        """
        Busca entidades por criterios específicos.

        Args:
            **filters: Criterios de búsqueda

        Returns:
            Lista de entidades que coinciden con los criterios
        """
        query = self.session.query(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        return list(query.all())

    def find_one_by(self, **filters: Any) -> EntityType | None:
        """
        Busca una entidad por criterios específicos.

        Args:
            **filters: Criterios de búsqueda

        Returns:
            Primera entidad que coincide con los criterios o None
        """
        query = self.session.query(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        return query.first()
