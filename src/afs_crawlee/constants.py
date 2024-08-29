BASE_TEMPLATE = 'https://www.accommodationforstudents.com/_next/data/{build_id}'
SEARCH_PATH = '/search-results.json?&geo=false&page={page}&country=gb&location={item}'
LISTING_PATH = '/property/{item}.json'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 '
        'Safari/537.36'
    ),
    'Accept': (
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,'
        '*/*;q=0.8'
    ),
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Connection': 'keep-alive',
}

TARGET_LOCATIONS = ['London', 'Manchester']
