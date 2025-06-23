import sys
from scraper.google_maps_scraper import GoogleMapsScraper
from utils.logger import Logger

class ScrapingApplication:
    def __init__(self):
        self.logger = Logger()
        self.scraper = None
    
    def validate_arguments(self) -> str:
        if len(sys.argv) != 2:
            error_msg = "Invalid arguments provided"
            self.logger.error(error_msg)
            self._print_usage()
            raise ValueError(error_msg)
        
        search_term = sys.argv[1].strip()
        if not search_term:
            error_msg = "Search term cannot be empty"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        if len(search_term) < 2:
            error_msg = "Search term must be at least 2 characters long"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        return search_term
    
    def _print_usage(self) -> None:
        print("Usage: python3 main.py <search_term>")
        print("Examples:")
        print("  python3 main.py pharmacy")
        print("  python3 main.py restaurant")
        print("  python3 main.py hotel")
    
    def initialize_scraper(self) -> None:
        try:
            self.scraper = GoogleMapsScraper(self.logger)
        except Exception as e:
            error_msg = f"Failed to initialize scraper: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def run_scraping(self, search_term: str) -> None:
        if not self.scraper:
            raise RuntimeError("Scraper not initialized")
        
        try:
            self.logger.info(f"Starting Google Maps scraper for: {search_term}")
            self.scraper.scrape_businesses(search_term)
            self.logger.success("Scraping completed successfully")
        except KeyboardInterrupt:
            self.logger.warning("Scraping interrupted by user")
            raise
        except Exception as e:
            error_msg = f"Scraping process failed: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def cleanup(self) -> None:
        try:
            if self.scraper:
                self.scraper.cleanup()
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def run(self) -> None:
        exit_code = 0
        
        try:
            search_term = self.validate_arguments()
            self.initialize_scraper()
            self.run_scraping(search_term)
        except (ValueError, RuntimeError) as e:
            exit_code = 1
        except KeyboardInterrupt:
            self.logger.warning("Application interrupted by user")
            exit_code = 130
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            exit_code = 1
        finally:
            self.cleanup()
            sys.exit(exit_code)

def main() -> None:
    app = ScrapingApplication()
    app.run()

if __name__ == "__main__":
    main()