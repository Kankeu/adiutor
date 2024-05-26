import os
import sys

PARENT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(PARENT_DIR)

from .web_search import WebSearch
from .web_scraper import WebScraper