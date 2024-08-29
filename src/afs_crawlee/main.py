from .custom_crawler import CustomCrawler
from .router import router


async def main() -> None:
    """The main function that starts crawling."""
    crawler = CustomCrawler(max_requests_per_crawl=50, request_handler=router)

    # Run the crawler with the initial list of URLs.
    await crawler.run(['https://www.accommodationforstudents.com/'])

    await crawler.export_data('results.json')
