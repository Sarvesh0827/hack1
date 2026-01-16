"""
Refactored WebAgent using pluggable retriever backends.
"""
import asyncio
import logging
from typing import List
from app.models import ResearchTask, ResearchFinding
from app.seeds import KEYWORDS
from app.retrievers import get_retriever, Document

logger = logging.getLogger(__name__)

class WebAgent:
    def __init__(self):
        self.retriever = get_retriever()
        self.trace_log = []  # For UI display
        
    def _score_relevance(self, content: str) -> int:
        """Scores content based on keyword hits."""
        score = 0
        content_lower = content.lower()
        for kw in KEYWORDS:
            score += content_lower.count(kw)
        return score
    
    async def execute_task(self, task: ResearchTask) -> ResearchFinding:
        """
        Executes research task using configured retriever backend.
        """
        print(f"--- WEB AGENT: Processing '{task.description}' ---")
        
        # 1. Search for URLs
        url_candidates = await self.retriever.search(task.description, max_results=8)
        urls = [candidate.url for candidate in url_candidates]
        print(f"[WEB_AGENT] Found {len(urls)} URLs to fetch")
        
        # 2. Fetch documents in parallel
        documents = await self.retriever.fetch_many(urls)
        print(f"[WEB_AGENT] Successfully fetched {len(documents)} documents")
        
        # Log retrieval methods for UI
        for doc in documents:
            self.trace_log.append({
                "url": doc.url,
                "method": doc.retrieval_method,
                "text_length": doc.text_length,
                "title": doc.title
            })
        
        # 3. Score and rank documents
        scored_docs = []
        for doc in documents:
            score = self._score_relevance(doc.text)
            scored_docs.append((doc, score))
        
        # Sort by relevance score
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # 4. Select top K documents
        top_k = 3
        top_docs = scored_docs[:top_k]
        
        if not top_docs:
            return ResearchFinding(
                source_url="N/A",
                content="No relevant content extracted.",
                relevance_score=0.0
            )
        
        # 5. Combine top documents
        combined_text = ""
        urls_list = []
        for doc, score in top_docs:
            # Truncate to 3000 chars per document
            truncated = doc.text[:3000]
            combined_text += f"\n\n=== SOURCE: {doc.url} (Score: {int(score)}, Method: {doc.retrieval_method}) ===\n{truncated}"
            urls_list.append(doc.url)
        
        print(f"[WEB_AGENT] Final selection: {len(top_docs)} sources")
        
        return ResearchFinding(
            source_url="Multiple Sources",
            content=combined_text,
            relevance_score=1.0,
            extracted_data={
                "source_count": len(top_docs),
                "urls": urls_list,
                "retrieval_methods": [doc.retrieval_method for doc, _ in top_docs]
            }
        )
    
    def get_trace_log(self) -> List[dict]:
        """Get browsing trace for UI."""
        return self.trace_log
    
    def clear_trace_log(self):
        """Clear trace log."""
        self.trace_log = []
