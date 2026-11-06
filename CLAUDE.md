# CLAUDE.md：陈靖个人网站（Jing Chen Homes）

## 基本信息
- 线上网址：https://jingchenhomes.vercel.app/
- 正式域名：https://www.homesbyjingchen.com/（主网址带 www；Vercel 已设置 homesbyjingchen.com 用 308 跳转到 www）。2026-09-24 起代码里的 canonical、og、JSON-LD、robots、sitemap 都统一用这个域名。这个域名原来指向一个 WordPress 旧站，改成 Vercel 需要在域名的 DNS 管理处修改记录
- GitHub：https://github.com/joanne645/jingchenhomes，分支 `main`
- 部署：Vercel 项目 `jingchenhomes`（团队 pinnacle2026）已连接 GitHub。推送到 `main` 后会自动部署，不需要另外手动部署
- Mac 上的本地仓库：`~/BQ2026/经纪人网站/jingchenhomes`（2026-09-24 建立，和 origin/main 同步）
- 技术：纯静态 HTML/CSS/JS + 一个 Vercel Function，没有框架和包管理器（Vercel Framework = Other）。HTML 由本地 Python 脚本生成后提交，Vercel 不运行构建
- 后台用 Supabase（CDN 加载 supabase-js@2），公开配置在 `config.js`（只有 publishable key）

## 目录结构（2026-11 V2 起）
- **全站页面都是生成的，不要直接改 HTML。** `python3 tools/build_site.py` 生成除中文城市页外的全部页面和 sitemap.xml；`python3 tools/build_city_guides.py` 生成 `cities/*.html`。两者都只用 Python 自带库。改了 site.css 的导航、页脚、成交卡片部分，要同步 `cities/chrome.css`
- 英文在 `/en/` 下一一对应：`index`、`buy`、`sell`、`areas`、`homeowner`、`sold`、`insights`、`about`、`contact`、`privacy`、`calculators/*`、`insights/*`、`guides/*`、`areas/san-jose/**`、`cities/*`（英文城市页是精简版）
- 公共文件：`site.css`、`site.js`；`tools/site_chrome.py`（导航、页脚、DRE；拿到 BQ Realty 经纪公司 DRE 号填 `BROKER_DRE`）；改样式后换 `ASSET_VER`
- 内容位置：
  - `tools/build_site.py`：各栏目首页、关于、联系、隐私的文案
  - `tools/v2-content/articles/<slug>.json|.zh.html|.en.html`：32 篇文章 + 3 篇城市比较；写作规范 `tools/v2-content/WRITER_BRIEF.md`；检查 `python3 tools/v2-content/check_articles.py`
  - `tools/page-content/buy.html`、`sell.html`：买房六步、卖房说明的中文；英文在 `tools/v2-content/pages/`
  - `tools/v2-content/en-cities/<slug>.json`：英文城市页
  - `tools/v2-content/zip/<邮编>.json`：San Jose 邮编页内容。**新增邮编只需加这个文件和 `images/zip/<邮编>-1.webp`（可 -2、-3），再在 `tools/site-data/sj-zip-reference.json` 的 areas/zips 加一行**。网站不用框架，所以用 JSON 代替 MDX
  - San Jose 城市页和 `/en/cities/san-jose.html` 的图文栏目：`tools/sj_sections.py`（中英文共用模板）；文字 `tools/city-content/san-jose.json`、`san-jose-sections.json`，英文 `tools/v2-content/en-cities/san-jose-full.json`、`san-jose-sections.en.json`；照片和授权记录 `tools/city-content/san-jose-photos.json`（license 写“未核实”的待换授权照片）
  - 邮编详情页深度阅读：`tools/city-content/sj-zip-deep.json`（10 个 ZIP，中英文）
  - `tools/fetch_commons_photos.py`：在 Mac 终端运行，取 Commons 候选照片和授权记录到 `.photo_candidates/`
  - `tools/site-data/sold.json`：33 笔成交，`side` 为 buyer/seller/null；`market.json`：10 城市场数据
  - `tools/site-data/sj-zip-market.json`：同周期邮编数据，运行 `python3 tools/fetch_zip_market.py` 生成（需能访问 Redfin 数据文件）。有这个文件时页面用它，并去掉“预览版”提示；没有时用 `sj-zip-reference.json` 的历史参考数字
  - `tools/v2-content/transfer-tax.json`：卖房计算器的转让税
- 表单：`contact.html` → `/api/lead`（`api/lead.js`）→ Supabase `leads` 表 → Resend 邮件。环境变量 `RESEND_API_KEY`、`LEAD_NOTIFY_EMAIL`、可选 `LEAD_FROM_EMAIL`。只有写库成功才显示成功。本地 python 预览没有 /api，提交会显示失败，这是正常的；测试要用 Vercel 预览网址
- `api/keepalive.js` + `vercel.json` crons：防止 Supabase 暂停。`dashboard/`：客户咨询后台。`supabase/schema.sql`：建表
- 城市地图：OpenStreetMap、Census TIGERweb、Census Geocoder，在访客浏览器实时读取；学校招生范围不画图，只给学区官方入口
- 内容约定：不写通勤分钟数、学校排名、人口或族裔；市场数字必须写来源、口径、日期；不同来源或周期不混用；学校不保证；不写未确认的服务承诺、成绩、资格；公平住房；Redfin、Zillow 等房源照片不用于邮编页
- `tools/check_links.py`：检查全站外部链接（在能上网的终端运行）

## 运行和检查（已验证的命令）
- 本地预览：`cd ~/BQ2026/经纪人网站/jingchenhomes && python3 -m http.server 8000`，然后打开 http://localhost:8000
- 重新生成全站：`python3 tools/build_site.py && python3 tools/build_city_guides.py`
- 取邮编同周期数据：`python3 tools/fetch_zip_market.py`
- 检查外部链接：`python3 tools/check_links.py`
- 发布：`git add <本次文件> && git commit -m "..." && git push origin main`，Vercel 会自动上线

## 约定
- 联系方式、执照、成交、评价只能使用陈靖提供或已确认的内容。现有的成交和评价数据来源见 README
- 优先沿用现有的结构和样式，不更换框架
- 最终的推送由用户执行
