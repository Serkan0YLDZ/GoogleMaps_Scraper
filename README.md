# Google Maps Scraper 

This is a Python project designed to scrape business information from Google Maps. It provides two main scripts for different scraping needs: one for comprehensive data extraction including reviews, and another for extracting business details without reviews.

## Usage

### 1. Scrape Business Information with Reviews (main.py)

This script scrapes detailed business information, including customer reviews, for a given search term.

```bash
python3 main.py "your search query"
```
Replace `"your search query"` with the actual term you want to search for (e.g., "restaurants in New York").

### 2. Scrape Business Information without Reviews (main_no_reviews.py)

This script scrapes business information, excluding customer reviews, for a given search term. This can be faster for scenarios where review data is not needed.

```bash
python3 main_no_reviews.py "your search query"
```
Replace `"your search query"` with the actual term you want to search for.

## Project Structure

*   `main.py`: The main script to start the scraping process, including reviews.
*   `main_no_reviews.py`: A variant of the main script to scrape business information without reviews.
*   `modules/`: Contains modular components for browser management, business data handling, data saving, data scraping logic, and scroll handling.
*   `utils/`: Contains utility functions, such as XPath helpers.
*   `data/`: (Expected) Directory where scraped data (e.g., Excel files) will be saved.
*   `__pycache__/`: Python cache directories.

## Dependencies
*   A compatible WebDriver (e.g., ChromeDriver) for your preferred browser.

## Error Handling

The scripts include basic error handling for issues like incorrect usage, empty search queries, browser initialization failures, and unexpected errors during scraping. User interruption (`Ctrl+C`) is also handled gracefully.


