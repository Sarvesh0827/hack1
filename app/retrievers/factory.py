"""
Factory for creating retriever instances based on configuration.
"""
import os
from dotenv import load_dotenv
from .base import BaseRetriever
from .http_retriever import HttpRetriever
from .tinyfish_retriever import TinyFishRetriever

load_dotenv()

def get_retriever() -> BaseRetriever:
    """
    Get the configured retriever backend.
    Reads from RETRIEVER_BACKEND env var (defaults to 'http').
    """
    backend = os.getenv("RETRIEVER_BACKEND", "http").lower()
    
    if backend == "tinyfish":
        print("[RETRIEVER_FACTORY] Using TinyFish retriever")
        return TinyFishRetriever()
    else:
        print("[RETRIEVER_FACTORY] Using HTTP retriever")
        return HttpRetriever()
