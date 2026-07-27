#!/usr/bin/env python3
"""
اسکرپر حرفه‌ای محصولات لیمون
استخراج نام، کد، تصاویر و قیمت از limonware.com
"""
import json, os, sys, time, random, re, hashlib
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urljoin, unquote

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
BASE_URL = 'https://limonware.com'
ua = UserAgent()

PRODUCT_URLS = [
    '/product/%d8%a8%d8%a7%d9%86%da%a9%d9%87-%d8%b4%db%8c%d8%a7%d8%b1%d8%af%d8%a7%d8%b1-%d8%af%d8%b1%d8%a8-%da%86%d9%88%d8%a8%db%8c-900-%d9%85%db%8c%d9%84%db%8c-%d9%84%db%8c%d8%aa%d8%b1/',
    '/product/%d8%a8%d8%a7%d9%86%da%a9%d9%87-%d8%b4%db%8c%d8%b4%d9%87-%d8%a7%db%8c-260-%d9%85%db%8c%d9%84%db%8c-%d9%84%db%8c%d8%aa%d8%b1/',
    '/product/%d8%b3%d8%a8%d8%af-%d9%86%d8%a7%d9%86-%d9%85%d8%b1%d8%a8%d8%b9-%d9%81%d9%84%d8%b2%db%8c-2/',
    '/product/%d8%b3%d8%b7%d9%84-%d8%b4%db%8c%d8%a7%d8%b1%d8%af%d8%a7%d8%b1-%d8%af%d8%b1%d8%a8-%da%86%d9%88%d8%a8%db%8c-12-%d9%84%db%8c%d8%aa%d8%b1/',
    '/product/%d8%b3%d8%b7%d9%84-%d8%b4%db%8c%d8%a7%d8%b1%d8%af%d8%a7%d8%b1-%d8%af%d8%b1%d8%a8-%da%86%d9%88%d8%a8%db%8c-3-%d9%84%db%8c%d8%aa%d8%b1/',
    '/product/%d8%b3%d8%b7%d9%84-%d8%b4%db%8c%d8%a7%d8%b1%d8%af%d8%a7%d8%b1-%d8%af%d8%b1%d8%a8-%da%86%d9%88%d8%a8%db%8c-9-%d9%84%db%8c%d8%aa%d8%b1/',
    '/product/%d9%84%db%8c%d9%88%d8%a7%d9%86-%d8%b4%db%8c%d8%b4%d9%87-%d8%a7%db%8c-410-%d8%b3%db%8c-%d8%b3%db%8c/',
    '/product/%da%a9%d8%a7%d9%86%d8%aa%d8%b1-%d9%86%da%af%d9%87%d8%af%d8%a7%d8%b1%d9%86%d8%af%d9%87-%d8%a7%da%a9%d8%b1%d9%88%d9%84%db%8c%da%a9/',
]

def extract_product_name(name_str):
    """خالص‌سازی نام محصول از تگ title"""
    parts = re.split(r'[-–—]\s*', name_str)
    if len(parts) > 1:
        return parts[0].strip()
    return name_str.strip()

def extract_volume(name):
    for pattern, unit in [
        (r'(\d+)\s*میلی\s*لیتر', 'ml'),
        (r'(\d+)\s*لیتر', 'litre'),
        (r'(\d+)\s*سی\s*سی', 'cc'),
        (r'(\d+)\s*نفره', 'person'),
        (r'(\d+)\s*تکه', 'piece'),
    ]:
        m = re.search(pattern, name, re.IGNORECASE)
        if m:
            return int(m.group(1)), unit
    return None, None

def guess_category(name):
    keywords = [
        ('بانکه', 'بانکه و شیشه'),
        ('بطری', 'بطری'),
        ('ماکروویو', 'ظروف ماکروویو'),
        ('سطل', 'سطل و ظروف بزرگ'),
        ('سبد', 'سبد'),
        ('لیوان', 'لیوان'),
        ('کانتر', 'نظم دهنده'),
        ('نظم', 'نظم دهنده'),
        ('جا ', 'نظم دهنده'),
        ('جهیزیه', 'سرویس جهیزیه'),
        ('بهداشتی', 'سرویس بهداشتی'),
        ('فریزری', 'ظروف فریزری'),
        ('مسافرتی', 'سرویس مسافرتی'),
        ('ظروف شیشه', 'ظروف شیشه ای'),
        ('قابلمه', 'لوازم آشپزخانه'),
        ('قاشق', 'لوازم آشپزخانه'),
        ('کریستال', 'ظروف شیشه ای'),
    ]
    for kw, cat in keywords:
        if kw in name:
            return cat
    return 'سایر محصولات'

def generate_code(name, category, idx):
    prefixes = {
        'بانکه و شیشه': 'BG', 'بطری': 'BT', 'ظروف ماکروویو': 'MW',
        'سطل و ظروف بزرگ': 'SL', 'سبد': 'SD', 'لیوان': 'LV',
        'نظم دهنده': 'NZ', 'سرویس جهیزیه': 'JZ', 'سرویس بهداشتی': 'BH',
        'ظروف فریزری': 'FZ', 'ظروف شیشه ای': 'GL', 'سرویس مسافرتی': 'MS',
        'لوازم آشپزخانه': 'AK', 'طرح بافت': 'BF', 'طرح روستیک': 'RS',
    }
    prefix = prefixes.get(category, 'LM')
    vol, unit = extract_volume(name)
    if vol:
        return f'LM-{prefix}-{vol:03d}'
    return f'LM-{prefix}-{idx+1:03d}'

def download_image(img_url):
    """دانلود تصویر و ذخیره"""
    try:
        if not img_url.startswith('http'):
            img_url = urljoin(BASE_URL, img_url)
        ext = os.path.splitext(img_url.split('?')[0])[1].lower()
        if ext not in ('.jpg', '.jpeg', '.png', '.webp'):
            ext = '.webp'
        url_hash = hashlib.md5(img_url.encode()).hexdigest()[:10]
        filename = f'img_{url_hash}{ext}'
        filepath = os.path.join(UPLOADS_DIR, filename)
        if os.path.exists(filepath):
            return filename
        headers = {'User-Agent': ua.random, 'Referer': BASE_URL}
        resp = requests.get(img_url, headers=headers, timeout=30)
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            print(f'  Downloaded: {filename} ({len(resp.content)//1024}KB)')
            return filename
    except Exception as e:
        print(f'  Download error: {e}')
    return None

def scrape_product(product_url):
    """اسکرپ یک صفحه محصول"""
    url = urljoin(BASE_URL, product_url)
    print(f'\nScraping: {url}')
    headers = {'User-Agent': ua.random}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f'  HTTP {resp.status_code}')
            return None
    except Exception as e:
        print(f'  Error: {e}')
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Extract name from <title>
    title = soup.select_one('title')
    name = title.get_text(strip=True) if title else None
    if name:
        name = extract_product_name(name)

    # Extract price
    price_irr = 0
    price_el = soup.select_one('.price .woocommerce-Price-amount, .price bdi, ins .woocommerce-Price-amount')
    if not price_el:
        price_el = soup.select_one('.price')
    if price_el:
        price_text = price_el.get_text(strip=True)
        price_match = re.findall(r'[\d,]+', price_text.replace(',', ''))
        if price_match:
            price_irr = int(price_match[0]) * 10

    # Extract SKU
    code = ''
    sku_el = soup.select_one('.sku')
    if sku_el:
        code = sku_el.get_text(strip=True)

    # Extract description
    desc = ''
    desc_el = soup.select_one('.woocommerce-product-details__short-description, [class*="short-description"]')
    if desc_el:
        desc = desc_el.get_text(strip=True)[:300]

    # Extract images
    images = []
    all_imgs = soup.select('img[src*="wp-content/uploads"]')
    for img in all_imgs:
        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
        if src and 'logo' not in src.lower() and 'icon' not in src.lower():
            if not src.startswith('http'):
                src = urljoin(BASE_URL, src)
            if src not in [i['url'] for i in images]:
                # Filter out small/thumb images
                if '300x' not in src and '150x' not in src and '100x' not in src:
                    images.append({'url': src, 'priority': 'main'})

    # Category
    category = guess_category(name)

    # Generate code if not found
    if not code:
        code = generate_code(name, category, 0)

    # Download images
    local_images = []
    for img in images[:5]:
        fname = download_image(img['url'])
        if fname:
            local_images.append(f'/uploads/{fname}')

    print(f'  Name: {name}')
    print(f'  Code: {code}')
    print(f'  Price: {price_irr}')
    print(f'  Images: {len(local_images)}')
    print(f'  Category: {category}')

    return {
        'name': name,
        'brand': 'لیمون',
        'category': category,
        'code': code,
        'priceIRR': price_irr if price_irr else 0,
        'profitPercent': 200,
        'stock': random.randint(5, 40),
        'showPrice': price_irr > 0,
        'inquiryEnabled': price_irr == 0,
        'description': desc or f'{name} - محصول با کیفیت لیمون',
        'longDescription': f'{desc or name} | کیفیت تضمینی لیمون | ارسال سریع | بسته‌بندی ایمن',
        'images': local_images if local_images else [f'https://picsum.photos/seed/{hashlib.md5(name.encode()).hexdigest()[:8]}_1/400/400'],
        'image': local_images[0] if local_images else f'https://picsum.photos/seed/{hashlib.md5(name.encode()).hexdigest()[:8]}_1/400/400',
        'specs': {'جنس': 'شیشه بوروسیلیکات' if 'شیشه' in name else 'پلاستیک با کیفیت', 'ابعاد': 'استاندارد'},
        'guarantee': True,
        'tag': None,
        'soldCount': random.randint(0, 50),
        'viewCount': random.randint(20, 300),
        'createdAt': '2025-01-01T00:00:00.000Z'
    }

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    print('='*60)
    print('  Limon Products Scraper - Professional Edition')
    print('='*60)

    products = []
    for i, url in enumerate(PRODUCT_URLS):
        product = scrape_product(url)
        if product:
            product['id'] = f'prod_{i+1}'
            products.append(product)
        time.sleep(random.uniform(1.5, 3.0))

    if products:
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f'\nSaved {len(products)} products to {PRODUCTS_FILE}')

        # Print summary
        print('\nSummary:')
        for p in products:
            print(f'  [{p["code"]}] {p["name"][:60]} | {p["category"]}')
    else:
        print('\nNo products scraped!')
        sys.exit(1)

if __name__ == '__main__':
    main()
