import time

class ScrollHandler:
    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.scroll_attempts = 0
        self.max_scroll_attempts = 3
    
    def scroll_results_panel(self):
        try:
            if self.check_end_of_list():
                print("[INFO] End of list reached - skipping scroll")
                return False
                
            results_panel = "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]"
            success = self.browser.scroll_element(results_panel, "down", 5000)
            if success:
                print("[INFO] Scrolled results panel")
                return True
            return False
        except Exception as e:
            print("[ERROR] Failed to scroll results panel: {}".format(str(e)))
            return False

    def scroll_results_panel_fast(self):
        try:
            if self.check_end_of_list():
                return False
            results_panel = "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]"
            escaped_xpath = results_panel.replace("'", "\\'")
            self.browser.driver.execute_script(f"""
                var element = document.evaluate('{escaped_xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (element) {{
                    element.scrollBy(0, 6000);
                }}
            """)
            return True
        except Exception as e:
            print("[ERROR] Fast scroll failed: {}".format(str(e)))
            return False

    def scroll_results_to_end_fast(self, max_iterations=10000):
        try:
            iterations = 0
            while not self.check_end_of_list() and iterations < max_iterations:
                self.scroll_results_panel_fast()
                iterations += 1
            if iterations >= max_iterations:
                print("[WARN] Reached max iterations during fast preload scrolling")
            return True
        except Exception as e:
            print("[ERROR] Failed during fast preload scrolling: {}".format(str(e)))
            return False
    
    def scroll_reviews_section(self, container_xpath):
        if self.scroll_attempts >= self.max_scroll_attempts:
            print("[INFO] Maximum scroll attempts ({}) reached. Stopping scroll.".format(self.max_scroll_attempts))
            return False
            
        success = self._scroll_reviews_primary(container_xpath)
        if not success and self.scroll_attempts < self.max_scroll_attempts:
            return self.scroll_reviews_section_alternative(container_xpath)
        return success
    
    def _scroll_reviews_primary(self, container_xpath):
        try:
            element = self.browser.wait_for_element(container_xpath, 5)
            if not element:
                print("[ERROR] Container element not found: {}".format(container_xpath))
                return False
            
            try:
                current_height = self.browser.driver.execute_script("return arguments[0].scrollHeight", element)
                current_scroll = self.browser.driver.execute_script("return arguments[0].scrollTop", element)
            except Exception as e:
                print("[ERROR] Failed to get scroll info: {}".format(str(e)))
                return False
            
            success = self.browser.scroll_element(container_xpath, "down", 6000)
            if success:
                
                try:
                    new_height = self.browser.driver.execute_script("return arguments[0].scrollHeight", element)
                    new_scroll = self.browser.driver.execute_script("return arguments[0].scrollTop", element)
                    
                    if new_height > current_height or new_scroll > current_scroll:
                        self.scroll_attempts = 0
                        return True
                    else:
                        self.scroll_attempts += 1
                        print("[INFO] No new content loaded (attempt {}/{})".format(self.scroll_attempts, self.max_scroll_attempts))
                        
                        if self.is_scroll_at_bottom(container_xpath):
                            return False
                        
                        if self.scroll_attempts >= self.max_scroll_attempts:
                            print("[INFO] Maximum scroll attempts reached, no more content available")
                            return False
                        return False 
                except Exception as e:
                    print("[ERROR] Failed to check new scroll info: {}".format(str(e)))
                    return False
            
            return False
            
        except Exception as e:
            print("[ERROR] Failed to scroll reviews section: {}".format(str(e)))
            return False

    def scroll_reviews_section_alternative(self, container_xpath):
        try:
            if self.scroll_attempts >= self.max_scroll_attempts:
                print("[INFO] Maximum scroll attempts ({}) reached in alternative method. Stopping.".format(self.max_scroll_attempts))
                return False
                
            if not self.browser.is_element_present(container_xpath, 3):
                print("[ERROR] Container not found: {}".format(container_xpath))
                self.scroll_attempts += 1
                return False
            
            escaped_xpath = container_xpath.replace("'", "\\'")
            
            try:
                self.browser.driver.execute_script(f"""
                    var element = document.evaluate('{escaped_xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (element) {{
                        element.scrollBy(0, 6000);
                    }}
                """)
                
                self.scroll_attempts += 1
                print("[INFO] Alternative scroll completed (attempt {}/{})".format(self.scroll_attempts, self.max_scroll_attempts))
                
                if self.scroll_attempts >= self.max_scroll_attempts:
                    print("[INFO] Maximum scroll attempts reached with alternative method")
                    return False
                    
                return True
            except Exception as e:
                print("[ERROR] Alternative scroll failed: {}".format(str(e)))
                self.scroll_attempts += 1
                return False
                
        except Exception as e:
            print("[ERROR] Alternative scroll method failed: {}".format(str(e)))
            self.scroll_attempts += 1
            return False
    
    # Removed unused check_scroll_end
    
    def check_end_of_list(self):
        try:
            end_message_xpath = "//*[contains(text(), \"You've reached the end of the list.\")]"
            return self.browser.is_element_present(end_message_xpath, 2)
        except Exception:
            return False
    
    # Removed unused smooth_scroll
    
    def is_scroll_at_bottom(self, container_xpath):
        try:
            element = self.browser.wait_for_element(container_xpath, 3)
            if not element:
                return True  
                
            scroll_height = self.browser.driver.execute_script("return arguments[0].scrollHeight", element)
            scroll_top = self.browser.driver.execute_script("return arguments[0].scrollTop", element)
            client_height = self.browser.driver.execute_script("return arguments[0].clientHeight", element)
            is_at_bottom = (scroll_top + client_height) >= (scroll_height - 10)
            return is_at_bottom
            
        except Exception as e:
            print("[ERROR] Failed to check if at bottom: {}".format(str(e)))
            return True
        
    def reset_scroll_attempts(self):
        self.scroll_attempts = 0
