import json
import logging
from datetime import datetime

def setup_logging():
    """تنظیم سیستم لاگ"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def save_json(data, filename):
    """ذخیره داده‌ها در فایل JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filename):
    """بارگذاری داده‌ها از فایل JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def generate_product_id(index):
    """تولید شناسه یکتا برای محصول"""
    return f"lim_{index:04d}"

def clean_text(text):
    """پاکسازی متن از فضاهای اضافی"""
    if text:
        return ' '.join(text.strip().split())
    return ''

def extract_number(text):
    """استخراج عدد از متن (برای قیمت)"""
    import re
    if text:
        numbers = re.findall(r'\d+', text.replace(',', ''))
        if numbers:
            return int(''.join(numbers))
    return 0
