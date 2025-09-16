from src.scraper import BaseScraper
from src.utils import random_delay

class StatenIslandScraper(BaseScraper):
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
            
            # Handle pagination (simplified example)
            # In real implementation, you would detect and navigate to next pages
            
            self.logger.info(f"Successfully scraped {len(self.listings)} listings from {self.site_name}")
            return self.listings
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            return []