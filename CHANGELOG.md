# CHANGELOG

## 2026-10-09（SEO 第一轮）
- 首页：标题、摘要和 H1 换成"湾区买房与卖房，从看懂城市和房子开始"；首屏写明"陈靖 Jing Chen｜加州湾区买房、卖房与城市选择"；三个按钮分别进入买房页、卖房页和咨询表单；"先明确你的下一步"四张卡片；城市版块加上导语；新增"两座城市之间，怎么做选择？"版块，链接三篇比较文章；联系表单前的文案换成"一次有准备的沟通"
- 新增湾区买房服务页 buy.html、卖房服务页 sell.html，使用实施包完整成稿
- 新增三篇城市比较文章：guides/fremont-vs-dublin.html、guides/dublin-vs-pleasanton.html、guides/sunnyvale-vs-cupertino.html，保留比较表、常见问题、官方学校与交通链接、资料核查日期
- 10 个城市页：搜索标题、摘要、H1 和导语按实施包配置；导航加买房、卖房、城市比较；Fremont、Dublin、Pleasanton、Sunnyvale、Cupertino 页加上相关比较文章的链接；电话可点击拨号
- 导航：电脑端加买房、卖房、城市指南、城市比较；手机端 ☰ 按钮改成真正的下拉菜单（原来只是滚动到表单），中英文主页都改了
- 咨询入口：服务页和文章的按钮都进入首页现有表单，自动选好意向（买房/卖房/换房）并预填留言提纲；表单仍然写入 Supabase leads 表，没有新建表单
- 删除对内说明：找房版块的"正式上线后……连接 MLS / IDX"、评价区的"请提供 Google 商家资料"、页脚的"正式网站建议使用……素材"、提示条里的"Demo"；数据库没连上时的提示改为请访客直接致电
- 技术：vercel.json 新增 /home 和 /home/ 永久跳转到首页（其他不存在的网址仍然是 404）；sitemap.xml 增至 17 个网址；每个页面有独立的 title、description、canonical 和分享信息；只有中文的页面不加 hreflang
- 更换失效链接：San Jose 的 East Side Union 高中学区查询入口、Pleasanton 水井项目页、Mountain View 的 VTA 橙线时刻表；删除 Dublin 一条失效的资料来源
- 新增 pages.css、tools/build_pages.py、tools/seo-meta.json、tools/page-content/；tools/check_links.py 现在也检查服务页和比较文章，并能处理带中文或弯引号的网址

## 2026-10-08
- 新增"城市生活指南"：10 个城市各有独立页面（Palo Alto 原地址不变，另外 9 个是新页面），统一结构为 概览 → 地图 → 片区比较 → 工作日与周末 → 学校与入学 → 住房与成本 → 实地看区路线 → 城市比较与咨询 → 资料来源
- Palo Alto 页面重写：保留城市历史和原有社区，删掉了来源不可靠的人口、收入、族裔比例和 Zillow 价格数字，以及"我把原来的卡片改成……"这类制作说明
- 城市页地图：城市边界、学区范围（U.S. Census Bureau TIGERweb）、轨道站和日常设施标记、官方上学路线和环境查询入口，分五个图层切换
- 中英文主页：10 个城市方框全部链接到对应指南，方框文案改为各城市的具体生活特点；找房下拉菜单补上 Milpitas 和 Dublin；从城市页点咨询按钮进入时自动预选城市、预填留言
- sitemap.xml 加入 10 个城市页；vercel.json 把旧网址 /communities/<城市> 跳转到对应城市页
- 新增 tools/（城市页生成脚本、城市内容 JSON、外链检查脚本）

## 2026-09-24
- keepalive 改为调用专用的数据库函数 keepalive()：原来读取 leads 表，因为访客没有读取权限会返回 401，现在改成正常返回 200 的查询；新增 schema.sql 第 6 部分
- 确认后台恢复正常：可以登录，看到 4 条咨询
- Supabase 免费版项目曾被自动暂停，导致后台登录不上、表单提交不了，用户已手动恢复。新增 api/keepalive.js + Vercel Cron（每天一次）防止再次暂停
- 客户咨询后台登录失败时显示具体原因（密码错误 / 邮箱未验证 / 连不上数据库），不再只显示“邮箱或密码不对”
- 域名上线：DNS 改好后，www.homesbyjingchen.com 显示新网站，homesbyjingchen.com 自动跳转到 www
- 新增英文版 /en/，导航栏加 EN / 中文 一键切换（切换时保留当前版块）；加 hreflang；sitemap 加 /en/；旧 WordPress 英文网址跳转改为指向英文版对应版块。英文页去掉了中文页上两句对内的说明（Google 评价请提供链接、建议使用 MLS 素材）
- 成交案例：给 963 Bellomo Ave（BQ 同事 Bill Qin 的 listing）和 4131 Pleasanton Ave（陈靖自己的 listing）加了封面图，引用 Redfin 上的 listing 主图，图片加载失败时自动隐藏
- 正式域名改为 www.homesbyjingchen.com（与 Vercel 设置的主网址一致）：更新 index.html 里的 canonical、og:url、og:image、JSON-LD，更新 robots.txt 和 sitemap.xml（新增 Palo Alto 页），Palo Alto 页新增 canonical
- vercel.json 新增旧 WordPress 网址的永久跳转（/buy/ /sell/ /home-search/ /listings/ /success-stories/ /resources/ /home-valuation/ /communities/* /about/ /contact/）
- 接手项目：建立本地仓库，新增 CLAUDE.md、PROJECT_STATUS.md、CHANGELOG.md（网站页面没有改动）

## 2026-09-10 及之前（来自 Git 记录）
- 7d95462 新增 Palo Alto 城市详情页，主站城市方框加上链接
- f464f7b 修复房源搜索按钮：跳转到 Zillow 对应城市真实搜索结果页
- 2193967 整体配色改为深蓝色主题，人像做色彩融合处理，修复标题换行挤压问题
- 2d16415 新增客户咨询后台和湾区市场数据
- 7bd3c63 Jing Chen Homes 上线版本
