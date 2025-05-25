import requests

def fetch_content(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"[Error fetching content: {e}]" 