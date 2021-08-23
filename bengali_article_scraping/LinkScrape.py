import sys, os
from SERPLinkScraperConfig import SERPLinkScraperConfig
from SERPLinkScraper import SERPLinkScraper

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Usage: python LinkScrape.py [CONFIG_FILE]")
    
    config_file = sys.argv[1]
    config = SERPLinkScraperConfig(config_file)
    scraper = SERPLinkScraper(config)
    scraper.run()

    