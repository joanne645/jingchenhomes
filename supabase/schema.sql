-- ============================================================
-- Jing Chen Homes · 网站留资表单 · Supabase 建表脚本
-- 使用方法：在 Supabase 项目里打开 SQL Editor，粘贴整段运行一次即可。
-- ============================================================

-- 1. 建表：存放网站表单提交的客户线索
create table if not exists public.leads (
  id           uuid primary key default gen_random_uuid(),
  created_at   timestamptz not null default now(),
  name         text not null,
  phone        text not null,
  email        text,
  intent       text,            -- 买房 / 卖房 / 换房 / 投资 / 其他
  message      text,
  source_url   text,            -- 提交时所在的页面地址
  referrer     text,            -- 从哪个页面跳转过来的
  status       text not null default 'new'  -- new / contacted / closed，方便你后续跟进
);

comment on table public.leads is '网站表单提交的客户咨询线索';

-- 2. 开启行级安全策略（RLS）—— 这是保护数据的关键一步
alter table public.leads enable row level security;

-- 3. 只允许匿名访客"新增"一条线索，不允许读取、修改或删除任何数据
--    这样即使 anon key 暴露在网页源代码里也是安全的：
--    访客只能往里面写自己刚填的这一条，看不到、也改不了别人的信息。
drop policy if exists "Allow anonymous insert" on public.leads;
create policy "Allow anonymous insert"
  on public.leads
  for insert
  to anon
  with check (true);

-- 3.1 显式授权 anon 角色可以对这张表执行 insert。
--     如果你在建项目时关闭了 "Automatically expose new tables"（更安全的做法，
--     Supabase 官方也推荐关闭），新建的表默认不会自动授权给 anon / authenticated，
--     没有这一句的话，就算上面的策略写对了，匿名访客也会因为"根本没有权限操作
--     这张表"而提交失败。加上这句之后，不管那个开关勾没勾，这份脚本都能正常用。
grant insert on public.leads to anon;

-- 4. 你自己登录 Supabase 后台（Table Editor）随时可以查看/导出所有线索，
--    因为你是用有完整权限的账号登录的，不受上面这条策略限制。

-- ============================================================
-- 可选：如果以后想直接在网页上收到新留资的邮件通知，
-- 可以在 Supabase 的 Database → Webhooks 里为 leads 表的 INSERT
-- 事件配置一个 Webhook，转发到 Zapier / Make / 邮件服务即可，
-- 不需要再改这份 schema。
-- ============================================================
