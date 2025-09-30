from abc import ABC, abstractmethod

class ServiceAdapter(ABC):
    """
    A basic interface for any adapter to your service.
    Then we'll make: OpenAIAdapter (MOCK), HttpAdapter, GrpcAdapter, CliAdapter, DbAdapter...
    """

    @abstractmethod
    async def ping(self) -> bool:
        """Checking service availability (may be no-op)"""
        raise NotImplementedError

    @abstractmethod
    async def run_task(self, payload: dict) -> dict:
        """Start/execute an operation in the service and return the result."""
        raise NotImplementedError