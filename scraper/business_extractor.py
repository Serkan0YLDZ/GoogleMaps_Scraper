import time
import uuid
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Dict, Optional, List, Tuple
from utils.logger import Logger

class BusinessExtractor:
    def __init__(self, driver: WebDriver, logger: Logger):
        self.driver = driver
        self.logger = logger
        self.timeout = 3  # Reduced from 1 to 3 for better reliability but still faster than default
        self._validate_dependencies()
    
    def _validate_dependencies(self) -> None:
        if not self.driver:
            raise ValueError("WebDriver instance is required")
        if not self.logger:
            raise ValueError("Logger instance is required")
    
    def extract_business_info(self) -> Optional[Dict[str, str]]:
        try:
            self.logger.extract("Starting business information extraction")
            
            business_info = {
                'id': str(uuid.uuid4()),
                'extraction_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'name': self._extract_business_name(),
                'rating': self._extract_rating(),
                'address': self._extract_address(),
                'phone': self._extract_phone(),
                'website': self._extract_website(),
                'hours': self._extract_hours(),
                'category': self._extract_category()
            }
            
            if business_info['name'] == "Unknown":
                self.logger.warning("Could not extract business name - data may be incomplete")
            
            self.logger.extract(f"Successfully extracted info for: {business_info['name']}")
            return business_info
            
        except WebDriverException as e:
            self.logger.error(f"WebDriver error during business extraction: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during business extraction: {e}")
            return None
    
    def _safe_find_element(self, locator_strategies: List[Tuple[str, str]], timeout: Optional[int] = None) -> Optional[str]:
        timeout = timeout or self.timeout
        
        for strategy, locator in locator_strategies:
            try:
                if strategy == "wait_xpath":
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, locator))
                    )
                    return element.text.strip() if element.text else None
                elif strategy == "xpath":
                    element = self.driver.find_element(By.XPATH, locator)
                    return element.text.strip() if element.text else None
                elif strategy == "css":
                    element = self.driver.find_element(By.CSS_SELECTOR, locator)
                    return element.text.strip() if element.text else None
                elif strategy == "css_attribute":
                    elements = self.driver.find_elements(By.CSS_SELECTOR, locator)
                    for element in elements:
                        attr_value = element.get_attribute('aria-label')
                        if attr_value:
                            return attr_value.strip()
            except (TimeoutException, NoSuchElementException):
                continue
            except Exception as e:
                self.logger.debug(f"Error with {strategy} strategy: {e}")
                continue
        
        return None
    
    def _extract_business_name(self) -> str:
        name_strategies = [
            ("wait_xpath", '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1'),
            ("xpath", "//h1[contains(@class, 'DUwDvf')]"),
            ("css", "h1.DUwDvf"),
            ("xpath", "//h1[@data-attrid='title']"),
        ]
        
        name = self._safe_find_element(name_strategies)
        return name if name else "Unknown"
    
    def _extract_rating(self) -> str:
        rating_strategies = [
            ("xpath", '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]'),
            ("css", "span.ceNzKf[aria-hidden='true']"),
            ("xpath", "//span[@class='ceNzKf' and @aria-hidden='true']"),
            ("css", ".ceNzKf"),
        ]
        
        rating = self._safe_find_element(rating_strategies)
        return rating if rating else "No rating"
    
    def _extract_address(self) -> str:
        try:
            address_elements = self.driver.find_elements(By.CSS_SELECTOR, 'button.CsEnBe[data-item-id="address"]')
            for element in address_elements:
                aria_label = element.get_attribute('aria-label')
                if aria_label and 'Address:' in aria_label:
                    address = aria_label.replace('Address:', '').strip()
                    return address if address else "No address"
            
            address_strategies = [
                ("xpath", "//button[@data-item-id='address']"),
                ("css", "[data-value='Address']"),
                ("xpath", "//span[contains(text(), 'Address')]/following-sibling::span"),
            ]
            
            address = self._safe_find_element(address_strategies)
            return address if address else "No address"
            
        except Exception as e:
            self.logger.debug(f"Error extracting address: {e}")
            return "No address"
    
    def _extract_phone(self) -> str:
        try:
            phone_elements = self.driver.find_elements(By.CSS_SELECTOR, 'button.CsEnBe[data-item-id*="phone"]')
            for element in phone_elements:
                aria_label = element.get_attribute('aria-label')
                if aria_label and 'Phone:' in aria_label:
                    phone = aria_label.replace('Phone:', '').strip()
                    return phone if phone else "No phone"
            
            phone_strategies = [
                ("xpath", "//button[contains(@data-item-id, 'phone')]"),
                ("css", "[data-value='Phone']"),
                ("xpath", "//span[contains(text(), 'Phone')]/following-sibling::span"),
            ]
            
            phone = self._safe_find_element(phone_strategies)
            return phone if phone else "No phone"
            
        except Exception as e:
            self.logger.debug(f"Error extracting phone: {e}")
            return "No phone"
    
    def _extract_website(self) -> str:
        try:
            website_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
            for element in website_elements:
                href = element.get_attribute('href')
                if href and href.startswith('http'):
                    return href
            
            website_strategies = [
                ("xpath", "//a[@data-item-id='authority']"),
                ("css", "a[data-value='Website']"),
                ("xpath", "//a[contains(@href, 'http')]"),
            ]
            
            for strategy, locator in website_strategies:
                try:
                    if strategy == "xpath":
                        element = self.driver.find_element(By.XPATH, locator)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, locator)
                    
                    href = element.get_attribute('href')
                    if href and href.startswith('http'):
                        return href
                except (NoSuchElementException, Exception):
                    continue
            
            return "No website"
            
        except Exception as e:
            self.logger.debug(f"Error extracting website: {e}")
            return "No website"
    
    def _extract_hours(self) -> str:
        try:
            hours_button = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-item-id="oh"]')
            if hours_button:
                aria_label = hours_button[0].get_attribute('aria-label')
                if aria_label:
                    return aria_label.strip()
            
            hours_strategies = [
                ("xpath", "//button[@data-item-id='oh']"),
                ("css", ".t39EBf"),
                ("xpath", "//div[contains(@class, 'OqCZI')]"),
            ]
            
            hours = self._safe_find_element(hours_strategies)
            return hours if hours else "No hours"
            
        except Exception as e:
            self.logger.debug(f"Error extracting hours: {e}")
            return "No hours"
    
    def _extract_category(self) -> str:
        try:
            category_strategies = [
                ("css", "button.DkEaL"),
                ("xpath", "//button[@class='DkEaL']"),
                ("css", ".DkEaL"),
                ("xpath", "//span[contains(@class, 'YhemCb')]"),
            ]
            
            category = self._safe_find_element(category_strategies)
            return category if category else "No category"
            
        except Exception as e:
            self.logger.debug(f"Error extracting category: {e}")
            return "No category"