from __future__ import annotations

import logging
from re import search
from typing import TYPE_CHECKING, Any, Unpack

from crawlee.basic_crawler import BasicCrawler, BasicCrawlerOptions, ContextPipeline
from crawlee.errors import SessionError
from crawlee.http_clients.curl_impersonate import CurlImpersonateHttpClient
from crawlee.http_crawler import HttpCrawlingContext
from crawlee.models import BaseRequestData
from orjson import loads

from afs_crawlee.constants import BASE_TEMPLATE, HEADERS

from .types import CustomContext

if TYPE_CHECKING:

    from collections.abc import AsyncGenerator, Iterable

    from crawlee.types import BasicCrawlingContext


class CustomCrawler(BasicCrawler[CustomContext]):
    """A crawler that fetches the request URL using `curl_impersonate` and parses the result with `orjson` and `re`."""

    def __init__(
        self,
        *,
        impersonate: str = 'chrome124',
        additional_http_error_status_codes: Iterable[int] = (),
        ignore_http_error_status_codes: Iterable[int] = (),
        **kwargs: Unpack[BasicCrawlerOptions[CustomContext]],
    ) -> None:

        self._build_id = None
        self._base_url = BASE_TEMPLATE

        kwargs['_context_pipeline'] = (
            ContextPipeline()
            .compose(self._make_http_request)
            .compose(self._handle_blocked_request)
            .compose(self._parse_http_response)
        )

        # Initialize curl_impersonate http client using TLS preset and necessary headers
        kwargs.setdefault(
            'http_client',
            CurlImpersonateHttpClient(
                additional_http_error_status_codes=additional_http_error_status_codes,
                ignore_http_error_status_codes=ignore_http_error_status_codes,
                impersonate=impersonate,
                headers=HEADERS,
            ),
        )

        kwargs.setdefault('_logger', logging.getLogger(__name__))

        super().__init__(**kwargs)

    async def _make_http_request(self, context: BasicCrawlingContext) -> AsyncGenerator[HttpCrawlingContext, None]:
        result = await self._http_client.crawl(
            request=context.request,
            session=context.session,
            proxy_info=context.proxy_info,
            statistics=self._statistics,
        )

        yield HttpCrawlingContext(
            request=context.request,
            session=context.session,
            proxy_info=context.proxy_info,
            add_requests=context.add_requests,
            send_request=context.send_request,
            push_data=context.push_data,
            log=context.log,
            http_response=result.http_response,
        )

    async def _handle_blocked_request(self, crawling_context: CustomContext) -> AsyncGenerator[CustomContext, None]:
        if self._retry_on_blocked:
            status_code = crawling_context.http_response.status_code

            if crawling_context.session and crawling_context.session.is_blocked_status_code(status_code=status_code):
                raise SessionError(f'Assuming the session is blocked based on HTTP status code {status_code}')

        yield crawling_context

    async def _parse_http_response(self, context: HttpCrawlingContext) -> AsyncGenerator[CustomContext, None]:

        page_data = None

        if context.http_response.headers['content-type'] == 'text/html; charset=utf-8':
            # Get Build ID for Next js from the start page of the site, form a link to next.js endpoints
            build_id = search(rb'"buildId":"(.{21})"', context.http_response.read()).group(1)
            self._build_id = build_id.decode('UTF-8')
            self._base_url = self._base_url.format(build_id=self._build_id)
        else:
            # Convert json to python dictionary
            page_data = context.http_response.read()
            page_data = page_data.decode('ISO-8859-1').encode('utf-8')
            page_data = loads(page_data)

        async def enqueue_links(
            *, path_template: str, items: list[str], user_data: dict[str, Any] | None = None, label: str | None = None
        ) -> None:

            requests = list[BaseRequestData]()
            user_data = user_data if user_data else {}

            for item in items:
                link_user_data = user_data.copy()

                if label is not None:
                    link_user_data.setdefault('label', label)

                if link_user_data.get('label') == 'SEARCH':
                    link_user_data['location'] = item

                url = self._base_url + path_template.format(item=item, **user_data)
                requests.append(BaseRequestData.from_url(url, user_data=link_user_data))

            await context.add_requests(requests)

        yield CustomContext(
            request=context.request,
            session=context.session,
            proxy_info=context.proxy_info,
            enqueue_links=enqueue_links,
            add_requests=context.add_requests,
            send_request=context.send_request,
            push_data=context.push_data,
            log=context.log,
            http_response=context.http_response,
            page_data=page_data,
        )
