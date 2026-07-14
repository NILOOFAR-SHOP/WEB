// netlify/functions/inquiries.js

const { readDB, writeDB, createResponse, INQUIRIES_FILE } = require('./utils');

exports.handler = async (event, context) => {
    if (event.httpMethod === 'OPTIONS') {
        return createResponse(200, {});
    }

    try {
        let inquiries = readDB(INQUIRIES_FILE);

        // --- GET: دریافت استعلام‌ها ---
        if (event.httpMethod === 'GET') {
            const { status } = event.queryStringParameters || {};
            let filtered = inquiries;
            if (status) filtered = filtered.filter(q => q.status === status);
            filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
            return createResponse(200, filtered);
        }

        // --- POST: ثبت استعلام جدید ---
        else if (event.httpMethod === 'POST') {
            const newInquiry = JSON.parse(event.body);
            
            if (!newInquiry.name || !newInquiry.phone || !newInquiry.productName) {
                return createResponse(400, { error: 'نام، شماره تماس و نام محصول الزامی است' });
            }

            newInquiry.id = `inq_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
            newInquiry.status = newInquiry.status || 'جدید';
            newInquiry.createdAt = new Date().toISOString();
            newInquiry.updatedAt = new Date().toISOString();

            inquiries.push(newInquiry);
            if (!writeDB(INQUIRIES_FILE, inquiries)) {
                return createResponse(500, { error: 'خطا در ذخیره‌سازی استعلام' });
            }

            return createResponse(201, newInquiry);
        }

        // --- PUT: به‌روزرسانی وضعیت استعلام ---
        else if (event.httpMethod === 'PUT') {
            const updatedData = JSON.parse(event.body);
            if (!updatedData.id) {
                return createResponse(400, { error: 'شناسه استعلام الزامی است' });
            }

            const index = inquiries.findIndex(q => q.id === updatedData.id);
            if (index === -1) {
                return createResponse(404, { error: 'استعلام یافت نشد' });
            }

            inquiries[index] = {
                ...inquiries[index],
                ...updatedData,
                updatedAt: new Date().toISOString(),
            };
            
            if (!writeDB(INQUIRIES_FILE, inquiries)) {
                return createResponse(500, { error: 'خطا در به‌روزرسانی' });
            }

            return createResponse(200, inquiries[index]);
        }

        // --- DELETE: حذف استعلام ---
        else if (event.httpMethod === 'DELETE') {
            const id = event.queryStringParameters?.id;
            if (!id) {
                return createResponse(400, { error: 'شناسه استعلام الزامی است' });
            }

            const newInquiries = inquiries.filter(q => q.id !== id);
            if (newInquiries.length === inquiries.length) {
                return createResponse(404, { error: 'استعلام یافت نشد' });
            }

            if (!writeDB(INQUIRIES_FILE, newInquiries)) {
                return createResponse(500, { error: 'خطا در حذف' });
            }

            return createResponse(200, { message: 'استعلام حذف شد', id });
        }

        return createResponse(405, { error: 'متد مجاز نیست' });

    } catch (error) {
        console.error('خطا:', error);
        return createResponse(500, { error: 'خطای داخلی سرور' });
    }
};
