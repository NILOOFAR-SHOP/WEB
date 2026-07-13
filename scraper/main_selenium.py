from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from config import *
from utils import *
import time

logger = setup_logging()

def setup_driver():
    """راه‌اندازی مرورگر Chrome در حالت headless"""
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_with_selenium():
    """اسکرپ با استفاده از Selenium برای سایت‌های جاوااسکریپتی"""
    logger.info("🚀 شروع اسکرپ با Selenium...")
    driver = setup_driver()
    products = []
    
    try:
        driver.get(PRODUCTS_URL)
        logger.info(f"📄 صفحه {PRODUCTS_URL} بارگذاری شد")
        
        # انتظار برای بارگذاری محصولات
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.product-item, .product-card, .product'))
            )
        except TimeoutException:
            logger.warning("⚠️ زمان بارگذاری محصولات به پایان رسید. ادامه با داده‌های موجود...")
        
        # اسکرول برای بارگذاری تمام محصولات
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        while scroll_attempts < 5:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_attempts += 1
        
        # پیدا کردن محصولات
        product_elements = driver.find_elements(By.CSS_SELECTOR, '.product-item, .product-card, .product')
        logger.info(f"✅ {len(product_elements)} محصول یافت شد")
        
        for idx, elem in enumerate(product_elements[:50], 1):
            try:
                # استخراج اطلاعات
                title_elem = elem.find_element(By.CSS_SELECTOR, 'h2, h3, .product-title a, .product-name a')
                title = clean_text(title_elem.text)
                
                # لینک
                link = title_elem.get_attribute('href')
                if not link:
                    link_elem = elem.find_element(By.CSS_SELECTOR, 'a')
                    link = link_elem.get_attribute('href')
                
                # قیمت
                price_elem = elem.find_element(By.CSS_SELECTOR, '.price, .product-price, .amount')
                price_text = clean_text(price_elem.text)
                price = extract_price(price_text)
                
                # تصویر
                img_elem = elem.find_element(By.CSS_SELECTOR, 'img')
                image_url = img_elem.get_attribute('src') or img_elem.get_attribute('data-src') or ''
                
                # کد محصول
                code = ''
                try:
                    code_elem = elem.find_element(By.CSS_SELECTOR, '.sku, .product-code')
                    code = clean_text(code_elem.text)
                except NoSuchElementException:
                    pass
                
                # ساخت محصول
                product = {
                    'id': generate_product_id(idx),
                    'name': title,
                    'brand': BRAND_NAME,
                    'category': 'عمومی',
                    'code': code,
                    'priceIRR': price,
                    'stock': 10,
                    'isOriginal': True,
                    'showPrice': True,
                    'image': image_url,
                    'images': [image_url] if image_url else [],
                    'description': f'محصول {title} از برند {BRAND_NAME}',
                    'specs': {},
                    'source_url': link or '',
                    'updated_at': datetime.now().isoformat(),
                }
                
                products.append(product)
                logger.info(f"✅ محصول {idx}: {title} استخراج شد")
                
            except Exception as e:
                logger.error(f"❌ خطا در استخراج محصول {idx}: {e}")
                continue
        
        logger.info(f"🎯 {len(products)} محصول استخراج شد")
        
    except Exception as e:
        logger.error(f"❌ خطای کلی در Selenium: {e}")
    finally:
        driver.quit()
    
    return products

def main():
    """تابع اصلی"""
    logger.info("🚀 شروع اسکرپ با Selenium...")
    
    products = scrape_with_selenium()
    
    if products:
        save_json(products, OUTPUT_FILE)
        logger.info(f"✅ داده‌ها در فایل {OUTPUT_FILE} ذخیره شد.")
        logger.info(f"📊 {len(products)} محصول ذخیره شد.")
    else:
        logger.error("❌ هیچ محصولی استخراج نشد!")
        exit(1)

if __name__ == "__main__":
    main()
