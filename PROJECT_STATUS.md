# PROJECT_STATUS

## 当前状态（2026-11-06）
V2 已于 2026-11-05 由用户推送 main（abb08e6..2bc0315）。片区图文样板（95125、95120）已由用户推送（eede55f）。
地区栏目视觉升级：San Jose 全部栏目和 10 个 ZIP 已完成，已由用户决定上线（2026-11-06），未再做线上预览。San Jose 栏目 11 张用户上传的图授权未核实，已去掉红标上线，风险用户知情，待换授权照片；看区路线疑似 AI 图未放。其他 9 个城市未改版。
样板用的 images/zip/95120-1.webp、95125-1.webp 是用户发来的图，来源和授权待确认；95125 这张看起来像 AI 生成图，上线前要换真实照片或由用户明确决定。

待办（原上线前清单）：
- [ ] 运行 python3 tools/fetch_zip_market.py 取得邮编同周期数据（或由陈靖提供 MLS 同周期数据）；核实前页面显示“预览版”
- [ ] 补 95118、95128、95126、95135 的正文（MDX 内容包）；目前只在总览表里，没有详情页
- [ ] 邮编页照片：要真实、当地、有使用权；截图里的 redfin.com、trulia.com 等图片和 AI 生成图不能用
- [ ] Resend 账号和 Vercel 环境变量 RESEND_API_KEY、LEAD_NOTIFY_EMAIL，然后在预览网址实测表单
- [ ] 陈靖用当前会员版 RPA 核对文章里的默认天数（17 天、3 个工作日、5 天等）
- [ ] 确认 95129、95120 页面引用的 Redfin、Realtor.com 数字（95124 已核到 Redfin 2026 年 9 月数字）
- [ ] 确认：33 笔成交的买卖方、BQ Realty DRE 号、REALTOR® 会员身份、JC Team 团队名是否合规、实际服务范围、About 素材、Google 商家链接
- [ ] 11 月 3 日选举后复查：Prop 37、Prop 43、地方转让税措施
- [ ] 运行 python3 tools/check_links.py；隐私说明请专业人士看一遍

## 当前状态（2026-10-09）
- SEO 第一轮已在本地完成（是否已推送以 Git 记录为准）：首页换上新定位和入口；新增 buy.html、sell.html 和 guides/ 下三篇城市比较文章；10 个城市页换成 SEO 标题、H1 和导语；/home 永久跳转到首页；sitemap 共 17 个网址
- 上线后要做的验证：打开 https://www.homesbyjingchen.com/home/ 应跳到首页；用自己的信息提交一次咨询表单，到后台确认收到后删除这条测试

## SEO 第一轮之后的待办（2026-10-09 新增）
- [ ] 用有权限的账号在 Google Search Console 提交 sitemap.xml，并查看新页面的抓取和索引状态（Claude 没有这个账号的权限）
- [ ] 网站目前没有安装访问统计（实施包里没有统计账号 ID，所以没有装）。如果陈靖有 Google Analytics 账号，把衡量 ID 发给 Claude 再接入
- [ ] 英文版的买房、卖房、城市和比较文章还没有（实施包列为后续项）。在完整英文译文上线之前，这些中文页不加 hreflang
- [ ] 旧 WordPress 网址 /buy/、/sell/ 目前仍跳到英文首页的服务版块；是否改为跳到新的 buy.html、sell.html 待确认
- [ ] 比较文章里 fremont.gov 的两个链接和 Dublin vs Pleasanton、Sunnyvale vs Cupertino 文章里的部分官方链接，Claude 的环境无法联网逐个打开；推送前可运行一次 `python3 tools/check_links.py`（现在会一并检查服务页和比较文章）
- [ ] 首页结构化数据里原有的评分信息（5.0 / 15 条，来自 Zillow）本轮没有改动，也没有复制到其他页面

## 之前的状态（2026-10-08）
- 10 个城市生活指南已做好（尚未推送时以 Git 记录为准）；页面由 `tools/build_city_guides.py` 从 `tools/city-content/*.json` 生成

## 之前的状态（2026-09-24）
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
- [x] 中文页评价区和页脚两句对内的说明已删除（2026-10-09）
- [x] 中文页手机横向滚动：2026-10-09 检查 390 宽度下已无横向滚动
- [ ] 10 个城市生活指南目前只有中文（英文主页的城市方框链接到中文指南，并注明 Chinese）
- [x] 防止 Supabase 自动暂停：Vercel Cron 每天调用 /api/keepalive（2026-09-24 加上）；上线后到 Vercel → Settings → Cron Jobs 确认，过几天到 Logs 看是否每天都有运行
- [x] 后台已恢复，可以正常登录（2026-09-24）
- [x] 已在 Supabase 创建 keepalive() 函数，/api/keepalive 返回 supabaseStatus 200（2026-09-24 验证）

## 城市生活指南的后续事项（2026-10-08 新增）
- [ ] 上线前在本地预览里确认地图：城市边界线、学区范围、车站和设施圆点是否都显示出来（这三样在 Claude 的工作环境里连不上官方服务，只用模拟数据测过）
- [x] 已运行 `python3 tools/check_links.py`（2026-10-08）；确认失效的 5 处链接已在 2026-10-09 更换或删除。报告里大量 URLError 是对方网站拒绝自动访问，不是链接失效，脚本已改成把这类归为"需人工确认"
- [ ] 内容里注明了日期的信息需要定期复查：学校边界与关闭合并、BART/Caltrain/公交线路、在建项目进度、门店是否营业。建议每季度看一次
- [ ] 2026 年 11 月之后要更新的几处：Palo Alto 的 Measure J（Cubberley）投票结果、Palo Alto Link 10 月 30 日停运、BART 区域资金措施投票结果（Fremont 页）、Pleasanton Measure HH、California School Dashboard 2026 版发布后的年份说明
- [ ] 研究时没能查证、因此没有写进页面的内容（如部分超市门店、个别医疗点地址），清单在本机的 tools/city-notes/待复核清单.md（只保存在这台电脑上，不会上传到 GitHub），陈靖可以按自己了解的情况补充
- [x] 主页找房版块里"正式上线后……连接 MLS / IDX"的说明已改成面向访客的文字（2026-10-09）
