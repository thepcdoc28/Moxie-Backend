import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_web(query, max_results=3):
    """
    Performs a web search using DuckDuckGo HTML version.
    Returns a list of dictionaries containing title, url, and snippet.
    """
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for result in soup.find_all('div', class_='result'):
            if len(results) >= max_results:
                break
                
            title_tag = result.find('a', class_='result__url')
            snippet_tag = result.find('a', class_='result__snippet')
            
            if title_tag and snippet_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href', '')
                if link.startswith('//duckduckgo.com/l/?uddg='):
                    link = urllib.parse.unquote(link.split('uddg=')[1].split('&')[0])
                snippet = snippet_tag.get_text(strip=True)
                
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet
                })
                
        return results
    except Exception as e:
        print(f"Web search error: {e}")
        return []
