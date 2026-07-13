import os
from fake_useragent import UserAgent

# تنظیمات پایه
BASE_URL = "https://limonware.com"
PRODUCTS_URL = "https://limonware.com/product/"

# سلکتورهای CSS (بر اساس ساختار فعلی سایت لیمون)
SELECTORS = {
    'product_list': '.product-item, .product-card, .col-lg-3, .col-md-4, .product-wrapper',
    'title': '.product-title a, .product-name a, .entry-title a, h2 a',
    'price': '.price, .product-price, .amount, .woocommerce-Price-amount',
    'image': '.product-image img, .attachment-shop_catalog, .wp-post-image, .product-thumbnail img',
    'description': '.product-description, .woocommerce-product-details__short-description, .summary .description',
    'code': '.sku, .product-code, .sku_wrapper .sku, .product_meta .sku',
    'category': '.product-category, .posted_in a, .product_cat',
    'specs': '.woocommerce-product-attributes tr, .product-specs tr, .specifications tr',
    'spec_key': '.woocommerce-product-attributes__label, .spec-label, th',
    'spec_value': '.woocommerce-product-attributes__value, .spec-value, td',
}

# هدرهای درخواست
def get_headers():
    ua = UserAgent()
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'TE': 'Trailers',
    }

# تنظیمات خروجی
OUTPUT_FILE = 'data/products.json'
BRAND_NAME = 'لیمون'
MAX_PAGES = 50  # حداکثر تعداد صفحات برای اسکرپ

# تنظیمات timeout
TIMEOUT = 30
RETRY_COUNT = 3
RETRY_DELAY = 5
