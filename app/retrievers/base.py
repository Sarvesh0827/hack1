"""
Base interface for document retrieval backends.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Document:
    """Represents a retrieved document."""
    url: str
    title: str
    text: str
    text_length: int
    raw_html: Optional[str] = None
    screenshot_path: Optional[str] = None
    retrieval_method: str = "unknown"  # "http", "tinyfish", "cache"
    
@dataclass
class UrlCandidate:
    """Represents a search result URL."""
    url: str
    title: str
    snippet: str

class BaseRetriever(ABC):
    """Abstract base class for retrieval backends."""
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> List[UrlCandidate]:
        """Search for URLs matching the query."""
        pass
    
    @abstractmethod
    async def fetch(self, url: str) -> Optional[Document]:
        """Fetch and extract content from a single URL."""
        pass
    
    async def fetch_many(self, urls: List[str]) -> List[Document]:
        """Fetch multiple URLs (default implementation)."""
        import asyncio
        tasks = [self.fetch(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [doc for doc in results if doc is not None]
