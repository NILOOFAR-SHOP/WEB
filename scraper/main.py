import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import *
from utils import *
import requests
from bs4 import BeautifulSoup
import time

logger = setup_logging()

def fetch_page(url, retry=RETRY_COUNT):
    """دریافت محتوای صفحه با مدیریت خطا"""
    for attempt in range(retry):
        try:
            headers = get_headers()
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            logger.warning(f"تلاش {attempt+1}/{retry} ناموفق: {e}")
            if attempt < retry - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                logger.error(f"❌ خطا در دریافت {url}: {e}")
                return None
    return None

def parse_product_detail(product_url):
    """استخراج اطلاعات کامل محصول"""
    html = fetch_page(product_url)
    if not html:
        return {}
    
    soup = BeautifulSoup(html, 'lxml')
    specs = {}
    description = ''
    code = ''
    images = []
    
    # تلاش با سلکتورهای مختلف
    try:
        desc_elem = soup.select_one('.product-description, .woocommerce-product-details__short-description, .summary .description')
        if desc_elem:
            description = clean_text(desc_elem.text)
    except:
        pass
    
    try:
        code_elem = soup.select_one('.sku, .product-code, .sku_wrapper .sku')
        if code_elem:
            code = clean_text(code_elem.text)
    except:
        pass
    
    try:
        # استخراج مشخصات فنی
        spec_rows = soup.select('.woocommerce-product-attributes tr, .product-specs tr, .specifications tr')
        for row in spec_rows:
            key_elem = row.select_one('th, .woocommerce-product-attributes__label, .spec-label')
            value_elem = row.select_one('td, .woocommerce-product-attributes__value, .spec-value')
            if key_elem and value_elem:
                key = clean_text(key_elem.text)
                value = clean_text(value_elem.text)
                if key and value:
                    specs[key] = value
    except:
        pass
    
    # استخراج تصاویر گالری
    try:
        gallery_imgs = soup.select('.woocommerce-product-gallery img, .product-gallery img')
        for img in gallery_imgs[:5]:
            src = img.get('src') or img.get('data-src')
            if src:
                if not src.startswith('http'):
                    src = BASE_URL + src
                images.append(src)
    except:
        pass
    
    return {
        'specs': specs,
        'description': description,
        'code': code,
        'gallery_images': images,
    }

def scrape_products():
    """اسکرپ اصلی"""
    logger.info("🚀 شروع اسکرپ...")
    
    html = fetch_page(PRODUCTS_URL)
    if not html:
        logger.warning("⚠️ صفحه اصلی دریافت نشد. ایجاد فایل نمونه...")
        # ایجاد فایل نمونه
        from create_sample import create_sample_products
        create_sample_products()
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    
    # پیدا کردن محصولات
    product_items = []
    for selector in ['.product-item', '.product-card', '.product', '.col-lg-3', '.col-md-4']:
        items = soup.select(selector)
        if items:
            product_items = items
            logger.info(f"✅ {len(items)} محصول با سلکتور '{selector}' یافت شد")
            break
    
    if not product_items:
        logger.warning("⚠️ هیچ محصولی یافت نشد. ایجاد فایل نمونه...")
        from create_sample import create_sample_products
        create_sample_products()
        return []
    
    products = []
    for idx, item in enumerate(product_items[:100], 1):
        try:
            # عنوان
            title_elem = item.select_one('h2, h3, .product-title a, .product-name a, .entry-title a')
            if not title_elem:
                continue
            title = clean_text(title_elem.text)
            
            # لینک
            link = title_elem.get('href')
            if not link:
                link_elem = item.select_one('a')
                if link_elem:
                    link = link_elem.get('href')
            if link and not link.startswith('http'):
                link = BASE_URL + link
            
            # قیمت
            price_elem = item.select_one('.price, .product-price, .amount, .woocommerce-Price-amount')
            price_text = clean_text(price_elem.text) if price_elem else ''
            price = extract_price(price_text)
            
            # تصویر
            img_elem = item.select_one('img')
            image_url = ''
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src') or ''
                if image_url and not image_url.startswith('http'):
                    image_url = BASE_URL + image_url
            
            # کد
            code_elem = item.select_one('.sku, .product-code')
            code = clean_text(code_elem.text) if code_elem else ''
            
            # دریافت جزئیات
            detail_data = {}
            if link:
                detail_data = parse_product_detail(link)
                time.sleep(0.3)
            
            product = {
                'id': generate_product_id(idx),
                'name': title,
                'brand': BRAND_NAME,
                'category': 'عمومی',
                'code': code or detail_data.get('code', ''),
                'priceIRR': price,
                'stock': 10,
                'isOriginal': True,
                'showPrice': True,
                'image': image_url,
                'images': [image_url] + detail_data.get('gallery_images', []) if image_url else detail_data.get('gallery_images', []),
                'description': detail_data.get('description', f'محصول {title} از برند {BRAND_NAME}'),
                'specs': detail_data.get('specs', {}),
                'source_url': link or '',
                'updated_at': datetime.now().isoformat(),
            }
            products.append(product)
            logger.info(f"✅ محصول {idx}: {title}")
            
        except Exception as e:
            logger.error(f"❌ خطا در محصول {idx}: {e}")
            continue
    
    logger.info(f"🎯 {len(products)} محصول استخراج شد")
    return products

def main():
    logger.info("🚀 شروع اسکرپ...")
    products = scrape_products()
    
    if products:
        save_json(products, OUTPUT_FILE)
        logger.info(f"✅ {len(products)} محصول در {OUTPUT_FILE} ذخیره شد.")
    else:
        # حتی اگر محصولی نباشد، یک فایل نمونه ایجاد می‌کنیم
        from create_sample import create_sample_products
        create_sample_products()
        logger.info("⚠️ فایل نمونه ایجاد شد.")

if __name__ == "__main__":
    main()
