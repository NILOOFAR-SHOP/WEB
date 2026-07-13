import json
import logging
import re
from datetime import datetime
from pathlib import Path

def setup_logging():
    """تنظیم سیستم لاگ‌گیری"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('scraper.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def ensure_data_dir():
    """ایجاد پوشه data در صورت عدم وجود"""
    Path('data').mkdir(exist_ok=True)

def save_json(data, filename):
    """ذخیره داده‌ها در فایل JSON با فرمت زیبا"""
    ensure_data_dir()
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=False)

def load_json(filename):
    """بارگذاری داده‌ها از فایل JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def generate_product_id(index, prefix='lim'):
    """تولید شناسه یکتا برای محصول"""
    return f"{prefix}_{str(index).zfill(4)}"

def clean_text(text):
    """پاکسازی متن از فضاهای اضافی و کاراکترهای خاص"""
    if not text:
        return ''
    # حذف فضاهای اضافی
    text = ' '.join(text.strip().split())
    # حذف کاراکترهای کنترل
    text = re.sub(r'[\x00-\x1f\x7f]', '', text)
    return text

def extract_number(text):
    """استخراج عدد از متن (برای قیمت و وزن)"""
    if not text:
        return 0
    # حذف کاما و فاصله
    cleaned = re.sub(r'[,\s]', '', text)
    # یافتن اعداد
    numbers = re.findall(r'\d+', cleaned)
    if numbers:
        return int(''.join(numbers))
    return 0

def extract_price(text):
    """استخراج قیمت از متن (پشتیبانی از تومان و ریال)"""
    if not text:
        return 0
    # حذف کاراکترهای غیرعددی به جز کاما و فاصله
    cleaned = re.sub(r'[^0-9,\s]', '', text)
    # تبدیل به عدد
    return extract_number(cleaned)

def format_product_for_export(product):
    """قالب‌بندی محصول برای خروجی JSON"""
    return {
        'id': product.get('id', ''),
        'name': product.get('name', ''),
        'brand': product.get('brand', 'لیمون'),
        'category': product.get('category', 'عمومی'),
        'code': product.get('code', ''),
        'priceIRR': product.get('priceIRR', 0),
        'stock': product.get('stock', 10),
        'isOriginal': product.get('isOriginal', True),
        'showPrice': product.get('showPrice', True),
        'image': product.get('image', ''),
        'images': product.get('images', []),
        'description': product.get('description', ''),
        'specs': product.get('specs', {}),
        'guarantee': product.get('guarantee', True),
        'tag': product.get('tag', None),
        'soldCount': product.get('soldCount', 0),
        'viewCount': product.get('viewCount', 0),
        'source_url': product.get('source_url', ''),
        'updated_at': datetime.now().isoformat(),
    }

def get_product_attributes(soup, selectors):
    """استخراج مشخصات فنی محصول از جدول"""
    specs = {}
    try:
        rows = soup.select(selectors.get('specs', ''))
        for row in rows:
            key_elem = row.select_one(selectors.get('spec_key', 'th'))
            value_elem = row.select_one(selectors.get('spec_value', 'td'))
            if key_elem and value_elem:
                key = clean_text(key_elem.text)
                value = clean_text(value_elem.text)
                if key and value:
                    specs[key] = value
    except Exception:
        pass
    return specs
