// netlify/functions/products.js

const { readDB, writeDB, createResponse, PRODUCTS_FILE } = require('./utils');

exports.handler = async (event, context) => {
    // پاسخ به درخواست OPTIONS (برای CORS)
    if (event.httpMethod === 'OPTIONS') {
        return createResponse(200, {});
    }

    try {
        // خواندن دیتابیس
        let products = readDB(PRODUCTS_FILE);

        // --- GET: دریافت همه محصولات ---
        if (event.httpMethod === 'GET') {
            // امکان فیلتر بر اساس برند یا دسته‌بندی از query string
            const { brand, category } = event.queryStringParameters || {};
            let filtered = products;
            if (brand) filtered = filtered.filter(p => p.brand === brand);
            if (category) filtered = filtered.filter(p => p.category === category);
            return createResponse(200, filtered);
        }

        // --- POST: افزودن محصول جدید ---
        else if (event.httpMethod === 'POST') {
            const newProduct = JSON.parse(event.body);
            
            // اعتبارسنجی
            if (!newProduct.name || !newProduct.brand) {
                return createResponse(400, { error: 'نام و برند الزامی است' });
            }

            // تولید ID یکتا
            newProduct.id = newProduct.id || `prod_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
            
            // تنظیم مقادیر پیش‌فرض
            newProduct.createdAt = newProduct.createdAt || new Date().toISOString();
            newProduct.updatedAt = new Date().toISOString();
            newProduct.soldCount = newProduct.soldCount || 0;
            newProduct.viewCount = newProduct.viewCount || 0;
            newProduct.stock = newProduct.stock || 0;
            newProduct.priceIRR = newProduct.priceIRR || 0;
            newProduct.profitPercent = newProduct.profitPercent || 200;
            newProduct.images = newProduct.images || [];
            newProduct.specs = newProduct.specs || {};

            // اضافه کردن به آرایه
            products.push(newProduct);
            
            // ذخیره در فایل
            if (!writeDB(PRODUCTS_FILE, products)) {
                return createResponse(500, { error: 'خطا در ذخیره‌سازی' });
            }

            return createResponse(201, newProduct);
        }

        // --- PUT: به‌روزرسانی محصول ---
        else if (event.httpMethod === 'PUT') {
            const updatedData = JSON.parse(event.body);
            if (!updatedData.id) {
                return createResponse(400, { error: 'شناسه محصول الزامی است' });
            }

            const index = products.findIndex(p => p.id === updatedData.id);
            if (index === -1) {
                return createResponse(404, { error: 'محصول یافت نشد' });
            }

            // به‌روزرسانی (بدون تغییر id و createdAt)
            const oldProduct = products[index];
            products[index] = {
                ...oldProduct,
                ...updatedData,
                id: oldProduct.id,
                createdAt: oldProduct.createdAt,
                updatedAt: new Date().toISOString(),
            };
            
            if (!writeDB(PRODUCTS_FILE, products)) {
                return createResponse(500, { error: 'خطا در ذخیره‌سازی' });
            }

            return createResponse(200, products[index]);
        }

        // --- DELETE: حذف محصول ---
        else if (event.httpMethod === 'DELETE') {
            const id = event.queryStringParameters?.id;
            if (!id) {
                return createResponse(400, { error: 'شناسه محصول الزامی است' });
            }

            const newProducts = products.filter(p => p.id !== id);
            if (newProducts.length === products.length) {
                return createResponse(404, { error: 'محصول یافت نشد' });
            }

            if (!writeDB(PRODUCTS_FILE, newProducts)) {
                return createResponse(500, { error: 'خطا در حذف' });
            }

            return createResponse(200, { message: 'محصول حذف شد', id });
        }

        // متد پشتیبانی نشده
        return createResponse(405, { error: 'متد مجاز نیست' });

    } catch (error) {
        console.error('خطا:', error);
        return createResponse(500, { error: 'خطای داخلی سرور', details: error.message });
    }
};
