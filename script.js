// ============================================================
//  جایگزینی localStorage با API سرور (Netlify Functions)
// ============================================================

// آدرس پایه API (در Netlify، مسیرها به /api/ products و ... نگاشت می‌شوند)
// برای استفاده در محیط محلی (Localhost) می‌توانید از آدرس کامل استفاده کنید:
// const API_BASE = 'http://localhost:8888/.netlify/functions';
// اما برای حالت تولید (Production) از مسیر نسبی استفاده کنید:
const API_BASE = '/.netlify/functions';

// ===== محصولات =====
async function fetchProducts() {
    try {
        const res = await fetch(`${API_BASE}/products`);
        if (!res.ok) throw new Error('خطا در دریافت محصولات');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return [];
    }
}

async function addProduct(product) {
    try {
        const res = await fetch(`${API_BASE}/products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(product),
        });
        if (!res.ok) throw new Error('خطا در افزودن محصول');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return null;
    }
}

async function updateProduct(product) {
    try {
        const res = await fetch(`${API_BASE}/products`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(product),
        });
        if (!res.ok) throw new Error('خطا در به‌روزرسانی محصول');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return null;
    }
}

async function deleteProduct(id) {
    try {
        const res = await fetch(`${API_BASE}/products?id=${id}`, {
            method: 'DELETE',
        });
        if (!res.ok) throw new Error('خطا در حذف محصول');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return null;
    }
}

// ===== سفارشات =====
async function fetchOrders(status = null) {
    try {
        let url = `${API_BASE}/orders`;
        if (status) url += `?status=${encodeURIComponent(status)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error('خطا در دریافت سفارشات');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return [];
    }
}

async function addOrder(order) {
    try {
        const res = await fetch(`${API_BASE}/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(order),
        });
        if (!res.ok) throw new Error('خطا در ثبت سفارش');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return null;
    }
}

async function updateOrderStatus(id, status) {
    try {
        const res = await fetch(`${API_BASE}/orders`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, status }),
        });
        if (!res.ok) throw new Error('خطا در به‌روزرسانی سفارش');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return null;
    }
}

async function deleteOrder(id) {
    try {
        const res = await fetch(`${API_BASE}/orders?id=${id}`, {
            method: 'DELETE',
        });
        if (!res.ok) throw new Error('خطا در حذف سفارش');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return null;
    }
}

// ===== نظرات =====
async function fetchReviews() {
    try {
        const res = await fetch(`${API_BASE}/reviews`);
        if (!res.ok) throw new Error('خطا در دریافت نظرات');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return [];
    }
}

async function addReview(review) {
    try {
        const res = await fetch(`${API_BASE}/reviews`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(review),
        });
        if (!res.ok) throw new Error('خطا در ثبت نظر');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return null;
    }
}

async function deleteReview(id) {
    try {
        const res = await fetch(`${API_BASE}/reviews?id=${id}`, {
            method: 'DELETE',
        });
        if (!res.ok) throw new Error('خطا در حذف نظر');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return null;
    }
}

// ===== استعلام‌ها =====
async function fetchInquiries(status = null) {
    try {
        let url = `${API_BASE}/inquiries`;
        if (status) url += `?status=${encodeURIComponent(status)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error('خطا در دریافت استعلام‌ها');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return [];
    }
}

async function addInquiry(inquiry) {
    try {
        const res = await fetch(`${API_BASE}/inquiries`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(inquiry),
        });
        if (!res.ok) throw new Error('خطا در ثبت استعلام');
        return await res.json();
    } catch (error) {
        console.error('خطا:', error);
        return null;
    }
}

// ============================================================
//  نمونه استفاده: بارگذاری محصولات هنگام لود صفحه
// ============================================================

// به جای خواندن از localStorage:
// const products = JSON.parse(localStorage.getItem('nilofor_products_v2')) || [];

// حالا از سرور می‌خوانیم:
async function initProducts() {
    const products = await fetchProducts();
    // حالا products را در متغیر سراسری یا رندر کنید
    window.productsData = products;
    renderProductPage(); // تابع رندر شما
}

// همچنین برای افزودن محصول جدید:
async function handleAddProduct(newProduct) {
    const result = await addProduct(newProduct);
    if (result) {
        // محصول با موفقیت اضافه شد
        await initProducts(); // دوباره لیست را به‌روز کنید
        showToast('محصول اضافه شد', 'gold');
    } else {
        showToast('خطا در افزودن محصول', 'error');
    }
}
