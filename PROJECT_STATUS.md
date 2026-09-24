# PROJECT_STATUS

## 当前状态（2026-09-24）
- 线上版本：commit 7d95462（新增 Palo Alto 城市详情页）
- 本地仓库已建立，与线上一致

## 重要决定
- 保留现有的 GitHub → Vercel 自动部署方式
- 旧的本地 HTML 文件（`../jing_chen_realtor_cn_demo.html`、`../jingchenhomes_complete_landing.html`）只作参考，不是线上源码

## 待办 / 待确认
- [x] 正式域名确定为 homesbyjingchen.com，代码里的网址已统一改好（尚未推送）
- [x] Vercel 已添加 homesbyjingchen.com（308 跳转到 www）和 www.homesbyjingchen.com；主网址用 www
- [x] DNS 已由原网站设置人改好（2026-09-24）：homesbyjingchen.com 跳转到 www.homesbyjingchen.com，打开的是新网站
- [x] 域名在 WordPress 管理，DNS 在 WordPress 后台修改
- [x] 旧 WordPress 站的网址（/buy/、/sell/、/communities/…、/about/、/contact/ 等）已在 vercel.json 里设置 301 跳转到新站对应版块，避免旧链接打不开
- [ ] 确认旧站的英文内容是否需要保留（新站目前只有中文）
- [ ] 确认这台 Mac 能否推送到 GitHub（第一次推送时验证）
- [ ] 可考虑在 robots.txt 里屏蔽 /dashboard/
- [ ] 湾区市场数据（Updated 2026.09）需要定期更新
- [ ] 仓库暂时保持公开（2026-09-24 决定）。如果以后改成私有：先确认 joanne@1pinnacle.com 已加入 GitHub 账号 joanne645，否则 Vercel 免费版可能拒绝自动部署
- [ ] 4056 Nevis St（Compass 的 listing，陈靖是买方经纪）因为照片版权问题暂时不放图；如果以后陈靖提供自己有权使用的照片，放到 images/ 目录
- [ ] 成交案例的封面图目前引用 Redfin、Homes.com、Zillow 的图片地址，对方网站改动后图片可能会失效；长期建议换成 images/ 目录里的本地图片
- [ ] 中文页评价区和页脚有两句对内的说明（“请提供陈靖 Google 商家资料…”、“正式网站建议使用…MLS / 摄影素材”），英文页已去掉，中文页是否也去掉待确认
- [ ] 中文页在手机上有轻微横向滚动（市场报告表格太宽），上线前就存在，待修
- [ ] Palo Alto 城市页目前只有中文
- [x] 防止 Supabase 自动暂停：Vercel Cron 每天调用 /api/keepalive（2026-09-24 加上）；上线后到 Vercel → Settings → Cron Jobs 确认，过几天到 Logs 看是否每天都有运行
- [x] 后台已恢复，可以正常登录（2026-09-24）
- [ ] 在 Supabase SQL Editor 运行 schema.sql 第 6 部分（创建 keepalive 函数），之后 /api/keepalive 应返回 supabaseStatus 200
