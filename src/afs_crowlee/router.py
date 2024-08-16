from crawlee.basic_crawler import Router

from .constants import LISTING_PATH, SEARCH_PATH, TARGET_LOCATIONS
from .custom_crawler import CustomContext

router = Router[CustomContext]()


@router.default_handler
async def default_handler(context: CustomContext) -> None:
    """Handle the start URL to get the Build ID and create search links."""
    context.log.info(f'default_handler is processing {context.request.url}')

    await context.enqueue_links(
        path_template=SEARCH_PATH, items=TARGET_LOCATIONS, label='SEARCH', user_data={'page': 1}
    )


@router.handler('SEARCH')
async def search_handler(context: CustomContext) -> None:
    """Handle the SEARCH URL generates links to listings and to the next search page."""
    context.log.info(f'category_handler is processing {context.request.url}')

    max_pages = context.page_data['pageProps']['initialPageCount']
    current_page = context.request.user_data['page']
    if current_page < max_pages:

        await context.enqueue_links(
            path_template=SEARCH_PATH,
            items=[context.request.user_data['location']],
            label='SEARCH',
            user_data={'page': current_page + 1},
        )

    listing_ids = [
        listing['property']['id']
        for group in context.page_data['pageProps']['initialListings']['groups']
        for listing in group['results']
        if listing.get('property')
    ]

    await context.enqueue_links(path_template=LISTING_PATH, items=listing_ids, label='LISTING')


@router.handler('LISTING')
async def listing_handler(context: CustomContext) -> None:
    """Handle the LISTING URL extracts data from the listings and saving it to a dataset."""
    context.log.info(f'category_handler is processing {context.request.url}')

    listing_data = context.page_data['pageProps']['viewModel']['propertyDetails']

    property_data = {
        'property_id': listing_data['id'],
        'property_type': listing_data['propertyType'],
        'location_latitude': listing_data['coordinates']['lat'],
        'location_longitude': listing_data['coordinates']['lng'],
        'address1': listing_data['address']['address1'],
        'address2': listing_data['address']['address2'],
        'city': listing_data['address']['city'],
        'postcode': listing_data['address']['postcode'],
        'bills_included': listing_data['terms']['billsIncluded'],
        'description': listing_data['description'],
        'bathrooms': listing_data['numberOfBathrooms'],
        'number_rooms': len(listing_data['rooms']),
        'rent_ppw': listing_data['terms']['rentPpw']['value'],
    }

    await context.push_data(property_data)
