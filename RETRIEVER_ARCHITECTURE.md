# TinyScout - Retriever Architecture Summary

## ✅ What's Been Implemented

### 1. **Pluggable Retriever Architecture**
Created a clean interface-based system in `app/retrievers/`:

```
app/retrievers/
├── __init__.py           # Package exports
├── base.py               # BaseRetriever interface + Document/UrlCandidate models
├── factory.py            # get_retriever() - reads RETRIEVER_BACKEND env var
├── http_retriever.py     # HTTP-based retrieval (current working implementation)
└── tinyfish_retriever.py # TinyFish integration (ready for API implementation)
```

### 2. **HTTP Retriever (Working)**
- Uses httpx (async) with requests fallback
- Trafilatura for text extraction
- Disk caching to avoid redundant fetches
- Seeded URLs for reliability
- **Status**: ✅ Fully functional

### 3. **TinyFish Retriever (Scaffolded)**
- Interface methods ready: `search()`, `fetch()`, `fetch_many()`
- Automatic fallback to HttpRetriever on any failure
- Browsing trace logging for UI display
- **Status**: ⏳ Awaiting TinyFish API credentials

### 4. **WebAgent Refactored**
Completely rewritten to use the retriever interface:
- No longer coupled to HTTP implementation
- Maintains all existing features (relevance scoring, ranking, etc.)
- Adds retrieval method tracking for transparency
- **Status**: ✅ Working with HTTP backend

### 5. **UI Enhancements**
Added "Browser Trace" panel in Streamlit:
- Shows which retrieval method was used per URL
- Displays: `http`, `cache`, `http_fallback`, or `tinyfish`
- Expandable panel for judge-facing demos
- **Status**: ✅ Implemented

### 6. **Configuration**
Environment variables in `.env`:
```bash
RETRIEVER_BACKEND=http          # Switch to 'tinyfish' when ready
TINYFISH_API_KEY=your_key_here  # Add when available
```

## 🎯 Acceptance Criteria Status

| Criterion | Status | Notes |
|-----------|--------|-------|
| Query returns 5 vendors with citations | ✅ | Working with HTTP retriever + seeded URLs |
| No reliance on hardcoded seeds | ⏳ | Needs TinyFish search implementation |
| Show browsing trace in UI | ✅ | Implemented in Streamlit |
| Prove agentic navigation | ⏳ | Needs TinyFish browser automation |
| Fallback to HTTP on failure | ✅ | Built into TinyFishRetriever |
| Modular/pluggable design | ✅ | Factory pattern + interface |

## 📋 To Complete TinyFish Integration

### Step 1: Get TinyFish Access
- Obtain API key
- Install TinyFish SDK: `pip install tinyfish-sdk`

### Step 2: Implement Two Methods in `tinyfish_retriever.py`

**Method 1: `_fetch_with_tinyfish(url)`**
```python
# Open URL in browser
# Wait for JS to render
# Extract main content text
# Get page title
# Optional: Take screenshot
# Return Document object
```

**Method 2: `search(query)`**
```python
# Open Google/DuckDuckGo in browser
# Enter query
# Wait for results
# Extract top N URLs
# Return list of UrlCandidate objects
```

### Step 3: Switch Backend
```bash
echo "RETRIEVER_BACKEND=tinyfish" >> .env
echo "TINYFISH_API_KEY=your_actual_key" >> .env
```

### Step 4: Test
```bash
export PYTHONPATH=$PYTHONPATH:. && streamlit run ui/dashboard.py
```

## 🔧 Current System Behavior

**With `RETRIEVER_BACKEND=http` (default):**
- Uses curated seed URLs
- Fast, reliable, cached
- Limited to static HTML sites
- ✅ Works end-to-end now

**With `RETRIEVER_BACKEND=tinyfish` (when implemented):**
- Live search engine scraping
- JS-rendered page support
- Bot-protected sites accessible
- Screenshot capture
- Falls back to HTTP on any error

## 📊 Architecture Benefits

1. **Modularity**: Swap retrievers without touching agent logic
2. **Testability**: Easy to mock retrievers for unit tests
3. **Fallback Safety**: Never fails completely (HTTP fallback)
4. **Transparency**: UI shows which method was used
5. **Future-Proof**: Easy to add new retrievers (e.g., Playwright, Selenium)

## 🚀 Next Actions

1. ✅ **Done**: Architecture + HTTP implementation
2. ⏳ **Pending**: TinyFish API access
3. ⏳ **Pending**: Implement `_fetch_with_tinyfish()` and `search()`
4. ⏳ **Pending**: Test with real TinyFish backend
5. ⏳ **Pending**: Compare HTTP vs TinyFish quality

## 📝 Files Changed

- `app/retrievers/` (new package)
- `app/agents/web_agent.py` (refactored)
- `ui/dashboard.py` (added browser trace)
- `.env.example` (added RETRIEVER_BACKEND)
- `TINYFISH_INTEGRATION.md` (implementation guide)

## ✨ Demo-Ready Features

Even without TinyFish, the system now:
- ✅ Shows retrieval method transparency
- ✅ Displays browsing trace
- ✅ Demonstrates modular architecture
- ✅ Proves fallback logic works
- ✅ Generates grounded reports with citations
