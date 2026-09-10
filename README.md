# Jing Chen Homes（绿色版）· 网站部署指南

这是根据你提供的绿色 Demo 重新做的完整版本，可以真实上线、真实收集客户留资。

## 这一版相比 Demo 稿做了什么

1. **加了 JC Team 的正式 logo**：放在导航栏和页脚，抠了透明底，深色/浅色导航状态下都清晰。
2. **修了标题"一个字占一行"的排版问题**：根本原因是"成交案例"标题那一行和页脚那一行用的是弹性布局（flex），在某些屏幕宽度下会被挤压到只剩一个字的宽度，导致标题被迫竖着一个字一行排列。现在改成标题至少保留一整行的空间，宽度不够时会整体换到下一行，而不是把字拆开——手机、平板、桌面各种宽度都测过，标题不会再被拆散。
3. **成交案例扩展成全部 33 笔真实记录**：数据来自 MLSListings 陈靖的经纪人主页（公开可查），首页显示最新 4 笔，"查看更多"按钮可以翻看剩余的 29 笔。每张卡片整体可点击，会在新标签页打开对应的真实房源页（详见下方"关于成交案例数据"一节）。
4. **新增"客户怎么说"评价板块**：内容是陈靖在 Zillow 上真实、可公开核实的认证评价（来自 zillow.com/profile/Jing727，目前 5.0 分 / 15 条评价），点击评分卡片或"查看全部评价"都会跳转到她真实的 Zillow 主页。**关于 Google 评价**：我没能找到一个可以直接核实、可嵌入的独立 Google 商家评价页面（她自己官网提到"5.0 Google Rating"但没有公开可核实的评价原文），所以这部分我没有编造具体评价内容——现在的处理是放了一个"Google 5.0 评分"入口，点击会跳转到 Google 搜索她的评价，方便访客自行核实。**如果你能提供陈靖 Google 商家资料（Google Business Profile）的分享链接**，或者几条真实评价的截图，我可以把这部分换成和 Zillow 评价一样、可以直接展示原文的真实卡片。
5. 图片做了压缩（webp 格式），"关于陈靖" lifestyle 大图从 813KB 压到 233KB，整体加载更快。
6. 表单从"演示提交"改成了真实写入数据库（做法和之前一致），加了隐藏防机器人字段。
7. 补了 SEO：用真实 logo 生成的网站图标、结构化数据、robots.txt、sitemap.xml。
8. 新增了私密的"客户咨询后台"（`/dashboard/`），陈靖登录后能直接看到网站表单收到的客户名单，不用给她 Supabase 账号（详见下方"客户咨询后台"一节）。
9. "湾区市场"板块从占位文字换成了真实内容：10 个核心城市近 3 个月成交中位价与同比变化的数据表、基于这些数据归纳的预算区间参考、10 个城市的基本特征介绍，以及 5 个真实可用的第三方买卖工具链接（房屋估值、月供计算、Closing Cost、Net Proceeds、Buyer Guide）（详见下方"关于湾区市场数据"一节）。

---

## 三步上线：Supabase → GitHub → Vercel

### 第 1 步：Supabase —— 建一个存放客户留资的数据库

1. 登录 [supabase.com](https://supabase.com) → **New project**，起个名字（比如 `jingchen-homes`），区域选离湾区近的（如 `West US`）。
2. 项目建好后，左侧 **SQL Editor → New query**，把仓库里 `supabase/schema.sql` 的全部内容粘贴进去，点 **Run**。这一步会建好 `leads` 表，并且设置好安全策略：网站访客只能新增自己的一条留资，看不到、也改不了别人的数据。
3. 左侧 **Project Settings → API**，复制 **Project URL** 和 **anon public** key。
4. 打开 `config.js`，把这两个值填进去：
   ```js
   window.CONFIG = {
     SUPABASE_URL: "https://xxxxxxxx.supabase.co",
     SUPABASE_ANON_KEY: "你复制的 anon public key",
   };
   ```

### 第 2 步：GitHub —— 建仓库、把代码传上去

```bash
cd jingchenhomes2
git init
git add .
git commit -m "Jing Chen Homes 绿色版首个版本"
```

去 GitHub 网页端 **New repository**（比如叫 `jingchenhomes`），然后：

```bash
git remote add origin https://github.com/你的用户名/jingchenhomes.git
git branch -M main
git push -u origin main
```

### 第 3 步：Vercel —— 一键部署上线

1. 登录 [vercel.com](https://vercel.com) → **Add New → Project**，选择刚才的仓库导入。
2. 纯静态网站，不需要任何构建设置，Framework 选 **Other**，直接 **Deploy**。
3. 几十秒后拿到 `xxx.vercel.app` 地址，网站已经真实上线。
4. 有自己的域名的话：项目 **Settings → Domains** 添加即可，Vercel 自动配 HTTPS。
5. **换域名后记得**把 `index.html` 里的 `og:url`、`canonical`、JSON-LD，以及 `robots.txt`、`sitemap.xml` 里的 `https://www.jingchenhomes.com/` 全部替换成真实域名，然后重新 `git push`。

---

## 上线前测试一遍表单

```bash
cd jingchenhomes2
python3 -m http.server 8000
```

打开 `http://localhost:8000`，提交一次测试表单，然后回 Supabase 的 **Table Editor → leads** 表确认这条数据进去了。

---

## 关于成交案例数据

现在展示的是陈靖近 3 年全部 33 笔真实成交记录，数据来自 MLSListings 经纪人主页（mlslistings.com/FindAnAgent/Profile/ClosedListings/02147119，公开可查）。首页默认显示最新 4 笔，"查看更多成交案例"按钮每点一次翻出 8 笔，翻完一轮后按钮变成"收起"。

其中 9 笔我额外核实了对应的 Zillow / Redfin / Homes.com 独立房源页并直接链接过去；剩下 24 笔因为没有一一核实到对应的独立房源页，链接统一指向 MLSListings 那个公开成交记录页面本身，保证每个链接都指向真实、可核实的来源，不会出现猜测或编造的链接。

（另外，MLSListings 原始数据里有一条"7564 Burnham Way, Dublin"，成交价只有 $4,000，明显是租赁记录混进了成交列表，不是真实卖房价格，我把这一条从展示里剔除了，避免误导访客。）

卡片上的房源缩略图，原来 4 张尝试直接引用 Zillow / Redfin / Homes.com 的图片地址（和原 Demo 一致的做法），这类第三方图片链接有时会失效或被平台屏蔽热链——代码里已经写好了失效时的优雅降级（自动隐藏图片，只保留文字信息卡片，不会显示破图标）；新加的 29 笔没有尝试配图，直接用文字卡片样式，视觉上和降级后的效果完全一致。如果想要 100% 稳定显示的房源图，最保险的做法是让陈靖把对外授权的房源照片发给你，换成 `images/` 目录下的本地图片。

## 关于客户评价内容的来源

评价板块目前展示的 6 条真实评价，原文引用自陈靖的 Zillow 认证客户评价页面（zillow.com/profile/Jing727，截至目前 5.0 分 / 15 条评价），逐字引用（她网站上完整可见），并附了跳转链接方便核实。Google 评价部分因为没找到可公开核实的独立评价原文，暂时只放了评分入口链接到 Google 搜索，没有编造具体评价内容——如果需要展示真实 Google 评价原文，请提供她的 Google 商家资料链接或截图，我会替换成真实内容。

---

## 客户咨询后台（给陈靖自己看客户留资，不用给她 Supabase 账号）

网站里新加了一个私密页面 `/dashboard/`，登录后能看到网站表单收到的所有客户咨询（跟你在 Supabase Table Editor 里看到的 `leads` 表内容一样），陈靖不需要注册 Supabase 账号、也碰不到你其他客户的项目数据。

**上线前需要做两件事：**

1. 在 Supabase 的 **SQL Editor** 里，把 `supabase/schema.sql` 最下面新加的第 5 部分（`Allow authenticated read` 那一段）跑一遍——如果你是整份文件重新跑一次也没问题，脚本可以重复执行。
2. 给陈靖建一个登录账号：Supabase 后台左侧 **Authentication → Users → Add user**，填她的邮箱，密码可以先设一个临时的告诉她，让她登录后自己在个人设置里改掉（Supabase Auth 目前没有内置"用户自己改密码"的现成页面，如果她想改密码，最简单的办法是你在 Authentication → Users 里直接帮她重设一个新的）。

设置好之后，陈靖访问 `https://jingchenhomes.vercel.app/dashboard/`（换成你正式域名的话就是 `https://homesbyjingchen.com/dashboard/`），输入邮箱密码登录，就能看到客户咨询列表了；这个页面没有放在导航栏里，也在 `robots.txt` 里可以考虑加一条不让搜索引擎收录（已经在页面里加了 `noindex`）。她登录的账号只能"查看"这一个项目的 `leads` 表，看不到、也改不了任何数据。

---

## 关于"湾区市场"板块的数据

"湾区市场"（首页导航"湾区市场"，锚点 `#market`）里的成交中位价数据来自 Redfin 各城市住房市场页面（Mountain View 交叉核对了 Zillow ZHVI），采集时间是 2026 年 9 月，页面上也标了 "Updated 2026.09" 的字样。**这类市场数据会随时间变化，建议每隔几个月找我或自己去 Redfin/Zillow 核对一次，更新 `index.html` 里 `id="market-report"` 这个表格的数字**，避免网站上挂着过期的价格误导访客。

"预算可以买哪里"和"城市与社区"两块内容是基于这份成交数据和公开的城市基本情况（比如 Cupertino 是 Apple 总部所在地、Mountain View 是 Google 总部所在地这类广为人知的事实）归纳整理的，不是逐字引用某个第三方报告。

"买卖工具"里的 5 个外部链接（Zillow 房屋估值、Bankrate 月供计算器、NerdWallet Closing Cost 计算器、HomeLight Net Proceeds 计算器、Bankrate Buyer Guide）都是发布前逐个打开验证过确实可用的免费公开工具，不是陈靖或 BQ Realty 自己开发的，页面上也用小字做了说明。

---

## 目录结构

```
jingchenhomes2/
├── index.html              网站主页
├── config.js                Supabase 公开配置
├── dashboard/index.html    客户咨询后台（陈靖登录查看留资用）
├── images/                   页面图片（含 logo.png 完整版、logo-nav.png 导航小图）
├── supabase/schema.sql      建表 + 权限脚本
├── favicon.svg / .ico / apple-touch-icon.png   用真实 logo 生成的网站图标
├── robots.txt / sitemap.xml
└── vercel.json               图片长期缓存配置
```

内容修改方式和之前一样：文案、图片都在 `index.html` 和 `images/` 里，改完 `git push` 一次，Vercel 会自动重新部署。
