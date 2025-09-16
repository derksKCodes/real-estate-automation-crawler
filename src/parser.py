from bs4 import BeautifulSoup
from src.utils import clean_text, format_price, extract_number

class Parser:
    @staticmethod
    def parse_listing_card(card_html, selectors):
        """Parse a single listing card with enhanced error handling"""
        soup = BeautifulSoup(card_html, 'lxml')
        listing = {}
        
        try:
            # Extract basic information with fallbacks
            listing['title'] = clean_text(Parser._extract_text(soup, selectors.get('product_title'))) or "No title"
            listing['price'] = format_price(Parser._extract_text(soup, selectors.get('price'))) or "Price not available"
            listing['location'] = clean_text(Parser._extract_text(soup, selectors.get('location'))) or "Location not available"
            
            # Extract URL with multiple fallback strategies
            url_selector = selectors.get('product_link')
            if url_selector:
                link = soup.select_one(url_selector)
                if link:
                    href = link.get('href')
                    if href:
                        # Handle relative URLs
                        if href.startswith('/'):
                            base_url = selectors.get('base_url', '')
                            listing['url'] = f"{base_url}{href}" if base_url else href
                        else:
                            listing['url'] = href
            
            # Extract image URL with multiple strategies
            image_selector = selectors.get('image_url')
            if image_selector:
                if '::attr(src)' in image_selector:
                    selector = image_selector.replace('::attr(src)', '')
                    img = soup.select_one(selector)
                    if img:
                        src = img.get('src') or img.get('data-src') or img.get('data-original')
                        if src:
                            listing['image_url'] = src
                else:
                    img = soup.select_one(image_selector)
                    if img:
                        src = img.get('src') or img.get('data-src') or img.get('data-original')
                        if src:
                            listing['image_url'] = src
            
            return listing
            
        except Exception as e:
            print(f"Error parsing listing card: {e}")
            return listing  # Return whatever we managed to parse
    
    @staticmethod
    def parse_listing_detail(detail_html, selectors):
        """Parse detailed listing information from a detail page"""
        soup = BeautifulSoup(detail_html, 'lxml')
        details = {}
        
        # Extract property details
        details['beds'] = extract_number(Parser._extract_text(soup, selectors.get('beds')))
        details['baths'] = extract_number(Parser._extract_text(soup, selectors.get('baths')))
        details['sqft'] = extract_number(Parser._extract_text(soup, selectors.get('sqft')))
        details['acres'] = extract_number(Parser._extract_text(soup, selectors.get('acres')))
        details['parking'] = clean_text(Parser._extract_text(soup, selectors.get('parking')))
        details['garage'] = clean_text(Parser._extract_text(soup, selectors.get('garage')))
        details['property_type'] = clean_text(Parser._extract_text(soup, selectors.get('property_type')))
        
        # Extract agent information
        agent = {}
        agent['name'] = clean_text(Parser._extract_text(soup, selectors.get('agent_name')))
        agent['license'] = clean_text(Parser._extract_text(soup, selectors.get('agent_license')))
        agent['office'] = clean_text(Parser._extract_text(soup, selectors.get('agent_office')))
        agent['phone'] = clean_text(Parser._extract_text(soup, selectors.get('agent_phone')))
        
        return {
            'details': details,
            'agent': agent
        }
    
    @staticmethod
    def _extract_text(soup, selector):
        """Extract text using CSS selector"""
        if not selector:
            return ""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else ""
    
    @staticmethod
    def extract_listing_cards(html, selectors):
        """Extract all listing cards from search results page"""
        soup = BeautifulSoup(html, 'lxml')
        list_container = selectors.get('list_container')
        product_card = selectors.get('product_card')
        
        if not list_container or not product_card:
            return []
        
        container = soup.select_one(list_container)
        if not container:
            return []
        
        return container.select(product_card)