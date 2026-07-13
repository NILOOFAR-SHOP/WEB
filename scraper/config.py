# تنظیمات اسکرپر
BASE_URL = "https://limonware.com"
PRODUCTS_URL = "https://limonware.com/product/"  # آدرس اصلی محصولات

# سلکتورهای CSS (بر اساس ساختار سایت لیمون)
SELECTORS = {
    'product_list': '.product-item',          # لیست محصولات
    'title': '.product-title a',              # عنوان
    'price': '.price',                        # قیمت
    'image': '.product-image img',            # تصویر
    'description': '.product-description',    # توضیحات
    'code': '.product-code',                  # کد محصول
    'category': '.product-category',          # دسته‌بندی
    'specs': '.product-specs tr',             # مشخصات فنی (جدول)
}

# هدرهای درخواست
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'fa-IR,fa;q=0.9,en;q=0.8',
}

# تنظیمات خروجی
OUTPUT_FILE = 'data/products.json'
BRAND_NAME = 'لیمون'
