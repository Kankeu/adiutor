import os
PARENT_DIR = os.path.dirname(os.path.realpath(__file__))

from bs4 import BeautifulSoup
import requests
import random
from urllib.parse import quote_plus
from duckduckgo_search import DDGS
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.retrievers import ArxivRetriever,WikipediaRetriever

class WebScraper:
    def __init__(self):
        self.ddg = DDGS()

    # Extract page contents using adapted retrievers
    def scrape_page(self, url):
        # Avg. length of a token is ~ 3.75 and context window 2048
        max_chars = int(2048*3.5)
        def clean(text):
            text = text.strip()
            last_text = text
            text = text.replace("\n\n\n","\n\n").replace("   ","  ")
            while(text!=last_text):
                last_text = text
                text = text.replace("\n\n\n","\n\n").replace("   ","  ")
            return "\n".join(line for line in text.split("\n"))

        if url.endswith(".pdf"):
            loader = PyMuPDFLoader(url)
            doc = loader.load()
            return clean(str(doc)).strip()[:max_chars]
        elif "arxiv.org" in url:
            query = url.split("/")[-1]
            retriever = ArxivRetriever(load_max_docs=1, doc_content_chars_max=max_chars)
            docs = retriever.get_relevant_documents(query=query)
            return docs[0].page_content.strip()
        elif "wikipedia.org" in url:
            query = url.split("/")[-1]
            retriever = WikipediaRetriever(load_max_docs=1, doc_content_chars_max=max_chars)
            docs = retriever.get_relevant_documents(query=query)
            return docs[0].page_content.strip()
        else:
            response,_ = self._get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            for script in soup(["script", "style"]):
                script.extract()

            return clean(soup.get_text()).strip()[:max_chars]

    # Choose randomly a user agent for web search
    def get_random_user_agent(self):
        len1 = len(USER_AGENTS_LEVEL_1)
        len2 = len(USER_AGENTS_LEVEL_2)
        len3 = len(USER_AGENTS_LEVEL_3)
        USER_AGENTS = USER_AGENTS_LEVEL_1 + USER_AGENTS_LEVEL_2 + USER_AGENTS_LEVEL_3
        weights = [25*len3/len1 for _ in USER_AGENTS_LEVEL_1] + [5*len3/len2 for _ in USER_AGENTS_LEVEL_2] +  [1 for _ in USER_AGENTS_LEVEL_3]
        return random.choices(USER_AGENTS,weights=[AGENT_HITS.get(USER_AGENTS[i],1)*w for i,w in enumerate(weights)])[0]


    def _get(self, url, params=None):
        user_agent = self.get_random_user_agent()
        try:
            response = requests.get(
                url=url,
                headers={
                    "User-Agent": user_agent
                },
                params=params,
                timeout=3,
            )
            response.raise_for_status()
        except Exception as e:
            raise e
        return response,user_agent

    # Perform web search
    def search(self,query,k=3):
        try:
            return self.duckduckgo(query,k=k)
        except Exception as e:
            print(e)
            return self.google(query,k=k)

    def duckduckgo(self,query,k=3):
        results = self.ddg.text(query, region='wt-wt', max_results=k)
        return [SearchResult(res["href"],res["title"],res["body"],self.scrape_page(res["href"])) for res in results]

    def google(self, query, k=3):
        params = {"q": quote_plus(query), "num": k*2, "hl": "en", "start": 0}
        results = []
        trials = 1
        fails = 0
        while 0 < params["num"]:
            try:
                params["offset"] = k - params["num"]
                response,user_agent = self._get("https://www.google.com/search", params=params)

                soup = BeautifulSoup(response.text, "html.parser")
                blocks = soup.find_all("div", attrs={"class": "g"})
                for block in blocks:
                    link = block.find("a", href=True)
                    title = block.find("h3")
                    snippet = block.find("div", {"style": "-webkit-line-clamp:2"})
                    if link and title and snippet:
                        AGENT_HITS[user_agent] = AGENT_HITS.get(user_agent,1) + 1
                        params["num"] -= 1
                        results.append(SearchResult(link["href"], title.text, snippet.text, self.scrape_page(link["href"])))
                if trials == 3 or len(results) >= k:
                    return results[:k]
                trials += 1
            except Exception as e:
                fails += 1
                if fails >= 50:
                    return []
        return results



USER_AGENTS_LEVEL_1 = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
]

USER_AGENTS_LEVEL_2 = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.3"
]

USER_AGENTS_LEVEL_3 = [u.strip() for u in open(PARENT_DIR+"/user_agents.txt").readlines() if "Mozilla/5.0" in u]

AGENT_HITS = {}

# Represent search result
class SearchResult:
    def __init__(self, url, title, snippet, page):
        self.url = url
        self.title = title
        self.snippet = snippet
        self.page = page

    def get_url(self):
        return self.url

    def get_title(self):
        return self.title

    def get_snippet(self):
        return self.snippet

    def get_page(self):
        return self.page

    def __repr__(self):
        return f"(url={self.url}, title={self.title}, snippet={self.snippet})"