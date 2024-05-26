import datetime
import os
PARENT_DIR = os.path.dirname(os.path.realpath(__file__))


import json
from .web_scraper import WebScraper,SearchResult

class WebSearch:
    def __init__(self,llm_api):
        self.llm_api = llm_api
        self.web_scraper = WebScraper()

    def get_aggregation_prompt(self,query,system_prompt,context):
        # Prompt to combine summarized page contents with sources (page identifier)
        system_prompt = system_prompt or ""
        return f"""<<SYS>>You are a useful and harmful information retriever. Based on the following web page contents of a web search answer the user query below. Formulate your answer in the Markdown syntax. Do not forget to indicate the page identifiers in your answer.
Today is {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}      
      
<</SYS>>
[INST]
Web page contents: ```
Page identifier: WSD-#1
Page content: Amor fati is a Latin phrase that translates to "love of fate" or "love of one's fate."

############################################

Page identifier: WSD-#2
Page content: Amor fati describes an attitude of accepting and even embracing everything that happens in life, both the positive and negative, with a sense of gratitude and positivity.
```

User query: What means amor fati?
[/INST]
Answer: Amor fati is a Latin phrase that translates to "love of fate" (WSD-#1) It describes an attitude of accepting and even embracing everything that happens in life (WSD-#2).

[INST]
Web page contents: ```{context}```

{system_prompt}          
User query: {query}
[/INST]
Answer:
"""

    def get_summary_prompt(self,query,system_prompt,context):
        # Prompt to summarize page contents
        return f"""<<SYS>>You are a useful and harmful information retriever. Do not mention that the text does not provide information about the query.
Today is {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}    

<</SYS>>
        
[INST]
{system_prompt}          
Summarize in detail the text below based on the following query: "{query}".

Text: ```{context}```
[/INST]
Summary:
"""

    async def process(self,query,system_prompt):
        # Retrieve page contents with DuckDuckGo or Google search
        results:list[SearchResult] = self.web_scraper.search(query,k=3)
        sources = [dict(id=i,url=r.get_url(),title=r.get_title(),text=r.get_snippet(),score=round(1-.2*(i/(len(results)-1)))) for i,r in enumerate(results)]
        yield json.dumps({"status":"ok","type":"metadata","payload":{"cost": round(len((" ".join(r.get_page() for r in results)).split()) / 10), "sources": sources}})
        options = {"temperature":1,"top_p":1,"max_gen_len":1024}
        context = ""
        for i,res in enumerate(results):
            # Model context is limited to 2048
            if len(context) > int(2048*3.5):
                continue
            summary = self.llm_api.generate(self.get_summary_prompt(query,system_prompt,res.get_page()),options=options)
            context += f"""
Page identifier: WSD-#{i+1}
Page content: {summary}

############################################

"""
        response = self.llm_api.generate(self.get_aggregation_prompt(query,system_prompt,context),options=options)
        yield json.dumps({"status":"ok","type":"web_search","payload":{"response":response}})

        yield json.dumps({"status":"done","type":"web_search","payload":None})
