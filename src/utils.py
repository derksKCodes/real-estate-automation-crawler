import re
import time
import random
import logging
from functools import wraps
from fake_useragent import UserAgent

def setup_logger(name, log_file, level=logging.INFO):
    """Set up a logger with file and console handlers"""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File handler
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    
    return logger

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def format_price(price_text):
    """Extract and format price from text"""
    if not price_text:
        return ""
    
    # Remove non-numeric characters except decimal point
    price = re.sub(r'[^\d.]', '', price_text)
    try:
        return f"${float(price):,.0f}"
    except ValueError:
        return price_text

def extract_number(text):
    """Extract numbers from text"""
    if not text:
        return None
    numbers = re.findall(r'\d+\.?\d*', text)
    return float(numbers[0]) if numbers else None

def random_delay(min_delay=1.0, max_delay=3.0):
    """Sleep for a random time between min and max seconds"""
    time.sleep(random.uniform(min_delay, max_delay))

def retry(max_attempts=3, delay=2.0, backoff=2.0, exceptions=(Exception,)):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise e
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

def get_random_user_agent():
    """Get a random user agent"""
    ua = UserAgent()
    return ua.random