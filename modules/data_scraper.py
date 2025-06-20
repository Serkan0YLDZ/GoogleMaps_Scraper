import re
from datetime import datetime
from utils.xpath_helpers import XPathHelper

class DataScraper:
    def __init__(self, browser_manager, scroll_handler):
        self.browser = browser_manager
        self.scroll_handler = scroll_handler
    
    def scrape_business_info(self, business_type):
        try:
            print("[INFO] Extracting business information...")
            
            business_name = self.browser.get_element_text(XPathHelper.BUSINESS_INFO['name'], timeout=15) # Zaman aşımını artırıyorum
            
            # Rating bilgisini aria-label niteliğinden çek ve ayrıştır
            raw_rating_label = self.browser.get_element_attribute(XPathHelper.BUSINESS_INFO['rating'], 'aria-label', timeout=15)
            rating = self._parse_rating_from_aria_label(raw_rating_label)
            
            address = self._extract_aria_label_info("Address:")
            phone = self._extract_aria_label_info("Phone:")
            website = self._extract_website_url(timeout=15) # Zaman aşımını artırıyorum
            maps_url = self.browser.get_current_url()
            
            business_data = {
                'business_name': business_name,
                'rating': rating,
                'address': address,
                'phone': phone,
                'website': website,
                'maps_url': maps_url,
                'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return business_data
            
        except Exception as e:
            print("[ERROR] Failed to scrape business info: {}".format(str(e)))
            return {}
    
    def scrape_reviews(self, business_type):
        try:
            print("[INFO] Clicking reviews button...")
            if not self.browser.click_element(XPathHelper.BUSINESS_INFO['reviews_button']):
                print("[ERROR] Failed to click reviews button")
                return []
            
            container_xpath = XPathHelper.SCROLL_CONTAINERS[business_type]
            
            print("[INFO] Starting review scrolling phase...")
            self._scroll_all_reviews(container_xpath)
            reviews = self._extract_all_reviews(business_type)
            
            print("[INFO] Total reviews extracted: {}".format(len(reviews)))
            return reviews
            
        except Exception as e:
            print("[ERROR] Failed to scrape reviews: {}".format(str(e)))
            return []
    
    def _scroll_all_reviews(self, container_xpath):
        try:
            self.scroll_handler.reset_scroll_attempts()
            
            while True:
                scroll_success = self.scroll_handler.scroll_reviews_section(container_xpath)
                if not scroll_success:
                    print("[INFO] No more reviews available or scroll limit reached")
                    break
                    
        except Exception as e:
            print("[ERROR] Failed during scrolling phase: {}".format(str(e)))
    
    def _extract_all_reviews(self, business_type):
        try:
            reviews = []
            review_index = 0
            current_base_div = None
            
            if business_type == 'type1':
                current_base_div = self._determine_correct_base_div(business_type)
            else:
                current_base_div = 10
            
            while True:
                review_xpath_dict = XPathHelper.get_review_xpath(business_type, review_index, current_base_div)
                
                if not self.browser.is_element_present(review_xpath_dict['reviewer_name'], 3):
                    break
                
                review_data = self.parse_review_element(review_xpath_dict, business_type)
                if review_data:
                    reviews.append(review_data)
                
                review_index += 1
            
            return reviews
            
        except Exception as e:
            print("[ERROR] Failed during extraction phase: {}".format(str(e)))
            return []
    
    def _determine_correct_base_div(self, business_type):
        try:
            test_xpath = XPathHelper.get_review_xpath(business_type, 0, 9)
            
            if self.browser.is_element_present(test_xpath['reviewer_name'], 3):
                return 9
            
            test_xpath = XPathHelper.get_review_xpath(business_type, 0, 10)
            
            if self.browser.is_element_present(test_xpath['reviewer_name'], 3):
                return 10
            
            return 9
            
        except Exception as e:
            return 9  
        
    def parse_review_element(self, review_xpath_dict, business_type):
        try:
            reviewer_name = self.browser.get_element_text(review_xpath_dict['reviewer_name'])
            review_date = self.browser.get_element_text(review_xpath_dict['review_date'])
            review_text = self._extract_review_text_for_current_review(review_xpath_dict, business_type)
            photos = self.extract_review_photos(review_xpath_dict['photos_container'])
            
            if not reviewer_name:
                return None
            
            return {
                'reviewer_name': reviewer_name,
                'review_text': review_text,
                'review_date': review_date,
                'photos': photos
            }
            
        except Exception as e:
            print("[ERROR] Failed to parse review element: {}".format(str(e)))
            return None

    def _extract_review_text_for_current_review(self, review_xpath_dict, business_type):
        try:
            base_path = review_xpath_dict['reviewer_name'].rsplit('/div/div/div[2]', 1)[0]
            text_container_xpath = f"{base_path}/div/div/div[4]/div[2]"
            text_elements = self.browser.find_elements(f"{text_container_xpath}//span[@class='wiI7pd']")
            
            if text_elements:
                text_element = text_elements[0]
                
                more_button_xpath = f"{text_container_xpath}//button[@aria-label='See more']"
                more_buttons = self.browser.find_elements(more_button_xpath)
                if more_buttons:
                    try:
                        self.browser.driver.execute_script("arguments[0].click();", more_buttons[0])
                        self.browser.wait(1)
                        
                        updated_text_elements = self.browser.find_elements(f"{text_container_xpath}//span[@class='wiI7pd']")
                        if updated_text_elements:
                            return updated_text_elements[0].text.strip()
                    except Exception:
                        pass
                    
                return text_element.text.strip()
            
            return self._extract_review_text_alternative(base_path)
            
        except Exception as e:
            print("[ERROR] Failed to extract review text for current review: {}".format(str(e)))
            return ""

    def _extract_review_text_alternative(self, base_path):
        try:
            alternative_paths = [
                f"{base_path}/div/div/div[4]/div[2]/span",
                f"{base_path}/div/div/div[4]/div[2]/div/span",
                f"{base_path}/div/div/div[4]/div[2]//span"
            ]
            
            for path in alternative_paths:
                elements = self.browser.find_elements(path)
                if elements:
                    text = elements[0].text.strip()
                    if text and len(text) > 10:
                        return text
            
            return ""
            
        except Exception:
            return ""

    def extract_review_photos(self, photos_container_xpath):
        try:
            photos = []
            button_elements = self.browser.find_elements(f"{photos_container_xpath}/button")
            
            for button in button_elements:
                style_attr = button.get_attribute("style")
                if style_attr:
                    url_match = re.search(r'background-image: url\("([^"]+)"\)', style_attr)
                    if url_match:
                        photos.append(url_match.group(1))
            
            return photos
            
        except Exception as e:
            print("[ERROR] Failed to extract review photos: {}".format(str(e)))
            return []
    
    def _extract_aria_label_info(self, label_type):
        try:
            elements = self.browser.find_elements("//*[contains(@aria-label, '{}')]".format(label_type))
            for element in elements:
                aria_label = element.get_attribute("aria-label")
                if aria_label and label_type in aria_label:
                    parts = aria_label.split(label_type)
                    if len(parts) > 1:
                        return parts[1].strip()
            return ""
        except Exception:
            return ""
    
    def _extract_website_url(self, timeout=5):
        try:
            website_element = self.browser.wait_for_element(XPathHelper.BUSINESS_INFO['website'], timeout)
            if website_element:
                href = website_element.get_attribute("href")
                if href:
                    return href
            return ""
        except Exception as e: # Hata yakalamayı iyileştiriyorum
            print(f"[ERROR] Failed to extract website URL: {e}")
            return ""
    
    def _parse_rating_from_aria_label(self, aria_label_text):
        try:
            if aria_label_text:
                match = re.search(r'^(\d+\.?\d*)', aria_label_text)
                if match:
                    return match.group(1)
            return ""
        except Exception as e:
            print(f"[ERROR] Failed to parse rating from aria-label: {e}")
            return ""
    
    def _extract_review_text_new(self, review_xpath_dict):
        try:
            review_divs = self.browser.find_elements("//div[@class='MyEned']")
            
            for div in review_divs:
                div_id = div.get_attribute("id")
                if not div_id:
                    continue
                
                text_xpaths = XPathHelper.get_review_text_xpath(div_id)
                
                more_buttons = self.browser.find_elements(text_xpaths['more_button'])
                if more_buttons:
                    try:
                        more_button = more_buttons[0]
                        self.browser.driver.execute_script("arguments[0].click();", more_button)
                        self.browser.wait(1)
                    except Exception:
                        pass
                
                text_elements = self.browser.find_elements(text_xpaths['text_span'])
                if not text_elements:
                    text_elements = self.browser.find_elements(text_xpaths['text_span_alt'])
                
                if text_elements:
                    text = text_elements[0].text.strip()
                    if text and len(text) > 10:
                        return text
            
            return self._extract_review_text_fallback()
            
        except Exception as e:
            print("[ERROR] Failed to extract review text: {}".format(str(e)))
            return ""
    
    def _extract_review_text_fallback(self):
        try:
            text_elements = self.browser.find_elements("//span[@class='wiI7pd']")
            if text_elements:
                for element in text_elements:
                    text = element.text.strip()
                    if text and len(text) > 10:
                        return text
            return ""
        except Exception:
            return ""
