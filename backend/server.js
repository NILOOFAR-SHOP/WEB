const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const multer = require('multer');

const app = express();
const PORT = process.env.PORT || 3001;
const DATA_DIR = path.join(__dirname, '..', 'data');
const UPLOADS_DIR = path.join(__dirname, '..', 'uploads');

app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

[UPLOADS_DIR, DATA_DIR].forEach(dir => { if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true }); });

// ===== CACHE CONTROL =====
const LONG_CACHE = 'public, max-age=31536000, immutable';
app.use((req, res, next) => {
  const p = req.path;
  if (p.startsWith('/uploads/') || p.startsWith('/vendor/') || p.startsWith('/icons/') || p.startsWith('/images/') || p === '/favicon.png' || p === '/robots.txt') {
    res.set('Cache-Control', LONG_CACHE);
  } else if (p === '/sw.js' || p === '/manifest.json') {
    res.set('Cache-Control', 'no-cache');
  } else if (p === '/' || p.endsWith('.html')) {
    res.set('Cache-Control', 'no-cache');
  }
  next();
});

const storage = multer.diskStorage({
  destination: UPLOADS_DIR,
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    cb(null, 'img_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6) + ext);
  }
});
const upload = multer({ storage, limits: { fileSize: 10 * 1024 * 1024 } });

function readJSON(filename) {
  const filePath = path.join(DATA_DIR, filename);
  try {
    if (!fs.existsSync(filePath)) return [];
    const raw = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(raw);
  } catch (e) {
    console.error('Error reading', filename, e.message);
    return [];
  }
}

function writeJSON(filename, data) {
  const filePath = path.join(DATA_DIR, filename);
  try {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
    return true;
  } catch (e) {
    console.error('Error writing', filename, e.message);
    return false;
  }
}

function readSettings() {
  const filePath = path.join(DATA_DIR, 'settings.json');
  try {
    if (!fs.existsSync(filePath)) return {};
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch (e) { return {}; }
}

function writeSettings(data) {
  const filePath = path.join(DATA_DIR, 'settings.json');
  try {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
    return true;
  } catch (e) { return false; }
}

function writeData(filename, data) {
  try {
    fs.writeFileSync(path.join(DATA_DIR, filename), JSON.stringify(data, null, 2), 'utf-8');
    return true;
  } catch (e) { return false; }
}

// ===== PRODUCTS =====
app.get('/api/products', (req, res) => {
  const products = readJSON('products.json');
  res.json(products);
});

app.post('/api/products', (req, res) => {
  const products = readJSON('products.json');
  const product = req.body;
  if (!product.id) product.id = 'prod_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
  product.createdAt = product.createdAt || new Date().toISOString();
  products.push(product);
  writeJSON('products.json', products);
  res.json({ success: true, product });
});

app.put('/api/products', (req, res) => {
  const products = readJSON('products.json');
  const updated = req.body;
  const idx = products.findIndex(p => p.id === updated.id);
  if (idx === -1) return res.status(404).json({ error: 'Product not found' });
  products[idx] = { ...products[idx], ...updated, updatedAt: new Date().toISOString() };
  writeJSON('products.json', products);
  res.json({ success: true, product: products[idx] });
});

app.delete('/api/products', (req, res) => {
  let products = readJSON('products.json');
  const id = req.query.id;
  products = products.filter(p => p.id !== id);
  writeJSON('products.json', products);
  res.json({ success: true });
});

// batch sync - prevents race conditions
app.post('/api/products/sync', (req, res) => {
  const allProducts = req.body.products || [];
  writeJSON('products.json', allProducts);
  res.json({ success: true });
});

// batch sync orders
app.post('/api/orders/sync', (req, res) => {
  writeJSON('orders.json', req.body.orders || []);
  res.json({ success: true });
});

// batch sync reviews
app.post('/api/reviews/sync', (req, res) => {
  writeJSON('reviews.json', req.body.reviews || []);
  res.json({ success: true });
});

// batch sync inquiries
app.post('/api/inquiries/sync', (req, res) => {
  writeJSON('inquiries.json', req.body.inquiries || []);
  res.json({ success: true });
});

// ===== ORDERS =====
app.get('/api/orders', (req, res) => {
  const orders = readJSON('orders.json');
  if (req.query.status) {
    return res.json(orders.filter(o => o.status === req.query.status));
  }
  res.json(orders);
});

app.post('/api/orders', (req, res) => {
  const orders = readJSON('orders.json');
  const order = req.body;
  if (!order.id) order.id = 'ord_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
  order.createdAt = order.createdAt || Date.now();
  orders.push(order);
  writeJSON('orders.json', orders);
  res.json({ success: true, order });
});

app.put('/api/orders', (req, res) => {
  const orders = readJSON('orders.json');
  const { id, status } = req.body;
  const idx = orders.findIndex(o => o.id === id);
  if (idx === -1) return res.status(404).json({ error: 'Order not found' });
  orders[idx].status = status;
  orders[idx].updatedAt = new Date().toISOString();
  writeJSON('orders.json', orders);
  res.json({ success: true, order: orders[idx] });
});

app.delete('/api/orders', (req, res) => {
  let orders = readJSON('orders.json');
  const id = req.query.id;
  orders = orders.filter(o => o.id !== id);
  writeJSON('orders.json', orders);
  res.json({ success: true });
});

// ===== REVIEWS =====
app.get('/api/reviews', (req, res) => {
  const reviews = readJSON('reviews.json');
  if (req.query.approved === 'true') {
    return res.json(reviews.filter(r => r.approved));
  }
  res.json(reviews);
});

app.post('/api/reviews', (req, res) => {
  const reviews = readJSON('reviews.json');
  const review = req.body;
  if (!review.id) review.id = 'rev_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
  review.createdAt = review.createdAt || Date.now();
  review.approved = review.approved !== undefined ? review.approved : true;
  reviews.push(review);
  writeJSON('reviews.json', reviews);
  res.json({ success: true, review });
});

app.delete('/api/reviews', (req, res) => {
  let reviews = readJSON('reviews.json');
  const id = req.query.id;
  reviews = reviews.filter(r => r.id !== id);
  writeJSON('reviews.json', reviews);
  res.json({ success: true });
});

// ===== INQUIRIES =====
app.get('/api/inquiries', (req, res) => {
  const inquiries = readJSON('inquiries.json');
  if (req.query.status) {
    return res.json(inquiries.filter(i => i.status === req.query.status));
  }
  res.json(inquiries);
});

app.post('/api/inquiries', (req, res) => {
  const inquiries = readJSON('inquiries.json');
  const inquiry = req.body;
  if (!inquiry.id) inquiry.id = 'inq_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
  inquiry.createdAt = inquiry.createdAt || Date.now();
  inquiries.push(inquiry);
  writeJSON('inquiries.json', inquiries);
  res.json({ success: true, inquiry });
});

// ===== SETTINGS =====
app.get('/api/settings', (req, res) => {
  const settings = readSettings();
  settings.products_count = readJSON('products.json').length;
  settings.orders_count = readJSON('orders.json').length;
  settings.reviews_count = readJSON('reviews.json').length;
  res.json(settings);
});

app.post('/api/settings', (req, res) => {
  const settings = readSettings();
  const updates = req.body;
  Object.assign(settings, updates);
  writeSettings(settings);
  res.json({ success: true, settings });
});

// ===== CART =====
function readCart() {
  const filePath = path.join(DATA_DIR, 'cart.json');
  try {
    if (!fs.existsSync(filePath)) return {};
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch (e) { return {}; }
}
function writeCart(data) { writeData('cart.json', data); }

app.get('/api/cart', (req, res) => { res.json(readCart()); });
app.post('/api/cart', (req, res) => { writeCart(req.body); res.json({ success: true }); });

// ===== UPLOAD IMAGE =====
app.post('/api/upload', upload.single('image'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });
  const url = '/uploads/' + req.file.filename;
  res.json({ success: true, url });
});

// ===== COUPONS =====
app.get('/api/coupons', (req, res) => {
  res.json(readJSON('coupons.json'));
});

app.post('/api/coupons', (req, res) => {
  const coupons = readJSON('coupons.json');
  coupons.push(req.body);
  writeJSON('coupons.json', coupons);
  res.json({ success: true });
});

// ===== SUBSCRIBERS =====
app.get('/api/subscribers', (req, res) => {
  res.json(readJSON('subscribers.json'));
});

app.post('/api/subscribers', (req, res) => {
  const subs = readJSON('subscribers.json');
  const { email } = req.body;
  if (!subs.includes(email)) {
    subs.push(email);
    writeJSON('subscribers.json', subs);
  }
  res.json({ success: true });
});

// ===== STATIC FILES =====
app.use('/uploads', express.static(UPLOADS_DIR));

// Server-side data injection for instant load
app.get('/', (req, res, next) => {
  const indexPath = path.join(__dirname, '..', 'index.html');
  try {
    let html = fs.readFileSync(indexPath, 'utf-8');
    const products = readJSON('products.json');
    const settings = readSettings();
    const reviews = readJSON('reviews.json');

    const preloadData = JSON.stringify({
      products: products,
      settings: settings,
      reviews: reviews
    });

    html = html.replace('</head>',
      '<script>window.__PRELOAD__=' + preloadData + ';</script></head>'
    );
    res.set('Content-Type', 'text/html; charset=utf-8');
    res.send(html);
  } catch(e) {
    next();
  }
});

app.use(express.static(path.join(__dirname, '..')));

app.listen(PORT, () => {
  console.log(`Nilofar API server running on http://localhost:${PORT}`);
});
