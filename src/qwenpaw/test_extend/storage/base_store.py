# -*- coding: utf-8 -*-
"""Abstract base class for all domain stores.

Provides the interface that both FileStore and MySQLStore implementations
must satisfy. Domain-specific stores are created via StorageFactory.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class BaseStore(ABC, Generic[T]):

    @abstractmethod
    async def create(self, item: T) -> T:
        ...

    @abstractmethod
    async def get(self, item_id: str) -> Optional[T]:
        ...

    @abstractmethod
    async def list_all(self, **filters) -> list[T]:
        ...

    @abstractmethod
    async def update(self, item: T) -> T:
        ...

    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        ...

    @abstractmethod
    async def exists(self, item_id: str) -> bool:
        ...


__all__ = ["BaseStore"]
