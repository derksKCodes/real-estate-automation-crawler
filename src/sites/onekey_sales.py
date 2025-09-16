from src.scraper import BaseScraper
from src.utils import random_delay
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

class OneKeySalesScraper(BaseScraper):
    def scrape(self):
        self.logger.info(f"Starting scraper: {self.site_name}")
        
        try:
            # Construct search URL
            base_url = self.config['base_url']
            search_url = self.config['search_url']
            full_url = f"{base_url}{search_url}"
            
            # Fetch first page
            html = self.fetch_search_page(full_url)
            if not html:
                self.logger.error("Failed to fetch initial search page")
                return []
            
            # Parse listings from first page
            cards = self.parse_search_page(html)
            self.logger.info(f"Found {len(cards)} listing cards on first page")
            
            # Process each listing
            for i, card in enumerate(cards):
                self.logger.info(f"Processing listing {i+1}/{len(cards)}")
                listing = self.process_listing_card(str(card))
                if listing:
                    self.listings.append(listing)
                random_delay(self.config.get('delay', 2.0) / 2, self.config.get('delay', 3.0))
            
            # Handle pagination for OneKey MLS
            page_num = 2
            max_pages = 5  # Limit pages for demo purposes
            
            while page_num <= max_pages:
                try:
                    next_page_btn = self.selenium_scraper.driver.find_element(
                        By.CSS_SELECTOR, f"a.page-link[data-page='{page_num}']"
                    )
                    
                    if next_page_btn:
                        self.logger.info(f"Navigating to page {page_num}")
                        next_page_btn.click()
                        
                        # Wait for page to load
                        WebDriverWait(self.selenium_scraper.driver, self.config['timeout']).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, self.config['selectors']['list_container']))
                        )
                        
                        # Get updated page source
                        html = self.selenium_scraper.driver.page_source
                        cards = self.parse_search_page(html)
                        self.logger.info(f"Found {len(cards)} listing cards on page {page_num}")
                        
                        # Process each listing on this page
                        for i, card in enumerate(cards):
                            self.logger.info(f"Processing listing {i+1}/{len(cards)} on page {page_num}")
                            listing = self.process_listing_card(str(card))
                            if listing:
                                self.listings.append(listing)
                            random_delay(self.config.get('delay', 2.0) / 2, self.config.get('delay', 3.0))
                        
                        page_num += 1
                    else:
                        break
                        
                except (TimeoutException, Exception) as e:
                    self.logger.warning(f"Pagination stopped at page {page_num}: {e}")
                    break
            
            self.logger.info(f"Successfully scraped {len(self.listings)} listings from {self.site_name}")
            return self.listings
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            return []