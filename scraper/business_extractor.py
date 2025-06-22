import time
import gc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class BusinessExtractor:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger
    
    def extract_business_info(self):
        try:
            business_info = {}
            
            business_info['name'] = self._extract_business_name()
            business_info['rating'] = self._extract_rating()
            business_info['address'] = self._extract_address()
            business_info['phone'] = self._extract_phone()
            
            return business_info
            
        except Exception as e:
            self.logger.error(f"Failed to extract business info: {str(e)}")
            return None
    
    def _extract_business_name(self):
        try:
            name_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1'
            name_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, name_xpath))
            )
            return name_element.text.strip()
        except (TimeoutException, NoSuchElementException):
            return "Unknown"
    
    def _extract_rating(self):
        try:
            rating_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]'
            rating_element = self.driver.find_element(By.XPATH, rating_xpath)
            return rating_element.text.strip()
        except NoSuchElementException:
            return "No rating"
    
    def _extract_address(self):
        try:
            address_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button.CsEnBe[data-item-id="address"]')
            for button in address_buttons:
                aria_label = button.get_attribute('aria-label')
                if aria_label and 'Address:' in aria_label:
                    return aria_label.replace('Address:', '').strip()
            return "No address"
        except Exception:
            return "No address"
    
    def _extract_phone(self):
        try:
            phone_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button.CsEnBe[data-item-id*="phone"]')
            for button in phone_buttons:
                aria_label = button.get_attribute('aria-label')
                if aria_label and 'Phone:' in aria_label:
                    return aria_label.replace('Phone:', '').strip()
            return "No phone"
        except Exception:
            return "No phone"