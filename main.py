import sys
from scraper import GoogleMapsScraper

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 main.py '<search_word>'")
        sys.exit(1)
    
    search_word = sys.argv[1]
    scraper = GoogleMapsScraper()
    
    try:
        scraper.start_scraping(search_word)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        scraper.close()
    finally:
        input("Press Enter to close the browser...")
        scraper.close()

if __name__ == "__main__":
    main()
