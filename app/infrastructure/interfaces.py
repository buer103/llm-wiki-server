from abc import ABC, abstractmethod
from typing import BinaryIO


class ObjectStorage(ABC):
    @abstractmethod
    def put(self, key: str, stream: BinaryIO, content_type: str | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str) -> bytes:
        raise NotImplementedError


class TaskPublisher(ABC):
    @abstractmethod
    def publish(self, topic: str, key: str, payload: bytes) -> None:
        raise NotImplementedError


class SearchIndex(ABC):
    @abstractmethod
    def index(self, index_name: str, document_id: str, document: dict) -> None:
        raise NotImplementedError


class Cache(ABC):
    @abstractmethod
    def get(self, key: str) -> bytes | None:
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: bytes, ttl_seconds: int | None = None) -> None:
        raise NotImplementedError


class LLMClient(ABC):
    @abstractmethod
    def complete(self, *, model: str, messages: list[dict], **kwargs) -> str:
        raise NotImplementedError


class Authenticator(ABC):
    @abstractmethod
    def authenticate(self, authorization: str | None) -> dict:
        raise NotImplementedError
