import time
import gc
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .business_extractor import BusinessExtractor
from .review_extractor import ReviewExtractor
from .excel_manager import ExcelManager

class GoogleMapsScraper:
    def __init__(self, logger):
        self.logger = logger
        self.driver = None
        self.business_extractor = None
        self.review_extractor = None
        self.excel_manager = ExcelManager()
        self.memory_cleanup_counter = 0
        self.total_businesses_processed = 0
        
    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.business_extractor = BusinessExtractor(self.driver, self.logger)
        self.review_extractor = ReviewExtractor(self.driver, self.logger)
    
    def _navigate_to_search(self, search_term):
        search_url = f"https://www.google.com/maps/search/{search_term}/?hl=en"
        self.driver.get(search_url)
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'))
        )
        time.sleep(3)
    
    def _get_search_results_count(self):
        container_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'
        container = self.driver.find_element(By.XPATH, container_xpath)
        
        result_count = 0
        div_index = 3
        
        while div_index <= 100:
            try:
                result_xpath = f'{container_xpath}/div[{div_index}]'
                self.driver.find_element(By.XPATH, result_xpath)
                result_count += 1
                div_index += 2
            except NoSuchElementException:
                break
        
        return result_count
    
    def _click_search_result(self, result_index):
        div_index = 3 + (result_index * 2)
        result_xpath = f'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[{div_index}]'
        
        for attempt in range(3):
            try:
                result_element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, result_xpath))
                )
                result_element.click()
                
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]'))
                )
                time.sleep(2)
                return True
                
            except (TimeoutException, NoSuchElementException) as e:
                if attempt == 2:
                    self.logger.error(f"Failed to click search result {result_index + 1}")
                    return False
                time.sleep(2 ** attempt)
        
        return False
    
    def _scroll_results_navbar(self):
        try:
            container_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'
            container = self.driver.find_element(By.XPATH, container_xpath)
            
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(3)
            
            if "You've reached the end of the list." in self.driver.page_source:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to scroll results navbar: {str(e)}")
            return True
    
    def scrape_businesses(self, search_term):
        try:
            self._setup_driver()
            self._navigate_to_search(search_term)
            
            business_data_batch = []
            result_index = 0
            
            while True:
                if not self._click_search_result(result_index):
                    if self.memory_cleanup_counter == 3:
                        self.logger.info(f"Completed batch {result_index - 2}-{result_index}, scrolling results navbar")
                        
                        if not self._scroll_results_navbar():
                            break
                        
                        self.memory_cleanup_counter = 0
                        continue
                    else:
                        break
                
                self.total_businesses_processed += 1
                
                try:
                    business_info = self.business_extractor.extract_business_info()
                    if business_info:
                        self.logger.process(f"Processing business {self.total_businesses_processed}: {business_info.get('name', 'Unknown')}")
                        
                        business_data_batch.append(business_info)
                        
                        review_type = self.review_extractor.classify_review_type()
                        self.logger.classify(f"Review type detected: Type {review_type}")
                        
                        reviews_data = self.review_extractor.extract_all_reviews(review_type)
                        
                        if reviews_data:
                            self.logger.save(f"Saved {len(reviews_data)} reviews to Excel, cleared from memory")
                            self.excel_manager.save_reviews_to_excel(reviews_data, business_info.get('name', 'Unknown'))
                        
                        del reviews_data
                        gc.collect()
                        
                        self.memory_cleanup_counter += 1
                        
                        if len(business_data_batch) >= 5:
                            self.excel_manager.save_businesses_to_excel(business_data_batch)
                            business_data_batch.clear()
                        
                        if self.memory_cleanup_counter == 3:
                            self.logger.info(f"Completed batch {result_index - 2}-{result_index}, scrolling results navbar")
                            
                            if not self._scroll_results_navbar():
                                break
                            
                            self.memory_cleanup_counter = 0
                    
                except Exception as e:
                    self.logger.error(f"Failed to process business at index {result_index}: {str(e)}")
                
                result_index += 1
            
            if business_data_batch:
                self.excel_manager.save_businesses_to_excel(business_data_batch)
            
            self.logger.success(f"Scraping completed. Total businesses: {self.total_businesses_processed}")
            
        except Exception as e:
            self.logger.error(f"Critical error in scrape_businesses: {str(e)}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
            gc.collect()