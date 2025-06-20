from utils.xpath_helpers import XPathHelper
import time

class BusinessManager:
    def __init__(self, browser_manager, data_scraper, data_saver, scroll_handler):
        self.browser = browser_manager
        self.data_scraper = data_scraper
        self.data_saver = data_saver
        self.scroll_handler = scroll_handler
        self.current_business_index = 0
        self.total_businesses_processed = 0
        self.total_reviews_extracted = 0
    
    def initialize_search(self, search_word):
        try:
            search_url = f"https://www.google.com/maps/search/{search_word}/?hl=en"
            print("[INFO] Starting Google Maps scraper for: {}".format(search_word))
            
            if not self.browser.navigate_to_url(search_url):
                return False
            
            return self._wait_for_results()
            
        except Exception as e:
            print("[ERROR] Failed to initialize search: {}".format(str(e)))
            return False
    
    def get_business_list(self):
        try:
            businesses_found = 0
            index = 0
            
            while True:
                business_xpath = XPathHelper.get_business_xpath(index)
                if self.browser.is_element_present(business_xpath, 3):
                    businesses_found += 1
                    index += 1
                else:
                    break            
            return businesses_found
            
        except Exception as e:
            print("[ERROR] Failed to get business list: {}".format(str(e)))
            return 0
    
    def determine_business_type(self, business_index):
        try:
            type_check_xpath = XPathHelper.get_business_type_xpath(business_index)
                        
            if self.browser.is_element_present(type_check_xpath, 3):
                element_text = self.browser.get_element_text(type_check_xpath)
                
                if element_text and "book online" in element_text.lower():
                    return "type2"
                else:
                    return "type1"
            else:
                return "type1"
            
        except Exception as e:
            print("[ERROR] Failed to determine business type for index {}: {}".format(business_index, str(e)))
            return "type1"
    
    def click_business(self, business_index):
        try:
            business_xpath = XPathHelper.get_business_xpath(business_index)
            success = self.browser.click_element(business_xpath)
            
            if success:
                return True
            
            return False
            
        except Exception as e:
            print("[ERROR] Failed to click business: {}".format(str(e)))
            return False
    
    def process_all_businesses(self):
        try:
            business_count = self.get_business_list()
            if business_count == 0:
                print("[ERROR] No businesses found")
                return False
            
            end_of_list_reached = False
            
            while True:
                business_xpath = XPathHelper.get_business_xpath(self.current_business_index)
                
                if not self.browser.is_element_present(business_xpath, 3):
                    if not end_of_list_reached:
                        if self.scroll_handler.check_end_of_list():
                            end_of_list_reached = True
                        elif not self.scroll_handler.scroll_results_panel():
                            print("[INFO] No more businesses to scroll")
                            break
                        continue
                    else:
                        break
                
                business_type = self.determine_business_type(self.current_business_index)
                print(f"[INFO] Processing business {self.current_business_index + 1}: Business type detected: {business_type}")
                
                if self.click_business(self.current_business_index):
                    self._process_single_business(business_type)
                
                self.current_business_index += 1
                self.total_businesses_processed += 1
                
                time.sleep(2)
            
            self._print_summary()
            return True
            
        except Exception as e:
            print("[ERROR] Failed to process businesses: {}".format(str(e)))
            return False
    
    def process_businesses_no_reviews(self):
        try:
            business_count = self.get_business_list()
            if business_count == 0:
                print("[ERROR] No businesses found")
                return False
            
            end_of_list_reached = False
            
            while True:
                business_xpath = XPathHelper.get_business_xpath(self.current_business_index)
                
                if not self.browser.is_element_present(business_xpath, 3):
                    if not end_of_list_reached:
                        if self.scroll_handler.check_end_of_list():
                            end_of_list_reached = True
                        elif not self.scroll_handler.scroll_results_panel():
                            print("[INFO] No more businesses to scroll")
                            break
                        continue
                    else:
                        break
                
                business_type = self.determine_business_type(self.current_business_index)
                print(f"[INFO] Processing business {self.current_business_index + 1}: Business type detected: {business_type}")
                
                if self.click_business(self.current_business_index):
                    self._process_single_business_no_reviews(business_type)
                
                self.current_business_index += 1
                self.total_businesses_processed += 1
                
                time.sleep(2)
            
            self._print_summary()
            return True
            
        except Exception as e:
            print("[ERROR] Failed to process businesses without reviews: {}".format(str(e)))
            return False

    def _process_single_business(self, business_type):
        try:
            business_data = self.data_scraper.scrape_business_info(business_type)
            if business_data:
                business_name = business_data.get('business_name', 'Unknown')
                
                reviews = self.data_scraper.scrape_reviews(business_type)
                self.total_reviews_extracted += len(reviews)
                
                print("[INFO] Extracting reviews (found {} reviews)...".format(len(reviews)))
                
                business_file = self.data_saver.save_business_info(business_data)
                
                if reviews:
                    reviews_data = {
                        'business_name': business_name,
                        'reviews': reviews,
                        'scraped_at': business_data.get('scraped_at', '')
                    }
                    reviews_file = self.data_saver.save_reviews(reviews_data)
                
                print("[INFO] Data saved successfully")
                
                self._clear_memory()
                
        except Exception as e:
            print("[ERROR] Failed to process single business: {}".format(str(e)))
    
    def _process_single_business_no_reviews(self, business_type):
        try:
            business_data = self.data_scraper.scrape_business_info(business_type)
            if business_data:
                self.data_saver.save_business_info(business_data)
                print("[INFO] Business info saved successfully (reviews skipped)")
            self._clear_memory()
        except Exception as e:
            print(f"[ERROR] Failed to process single business without reviews: {str(e)}")

    def _clear_memory(self):
        try:
            self.browser.driver.execute_script("window.gc && window.gc();")
        except Exception:
            pass
    
    def _wait_for_results(self):
        try:
            first_business_xpath = XPathHelper.get_business_xpath(0)
            if self.browser.wait_for_element(first_business_xpath, 15):
                return True
            
            print("[ERROR] No search results found")
            return False
            
        except Exception as e:
            print("[ERROR] Failed to wait for results: {}".format(str(e)))
            return False
    
    def _print_summary(self):
        print("[SUCCESS] Scraping completed successfully")
        print("[INFO] Total businesses processed: {}".format(self.total_businesses_processed))
        print("[INFO] Total reviews extracted: {}".format(self.total_reviews_extracted))
    
    def notify_scraping_complete(self):
        print("[INFO] Scraping workflow completed")
