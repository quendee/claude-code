from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    name: str
    description: str
    input_schema: dict

    def definition(self) -> dict:
        """Returns the tool definition to pass in the `tools` array of an API request."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }

    @abstractmethod
    def run(self, **kwargs) -> Any:
        pass
