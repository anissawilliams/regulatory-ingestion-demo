import requests
from bs4 import BeautifulSoup
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path

# Session with connection pooling
SESSION = None


def get_session():
    global SESSION
    if SESSION is None:
        SESSION = requests.Session()
        retry = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        SESSION.mount('http://', adapter)
        SESSION.mount('https://', adapter)
        SESSION.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    return SESSION


# Cache directory
CACHE_DIR = Path("scraper_cache")
CACHE_DIR.mkdir(exist_ok=True)


def get_cache_path(url):
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return CACHE_DIR / f"{url_hash}.json"


def scrape_url(url, source="EPA", use_cache=True, timeout=10):
    """Fast, cached scraper"""
    # Check cache
    if use_cache:
        cache_path = get_cache_path(url)
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                cached = json.load(f)
                print(f"📦 Using cached content ({len(cached.get('full_text', ''))} chars)")
                return cached

    try:
        session = get_session()
        response = session.get(url, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "lxml")

        # Remove noise elements
        for tag in soup(["header", "footer", "nav", "aside", "script", "style", "noscript", "iframe"]):
            tag.decompose()

        # Extract content - try multiple selectors
        main = (soup.find("main") or
                soup.find("article") or
                soup.find("div", class_=re.compile(r"content|main|body", re.I)) or
                soup.body)

        if not main:
            print(f"⚠️ Warning: Could not find main content area")
            return None

        # Get text with better formatting preservation
        clean_text = main.get_text(separator="\n", strip=True)

        # Clean up excessive whitespace but preserve paragraph structure
        clean_text = re.sub(r' +', ' ', clean_text)  # Multiple spaces -> single space
        clean_text = re.sub(r'\n +', '\n', clean_text)  # Remove leading spaces on lines
        clean_text = re.sub(r' +\n', '\n', clean_text)  # Remove trailing spaces on lines
        clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)  # Max 2 newlines (paragraph break)

        # Limit length but don't cut off mid-sentence
        if len(clean_text) > 50000:
            clean_text = clean_text[:50000]
            # Find last sentence boundary
            last_period = clean_text.rfind('.')
            if last_period > 45000:  # If we found a period in the last 5000 chars
                clean_text = clean_text[:last_period + 1]

        title = soup.title.string.strip() if soup.title else "Untitled"

        result = {
            "bill": title,
            "source": source,
            "url": url,
            "full_text": clean_text
        }

        # Cache result
        if use_cache:
            with open(cache_path, 'w') as f:
                json.dump(result, f)

        print(f"✅ Scraped {len(clean_text)} characters")

        return result

    except Exception as e:
        print(f"❌ Error scraping {url}: {str(e)}")
        return None


def scrape_multiple_urls(urls, source="EPA", max_workers=5):
    """Parallel scraping"""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(scrape_url, url, source): url for url in urls}
        for future in as_completed(future_to_url):
            result = future.result()
            if result:
                results.append(result)
    return results