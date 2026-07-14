// netlify/functions/orders.js

const { readDB, writeDB, createResponse, ORDERS_FILE } = require('./utils');

exports.handler = async (event, context) => {
    if (event.httpMethod === 'OPTIONS') {
        return createResponse(200, {});
    }

    try {
        let orders = readDB(ORDERS_FILE);

        // --- GET: دریافت سفارشات ---
        if (event.httpMethod === 'GET') {
            // امکان فیلتر بر اساس status یا phone
            const { status, phone } = event.queryStringParameters || {};
            let filtered = orders;
            if (status) filtered = filtered.filter(o => o.status === status);
            if (phone) filtered = filtered.filter(o => o.phone === phone);
            
            // مرتب‌سازی بر اساس تاریخ (جدیدترین اول)
            filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
            return createResponse(200, filtered);
        }

        // --- POST: ثبت سفارش جدید ---
        else if (event.httpMethod === 'POST') {
            const newOrder = JSON.parse(event.body);
            
            // اعتبارسنجی
            if (!newOrder.customer || !newOrder.phone) {
                return createResponse(400, { error: 'نام مشتری و شماره تماس الزامی است' });
            }

            newOrder.id = `ord_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
            newOrder.status = newOrder.status || 'جدید';
            newOrder.createdAt = new Date().toISOString();
            newOrder.updatedAt = new Date().toISOString();
            newOrder.items = newOrder.items || [];
            newOrder.total = newOrder.total || 0;
            newOrder.shippingCost = newOrder.shippingCost || 0;
            newOrder.tax = newOrder.tax || 0;
            newOrder.couponDiscount = newOrder.couponDiscount || 0;

            orders.push(newOrder);
            if (!writeDB(ORDERS_FILE, orders)) {
                return createResponse(500, { error: 'خطا در ذخیره‌سازی سفارش' });
            }

            return createResponse(201, newOrder);
        }

        // --- PUT: به‌روزرسانی وضعیت سفارش ---
        else if (event.httpMethod === 'PUT') {
            const updatedData = JSON.parse(event.body);
            if (!updatedData.id) {
                return createResponse(400, { error: 'شناسه سفارش الزامی است' });
            }

            const index = orders.findIndex(o => o.id === updatedData.id);
            if (index === -1) {
                return createResponse(404, { error: 'سفارش یافت نشد' });
            }

            orders[index] = {
                ...orders[index],
                ...updatedData,
                updatedAt: new Date().toISOString(),
            };
            
            if (!writeDB(ORDERS_FILE, orders)) {
                return createResponse(500, { error: 'خطا در به‌روزرسانی' });
            }

            return createResponse(200, orders[index]);
        }

        // --- DELETE: حذف سفارش ---
        else if (event.httpMethod === 'DELETE') {
            const id = event.queryStringParameters?.id;
            if (!id) {
                return createResponse(400, { error: 'شناسه سفارش الزامی است' });
            }

            const newOrders = orders.filter(o => o.id !== id);
            if (newOrders.length === orders.length) {
                return createResponse(404, { error: 'سفارش یافت نشد' });
            }

            if (!writeDB(ORDERS_FILE, newOrders)) {
                return createResponse(500, { error: 'خطا در حذف' });
            }

            return createResponse(200, { message: 'سفارش حذف شد', id });
        }

        return createResponse(405, { error: 'متد مجاز نیست' });

    } catch (error) {
        console.error('خطا:', error);
        return createResponse(500, { error: 'خطای داخلی سرور' });
    }
};
