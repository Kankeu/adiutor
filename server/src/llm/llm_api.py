import json
import asyncio
import requests

# Interface to communicate with AWS's LLM model
class LLMAPI:

    def __init__(self,url,api_token,options={"max_gen_len":1024,"temperature":1,"top_p":.9}):
        self.url = url
        self.options = options|{"api_token":api_token}
        self.timeout = 600000

    def generate(
            self,
            prompt,
            options={}
    ):
        res = requests.post(self.url,json={"prompt": prompt}|self.options|options,timeout=self.timeout)
        return json.loads(res.text)["body"]["generation"]

    def iter_over_async(self,ait, loop=asyncio.new_event_loop()):
        ait = ait.__aiter__()
        async def get_next():
            try: obj = await ait.__anext__(); return False, obj
            except StopAsyncIteration: return True, None
        while True:
            done, obj = loop.run_until_complete(get_next())
            if done: break
            yield obj