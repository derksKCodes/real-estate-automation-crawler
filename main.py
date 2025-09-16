import time
from src.config_loader import ConfigLoader
from src.exporter import Exporter
from src.utils import setup_logger

# Import all site scrapers
from src.sites.staten_island import StatenIslandScraper
from src.sites.brooklyn_mls import BrooklynMLSScraper
from src.sites.streeteasy_sales import StreetEasySalesScraper
from src.sites.streeteasy_rentals import StreetEasyRentalsScraper
from src.sites.onekey_sales import OneKeySalesScraper
from src.sites.onekey_rentals import OneKeyRentalsScraper
from src.sites.onekey_commercial_sales import OneKeyCommercialSalesScraper
from src.sites.onekey_commercial_rentals import OneKeyCommercialRentalsScraper
# Update src/main.py (enhancements)

def main():
    # Set up logging
    logger = setup_logger('main', 'logs/allsites.log')
    logger.info("Starting real estate multi-scraper")
    
    # Load configurations
    try:
        config_loader = ConfigLoader()
        sites = config_loader.get_all_sites()
        logger.info(f"Loaded configurations for {len(sites)} sites: {', '.join(sites)}")
    except Exception as e:
        logger.error(f"Failed to load configurations: {e}")
        return
    
    # Initialize exporter
    exporter = Exporter()
    
    # Map site names to scraper classes
    scraper_classes = {
        'staten_island': StatenIslandScraper,
        'brooklyn_mls': BrooklynMLSScraper,
        'streeteasy_sales': StreetEasySalesScraper,
        'streeteasy_rentals': StreetEasyRentalsScraper,
        'onekey_sales': OneKeySalesScraper,
        'onekey_rentals': OneKeyRentalsScraper,
        'onekey_commercial_sales': OneKeyCommercialSalesScraper,
        'onekey_commercial_rentals': OneKeyCommercialRentalsScraper
    }
    
    # Track overall statistics
    total_listings = 0
    successful_sites = 0
    failed_sites = 0
    
    # Scrape each site
    for site_name in sites:
        if site_name not in scraper_classes:
            logger.warning(f"No scraper class found for {site_name}, skipping")
            failed_sites += 1
            continue
        
        try:
            logger.info(f"Starting scraper: {site_name}")
            
            # Get config for this site
            config = config_loader.get_config(site_name)
            
            # Initialize and run scraper
            scraper_class = scraper_classes[site_name]
            scraper = scraper_class(site_name, config)
            listings = scraper.scrape()
            
            # Export results
            if listings:
                exporter.export_listings(listings, site_name)
                logger.info(f"Exported {len(listings)} listings from {site_name}")
                total_listings += len(listings)
                successful_sites += 1
            else:
                logger.warning(f"No listings scraped from {site_name}")
                failed_sites += 1
            
            # Clean up
            scraper.close()
            
        except Exception as e:
            logger.error(f"Error scraping {site_name}: {e}")
            failed_sites += 1
            continue
        
        # Delay between sites
        time.sleep(5)
    
    # Final summary
    logger.info(f"Finished scraping all sites. Successful: {successful_sites}, Failed: {failed_sites}, Total listings: {total_listings}")

if __name__ == "__main__":
    main()