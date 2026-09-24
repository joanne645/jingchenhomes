# CHANGELOG

## 2026-09-24
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
