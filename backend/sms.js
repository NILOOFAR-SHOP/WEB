const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');

function readJSON(filename) {
  const filePath = path.join(DATA_DIR, filename);
  try {
    if (!fs.existsSync(filePath)) return [];
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch (e) { return []; }
}

function writeJSON(filename, data) {
  try {
    fs.writeFileSync(path.join(DATA_DIR, filename), JSON.stringify(data, null, 2), 'utf-8');
    return true;
  } catch (e) { return false; }
}

function readSettings() {
  try {
    const fp = path.join(DATA_DIR, 'settings.json');
    if (!fs.existsSync(fp)) return {};
    return JSON.parse(fs.readFileSync(fp, 'utf-8'));
  } catch (e) { return {}; }
}

function getConfig() {
  const s = readSettings();
  return Object.assign({
    enabled: false,
    endpoint: '',
    method: 'POST',
    authType: 'none',
    apiKey: '',
    username: '',
    password: '',
    phoneField: 'phone',
    messageField: 'message',
    adminPhone: '+989153104827',
    adminEnabled: true,
    customerEnabled: true,
    extraFields: {}
  }, s.sms || {});
}

function getOutbox(limit) {
  const list = readJSON('sms_outbox.json');
  return limit ? list.slice(-limit) : list;
}

function logOutbox(entry) {
  const list = readJSON('sms_outbox.json');
  list.push(Object.assign({ at: new Date().toISOString() }, entry));
  while (list.length > 500) list.shift();
  writeJSON('sms_outbox.json', list);
}

async function httpSend(cfg, to, text) {
  const headers = { 'Content-Type': 'application/json' };
  if (cfg.authType === 'bearer' && cfg.apiKey) headers['Authorization'] = 'Bearer ' + cfg.apiKey;
  if (cfg.authType === 'basic') {
    const cred = Buffer.from((cfg.username || '') + ':' + (cfg.password || '')).toString('base64');
    headers['Authorization'] = 'Basic ' + cred;
  }
  const body = {};
  body[cfg.phoneField || 'phone'] = to;
  body[cfg.messageField || 'message'] = text;
  Object.assign(body, cfg.extraFields || {});

  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), 8000);
  try {
    const resp = await fetch(cfg.endpoint, {
      method: cfg.method || 'POST',
      headers,
      body: JSON.stringify(body),
      signal: ctl.signal
    });
    const txt = await resp.text();
    logOutbox({ to, text, status: resp.ok ? 'sent' : 'failed', http: resp.status, response: String(txt).slice(0, 300), provider: 'http' });
    return resp.ok;
  } catch (e) {
    logOutbox({ to, text, status: 'failed', error: String(e && e.message || e).slice(0, 300), provider: 'http' });
    return false;
  } finally {
    clearTimeout(timer);
  }
}

async function sendSms(to, text) {
  if (!to || !text) return false;
  const cfg = getConfig();
  if (!cfg.enabled) {
    logOutbox({ to, text, status: 'disabled' });
    return false;
  }
  if (!cfg.endpoint) {
    logOutbox({ to, text, status: 'queued' });
    return false;
  }
  return httpSend(cfg, to, text);
}

function fmtOrder(order) {
  let items = (order.items || []).map(i => `• ${i.name} ×${i.qty}`).join('\n');
  if (!items && order.productName) items = `• ${order.productName} ×${order.quantity || 1}`;
  if (!items) items = '—';
  const total = order.total || order.subtotal || '—';
  const addr = (order.shipping && order.shipping.address) || order.message || '—';
  return {
    admin: [
      '🛍️ سفارش جدید فروشگاه نیلوفر',
      `کد: ${order.id || '—'}`,
      `مشتری: ${order.customer || '—'}`,
      `تلفن: ${order.phone || '—'}`,
      'اقلام:',
      items,
      `مبلغ: ${total} تومان`,
      `پرداخت: ${order.payment || '—'}`,
      `آدرس: ${addr}`
    ].join('\n'),
    customer: [
      `سفارش شما در فروشگاه نیلوفر با موفقیت ثبت شد ✅`,
      `کد پیگیری: ${order.id || '—'}`,
      `مبلغ: ${total} تومان`,
      'به‌زودی همکاران ما برای هماهنگی با شما تماس خواهند گرفت.'
    ].join('\n')
  };
}

function notifyOrder(order) {
  const cfg = getConfig();
  const texts = fmtOrder(order);
  if (cfg.adminEnabled !== false && cfg.adminPhone) sendSms(cfg.adminPhone, texts.admin);
  if (cfg.customerEnabled !== false && order.phone) sendSms(order.phone, texts.customer);
}

module.exports = { getConfig, getOutbox, sendSms, notifyOrder };
