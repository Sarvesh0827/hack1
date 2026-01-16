# TinyFish Integration - Implementation Guide

## Overview
TinyFish integration is now architected and ready for implementation. The system uses a pluggable retriever pattern with automatic fallback to HTTP.

## Architecture

### Retriever Interface (`app/retrievers/base.py`)
- `BaseRetriever`: Abstract base class
- `Document`: Standardized document format
- `UrlCandidate`: Search result format

### Implementations
1. **HttpRetriever** (`http_retriever.py`) - Current working implementation
   - Uses httpx/requests + trafilatura
   - Seeded URLs for reliability
   - Caching enabled

2. **TinyFishRetriever** (`tinyfish_retriever.py`) - Ready for TinyFish API
   - Placeholder methods for TinyFish integration
   - Automatic fallback to HttpRetriever
   - Browsing trace logging

### Configuration
Set in `.env`:
```
RETRIEVER_BACKEND=http          # or 'tinyfish'
TINYFISH_API_KEY=your_key_here  # when available
```

## To Complete TinyFish Integration

### 1. Install TinyFish SDK
```bash
pip install tinyfish-sdk  # or whatever the package is called
```

### 2. Implement `_fetch_with_tinyfish()` in `tinyfish_retriever.py`

Replace the TODO section with actual TinyFish API calls:

```python
async def _fetch_with_tinyfish(self, url: str) -> Optional[Document]:
    # Create browser session
    browser = await self.tinyfish_client.create_browser()
    
    # Navigate to URL
    page = await browser.goto(url)
    await page.wait_for_load()
    
    # Extract content
    text = await page.extract_main_content()
    title = await page.get_title()
    
    # Optional: Take screenshot for debugging
    screenshot_path = f"screenshots/{hashlib.md5(url.encode()).hexdigest()}.png"
    await page.screenshot(screenshot_path)
    
    await browser.close()
    
    return Document(
        url=url,
        title=title,
        text=text,
        text_length=len(text),
        screenshot_path=screenshot_path,
        retrieval_method="tinyfish"
    )
```

### 3. Implement `search()` in `tinyfish_retriever.py`

```python
async def search(self, query: str, max_results: int = 5) -> List[UrlCandidate]:
    browser = await self.tinyfish_client.create_browser()
    
    # Navigate to search engine
    page = await browser.goto(f"https://www.google.com/search?q={query}")
    await page.wait_for_selector(".g")
    
    # Extract search results
    results = await page.extract_search_results(max_results=max_results)
    
    await browser.close()
    
    return [
        UrlCandidate(url=r['url'], title=r['title'], snippet=r['snippet'])
        for r in results
    ]
```

### 4. Switch to TinyFish Backend

Update `.env`:
```
RETRIEVER_BACKEND=tinyfish
TINYFISH_API_KEY=your_actual_key
```

## Current Status

✅ **Working Now:**
- HTTP retriever with seeded URLs
- Relevance scoring
- Document ranking
- Browser trace UI panel
- Automatic fallback logic

⏳ **Pending TinyFish API:**
- JS-rendered page fetching
- Live search engine scraping
- Screenshot capture
- Advanced navigation (scrolling, clicking)

## Testing

Test HTTP backend:
```bash
export RETRIEVER_BACKEND=http
export PYTHONPATH=$PYTHONPATH:. && streamlit run ui/dashboard.py
```

Test TinyFish backend (when implemented):
```bash
export RETRIEVER_BACKEND=tinyfish
export TINYFISH_API_KEY=your_key
export PYTHONPATH=$PYTHONPATH:. && streamlit run ui/dashboard.py
```

## UI Features

The Streamlit dashboard now shows:
- **Browser Trace Panel**: Shows which retrieval method was used per URL
- **Retrieval Methods**: Displays "http", "cache", or "tinyfish" for each source
- **Fallback Indicators**: Shows when fallback was triggered

## Next Steps

1. Get TinyFish API credentials
2. Install TinyFish SDK
3. Implement the two TODO methods in `tinyfish_retriever.py`
4. Test with `RETRIEVER_BACKEND=tinyfish`
5. Compare results quality between HTTP and TinyFish backends
