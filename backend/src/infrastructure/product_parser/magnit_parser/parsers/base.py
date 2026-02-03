from typing import Protocol, Any


class PageParser(Protocol):
    def parse(self, content: str) -> Any: ...







