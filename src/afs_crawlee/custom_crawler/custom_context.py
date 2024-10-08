from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from crawlee.basic_crawler import BasicCrawlingContext
from crawlee.http_crawler import HttpCrawlingResult

if TYPE_CHECKING:

    from collections.abc import Callable


@dataclass(frozen=True)
class CustomContext(HttpCrawlingResult, BasicCrawlingContext):
    """Crawling context used by CustomCrawler."""

    page_data: dict | None
    # not `EnqueueLinksFunction`` because we are breaking protocol since we are not working with HTML
    # and we are not using selectors
    enqueue_links: Callable
