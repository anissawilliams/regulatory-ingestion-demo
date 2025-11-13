import requests
from bs4 import BeautifulSoup

def scrape_url(url, source="Unknown"):
    print(f"Scraping {url}...")
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        full_text = "\n".join(p.get_text() for p in paragraphs if p.get_text().strip())
        #print("full text: " + full_text)
        return {
            "title": soup.title.string.strip() if soup.title else "Untitled",
            "source": source,
            "url": url,
            "full_text": full_text
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
