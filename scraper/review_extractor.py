import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from typing import List, Dict, Optional, Any
from utils.logger import Logger

class ReviewTypeDetector:
    # Class-level cache for review type
    _cached_review_type = None
    _cache_initialized = False
    
    def __init__(self, driver: WebDriver, logger: Logger):
        self.driver = driver
        self.logger = logger
        self.confidence_threshold = 4
        self.low_confidence_threshold = 2
    
    def detect_review_type(self) -> int:
        # Use cached result if available
        if ReviewTypeDetector._cache_initialized and ReviewTypeDetector._cached_review_type is not None:
            self.logger.classify(f"Using cached review type: {ReviewTypeDetector._cached_review_type}")
            return ReviewTypeDetector._cached_review_type
        
        try:
            # Fast exit strategy - check high confidence elements first
            if self._quick_type2_check():
                ReviewTypeDetector._cached_review_type = 2
                ReviewTypeDetector._cache_initialized = True
                self.logger.classify("Type 2 detected (quick check)")
                return 2
            
            # Full detection only if quick check fails
            type2_score = self._calculate_type2_confidence()
            div3_exists = self._check_div3_existence()
            
            if type2_score >= self.confidence_threshold:
                ReviewTypeDetector._cached_review_type = 2
                ReviewTypeDetector._cache_initialized = True
                self.logger.classify(f"Type 2 detected with high confidence: {type2_score}")
                return 2
            
            if not div3_exists and type2_score >= self.low_confidence_threshold:
                ReviewTypeDetector._cached_review_type = 2
                ReviewTypeDetector._cache_initialized = True
                self.logger.classify(f"Type 2 detected (no div[3], confidence: {type2_score})")
                return 2
            
            if not div3_exists and type2_score < self.low_confidence_threshold:
                ReviewTypeDetector._cached_review_type = 1
                ReviewTypeDetector._cache_initialized = True
                self.logger.error("Critical: Neither Type 1 nor Type 2 viable")
                return 1
            
            ReviewTypeDetector._cached_review_type = 1
            ReviewTypeDetector._cache_initialized = True
            self.logger.classify(f"Type 1 detected (Type 2 confidence too low: {type2_score})")
            return 1
            
        except Exception as e:
            ReviewTypeDetector._cached_review_type = 1
            ReviewTypeDetector._cache_initialized = True
            self.logger.error(f"Error detecting review type: {e}, defaulting to Type 1")
            return 1
    
    def _quick_type2_check(self) -> bool:
        """Fast check for Type 2 indicators"""
        try:
            # Check only the most reliable indicators first
            elements = self.driver.find_elements(By.CSS_SELECTOR, '.s35xed')
            if elements:
                return True
            
            elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="scheduling"]')
            if elements:
                return True
            
            return False
        except Exception:
            return False
    
    def _calculate_type2_confidence(self) -> int:
        score = 0
        
        # Removed text indicators (slowest operation)
        score += self._check_high_confidence_elements() * 3
        score += self._check_xpath_selectors() * 2
        
        return score
    
    def _check_high_confidence_elements(self) -> int:
        selectors = ['.s35xed', '.faY1Me', 'a[href*="scheduling/patient-lookup"]']
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return 1
            except Exception:
                continue
        return 0
    
    def _check_text_indicators(self) -> int:
        indicators = ["Browse and book now", "See prices and availability", "Book online"]
        
        try:
            page_source = self.driver.page_source
            if any(indicator in page_source for indicator in indicators):
                return 1
        except Exception:
            pass
        return 0
    
    def _check_xpath_selectors(self) -> int:
        # Reduced to most effective XPaths only
        xpaths = [
            "//a[contains(@href, 'scheduling')]",
            "//span[text()='Book online']"
        ]
        
        for xpath in xpaths:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements:
                    return 1
            except Exception:
                continue
        return 0
    
    def _check_div3_existence(self) -> bool:
        try:
            self.driver.find_element(By.XPATH, 
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]')
            return True
        except NoSuchElementException:
            return False

class ReviewScrollManager:
    # Class-level cache for successful scroll container
    _cached_scroll_xpath = None
    _cached_review_type = None
    
    def __init__(self, driver: WebDriver, logger: Logger):
        self.driver = driver
        self.logger = logger
        self.max_no_change_count = 3
    
    def get_scroll_container(self, review_type: int) -> Optional[Any]:
        # Use cached container if available and same review type
        if (ReviewScrollManager._cached_scroll_xpath and 
            ReviewScrollManager._cached_review_type == review_type):
            try:
                container = self.driver.find_element(By.XPATH, ReviewScrollManager._cached_scroll_xpath)
                self.logger.extract(f"Using cached scroll container: {ReviewScrollManager._cached_scroll_xpath}")
                return container
            except NoSuchElementException:
                # Cache invalid, clear it
                ReviewScrollManager._cached_scroll_xpath = None
                ReviewScrollManager._cached_review_type = None
        
        scroll_areas = self._get_scroll_area_candidates(review_type)
        
        for xpath in scroll_areas:
            try:
                container = self.driver.find_element(By.XPATH, xpath)
                # Cache successful xpath
                ReviewScrollManager._cached_scroll_xpath = xpath
                ReviewScrollManager._cached_review_type = review_type
                self.logger.extract(f"Found and cached scroll container: {xpath}")
                return container
            except NoSuchElementException:
                continue
        
        self.logger.error("No scroll container found")
        return None
    
    def _get_scroll_area_candidates(self, review_type: int) -> List[str]:
        if review_type == 2:
            return [
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[5]',
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]',
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[4]',
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div'
            ]
        else:
            return [
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]',
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div'
            ]
    
    def scroll_to_bottom(self, review_type: int) -> bool:
        container = self.get_scroll_container(review_type)
        if not container:
            return False
        
        try:
            return self._perform_scroll(container)
        except Exception as e:
            self.logger.error(f"Scroll operation failed: {e}")
            return False
    
    def _perform_scroll(self, container: Any) -> bool:
        last_height = self.driver.execute_script("return arguments[0].scrollHeight", container)
        no_change_count = 0
        
        self.logger.extract("Starting scroll operation")
        
        while True:
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)            
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", container)
            
            if new_height == last_height:
                no_change_count += 1
                if no_change_count >= self.max_no_change_count:
                    self.logger.extract("No new content loaded, scroll complete")
                    break
                time.sleep(2)
            else:
                no_change_count = 0
                last_height = new_height
        
        return True


class ReviewParser:
    def __init__(self, driver: WebDriver, logger: Logger):
        self.driver = driver
        self.logger = logger
        self.review_selectors = [
            '.jftiEf.fontBodyMedium',
            '.jftiEf',
            '[data-review-id]'
        ]
    
    def extract_reviews(self) -> List[Dict[str, Any]]:
        try:
            review_elements = self._find_review_elements()
            if not review_elements:
                return []
            
            reviews = []
            successful_count = 0
            
            for element in review_elements:
                try:
                    review_data = self._parse_single_review(element)
                    if review_data and review_data.get('reviewer_name'):
                        reviews.append(review_data)
                        successful_count += 1
                except Exception:
                    continue
            
            self.logger.extract(f"Successfully parsed {successful_count}/{len(review_elements)} reviews")
            return reviews
            
        except Exception as e:
            self.logger.error(f"Failed to extract reviews: {e}")
            return []
    
    def _find_review_elements(self) -> List[Any]:
        for selector in self.review_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    self.logger.extract(f"Found {len(elements)} elements with selector: {selector}")
                    return elements
            except Exception:
                continue
        
        self.logger.extract("No review elements found")
        return []
    
    def _parse_single_review(self, element: Any) -> Optional[Dict[str, Any]]:
        try:
            review_data = {}
            
            review_data['reviewer_name'] = self._safe_extract_text(element, '.d4r55', "Anonymous")
            review_data['review_text'] = self._safe_extract_text(element, '.wiI7pd', "")
            review_data['review_date'] = self._safe_extract_text(element, '.rsqaWe', "")
            review_data['rating'] = self._extract_rating(element)
            review_data['media_links'] = self._extract_media_links(element)
            review_data['review_id'] = self._extract_review_id(element)
            
            return review_data
            
        except Exception:
            return None
    
    def _safe_extract_text(self, parent_element: Any, selector: str, default: str) -> str:
        try:
            element = parent_element.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip() if element.text else default
        except NoSuchElementException:
            return default
    
    def _extract_rating(self, element: Any) -> str:
        try:
            rating_element = element.find_element(By.CSS_SELECTOR, '[aria-label*="stars"]')
            return rating_element.get_attribute('aria-label') or "No rating"
        except NoSuchElementException:
            return "No rating"
    
    def _extract_media_links(self, element: Any) -> str:
        try:
            photo_urls = []
            
            photo_containers = element.find_elements(By.CSS_SELECTOR, '.KtCyie')
            
            for container in photo_containers:
                buttons = container.find_elements(By.CSS_SELECTOR, 'button.Tya61d')
                for button in buttons:
                    style_attr = button.get_attribute('style')
                    if style_attr and 'background-image: url(' in style_attr:
                        start = style_attr.find('url("') + 5
                        end = style_attr.find('")', start)
                        if start > 4 and end > start:
                            photo_url = style_attr[start:end]
                            if 'googleusercontent.com' in photo_url:
                                photo_urls.append(photo_url)
            
            if not photo_urls:
                media_elements = element.find_elements(By.CSS_SELECTOR, 'img[src*="googleusercontent"]')
                links = [img.get_attribute('src') for img in media_elements if img.get_attribute('src')]
                photo_urls.extend(links)
            
            return ', '.join(photo_urls)
        except Exception:
            return ""
    
    def _extract_review_id(self, element: Any) -> str:
        try:
            return element.get_attribute('data-review-id') or ""
        except Exception:
            return ""

class ReviewTabNavigator:
    def __init__(self, driver: WebDriver, logger: Logger):
        self.driver = driver
        self.logger = logger
        self.wait_timeout = 3
        self.reviews_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[3]/div/div/button[2]'
    
    def navigate_to_reviews(self) -> bool:
        try:
            # Direct XPath approach - much faster
            reviews_button = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.element_to_be_clickable((By.XPATH, self.reviews_xpath))
            )
            reviews_button.click()
            self.logger.extract("Successfully navigated to reviews tab (direct XPath)")
            return True
            
        except TimeoutException:
            # Fallback to original method if direct XPath fails
            self.logger.warning("Direct XPath failed, trying fallback method")
            return self._fallback_navigate_to_reviews()
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to reviews tab: {e}")
            return False
    
    def _fallback_navigate_to_reviews(self) -> bool:
        try:
            review_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button.hh2c6[role="tab"]')
            
            for button in review_buttons:
                aria_label = button.get_attribute('aria-label')
                if aria_label and 'Reviews for' in aria_label:
                    button.click()
                    time.sleep(1)  # Reduced from 2 seconds
                    self.logger.extract("Successfully navigated to reviews tab (fallback)")
                    return True
            
            self.logger.warning("Reviews tab not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Fallback navigation failed: {e}")
            return False


class ReviewExtractor:
    def __init__(self, driver: WebDriver, logger: Logger):
        self.driver = driver
        self.logger = logger
        self.type_detector = ReviewTypeDetector(driver, logger)
        self.scroll_manager = ReviewScrollManager(driver, logger)
        self.parser = ReviewParser(driver, logger)
        self.navigator = ReviewTabNavigator(driver, logger)
    
    def classify_review_type(self) -> int:
        return self.type_detector.detect_review_type()
    
    def extract_all_reviews(self, review_type: int) -> List[Dict[str, Any]]:
        try:
            self.logger.extract("Starting review extraction process")
            
            if not self.navigator.navigate_to_reviews():
                self.logger.error("Could not navigate to reviews tab")
                return []
            
            scroll_success = self.scroll_manager.scroll_to_bottom(review_type)
            
            if not scroll_success and review_type == 2:
                self.logger.extract("Type 2 scroll failed, trying Type 1")
                scroll_success = self.scroll_manager.scroll_to_bottom(1)
            
            if not scroll_success:
                self.logger.warning("Scroll failed, extracting visible reviews")
            
            reviews_data = self.parser.extract_reviews()
            
            if not reviews_data and review_type == 2:
                self.logger.extract("No reviews with Type 2, trying Type 1 extraction")
                reviews_data = self.parser.extract_reviews()
            
            self.logger.extract(f"Extracted {len(reviews_data)} reviews")
            return reviews_data
            
        except Exception as e:
            self.logger.error(f"Critical error in review extraction: {e}")
            
            if review_type == 2:
                self.logger.extract("Attempting Type 1 recovery")
                try:
                    return self.extract_all_reviews(1)
                except Exception as fallback_error:
                    self.logger.error(f"Type 1 fallback failed: {fallback_error}")
            
            return []