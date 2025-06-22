import time
import gc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ReviewExtractor:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger
        self.scroll_timeout = 30
    
    def classify_review_type(self):
        try:
            # Multi-Layer Detection for Type 2 (Try Type 2 detection FIRST)
            type2_confidence_score = 0
            detection_methods = []
            div3_exists = False
            
            # Check if div[3] exists (for Type 1 validation later)
            div3_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]'
            try:
                div3_element = self.driver.find_element(By.XPATH, div3_xpath)
                div3_exists = True
            except NoSuchElementException:
                self.logger.extract("div[3] not found - will check for Type 2 before failing")
            
            # Multi-Layer Detection for Type 2 (Conservative Approach)
            
            # Layer 1: URL Pattern Detection (Weight: 3)
            try:
                current_url = self.driver.current_url
                if 'scheduling' in current_url or 'book' in current_url:
                    type2_confidence_score += 3
                    detection_methods.append("URL pattern")
            except Exception:
                pass
            
            # Layer 2: High-Confidence Element Detection (Weight: 3)
            type2_high_confidence_selectors = [
                '.s35xed',  # Book online container
                '.faY1Me',  # Book content container
                'a[href*="scheduling/patient-lookup"]',  # CVS booking link
            ]
            
            for selector in type2_high_confidence_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 0:
                        type2_confidence_score += 3
                        detection_methods.append(f"Element: {selector}")
                        break  # Only count once for high-confidence
                except Exception:
                    continue
            
            # Layer 3: Text-based Detection (Weight: 2)
            type2_text_indicators = [
                "Browse and book now",
                "See prices and availability",
                "Book online"
            ]
            
            try:
                page_source = self.driver.page_source
                for indicator in type2_text_indicators:
                    if indicator in page_source:
                        type2_confidence_score += 2
                        detection_methods.append(f"Text: {indicator}")
                        break  # Only count once for text detection
            except Exception:
                pass
            
            # Layer 4: XPath-based Detection (Weight: 2)
            type2_xpath_selectors = [
                "//span[text()='Book online']",
                "//span[text()='Browse and book now']",
                "//a[contains(@href, 'scheduling')]",
                "//a[contains(@href, 'book')]"
            ]
            
            for xpath in type2_xpath_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    if elements and len(elements) > 0:
                        type2_confidence_score += 2
                        detection_methods.append(f"XPath: {xpath}")
                        break  # Only count once for XPath detection
                except Exception:
                    continue
            
            # Layer 5: div[5] Analysis (Weight: 1, only if div[5] exists)
            try:
                div5_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[5]'
                div5_element = self.driver.find_element(By.XPATH, div5_xpath)
                div5_text = div5_element.text.lower()
                
                booking_keywords = ['book', 'browse', 'availability', 'scheduling', 'reserve']
                if any(keyword in div5_text for keyword in booking_keywords):
                    type2_confidence_score += 1
                    detection_methods.append("div[5] analysis")
            except NoSuchElementException:
                # div[5] doesn't exist - this is normal for Type 1
                pass
            except Exception:
                pass
            
            # Decision Logic: Require high confidence for Type 2
            # Minimum score of 4 needed to classify as Type 2
            if type2_confidence_score >= 4:
                detection_info = ", ".join(detection_methods)
                self.logger.classify(f"Type 2 detected (confidence: {type2_confidence_score}) via: {detection_info}")
                return 2
            else:
                # If Type 2 confidence is low, check if Type 1 is viable
                if not div3_exists:
                    if type2_confidence_score >= 2:  # Lower threshold when div[3] doesn't exist
                        detection_info = ", ".join(detection_methods)
                        self.logger.classify(f"Type 2 detected (div[3] missing, confidence: {type2_confidence_score}) via: {detection_info}")
                        return 2
                    else:
                        self.logger.error("Critical: Neither Type 1 (no div[3]) nor Type 2 (low confidence) viable")
                        return 1  # Default fallback
                else:
                    if type2_confidence_score > 0:
                        detection_info = ", ".join(detection_methods)
                        self.logger.classify(f"Type 1 detected (Type 2 confidence too low: {type2_confidence_score}) methods: {detection_info}")
                    else:
                        self.logger.classify("Type 1 detected (no booking features found)")
                    return 1
            
        except Exception as e:
            self.logger.error(f"Failed to classify review type: {str(e)} - Defaulting to Type 1")
            return 1
    
    def _navigate_to_reviews_tab(self):
        try:
            reviews_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button.hh2c6[role="tab"]')
            
            for button in reviews_buttons:
                aria_label = button.get_attribute('aria-label')
                if aria_label and 'Reviews for' in aria_label:
                    button.click()
                    time.sleep(3)
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to reviews tab: {str(e)}")
            return False
    
    def _get_scroll_area_xpath(self, review_type):
        if review_type == 2:
            return '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[5]'
        else:
            return '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]'
    
    def _scroll_to_bottom(self, review_type):
        try:
            scroll_xpath = self._get_scroll_area_xpath(review_type)
            
            # SAFETY CHECK: Ensure scroll container exists
            try:
                scroll_container = self.driver.find_element(By.XPATH, scroll_xpath)
                self.logger.extract(f"Type {review_type} scroll container found")
            except NoSuchElementException:
                # If Type 2 scroll area doesn't exist, fallback to Type 1
                if review_type == 2:
                    self.logger.extract("Type 2 scroll area (div[5]) not found, falling back to Type 1")
                    scroll_xpath = self._get_scroll_area_xpath(1)
                    try:
                        scroll_container = self.driver.find_element(By.XPATH, scroll_xpath)
                        self.logger.extract("Type 1 fallback scroll container found")
                    except NoSuchElementException:
                        # Try alternative scroll areas for Type 2
                        alternative_scroll_areas = [
                            '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[4]',  # Alternative div[4]
                            '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div',  # Parent container
                        ]
                        
                        for alt_xpath in alternative_scroll_areas:
                            try:
                                scroll_container = self.driver.find_element(By.XPATH, alt_xpath)
                                self.logger.extract(f"Alternative scroll container found: {alt_xpath}")
                                break
                            except NoSuchElementException:
                                continue
                        else:
                            self.logger.error("Critical: No scroll container found")
                            return False
                else:
                    self.logger.error("Type 1 scroll container not found")
                    return False
            
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_container)
            start_time = time.time()
            no_change_count = 0
            
            self.logger.extract(f"Starting scroll in Type {review_type} area")
            
            while True:
                # Scroll to bottom
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
                time.sleep(2)
                
                # Check for new content
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_container)
                
                if new_height == last_height:
                    no_change_count += 1
                    # Give it 2 more chances before stopping
                    if no_change_count >= 3:
                        self.logger.extract("No new content loaded, scroll complete")
                        break
                    time.sleep(2)  # Wait a bit more for slow loading
                else:
                    no_change_count = 0  # Reset counter if new content found
                    last_height = new_height
                
                # Timeout protection
                if time.time() - start_time > self.scroll_timeout:
                    self.logger.extract("Scroll timeout reached, stopping")
                    break
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to scroll reviews: {str(e)}")
            return False
    
    def _extract_review_elements(self, review_type):
        try:
            reviews = []
            
            # Try multiple selectors for maximum compatibility
            review_selectors = [
                '.jftiEf.fontBodyMedium',  # Primary selector
                '.jftiEf',  # Fallback selector
                '[data-review-id]'  # Alternative selector based on review ID
            ]
            
            review_elements = []
            for selector in review_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        review_elements = elements
                        self.logger.extract(f"Found {len(elements)} elements with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not review_elements:
                self.logger.extract("No review elements found with any selector")
                return []
            
            # Parse each review element
            successful_extractions = 0
            for i, element in enumerate(review_elements):
                try:
                    review_data = self._parse_review_element(element)
                    if review_data and review_data.get('reviewer_name'):  # Ensure we have meaningful data
                        reviews.append(review_data)
                        successful_extractions += 1
                except Exception as e:
                    continue
            
            self.logger.extract(f"Successfully parsed {successful_extractions} out of {len(review_elements)} elements")
            return reviews
            
        except Exception as e:
            self.logger.error(f"Failed to extract review elements: {str(e)}")
            return []
    
    def _parse_review_element(self, element):
        try:
            review_data = {}
            
            try:
                reviewer_name = element.find_element(By.CSS_SELECTOR, '.d4r55').text
                review_data['reviewer_name'] = reviewer_name
            except NoSuchElementException:
                review_data['reviewer_name'] = "Anonymous"
            
            try:
                review_text = element.find_element(By.CSS_SELECTOR, '.wiI7pd').text
                review_data['review_text'] = review_text
            except NoSuchElementException:
                review_data['review_text'] = ""
            
            try:
                review_date = element.find_element(By.CSS_SELECTOR, '.rsqaWe').text
                review_data['review_date'] = review_date
            except NoSuchElementException:
                review_data['review_date'] = ""
            
            try:
                rating_element = element.find_element(By.CSS_SELECTOR, '[aria-label*="stars"]')
                rating_text = rating_element.get_attribute('aria-label')
                review_data['rating'] = rating_text
            except NoSuchElementException:
                review_data['rating'] = "No rating"
            
            try:
                media_elements = element.find_elements(By.CSS_SELECTOR, 'img[src*="googleusercontent"]')
                media_links = [img.get_attribute('src') for img in media_elements]
                review_data['media_links'] = ', '.join(media_links) if media_links else ""
            except Exception:
                review_data['media_links'] = ""
            
            try:
                review_id = element.get_attribute('data-review-id')
                review_data['review_id'] = review_id if review_id else ""
            except Exception:
                review_data['review_id'] = ""
            
            return review_data
            
        except Exception as e:
            return None
    
    def extract_all_reviews(self, review_type):
        try:
            self.logger.extract("Starting review extraction process...")
            
            # Navigate to reviews tab
            if not self._navigate_to_reviews_tab():
                self.logger.error("Could not navigate to reviews tab")
                return []
            
            self.logger.extract(f"Found reviews, attempting Type {review_type} scroll...")
            
            # Try scrolling with the detected type
            scroll_success = self._scroll_to_bottom(review_type)
            
            # If Type 2 fails, automatically fallback to Type 1
            if not scroll_success and review_type == 2:
                self.logger.extract("Type 2 scroll failed, falling back to Type 1...")
                scroll_success = self._scroll_to_bottom(1)
                if scroll_success:
                    self.logger.extract("Type 1 fallback successful")
            
            # If still no success, try to extract what we can
            if not scroll_success:
                self.logger.extract("Scroll failed, attempting to extract visible reviews...")
            
            # Extract reviews regardless of scroll success
            reviews_data = self._extract_review_elements(review_type)
            
            # If no reviews found with Type 2, try Type 1 extraction
            if len(reviews_data) == 0 and review_type == 2:
                self.logger.extract("No reviews found with Type 2, trying Type 1 extraction...")
                reviews_data = self._extract_review_elements(1)
            
            self.logger.extract(f"Extracted {len(reviews_data)} reviews")
            
            return reviews_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract reviews: {str(e)}")
            
            # Ultimate fallback: Try Type 1 if we were trying Type 2
            if review_type == 2:
                self.logger.extract("Critical error in Type 2, attempting Type 1 recovery...")
                try:
                    return self.extract_all_reviews(1)
                except Exception as fallback_error:
                    self.logger.error(f"Type 1 fallback also failed: {str(fallback_error)}")
                    return []
            
            return []