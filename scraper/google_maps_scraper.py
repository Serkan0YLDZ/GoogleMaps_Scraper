import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Optional, List, Dict, Any
from .business_extractor import BusinessExtractor
from .review_extractor import ReviewExtractor
from .excel_manager import ExcelManager
from utils.logger import Logger

class WebDriverManager:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.driver = None
    
    def create_driver(self) -> WebDriver:
        try:
            chrome_options = self._get_chrome_options()
            self.driver = webdriver.Chrome(options=chrome_options)
            self._configure_driver()
            self.logger.info("WebDriver initialized successfully")
            return self.driver
        except Exception as e:
            error_msg = f"Failed to initialize WebDriver: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _get_chrome_options(self) -> Options:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        return chrome_options
    
    def _configure_driver(self) -> None:
        if not self.driver:
            raise RuntimeError("Driver not initialized")
        
        self.driver.maximize_window()
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.implicitly_wait(2)  # Reduced from 5 to 2 seconds
    
    def quit_driver(self) -> None:
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None

class SearchNavigator:
    def __init__(self, driver: WebDriver, logger: Logger):
        self.driver = driver
        self.logger = logger
        self.timeout = 10
    
    def navigate_to_search(self, search_term: str) -> None:
        if not search_term or not search_term.strip():
            raise ValueError("Search term cannot be empty")
        
        try:
            search_url = f"https://www.google.com/maps/search/{search_term.strip()}/?hl=en"
            self.logger.info(f"Navigating to: {search_url}")
            
            self.driver.get(search_url)
            self._wait_for_search_results()
            self.logger.info("Successfully navigated to search results")
            
        except Exception as e:
            error_msg = f"Failed to navigate to search results: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _wait_for_search_results(self) -> None:
        results_container = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'
        
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.XPATH, results_container))
            )
            time.sleep(0.5)
        except TimeoutException as e:
            raise RuntimeError("Search results container not found") from e


class ResultsManager:
    def __init__(self, driver: WebDriver, logger: Logger):
        self.driver = driver
        self.logger = logger
        self.results_container_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'
        
    def get_results_count(self) -> int:
        try:
            container = self.driver.find_element(By.XPATH, self.results_container_xpath)
            result_count = 0
            div_index = 3
            
            while div_index <= 100:
                try:
                    result_xpath = f'{self.results_container_xpath}/div[{div_index}]'
                    self.driver.find_element(By.XPATH, result_xpath)
                    result_count += 1
                    div_index += 2
                except NoSuchElementException:
                    break
            
            self.logger.info(f"Found {result_count} search results")
            return result_count
            
        except Exception as e:
            self.logger.error(f"Error counting results: {e}")
            return 0
    
    def click_search_result(self, result_index: int) -> bool:
        div_index = 3 + (result_index * 2)
        result_xpath = f'{self.results_container_xpath}/div[{div_index}]'
        
        for attempt in range(3):
            try:
                result_element = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, result_xpath))
                )
                result_element.click()
                
                self._wait_for_business_details()
                self.logger.extract(f"Successfully clicked result {result_index + 1}")
                return True
                
            except (TimeoutException, NoSuchElementException) as e:
                if attempt == 2:
                    self.logger.error(f"Failed to click result {result_index + 1} after 3 attempts")
                    return False
                time.sleep(2 ** attempt)
        
        return False
    
    def _wait_for_business_details(self) -> None:
        business_details_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]'
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, business_details_xpath))
        )
        time.sleep(1)  # Reduced from 2 to 1 second
    
    def scroll_results_navbar(self) -> bool:
        try:
            container = self.driver.find_element(By.XPATH, self.results_container_xpath)
            
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            
            if "You've reached the end of the list." in self.driver.page_source:
                self.logger.info("Reached end of search results - stopping scroll but continuing data extraction")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to scroll results navbar: {e}")
            return False


class GoogleMapsScraper:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.driver_manager = WebDriverManager(logger)
        self.navigator = None
        self.results_manager = None
        self.business_extractor = None
        self.review_extractor = None
        self.excel_manager = ExcelManager()
        self.batch_size = 5
        self.total_businesses_processed = 0
        
    def _initialize_components(self) -> None:
        try:
            driver = self.driver_manager.create_driver()
            self.navigator = SearchNavigator(driver, self.logger)
            self.results_manager = ResultsManager(driver, self.logger)
            self.business_extractor = BusinessExtractor(driver, self.logger)
            self.review_extractor = ReviewExtractor(driver, self.logger)
            self.logger.info("All components initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize components: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def scrape_businesses(self, search_term: str) -> None:
        if not search_term or not search_term.strip():
            raise ValueError("Search term cannot be empty")
        
        try:
            self._initialize_components()
            self.navigator.navigate_to_search(search_term)
            
            business_data_batch = []
            result_index = 0
            
            self.logger.info(f"Starting business scraping for: {search_term}")
            
            while True:
                if not self.results_manager.click_search_result(result_index):
                    scroll_success = self.results_manager.scroll_results_navbar()
                    if not scroll_success:
                        break
                    continue
                
                try:
                    business_info = self._process_single_business(result_index)
                    if business_info:
                        business_name = business_info.get('name', 'Unknown')
                        print(f"[SCRAPER] Adding business '{business_name}' to batch")
                        business_data_batch.append(business_info)
                        
                        if len(business_data_batch) >= self.batch_size:
                            self._save_business_batch(business_data_batch)
                            business_data_batch.clear()
                
                except Exception as e:
                    self.logger.error(f"Error processing business at index {result_index}: {e}")
                
                result_index += 1
            
            if business_data_batch:
                self._save_business_batch(business_data_batch)
            
            self.logger.success(f"Scraping completed. Total businesses processed: {self.total_businesses_processed}")
            
        except Exception as e:
            error_msg = f"Critical error in scrape_businesses: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        finally:
            self.cleanup()
    
    def _process_single_business(self, result_index: int) -> Optional[Dict[str, Any]]:
        try:
            self.total_businesses_processed += 1
            
            business_info = self.business_extractor.extract_business_info()
            if not business_info:
                self.logger.warning(f"Could not extract business info for result {result_index + 1}")
                return None
            
            business_name = business_info.get('name', 'Unknown')
            self.logger.process(f"Processing business {self.total_businesses_processed}: {business_name}")
            
            review_type = self.review_extractor.classify_review_type()
            self.logger.classify(f"Review type detected: Type {review_type}")
            
            reviews_data = self.review_extractor.extract_all_reviews(review_type)
            
            if reviews_data:
                self.logger.save(f"Extracted {len(reviews_data)} reviews for {business_name}")
                self.excel_manager.save_reviews_to_excel(reviews_data, business_name)
            else:
                self.logger.warning(f"No reviews found for {business_name}")
            
            return business_info
            
        except Exception as e:
            self.logger.error(f"Error processing business: {e}")
            return None
    
    def _save_business_batch(self, business_data_batch: List[Dict[str, Any]]) -> None:
        try:
            business_names = [b.get('name', 'Unknown') for b in business_data_batch]
            print(f"[SCRAPER] Saving batch with businesses: {business_names}")
            self.excel_manager.save_businesses_to_excel(business_data_batch)
            self.logger.save(f"Saved batch of {len(business_data_batch)} businesses to Excel")
        except Exception as e:
            self.logger.error(f"Failed to save business batch: {e}")
    
    def cleanup(self) -> None:
        try:
            self.driver_manager.quit_driver()
            self.logger.info("Cleanup completed successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")