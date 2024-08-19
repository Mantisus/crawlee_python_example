from crawlee.storages.dataset import Dataset

from .custom_crawler import CustomCrawler
from .router import router


async def main() -> None:
    """The main function that starts crawling."""
    crawler = CustomCrawler(max_requests_per_crawl=50, request_handler=router)

    # Run the crawler with the initial list of URLs.
    await crawler.run(['https://www.accommodationforstudents.com/'])

    dataset = await Dataset.open()
    await dataset.export_to(key='properties', content_type='json', to_key_value_store_name='results')
