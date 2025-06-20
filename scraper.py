from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import openpyxl
from datetime import datetime
import os

class GoogleMapsScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.business_data = []
        self.reviews_data = []
        self.setup_driver()
        self.setup_excel()
    
    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 10)
            
            print("Chrome browser initialized successfully")
        except WebDriverException as e:
            print(f"Failed to initialize Chrome browser: {str(e)}")
            raise
    
    def setup_excel(self):
        try:
            self.business_workbook = openpyxl.Workbook()
            self.business_sheet = self.business_workbook.active
            self.business_sheet.title = "Business Data"
            self.business_sheet.append([
                "Name", "Rating", "Address", "Phone", "Google Maps Link", "Timestamp"
            ])
            
            self.reviews_workbook = openpyxl.Workbook()
            self.reviews_sheet = self.reviews_workbook.active
            self.reviews_sheet.title = "Reviews Data"
            self.reviews_sheet.append(["Business Name", "Reviewer Name", "Rating", "Review Text", "Review Date", "Photos", "Timestamp"])
            
            print("Excel files initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Excel files: {str(e)}")
            raise

    def start_scraping(self, search_word):
        try:
            url = f"https://www.google.com/maps/search/{search_word}/?hl=en"
            print(f"Opening Google Maps with search: {search_word}")
            self.driver.get(url)
            
            print("Waiting for search results to load...")
            time.sleep(3)
            
            self.wait_for_results()
            self.click_first_result()
            self.extract_business_data()
            self.navigate_to_reviews()
            self.scroll_and_load_all_reviews()
            self.extract_all_reviews_data()
            self.save_excel_files()
            
        except Exception as e:
            print(f"Error during scraping: {str(e)}")
            raise
    
    def wait_for_results(self):
        try:
            results_container_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'
            self.wait.until(EC.presence_of_element_located((By.XPATH, results_container_xpath)))
            print("Search results container found")
        except TimeoutException as e:
            print(f"Failed to find search results container: {str(e)}")
            raise
    
    def click_first_result(self):
        try:
            first_result_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[3]'
            first_result = self.wait.until(EC.element_to_be_clickable((By.XPATH, first_result_xpath)))
            
            try:
                link_element = first_result.find_element(By.XPATH, './/div/a')
                google_maps_link = link_element.get_attribute('href')
                self.current_maps_link = google_maps_link
                print(f"Google Maps link extracted: {google_maps_link}")
            except NoSuchElementException:
                self.current_maps_link = "N/A"
                print("Could not extract Google Maps link")
            
            print("Clicking on the first search result...")
            first_result.click()
            
            time.sleep(2)
            
            detail_panel_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]'
            self.wait.until(EC.presence_of_element_located((By.XPATH, detail_panel_xpath)))
            print("First search result opened successfully")
            
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Failed to click first search result: {str(e)}")
            raise
    
    def extract_business_data(self):
        try:
            print("Extracting basic business information...")
            time.sleep(2)
            
            business_info = {}
            
            name_selectors = [
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1',
                'h1[data-attrid="title"]',
                '.x3AX1-LfntMc-header-title-title',
                '.qrShPb h1',
                'h1.fontHeadlineLarge'
            ]
            
            business_info['name'] = self.extract_text_by_multiple_selectors(name_selectors) or "N/A"
            print(f"Business name extracted: {business_info['name']}")
            
            rating_selectors = [
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]',
                '.ceNzKf[aria-hidden="true"]',
                'span.fontDisplayLarge'
            ]
            
            business_info['rating'] = self.extract_text_by_multiple_selectors(rating_selectors) or "N/A"
            print(f"Rating extracted: {business_info['rating']}")
            
            address_selectors = [
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[9]/div[3]/button/div/div[2]/div[1]',
                'button[data-item-id="address"] .fontBodyMedium',
                '[data-item-id="address"] .Io6YTe',
                'button[aria-label*="Address"] .fontBodyMedium'
            ]
            
            business_info['address'] = self.extract_text_by_multiple_selectors(address_selectors) or "N/A"
            print(f"Address extracted: {business_info['address']}")
            
            phone_selectors = [
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[9]/div[4]/button/div/div[2]/div[1]',
                'button[data-item-id*="phone"] .fontBodyMedium',
                '[data-value="Phone number"] .fontBodyMedium',
                'button[aria-label*="Phone"] .fontBodyMedium'
            ]
            
            business_info['phone'] = self.extract_text_by_multiple_selectors(phone_selectors) or "N/A"
            print(f"Phone extracted: {business_info['phone']}")
            
            business_info['google_maps_link'] = getattr(self, 'current_maps_link', 'N/A')
            business_info['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.current_business = business_info
            self.business_data.append(self.current_business)
            print("Basic business information extraction completed")
            
        except Exception as e:
            print(f"Error extracting business data: {str(e)}")
            self.current_business = {'name': 'N/A', 'rating': 'N/A', 'address': 'N/A', 'phone': 'N/A', 'google_maps_link': 'N/A', 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            self.business_data.append(self.current_business)

    def extract_text_by_multiple_selectors(self, selectors):
        for selector in selectors:
            try:
                if selector.startswith('//*') or selector.startswith('//'):
                    element = self.driver.find_element(By.XPATH, selector)
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text and text != "N/A":
                    return text
            except (NoSuchElementException, WebDriverException):
                continue
        return None

    def navigate_to_reviews(self):
        try:
            print("Navigating to reviews section...")
            reviews_tab_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[3]/div/div/button[2]/div[2]/div[2]'
            reviews_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, reviews_tab_xpath)))
            reviews_tab.click()
            time.sleep(3)
            print("Successfully navigated to reviews section")
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Failed to navigate to reviews: {str(e)}")
            raise

    def scroll_and_load_all_reviews(self):
        try:
            print("Starting to scroll and load all reviews...")
            
            reviews_container_selectors = [
                '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[5]',
                '[role="main"] [data-reviewid]',
                '.m6QErb[data-reviewid]'
            ]
            
            reviews_container = None
            for selector in reviews_container_selectors:
                try:
                    if selector.startswith('//*') or selector.startswith('//'):
                        reviews_container = self.driver.find_element(By.XPATH, selector)
                    else:
                        reviews_container = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not reviews_container:
                raise Exception("Could not find reviews container")
            
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", reviews_container)
            scroll_attempts = 0
            max_scroll_attempts = 50
            no_new_content_count = 0
            max_no_new_content = 5
            
            while scroll_attempts < max_scroll_attempts and no_new_content_count < max_no_new_content:
                try:
                    self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", reviews_container)
                    time.sleep(2)
                    
                    new_height = self.driver.execute_script("return arguments[0].scrollHeight", reviews_container)
                    
                    if new_height == last_height:
                        no_new_content_count += 1
                        print(f"No new content loaded, attempt {no_new_content_count}/{max_no_new_content}")
                    else:
                        no_new_content_count = 0
                        last_height = new_height
                        print(f"Scrolled - New content loaded (attempt {scroll_attempts + 1})")
                    
                    scroll_attempts += 1
                    
                    current_reviews = self.driver.find_elements(By.CSS_SELECTOR, '[data-reviewid]')
                    print(f"Currently loaded {len(current_reviews)} reviews")
                    
                except Exception as e:
                    print(f"Error during scrolling attempt {scroll_attempts}: {str(e)}")
                    scroll_attempts += 1
                    continue
            
            final_reviews = self.driver.find_elements(By.CSS_SELECTOR, '[data-reviewid]')
            print(f"Scrolling completed. Total reviews found: {len(final_reviews)}")
            
        except Exception as e:
            print(f"Error during scrolling: {str(e)}")
            print("Continuing with currently loaded reviews...")

    def extract_all_reviews_data(self):
        try:
            print("Extracting all reviews data...")
            time.sleep(2)
            
            review_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-reviewid]')
            
            if not review_elements:
                alternative_selectors = [
                    '.jftiEf.fontBodyMedium',
                    '.MyEned',
                    '[jsaction*="review"]'
                ]
                
                for selector in alternative_selectors:
                    try:
                        review_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if review_elements:
                            break
                    except Exception:
                        continue
            
            print(f"Found {len(review_elements)} review elements")
            
            extracted_reviews = []
            
            for i, review_element in enumerate(review_elements):
                try:
                    review_data = self.extract_single_review_from_element(review_element, i + 1)
                    if review_data:
                        extracted_reviews.append(review_data)
                        print(f"Review {len(extracted_reviews)} extracted: {review_data['reviewer_name']}")
                        
                except Exception as e:
                    print(f"Error processing review element {i + 1}: {str(e)}")
                    continue
            
            self.reviews_data.extend(extracted_reviews)
            print(f"Total reviews extracted: {len(extracted_reviews)}")
                    
        except Exception as e:
            print(f"Error extracting reviews: {str(e)}")

    def extract_single_review_from_element(self, review_element, review_number):
        try:
            review_data = {}
            review_data['business_name'] = self.current_business.get('name', 'N/A')
            
            reviewer_name_selectors = ['.d4r55', '.X43Kjb', '[data-personalization-key] span']
            review_data['reviewer_name'] = self.extract_text_from_element(review_element, reviewer_name_selectors) or "N/A"
            
            try:
                rating_element = review_element.find_element(By.CSS_SELECTOR, '.kvMYJc[role="img"], [aria-label*="star"], .Fam1ne .kvMYJc')
                aria_label = rating_element.get_attribute('aria-label')
                if aria_label:
                    rating_parts = aria_label.split()
                    if rating_parts:
                        rating_match = rating_parts[0]
                        review_data['rating'] = rating_match if rating_match.replace('.', '').isdigit() else "N/A"
                    else:
                        review_data['rating'] = "N/A"
                else:
                    review_data['rating'] = "N/A"
            except NoSuchElementException:
                review_data['rating'] = "N/A"
            
            review_text_selectors = ['.wiI7pd', '.MyEned', '.review-text', '[data-expandable-section]']
            review_data['review_text'] = self.extract_text_from_element(review_element, review_text_selectors) or "N/A"
            
            review_date_selectors = ['.rsqaWe', '.DU9Pgb', '.review-date']
            review_data['review_date'] = self.extract_text_from_element(review_element, review_date_selectors) or "N/A"
            
            try:
                photo_elements = review_element.find_elements(By.CSS_SELECTOR, '.Tya61d, .loaded[style*="background-image"]')
                photo_links = []
                for photo_elem in photo_elements:
                    style = photo_elem.get_attribute('style')
                    if style and 'background-image: url(' in style:
                        url_start = style.find('url("') + 5
                        url_end = style.find('")', url_start)
                        photo_url = style[url_start:url_end]
                        if 'googleusercontent' in photo_url:
                            photo_links.append(photo_url)
                
                review_data['photos'] = ', '.join(photo_links) if photo_links else "N/A"
            except Exception:
                review_data['photos'] = "N/A"
            
            review_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if (review_data['reviewer_name'] != "N/A" and 
                review_data['review_text'] != "N/A" and 
                len(review_data['review_text']) > 5):
                return review_data
            else:
                return None
            
        except Exception as e:
            print(f"Error extracting single review: {str(e)}")
            return None

    def extract_text_from_element(self, parent_element, selectors):
        for selector in selectors:
            try:
                element = parent_element.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text and text != "N/A":
                    return text
            except NoSuchElementException:
                continue
        return None

    def save_excel_files(self):
        try:
            for business in self.business_data:
                self.business_sheet.append([
                    business.get('name', 'N/A'),
                    business.get('rating', 'N/A'),
                    business.get('address', 'N/A'),
                    business.get('phone', 'N/A'),
                    business.get('google_maps_link', 'N/A'),
                    business.get('timestamp', 'N/A')
                ])
            
            for review in self.reviews_data:
                self.reviews_sheet.append([
                    review.get('business_name', 'N/A'),
                    review.get('reviewer_name', 'N/A'),
                    review.get('rating', 'N/A'),
                    review.get('review_text', 'N/A'),
                    review.get('review_date', 'N/A'),
                    review.get('photos', 'N/A'),
                    review.get('timestamp', 'N/A')
                ])
            
            business_filename = f"business_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            reviews_filename = f"reviews_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            self.business_workbook.save(business_filename)
            self.reviews_workbook.save(reviews_filename)
            
            print(f"Business data saved to: {business_filename}")
            print(f"Reviews data saved to: {reviews_filename}")
            
        except Exception as e:
            print(f"Error saving Excel files: {str(e)}")
    
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                print("Browser closed")
            except Exception as e:
                print(f"Error closing browser: {str(e)}")
