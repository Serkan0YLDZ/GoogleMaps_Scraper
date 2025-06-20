import sys
from modules.browser_manager import BrowserManager
from modules.business_manager import BusinessManager
from modules.data_scraper import DataScraper
from modules.data_saver import DataSaver
from modules.scroll_handler import ScrollHandler

def main():
    if len(sys.argv) != 2:
        print("[ERROR] Usage: python3 main.py {search_word}")
        sys.exit(1)
    
    search_word = sys.argv[1].strip()
    
    if not search_word:
        print("[ERROR] Search word cannot be empty")
        sys.exit(1)
    
    browser_manager = None
    
    try:
        browser_manager = BrowserManager()
        if not browser_manager.initialize_driver():
            print("[ERROR] Failed to initialize browser")
            sys.exit(1)
        
        data_saver = DataSaver()
        scroll_handler = ScrollHandler(browser_manager)
        data_scraper = DataScraper(browser_manager, scroll_handler)
        business_manager = BusinessManager(browser_manager, data_scraper, data_saver, scroll_handler)
        
        if not business_manager.initialize_search(search_word):
            print("[ERROR] Failed to initialize search")
            sys.exit(1)
        
        success = business_manager.process_all_businesses()
        
        if success:
            business_manager.notify_scraping_complete()
        else:
            print("[ERROR] Scraping process failed")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n[INFO] Scraping interrupted by user")
    
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        sys.exit(1)
    
    finally:
        if browser_manager:
            browser_manager.close_browser()

if __name__ == "__main__":
    main()
