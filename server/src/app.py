import os
APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(APP_PATH, 'public/')
import json

from flask import Flask, Response, jsonify, request, stream_with_context,render_template
from flask_cors import CORS
import asyncio
import nest_asyncio

from .llm.llm_api import LLMAPI
from .calendar import Calendar,TodoAPI,Weather
from .web_search import WebSearch

nest_asyncio.apply()
app = Flask(__name__, static_url_path="/",static_folder=TEMPLATE_PATH)

CORS(app)

# API Token of LLM
LLM_URL = "https://6xtdhvodk2.execute-api.us-west-2.amazonaws.com/dsa_llm/generate"
LLM_API_TOKEN = "E3E4C979979A432398D1599C22046375"

@app.route("/api/query", methods=["POST"])
def query_index():
    data = json.loads(request.data.decode("UTF-8"))

    payload = data.get("payload")
    settings = data.get("settings",{})
    settings["url"] = settings["url"].strip() if settings.get("url",None) else None
    settings["api_token"] = settings["api_token"].strip() if settings.get("api_token",None) else None
    settings["system_prompt"] = settings["system_prompt"].strip() if settings.get("system_prompt",None) else None

    llm_api = LLMAPI(settings["url"] or LLM_URL,settings["api_token"] or LLM_API_TOKEN)
    calendar = Calendar(llm_api)
    web_search = WebSearch(llm_api)

    if payload["feature"]=="calendar":
        # Stream the server response
        return Response(stream_with_context(llm_api.iter_over_async(calendar.process(payload["query"],system_prompt=settings["system_prompt"],commit=payload.get("commit",True)))))
    if payload["feature"]=="web_search":
        # Stream the server response
        return Response(stream_with_context(llm_api.iter_over_async(web_search.process(payload["query"],system_prompt=settings["system_prompt"]))))


@app.route("/api/calendar", methods=["GET"])
def calendar():
    # Return all tasks and weather forecasts
    return jsonify(dict(tasks=[t.json() for t in TodoAPI().get_all()],forecasts=[f.json() for f in asyncio.run(Weather().get("Kaiserslautern"))]))

@app.route("/")
def public():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run()
