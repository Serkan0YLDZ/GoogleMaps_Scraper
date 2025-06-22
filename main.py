import sys
import gc
from scraper.google_maps_scraper import GoogleMapsScraper
from utils.logger import Logger

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <search_term>")
        print("Examples:")
        print("  python3 main.py pharmacy")
        print("  python3 main.py restaurant") 
        print("  python3 main.py hotel")
        sys.exit(1)
    
    search_term = sys.argv[1]
    logger = Logger()
    
    try:
        logger.info(f"Starting Google Maps scraper for: {search_term}")
        
        scraper = GoogleMapsScraper(logger)
        scraper.scrape_businesses(search_term)
        
        logger.success("Scraping completed successfully")
        
    except KeyboardInterrupt:
        logger.error("Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Critical error occurred: {str(e)}")
        sys.exit(1)
    finally:
        gc.collect()

if __name__ == "__main__":
    main()