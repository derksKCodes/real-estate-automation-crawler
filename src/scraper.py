from abc import ABC, abstractmethod
from src.selenium_scraper import SeleniumScraper
from src.parser import Parser
from src.utils import setup_logger, random_delay, retry
import time

class BaseScraper(ABC):
    def __init__(self, site_name, config):
        self.site_name = site_name
        self.config = config
        self.logger = setup_logger(site_name, f'logs/{site_name}.log')
        self.selenium_scraper = SeleniumScraper(headless=True, timeout=config.get('timeout', 30))
        self.parser = Parser()
        self.listings = []
    
    @abstractmethod
    def scrape(self):
        """Main scraping method to be implemented by each site scraper"""
        pass
    
    def fetch_search_page(self, page_url):
        """Fetch a search results page with enhanced error handling"""
        try:
            list_container_selector = self.config['selectors'].get('list_container')
            html = self.selenium_scraper.fetch_page(page_url, list_container_selector)
            
            # Verify we got meaningful content
            if html and len(html) > 1000:  # Basic check for meaningful content
                return html
            else:
                self.logger.warning(f"Page content seems empty or too short: {page_url}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching search page {page_url}: {e}")
            return None
    
    def parse_search_page(self, html):
        """Parse search results page and extract listing cards"""
        try:
            cards = self.parser.extract_listing_cards(html, self.config['selectors'])
            return cards
        except Exception as e:
            self.logger.error(f"Error parsing search page: {e}")
            return []
    
    def fetch_listing_detail(self, listing_url):
        """Fetch detailed listing page"""
        try:
            # Handle relative URLs
            if listing_url.startswith('/'):
                base_url = self.config['base_url']
                full_url = f"{base_url}{listing_url}"
            else:
                full_url = listing_url
            
            html = self.selenium_scraper.fetch_page(full_url)
            return html
        except Exception as e:
            self.logger.error(f"Error fetching listing detail {listing_url}: {e}")
            return None
    
    def parse_listing_detail(self, html):
        """Parse detailed listing information"""
        try:
            detail_info = self.parser.parse_listing_detail(html, self.config['selectors'])
            return detail_info
        except Exception as e:
            self.logger.error(f"Error parsing listing detail: {e}")
            return {'details': {}, 'agent': {}}
    
    def process_listing_card(self, card_html):
        """Process a single listing card with enhanced error handling"""
        try:
            # Parse basic info from card
            listing = self.parser.parse_listing_card(card_html, self.config['selectors'])
            
            if not listing:
                self.logger.warning("Failed to parse basic listing info from card")
                return None
            
            # Fetch detail page if URL is available
            if 'url' in listing and listing['url']:
                detail_html = self.fetch_listing_detail(listing['url'])
                if detail_html:
                    detail_info = self.parse_listing_detail(detail_html)
                    listing.update(detail_info)
                else:
                    self.logger.warning(f"Failed to fetch detail page for {listing.get('url', 'unknown')}")
            
            # Add timestamp
            from datetime import datetime
            listing['scraped_at'] = datetime.now().isoformat()
            
            return listing
            
        except Exception as e:
            self.logger.error(f"Error processing listing card: {e}")
            return None
    
    def navigate_pagination(self):
        """Handle pagination - to be implemented by subclasses if needed"""
        # This is a basic implementation that can be overridden
        return []
    
    def close(self):
        """Clean up resources"""
        self.selenium_scraper.close()
    
    def __del__(self):
        self.close()