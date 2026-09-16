from __future__ import annotations

from abc import ABC, abstractmethod


class ProviderError(RuntimeError):
    pass


class Provider(ABC):
    name: str

    @abstractmethod
    def lookup(self, value: str):
        raise NotImplementedError
