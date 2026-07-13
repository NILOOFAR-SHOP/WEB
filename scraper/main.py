import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from config import *
from utils import *

logger = setup_logging()

def fetch_page(url):
    """دریافت محتوای صفحه با مدیریت خطا"""
    try:
        ua = UserAgent()
        headers = HEADERS.copy()
        headers['User-Agent'] = ua.random
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        logger.error(f"خطا در دریافت صفحه {url}: {e}")
        return None

def parse_product_detail(product_url):
    """استخراج اطلاعات کامل یک محصول از صفحه جزئیات"""
    html = fetch_page(product_url)
    if not html:
        return {}
    
    soup = BeautifulSoup(html, 'lxml')
    
    # استخراج مشخصات فنی
    specs = {}
    spec_rows = soup.select(SELECTORS['specs'])
    for row in spec_rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            key = clean_text(cells[0].text)
            value = clean_text(cells[1].text)
            if key and value:
                specs[key] = value
    
    # استخراج توضیحات کامل
    desc_elem = soup.select_one(SELECTORS['description'])
    description = clean_text(desc_elem.text) if desc_elem else ''
    
    # استخراج کد محصول
    code_elem = soup.select_one(SELECTORS['code'])
    product_code = clean_text(code_elem.text) if code_elem else ''
    
    return {
        'specs': specs,
        'description': description,
        'code': product_code,
    }

def scrape_products():
    """اسکرپ اصلی - استخراج لیست محصولات"""
    logger.info("شروع اسکرپ محصولات لیمون...")
    
    # دریافت صفحه اصلی محصولات
    html = fetch_page(PRODUCTS_URL)
    if not html:
        logger.error("خطا در دریافت صفحه اصلی")
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    product_items = soup.select(SELECTORS['product_list'])
    
    logger.info(f"تعداد {len(product_items)} محصول یافت شد")
    
    products = []
    
    for idx, item in enumerate(product_items, 1):
        try:
            # استخراج اطلاعات اولیه
            title_elem = item.select_one(SELECTORS['title'])
            title = clean_text(title_elem.text) if title_elem else f"محصول {idx}"
            
            # لینک جزئیات
            link = title_elem.get('href') if title_elem else ''
            if link and not link.startswith('http'):
                link = BASE_URL + link
            
            # قیمت
            price_elem = item.select_one(SELECTORS['price'])
            price_text = clean_text(price_elem.text) if price_elem else ''
            price = extract_number(price_text)
            
            # تصویر
            img_elem = item.select_one(SELECTORS['image'])
            image_url = img_elem.get('src') if img_elem else ''
            if image_url and not image_url.startswith('http'):
                image_url = BASE_URL + image_url
            
            # دسته‌بندی
            cat_elem = item.select_one(SELECTORS['category'])
            category = clean_text(cat_elem.text) if cat_elem else 'عمومی'
            
            # دریافت اطلاعات کامل از صفحه جزئیات
            detail_data = {}
            if link:
                detail_data = parse_product_detail(link)
            
            # ساخت شناسه یکتا
            product_id = generate_product_id(idx)
            
            # ساخت شیء محصول
            product = {
                'id': product_id,
                'name': title,
                'brand': BRAND_NAME,
                'category': category,
                'code': detail_data.get('code', ''),
                'priceIRR': price,
                'stock': 10,  # مقدار پیش‌فرض
                'isOriginal': True,
                'showPrice': True,
                'image': image_url,
                'images': [image_url] if image_url else [],
                'description': detail_data.get('description', f'محصول {title} از برند {BRAND_NAME}'),
                'specs': detail_data.get('specs', {}),
                'source_url': link,
                'updated_at': datetime.now().isoformat(),
                'soldCount': 0,
                'viewCount': 0,
            }
            
            products.append(product)
            logger.info(f"✅ محصول {idx}: {title} استخراج شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در استخراج محصول {idx}: {e}")
            continue
    
    logger.info(f"🎯 استخراج کامل شد. {len(products)} محصول دریافت شد.")
    return products

def main():
    """تابع اصلی"""
    logger.info("🚀 شروع اسکرپ محصولات لیمون ایران...")
    
    products = scrape_products()
    
    if products:
        # ذخیره در فایل JSON
        save_json(products, OUTPUT_FILE)
        logger.info(f"✅ داده‌ها در فایل {OUTPUT_FILE} ذخیره شد.")
        
        # نمایش آمار
        total = len(products)
        has_price = sum(1 for p in products if p['priceIRR'] > 0)
        has_image = sum(1 for p in products if p['image'])
        logger.info(f"📊 آمار: {total} محصول, {has_price} دارای قیمت, {has_image} دارای تصویر")
    else:
        logger.error("❌ هیچ محصولی استخراج نشد!")

if __name__ == "__main__":
    main()
