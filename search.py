# search.py

import os
from exa_py import Exa
from dotenv import load_dotenv

load_dotenv()

def search_exa(query, num_results=5, **kwargs):
    exa = Exa(api_key=os.getenv("EXA_API_KEY"))
    result = exa.search_and_contents(query, **kwargs)
    results = []
    for item in result.results[:num_results]:
        url = item.url
        title = item.title
        summary = item.summary
        results.append((url, title, summary))
    return results