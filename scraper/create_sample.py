import json
from datetime import datetime
from utils import ensure_data_dir, save_json

def create_sample_products():
    """ایجاد فایل نمونه برای تست"""
    products = [
        {
            "id": "lim_0001",
            "name": "ست ظروف فریزری ۱۲ تکه لیمون",
            "brand": "لیمون",
            "category": "ظروف فریزری",
            "code": "LIM-FRZ-001",
            "priceIRR": 2500000,
            "stock": 15,
            "isOriginal": True,
            "showPrice": True,
            "image": "https://picsum.photos/seed/limon1/400/400",
            "images": [
                "https://picsum.photos/seed/limon1_1/400/400",
                "https://picsum.photos/seed/limon1_2/400/400"
            ],
            "description": "ست ظروف فریزری ۱۲ تکه لیمون، مناسب برای نگهداری مواد غذایی در فریزر. دارای درب محکم و ضد نشت.",
            "specs": {
                "جنس": "پلیمر مرغوب",
                "تعداد قطعه": "۱۲",
                "قابلیت شستشو": "دارد",
                "مقاومت دمایی": "۲۰- تا ۱۲۰ درجه"
            },
            "source_url": "https://limonware.com/product/lim-frz-001",
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": "lim_0002",
            "name": "سرویس ۶ نفره لیمون",
            "brand": "لیمون",
            "category": "سرویس بهداشتی",
            "code": "LIM-SER-006",
            "priceIRR": 3800000,
            "stock": 8,
            "isOriginal": True,
            "showPrice": True,
            "image": "https://picsum.photos/seed/limon2/400/400",
            "images": [
                "https://picsum.photos/seed/limon2_1/400/400",
                "https://picsum.photos/seed/limon2_2/400/400"
            ],
            "description": "سرویس ۶ نفره لیمون، شامل بشقاب، کاسه و لیوان. طراحی مدرن و کیفیت بالا.",
            "specs": {
                "جنس": "چینی درجه یک",
                "تعداد قطعه": "۱۸",
                "قابلیت مایکروویو": "دارد"
            },
            "source_url": "https://limonware.com/product/lim-ser-006",
            "updated_at": datetime.now().isoformat()
        }
    ]
    ensure_data_dir()
    save_json(products, 'data/products.json')
    print(f"✅ {len(products)} محصول نمونه ایجاد شد.")

if __name__ == "__main__":
    create_sample_products()
