// netlify/functions/utils.js

const fs = require('fs');
const path = require('path');

// مسیر پوشه داده‌ها (در سرور Netlify)
const DATA_DIR = path.join(__dirname, '..', '..', 'data');
const PRODUCTS_FILE = path.join(DATA_DIR, 'products.json');
const ORDERS_FILE = path.join(DATA_DIR, 'orders.json');
const REVIEWS_FILE = path.join(DATA_DIR, 'reviews.json');
const INQUIRIES_FILE = path.join(DATA_DIR, 'inquiries.json');

// تابع کمکی برای اطمینان از وجود پوشه data
function ensureDataDir() {
    if (!fs.existsSync(DATA_DIR)) {
        fs.mkdirSync(DATA_DIR, { recursive: true });
    }
}

// تابع خواندن دیتابیس
function readDB(filePath) {
    try {
        ensureDataDir();
        if (!fs.existsSync(filePath)) {
            // اگر فایل وجود نداشت، یک آرایه خالی برمی‌گردانیم
            return [];
        }
        const data = fs.readFileSync(filePath, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error(`خطا در خواندن فایل ${filePath}:`, error);
        return [];
    }
}

// تابع نوشتن در دیتابیس
function writeDB(filePath, data) {
    try {
        ensureDataDir();
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
        return true;
    } catch (error) {
        console.error(`خطا در نوشتن فایل ${filePath}:`, error);
        return false;
    }
}

// هدرهای CORS مشترک
const CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
};

// تابع پاسخ استاندارد
function createResponse(statusCode, body, headers = {}) {
    return {
        statusCode,
        headers: { ...CORS_HEADERS, ...headers },
        body: JSON.stringify(body),
    };
}

// صادر کردن توابع
module.exports = {
    readDB,
    writeDB,
    createResponse,
    CORS_HEADERS,
    PRODUCTS_FILE,
    ORDERS_FILE,
    REVIEWS_FILE,
    INQUIRIES_FILE,
};
