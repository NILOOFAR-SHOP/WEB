import requests
import time
from bs4 import BeautifulSoup
from config import *
from utils import *

logger = setup_logging()

def fetch_page(url, retry=RETRY_COUNT):
    """دریافت محتوای صفحه با مدیریت خطا و تلاش مجدد"""
    for attempt in range(retry):
        try:
            headers = get_headers()
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            logger.warning(f"تلاش {attempt+1}/{retry} برای {url} ناموفق: {e}")
            if attempt < retry - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                logger.error(f"خطا در دریافت {url}: {e}")
                return None
    return None

def parse_product_detail(product_url):
    """استخراج اطلاعات کامل یک محصول از صفحه جزئیات"""
    html = fetch_page(product_url)
    if not html:
        return {}
    
    soup = BeautifulSoup(html, 'lxml')
    
    # استخراج مشخصات فنی
    specs = get_product_attributes(soup, SELECTORS)
    
    # استخراج توضیحات
    desc_elem = soup.select_one(SELECTORS['description'])
    description = clean_text(desc_elem.text) if desc_elem else ''
    
    # استخراج کد محصول
    code_elem = soup.select_one(SELECTORS['code'])
    product_code = clean_text(code_elem.text) if code_elem else ''
    
    # استخراج تصاویر اضافی (گالری)
    images = []
    gallery_imgs = soup.select('.woocommerce-product-gallery img, .product-gallery img')
    for img in gallery_imgs:
        src = img.get('src') or img.get('data-src')
        if src:
            if not src.startswith('http'):
                src = BASE_URL + src
            images.append(src)
    
    return {
        'specs': specs,
        'description': description,
        'code': product_code,
        'gallery_images': images[:5],  # حداکثر ۵ تصویر
    }

def scrape_products():
    """اسکرپ اصلی - استخراج لیست محصولات"""
    logger.info("🚀 شروع اسکرپ محصولات لیمون...")
    
    # دریافت صفحه اصلی محصولات
    html = fetch_page(PRODUCTS_URL)
    if not html:
        logger.error("❌ خطا در دریافت صفحه اصلی")
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    
    # پیدا کردن محصولات با چندین سلکتور مختلف
    product_items = []
    for selector in SELECTORS['product_list'].split(', '):
        items = soup.select(selector)
        if items:
            product_items = items
            logger.info(f"✅ {len(items)} محصول با سلکتور '{selector}' یافت شد")
            break
    
    if not product_items:
        logger.warning("⚠️ هیچ محصولی یافت نشد. ساختار سایت ممکن است تغییر کرده باشد.")
        return []
    
    products = []
    
    for idx, item in enumerate(product_items[:100], 1):  # حداکثر ۱۰۰ محصول
        try:
            # استخراج عنوان و لینک
            title_elem = item.select_one(SELECTORS['title'])
            if not title_elem:
                continue
                
            title = clean_text(title_elem.text)
            link = title_elem.get('href')
            if link and not link.startswith('http'):
                link = BASE_URL + link
            
            # استخراج قیمت
            price_elem = item.select_one(SELECTORS['price'])
            price_text = clean_text(price_elem.text) if price_elem else ''
            price = extract_price(price_text)
            
            # استخراج تصویر
            img_elem = item.select_one(SELECTORS['image'])
            image_url = ''
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src') or ''
                if image_url and not image_url.startswith('http'):
                    image_url = BASE_URL + image_url
            
            # استخراج دسته‌بندی
            cat_elem = item.select_one(SELECTORS['category'])
            category = clean_text(cat_elem.text) if cat_elem else 'عمومی'
            
            # استخراج کد محصول (اگر در صفحه اصلی موجود باشد)
            code_elem = item.select_one(SELECTORS['code'])
            code = clean_text(code_elem.text) if code_elem else ''
            
            # دریافت اطلاعات کامل از صفحه جزئیات
            detail_data = {}
            if link:
                detail_data = parse_product_detail(link)
                time.sleep(0.5)  # تاخیر برای جلوگیری از blocking
            
            # ترکیب اطلاعات
            product = {
                'id': generate_product_id(idx),
                'name': title,
                'brand': BRAND_NAME,
                'category': category,
                'code': code or detail_data.get('code', ''),
                'priceIRR': price,
                'stock': 10,
                'isOriginal': True,
                'showPrice': True,
                'image': image_url,
                'images': [image_url] + detail_data.get('gallery_images', []) if image_url else detail_data.get('gallery_images', []),
                'description': detail_data.get('description', f'محصول {title} از برند {BRAND_NAME}'),
                'specs': detail_data.get('specs', {}),
                'source_url': link,
                'updated_at': datetime.now().isoformat(),
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
    logger.info("🚀 شروع اسکرپ خودکار محصولات لیمون...")
    
    products = scrape_products()
    
    if products:
        # ذخیره در فایل JSON
        save_json(products, OUTPUT_FILE)
        logger.info(f"✅ داده‌ها در فایل {OUTPUT_FILE} ذخیره شد.")
        
        # نمایش آمار
        total = len(products)
        has_price = sum(1 for p in products if p['priceIRR'] > 0)
        has_image = sum(1 for p in products if p['image'])
        has_code = sum(1 for p in products if p['code'])
        logger.info(f"📊 آمار: {total} محصول, {has_price} دارای قیمت, {has_image} دارای تصویر, {has_code} دارای کد")
    else:
        logger.error("❌ هیچ محصولی استخراج نشد!")
        exit(1)

if __name__ == "__main__":
    main()
