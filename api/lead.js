// 网站咨询表单的后端（Vercel Serverless Function）
// 流程：校验 → 反垃圾 → 写入 Supabase leads 表 → 发邮件通知陈靖
// 只有写入数据库成功才向访客显示成功；邮件失败不影响线索保存，后台仍能看到。
//
// 需要在 Vercel 项目的 Environment Variables 里设置：
//   RESEND_API_KEY      Resend 的 API Key（发通知邮件）
//   LEAD_NOTIFY_EMAIL   接收通知的邮箱
//   LEAD_FROM_EMAIL     可选，发件人。不设置时用 Resend 的测试发件人 onboarding@resend.dev，
//                       这时收件邮箱必须是注册 Resend 用的邮箱
const SUPABASE_URL = 'https://mganqyhvbjndisuofzed.supabase.co';
const SUPABASE_KEY = 'sb_publishable_2qXy0ASRXF6VzGw732b7qA_hWygji0z';

const INTENTS = ['买房', '卖房', '估值', '换房', '投资', '其他'];
const MIN_ELAPSED_MS = 2500;
const RATE_WINDOW_MS = 10 * 60 * 1000;
const RATE_MAX = 5;
const hits = new Map(); // 单实例内的简单限流，配合蜜罐和提交时长一起用

const clean = (v, max) => String(v == null ? '' : v).replace(/\u0000/g, '').trim().slice(0, max);
const escHtml = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function allowedOrigin(origin) {
  if (!origin) return true;
  try {
    const h = new URL(origin).hostname;
    return h === 'www.homesbyjingchen.com' || h === 'homesbyjingchen.com' || h.endsWith('.vercel.app') || h === 'localhost';
  } catch (e) { return false; }
}

function rateLimited(ip) {
  const now = Date.now();
  const list = (hits.get(ip) || []).filter((t) => now - t < RATE_WINDOW_MS);
  list.push(now);
  hits.set(ip, list);
  return list.length > RATE_MAX;
}

async function notify(lead) {
  const key = process.env.RESEND_API_KEY;
  const to = process.env.LEAD_NOTIFY_EMAIL;
  if (!key || !to) return { sent: false, reason: 'email_not_configured' };
  const rows = [['姓名', lead.name], ['电话', lead.phone], ['Email', lead.email], ['需求类型', lead.intent], ['留言', lead.message], ['来源页面', lead.source_url]]
    .filter(([, v]) => v)
    .map(([k, v]) => `<tr><td style="padding:6px 12px 6px 0;color:#666;vertical-align:top;white-space:nowrap">${k}</td><td style="padding:6px 0;white-space:pre-wrap">${escHtml(v)}</td></tr>`)
    .join('');
  const payload = {
    from: process.env.LEAD_FROM_EMAIL || 'Jing Chen Homes <onboarding@resend.dev>',
    to: [to],
    subject: `网站新咨询：${lead.intent || '未选择'} · ${lead.name}`,
    html: `<table style="font:15px/1.6 sans-serif;border-collapse:collapse">${rows}</table>`,
  };
  if (lead.email) payload.reply_to = lead.email;
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!r.ok) return { sent: false, reason: `resend_${r.status}: ${await r.text()}` };
  return { sent: true };
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method_not_allowed' });
  if (!allowedOrigin(req.headers.origin)) return res.status(403).json({ ok: false, error: 'forbidden' });

  const b = typeof req.body === 'string' ? (() => { try { return JSON.parse(req.body); } catch (e) { return {}; } })() : (req.body || {});

  // 蜜罐被填写：按成功返回，不保存
  if (b.company_website) return res.status(200).json({ ok: true });

  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
  if (rateLimited(ip)) return res.status(429).json({ ok: false, error: 'too_many' });
  if (Number(b.elapsed) < MIN_ELAPSED_MS) return res.status(422).json({ ok: false, error: 'too_fast' });

  const name = clean(b.name, 100);
  const phone = clean(b.phone, 40);
  const email = clean(b.email, 160);
  const intent = INTENTS.includes(b.intent) ? b.intent : '';
  const city = clean(b.city, 40);
  const text = clean(b.message, 3000);
  if (!name || (!phone && !email) || !intent) return res.status(422).json({ ok: false, error: 'missing_fields' });
  if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return res.status(422).json({ ok: false, error: 'bad_email' });
  if ((text.match(/https?:\/\//gi) || []).length > 2) return res.status(422).json({ ok: false, error: 'too_many_links' });

  const lang = b.lang === 'en' ? 'English' : '中文';
  const lead = {
    name, phone, email: email || null, intent,
    message: [city ? `城市：${city}` : '', `语言：${lang}`, text].filter(Boolean).join('\n'),
    source_url: clean(b.source_url, 500),
    referrer: clean(b.referrer, 500),
  };

  try {
    const r = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
      method: 'POST',
      headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}`, 'Content-Type': 'application/json', Prefer: 'return=minimal' },
      body: JSON.stringify(lead),
    });
    if (!r.ok) {
      console.error('leads insert failed', r.status, await r.text());
      return res.status(502).json({ ok: false, error: 'save_failed' });
    }
  } catch (err) {
    console.error('leads insert error', err);
    return res.status(502).json({ ok: false, error: 'save_failed' });
  }

  let mail = { sent: false };
  try {
    mail = await notify(lead);
    if (!mail.sent) console.error('lead email not sent:', mail.reason);
  } catch (err) {
    console.error('lead email error', err);
  }
  return res.status(200).json({ ok: true, notified: mail.sent });
};
