#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from utils.logger import Logger
from scraper.review_extractor import ReviewParser

def test_photo_extraction():
    logger = Logger()
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        html_content = '''
        <div class="KtCyie">
            <button class="Tya61d" style="background-image: url(&quot;https://lh3.googleusercontent.com/test1.jpg&quot;);"></button>
            <button class="Tya61d" style="background-image: url(&quot;https://lh3.googleusercontent.com/test2.jpg&quot;);"></button>
        </div>
        '''
        
        driver.get("data:text/html," + html_content)
        
        parser = ReviewParser(driver, logger)
        element = driver.find_element(By.TAG_NAME, "body")
        
        media_links = parser._extract_media_links(element)
        
        print(f"Extracted photo URLs: {media_links}")
        
        if "test1.jpg" in media_links and "test2.jpg" in media_links:
            print("SUCCESS: Photo extraction working correctly!")
        else:
            print("FAILURE: Photo extraction not working")
            
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_photo_extraction()
