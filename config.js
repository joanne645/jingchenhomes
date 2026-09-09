// ⚠️ 这个文件只放"公开可用"的配置，不涉及任何密码或私密密钥。
// Supabase 的 anon key 是设计给浏览器端公开使用的，配合下面 schema.sql 里的
// RLS（行级安全策略：只允许匿名用户 insert，不允许 select/update/delete）
// 一起使用是安全的标准做法。

window.CONFIG = {
  // 在 Supabase 项目里：Project Settings → API → Project URL
  SUPABASE_URL: "https://mganqyhvbjndisuofzed.supabase.co",

  // Publishable key（原来叫 anon public key），来自 Project Settings → API
  SUPABASE_ANON_KEY: "sb_publishable_2qXy0ASRXF6VzGw732b7qA_hWygji0z",
};
