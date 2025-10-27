"""
Web scraping module for HTML/JSON data extraction.

This module provides functionality to scrape and extract structured data
from golf course websites and related sources.
"""

from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
import json
import logging

logger = logging.getLogger(__name__)


class WebScraper:
    """
    Web scraper for extracting golf course data from HTML and JSON sources.
    
    Features:
    - HTML parsing with BeautifulSoup
    - JSON data extraction
    - Configurable extraction rules
    - Error handling and retries
    """
    
    def __init__(self, timeout: int = 30, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the web scraper.
        
        Args:
            timeout: Request timeout in seconds
            headers: Optional custom HTTP headers
        """
        self.timeout = timeout
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (compatible; GolfCourseBot/1.0)'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_html(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse HTML content from a URL.
        
        Args:
            url: The URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except requests.RequestException as e:
            logger.error(f"Failed to fetch HTML from {url}: {e}")
            return None
    
    def fetch_json(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch JSON data from a URL.
        
        Args:
            url: The URL to fetch
            
        Returns:
            Parsed JSON data or None if failed
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.error(f"Failed to fetch JSON from {url}: {e}")
            return None
    
    def extract_golf_course_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract golf course information from parsed HTML.
        
        This is a template method that should be customized based on
        the specific structure of the target website.
        
        Args:
            soup: BeautifulSoup object containing the HTML
            
        Returns:
            Dictionary with extracted golf course data
        """
        data = {
            'name': None,
            'address': None,
            'phone': None,
            'holes': None,
            'par': None,
            'yardage': None,
            'rating': None,
            'slope': None,
            'amenities': [],
            'description': None
        }
        
        # Example extraction logic (customize based on actual HTML structure)
        # This demonstrates the pattern - users should extend this
        title = soup.find('h1', class_='course-name')
        if title:
            data['name'] = title.get_text(strip=True)
        
        description = soup.find('div', class_='course-description')
        if description:
            data['description'] = description.get_text(strip=True)
        
        # Extract structured data if available
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                structured_data = json.loads(json_ld.string)
                data['structured_data'] = structured_data
            except json.JSONDecodeError:
                pass
        
        return data
    
    def extract_with_selectors(
        self,
        soup: BeautifulSoup,
        selectors: Dict[str, Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Extract data using custom CSS selectors.
        
        Args:
            soup: BeautifulSoup object
            selectors: Dictionary mapping field names to selector configs
                      e.g., {'name': {'selector': 'h1.title', 'attr': 'text'}}
        
        Returns:
            Extracted data dictionary
        """
        data = {}
        
        for field, config in selectors.items():
            selector = config.get('selector')
            attr = config.get('attr', 'text')
            multiple = config.get('multiple', False)
            
            if multiple:
                elements = soup.select(selector)
                if attr == 'text':
                    data[field] = [el.get_text(strip=True) for el in elements]
                else:
                    data[field] = [el.get(attr) for el in elements]
            else:
                element = soup.select_one(selector)
                if element:
                    if attr == 'text':
                        data[field] = element.get_text(strip=True)
                    else:
                        data[field] = element.get(attr)
        
        return data
    
    def scrape_golf_course(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Complete workflow to scrape golf course data from a URL.
        
        Args:
            url: URL of the golf course page
            
        Returns:
            Extracted golf course data
        """
        soup = self.fetch_html(url)
        if not soup:
            return None
        
        return self.extract_golf_course_info(soup)
