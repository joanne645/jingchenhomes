# CLAUDE.md：陈靖个人网站（Jing Chen Homes）

## 基本信息
- 线上网址：https://jingchenhomes.vercel.app/
- 正式域名：https://www.homesbyjingchen.com/（主网址带 www；Vercel 已设置 homesbyjingchen.com 用 308 跳转到 www）。2026-09-24 起代码里的 canonical、og、JSON-LD、robots、sitemap 都统一用这个域名。这个域名原来指向一个 WordPress 旧站，改成 Vercel 需要在域名的 DNS 管理处修改记录
- GitHub：https://github.com/joanne645/jingchenhomes，分支 `main`
- 部署：Vercel 项目 `jingchenhomes`（团队 pinnacle2026）已连接 GitHub。推送到 `main` 后会自动部署，不需要另外手动部署
- Mac 上的本地仓库：`~/BQ2026/经纪人网站/jingchenhomes`（2026-09-24 建立，和 origin/main 同步）
- 技术：纯静态 HTML/CSS/JS，没有框架，也没有构建步骤和包管理器（Vercel Framework = Other）
- 表单和后台用 Supabase（通过 CDN 加载 supabase-js@2），公开配置在 `config.js`（只有 publishable key，没有私密密钥）

## 目录结构
- `index.html`：主页。所有样式和脚本都写在这个文件里
  - 版块锚点：`#top`、`#services`（买房/卖房）、`#homes`（找房，按钮跳转到 Zillow 城市搜索）、`#market`（`#market-report` 数据表 / `#market-budget` / `#market-cities` / `#market-tools`）、`#sold`（成交案例）、`#reviews`（客户评价）、`#about`、`#contact`（咨询表单 → Supabase `leads` 表）
- `en/index.html`：英文版主页（2026-09-24 新增）。内容与 `index.html` 一一对应，**改中文主页时要同步修改英文页**。图片、config.js、城市页用 `../` 相对路径引用；表单的“意向”选项 value 仍然用中文（买房/卖房/换房/投资/市场 / 其他），这样后台数据统一，source_url 会带 /en/
- 语言切换：两个页面导航栏里都有 `.lang-switch` 按钮（中文页显示 EN，英文页显示 中文），切换时会保留当前的版块锚点（#about 等）；页面里也加了 hreflang 标签
- `cities/palo-alto.html`：Palo Alto 城市详情页（主页 `#market-cities` 里的城市方框链接到这里）
- `dashboard/index.html`：客户咨询后台（Supabase Auth 登录后查看 leads，已加 noindex）
- `images/`：webp/png 图片；`vercel.json` 给图片设置了长期缓存（改图时要换文件名，否则浏览器可能继续显示旧图）
- `supabase/schema.sql`：建表脚本和 RLS 权限设置
- `README.md`：最初的部署说明（写的是“绿色版”，现在网站已改成深蓝主题）

## 运行和检查（已验证的命令）
- 本地预览：`cd ~/BQ2026/经纪人网站/jingchenhomes && python3 -m http.server 8000`，然后打开 http://localhost:8000
- 发布：`git add <本次文件> && git commit -m "..." && git push origin main`，Vercel 会自动上线

## 约定
- 联系方式、执照、成交、评价只能使用陈靖提供或已确认的内容。现有的成交和评价数据来源见 README
- 优先沿用现有的结构和样式，不更换框架
- 最终的推送由用户执行
