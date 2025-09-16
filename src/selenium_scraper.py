from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from src.utils import get_random_user_agent, random_delay, retry
import time

class SeleniumScraper:
    def __init__(self, headless=True, timeout=30):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        
    def setup_driver(self):
        """Set up Chrome WebDriver with options"""
        chrome_options = Options()
        if self.fetch_pageheadless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        try:
            driver_path = ChromeDriverManager().install()
            driver_path = str(Path(driver_path).with_name("chromedriver.exe"))
            self.logger.info(f"Using ChromeDriver executable: {driver_path}")

            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            print(f"Failed to setup driver: {e}")
            return False

    
    @retry(max_attempts=3, delay=2.0)
    def fetch_page(self, url, wait_for_element=None):
        """Fetch a page with Selenium and return the page source with enhanced stability"""
        if not self.driver:
            if not self.setup_driver():
                raise Exception("Failed to initialize WebDriver")
        
        try:
            self.driver.get(url)
            random_delay(1.0, 2.0)
            
            # Wait for specific element if provided
            if wait_for_element:
                try:
                    WebDriverWait(self.driver, self.timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
                    )
                except TimeoutException:
                    self.logger.warning(f"Timeout waiting for element {wait_for_element} on {url}")
                    # Continue anyway, we might still get some content
            
            # Wait for page to load completely with multiple checks
            try:
                WebDriverWait(self.driver, self.timeout).until(
                    lambda driver: driver.execute_script('return document.readyState') == 'complete'
                )
            except TimeoutException:
                self.logger.warning(f"Page {url} took too long to load completely")
            
            # Additional check for content presence
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: len(driver.page_source) > 1000
                )
            except TimeoutException:
                self.logger.warning(f"Page {url} has very little content")
            
            return self.driver.page_source
            
        except Exception as e:
            self.logger.error(f"Error fetching page {url}: {e}")
            # Try to recover driver
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            raise
    
    def click_element(self, selector):
        """Click on an element using CSS selector"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            element.click()
            random_delay(1.0, 2.0)
            return True
        except Exception as e:
            print(f"Error clicking element {selector}: {e}")
            return False
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the page"""
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            random_delay(0.5, 1.0)
        except Exception as e:
            print(f"Error scrolling to bottom: {e}")
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None