// 每天由 Vercel Cron 自动调用一次（见 vercel.json 的 "crons"），
// 让 Supabase 免费版项目保持“有人在用”，避免一周没活动被自动暂停。
// 只做一次只读查询，不写入、不修改任何数据；用的是网站本来就公开的 publishable key（同 config.js）。
const SUPABASE_URL = 'https://mganqyhvbjndisuofzed.supabase.co';
const SUPABASE_KEY = 'sb_publishable_2qXy0ASRXF6VzGw732b7qA_hWygji0z';

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  try {
    const r = await fetch(`${SUPABASE_URL}/rest/v1/leads?select=id&limit=1`, {
      headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}` },
    });
    // 访客没有读取权限时会返回空列表或 401，这都说明数据库已经收到并处理了这次请求
    res.status(200).json({ ok: true, supabaseStatus: r.status, at: new Date().toISOString() });
  } catch (err) {
    res.status(502).json({ ok: false, error: String(err), at: new Date().toISOString() });
  }
};
