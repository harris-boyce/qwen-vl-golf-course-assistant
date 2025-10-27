"""
Qwen-VL Golf Course Assistant

An extensible AI agent that integrates web scraping, satellite imagery analysis,
and large language models for golf course insights.
"""

__version__ = "0.1.0"
__author__ = "Harris Boyce"

from golf_assistant.agent.qwen_agent import QwenVLAgent
from golf_assistant.scraper.web_scraper import WebScraper
from golf_assistant.imagery.satellite_retriever import SatelliteRetriever

__all__ = [
    "QwenVLAgent",
    "WebScraper",
    "SatelliteRetriever",
]
