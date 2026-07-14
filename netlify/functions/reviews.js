// netlify/functions/reviews.js

const { readDB, writeDB, createResponse, REVIEWS_FILE } = require('./utils');

exports.handler = async (event, context) => {
    if (event.httpMethod === 'OPTIONS') {
        return createResponse(200, {});
    }

    try {
        let reviews = readDB(REVIEWS_FILE);

        // --- GET: دریافت نظرات (تایید شده) ---
        if (event.httpMethod === 'GET') {
            // فقط نظرات تایید شده نمایش داده شوند (برای کاربران)
            const approved = reviews.filter(r => r.approved !== false);
            return createResponse(200, approved);
        }

        // --- POST: ثبت نظر جدید ---
        else if (event.httpMethod === 'POST') {
            const newReview = JSON.parse(event.body);
            
            if (!newReview.name || !newReview.text || !newReview.rating) {
                return createResponse(400, { error: 'نام، متن و امتیاز الزامی است' });
            }

            newReview.id = `rev_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
            newReview.approved = newReview.approved !== undefined ? newReview.approved : true; // پیش‌فرض تایید
            newReview.date = new Date().toISOString();
            newReview.createdAt = new Date().toISOString();

            reviews.push(newReview);
            if (!writeDB(REVIEWS_FILE, reviews)) {
                return createResponse(500, { error: 'خطا در ذخیره‌سازی نظر' });
            }

            return createResponse(201, newReview);
        }

        // --- PUT: تایید یا ویرایش نظر (برای ادمین) ---
        else if (event.httpMethod === 'PUT') {
            const updatedData = JSON.parse(event.body);
            if (!updatedData.id) {
                return createResponse(400, { error: 'شناسه نظر الزامی است' });
            }

            const index = reviews.findIndex(r => r.id === updatedData.id);
            if (index === -1) {
                return createResponse(404, { error: 'نظر یافت نشد' });
            }

            reviews[index] = {
                ...reviews[index],
                ...updatedData,
                updatedAt: new Date().toISOString(),
            };
            
            if (!writeDB(REVIEWS_FILE, reviews)) {
                return createResponse(500, { error: 'خطا در به‌روزرسانی' });
            }

            return createResponse(200, reviews[index]);
        }

        // --- DELETE: حذف نظر ---
        else if (event.httpMethod === 'DELETE') {
            const id = event.queryStringParameters?.id;
            if (!id) {
                return createResponse(400, { error: 'شناسه نظر الزامی است' });
            }

            const newReviews = reviews.filter(r => r.id !== id);
            if (newReviews.length === reviews.length) {
                return createResponse(404, { error: 'نظر یافت نشد' });
            }

            if (!writeDB(REVIEWS_FILE, newReviews)) {
                return createResponse(500, { error: 'خطا در حذف' });
            }

            return createResponse(200, { message: 'نظر حذف شد', id });
        }

        return createResponse(405, { error: 'متد مجاز نیست' });

    } catch (error) {
        console.error('خطا:', error);
        return createResponse(500, { error: 'خطای داخلی سرور' });
    }
};
