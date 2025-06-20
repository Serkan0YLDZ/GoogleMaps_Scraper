from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

class BrowserManager:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def initialize_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 10)
            return True
            
        except WebDriverException as e:
            print("[ERROR] Failed to initialize browser: {}".format(str(e)))
            return False
    
    def navigate_to_url(self, url):
        try:
            self.driver.get(url)
            time.sleep(3)
            return True
        except WebDriverException as e:
            print("[ERROR] Failed to navigate to URL: {}".format(str(e)))
            return False
    
    def wait_for_element(self, xpath, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
        except TimeoutException:
            return None
    
    def click_element(self, xpath, timeout=10):
        try:
            element = self.wait_for_element(xpath, timeout)
            if element:
                self.driver.execute_script("arguments[0].click();", element)
                time.sleep(1)
                return True
            return False
        except Exception as e:
            print("[ERROR] Failed to click element {}: {}".format(xpath, str(e)))
            return False
    
    def get_element_text(self, xpath, timeout=5):
        try:
            element = self.wait_for_element(xpath, timeout)
            if element:
                return element.text.strip()
            return ""
        except Exception:
            return ""
    
    def get_element_attribute(self, xpath, attribute, timeout=5):
        try:
            element = self.wait_for_element(xpath, timeout)
            if element:
                return element.get_attribute(attribute)
            return ""
        except Exception:
            return ""
    
    def find_elements(self, xpath):
        try:
            return self.driver.find_elements(By.XPATH, xpath)
        except Exception:
            return []
    
    def scroll_element(self, xpath, direction="down", pixels=300):
        try:
            element = self.wait_for_element(xpath, 5)
            if element:
                try:                    
                    if direction == "down":
                        self.driver.execute_script(f"arguments[0].scrollTop += {pixels};", element)
                    else:
                        self.driver.execute_script(f"arguments[0].scrollTop -= {pixels};", element)
                    
                    time.sleep(0.5)  
                    
                    return True
                except Exception as js_error:
                    print("[ERROR] JavaScript execution failed: {}".format(str(js_error)))
                    return False
            else:
                print("[ERROR] Element not found for scrolling: {}".format(xpath))
                return False
        except Exception as e:
            print("[ERROR] Failed to scroll element: {}".format(str(e)))
            return False
    
    def close_browser(self):
        try:
            if self.driver:
                print("[INFO] Closing browser...")
                self.driver.quit()
                print("[INFO] Browser closed successfully")
        except Exception as e:
            print("[ERROR] Error closing browser: {}".format(str(e)))
    
    def is_element_present(self, xpath, timeout=2):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return True
        except TimeoutException:
            return False
    
    def get_current_url(self):
        try:
            return self.driver.current_url
        except Exception:
            return ""
