"""
HTTP-based retriever using httpx/requests + trafilatura.
This is the fallback/default retriever.
"""
import httpx
import trafilatura
import hashlib
import os
from typing import List, Optional
from .base import BaseRetriever, Document, UrlCandidate
from app.seeds import SEEDS_BY_CATEGORY

CACHE_DIR = "cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

class HttpRetriever(BaseRetriever):
    """Retrieves content using HTTP requests (no JS execution)."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
    def _get_cache_path(self, url: str) -> str:
        """Get cache file path for URL."""
        hash_digest = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(CACHE_DIR, f"{hash_digest}.txt")
    
    def _get_seeds_for_query(self, query: str) -> List[str]:
        """Get seeded URLs based on query keywords."""
        query_lower = query.lower()
        if "player" in query_lower or "competitor" in query_lower or "company" in query_lower:
            return SEEDS_BY_CATEGORY["key_players"]
        elif "trend" in query_lower or "future" in query_lower:
            return SEEDS_BY_CATEGORY["trends"]
        elif "need" in query_lower or "challenge" in query_lower or "gap" in query_lower:
            return SEEDS_BY_CATEGORY["unmet_needs"]
        else:
            return SEEDS_BY_CATEGORY["default"]
    
    async def search(self, query: str, max_results: int = 5) -> List[UrlCandidate]:
        """
        Search using seeded URLs (DDG disabled for reliability).
        Returns UrlCandidates from our curated seed list.
        """
        print(f"[HTTP_RETRIEVER] Using seeded URLs for query: {query[:50]}...")
        seed_urls = self._get_seeds_for_query(query)
        
        candidates = []
        for url in seed_urls[:max_results]:
            candidates.append(UrlCandidate(
                url=url,
                title=url.split("/")[-1] or url,
                snippet=f"Seeded URL for {query[:30]}"
            ))
        
        return candidates
    
    async def fetch(self, url: str) -> Optional[Document]:
        """Fetch URL using HTTP and extract text with trafilatura."""
        
        # Check cache first
        cache_path = self._get_cache_path(url)
        if os.path.exists(cache_path):
            print(f"[HTTP_RETRIEVER] Cache hit: {url}")
            with open(cache_path, "r", encoding="utf-8") as f:
                content = f.read()
            return Document(
                url=url,
                title="Cached Content",
                text=content,
                text_length=len(content),
                retrieval_method="cache"
            )
        
        print(f"[HTTP_RETRIEVER] Fetching: {url}")
        html_content = ""
        
        # Try httpx first
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, verify=True) as client:
                resp = await client.get(url, headers=self.headers)
                resp.raise_for_status()
                html_content = resp.text
        except Exception as e:
            print(f"[HTTP_RETRIEVER] Httpx failed for {url}: {e}. Trying requests...")
            # Fallback to requests
            try:
                import requests
                resp = requests.get(url, headers=self.headers, timeout=15, verify=True)
                resp.raise_for_status()
                html_content = resp.text
            except Exception as e2:
                print(f"[HTTP_RETRIEVER] Requests failed for {url}: {e2}")
                return None
        
        # Extract text
        try:
            extracted = trafilatura.extract(html_content, include_comments=False, include_tables=True)
            
            if extracted and len(extracted) > 200:
                # Cache it
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(extracted)
                
                return Document(
                    url=url,
                    title="Extracted Content",
                    text=extracted,
                    text_length=len(extracted),
                    raw_html=html_content[:1000],  # Store snippet
                    retrieval_method="http"
                )
            else:
                print(f"[HTTP_RETRIEVER] Content too thin: {url}")
                return None
        except Exception as e:
            print(f"[HTTP_RETRIEVER] Extraction failed for {url}: {e}")
            return None
