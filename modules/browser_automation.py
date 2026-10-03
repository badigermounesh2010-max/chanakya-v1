import logging
from typing import Dict, List, Any, Optional
import time

logger = logging.getLogger(__name__)

class BrowserAutomation:
    """Web automation using Selenium + Chrome"""
    
    def __init__(self, headless: bool = False):
        self.driver = None
        self.headless = headless
        self.init_browser()
    
    def init_browser(self):
        """Initialize Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            self.driver = webdriver.Chrome(options=options)
            self.By = By
            self.WebDriverWait = WebDriverWait
            self.EC = EC
            logger.info("✅ Browser initialized")
        except Exception as e:
            logger.error(f"❌ Browser init failed: {e}")
    
    def open_url(self, url: str, wait_time: int = 10):
        """Open URL in browser"""
        try:
            self.driver.get(url)
            time.sleep(wait_time / 10)  # Small delay
            logger.info(f"Opened: {url}")
            return True
        except Exception as e:
            logger.error(f"URL open error: {e}")
            return False
    
    def find_element(self, selector: str, by: str = 'css', wait: int = 10):
        """Find element by selector"""
        try:
            by_map = {'css': self.By.CSS_SELECTOR, 'xpath': self.By.XPATH, 'id': self.By.ID, 'class': self.By.CLASS_NAME}
            by_type = by_map.get(by, self.By.CSS_SELECTOR)
            element = self.WebDriverWait(self.driver, wait).until(
                self.EC.presence_of_element_located((by_type, selector))
            )
            return element
        except Exception as e:
            logger.error(f"Element find error: {e}")
            return None
    
    def click_element(self, selector: str, by: str = 'css'):
        """Click an element"""
        try:
            element = self.find_element(selector, by)
            if element:
                element.click()
                logger.info(f"Clicked: {selector}")
                return True
        except Exception as e:
            logger.error(f"Click error: {e}")
        return False
    
    def send_text(self, selector: str, text: str, by: str = 'css', clear_first: bool = True):
        """Send text to element"""
        try:
            element = self.find_element(selector, by)
            if element:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                logger.info(f"Text sent: {text[:50]}...")
                return True
        except Exception as e:
            logger.error(f"Text send error: {e}")
        return False
    
    def get_text(self, selector: str, by: str = 'css') -> Optional[str]:
        """Get element text"""
        try:
            element = self.find_element(selector, by)
            if element:
                return element.text
        except Exception as e:
            logger.error(f"Text get error: {e}")
        return None
    
    def scroll_to_element(self, selector: str, by: str = 'css'):
        """Scroll to element"""
        try:
            element = self.find_element(selector, by)
            if element:
                self.driver.execute_script('arguments[0].scrollIntoView(true);', element)
                time.sleep(0.5)
                logger.info(f"Scrolled to: {selector}")
                return True
        except Exception as e:
            logger.error(f"Scroll error: {e}")
        return False
    
    def wait_for_element(self, selector: str, by: str = 'css', timeout: int = 10) -> bool:
        """Wait for element to appear"""
        try:
            self.find_element(selector, by, wait=timeout)
            return True
        except Exception as e:
            logger.error(f"Wait error: {e}")
            return False
    
    def execute_script(self, script: str) -> Any:
        """Execute JavaScript"""
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            logger.error(f"Script execution error: {e}")
            return None
    
    def get_page_source(self) -> str:
        """Get page HTML"""
        return self.driver.page_source
    
    def screenshot(self, path: str = 'screenshot.png'):
        """Take screenshot"""
        try:
            self.driver.save_screenshot(path)
            logger.info(f"Screenshot saved: {path}")
            return path
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None
    
    def close(self):
        """Close browser"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Close error: {e}")

if __name__ == '__main__':
    logger.info("Browser automation module ready")
