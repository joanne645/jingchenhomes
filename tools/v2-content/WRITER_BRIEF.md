# V2 内容写作规范（文章批次共用）

网站：陈靖 Jing Chen，加州湾区 REALTOR®，BQ Realty，CA DRE #02147119，电话 925-917-4019。读者是湾区买家、卖家、房主，中文站和英文站各一份。今天是 2026-11-05。

## 每篇文章交付 3 个文件（目录 tools/v2-content/articles/）
- `<slug>.json`：
  {"slug":"...","category":"buy|sell|owner|area","reviewed":"2026-11-05",
   "zh":{"title":"页面标题","seo_title":"不超过30字｜陈靖","description":"70-110字摘要","lead":"导语，1-2句"},
   "en":{"title":"...","seo_title":"under 60 chars | Jing Chen","description":"120-155 chars","lead":"..."},
   "notice":null,            // 免责类型：null / "tax" / "legal" / "loan" / "tax-legal"
   "sources":[{"label":"机构：页面名","url":"https://..."}],  // 只列实际打开核对过的权威来源
   "related":["slug1","slug2","slug3"]}
- `<slug>.zh.html`、`<slug>.en.html`：正文片段（不含 h1、导语、免责、来源、CTA，这些由模板生成）。

## 允许的标签
h2 h3 p ul ol li strong em a；表格写成 `<div class="tablewrap"><table>…</table></div>`；提示框 `<aside class="note">…</aside>`。不要内联样式、不要图片、不要 h1。

## 站内链接（生成时按语言解析，中英文都用同样写法）
- 文章 `href="@article/<slug>"`　计算器 `href="@tool/buyer-costs"`、`href="@tool/net-proceeds"`
- 城市 `href="@city/dublin"`（slug：palo-alto cupertino sunnyvale mountain-view san-jose fremont milpitas dublin pleasanton san-ramon）
- 页面 `href="@page/contact"`、`@page/buy`、`@page/sell`、`@page/areas`、`@page/homeowner`、`@page/sold`、`@page/about`
外部链接写完整 https 地址。

## 全部文章 slug
buy：first-time-buyer-process, budget-preapproval, home-search, compare-cities, school-lookup, home-inspection, read-disclosures, cma-home-value, offer-strategy, escrow-closing, buyer-faq
sell：home-value-consultation, pre-listing-analysis, prep-and-repairs, staging-photography, marketing-plan, mls-online-exposure, open-house, offers-negotiation, seller-escrow-closing, sell-rental-property, seller-faq
owner：property-tax-insurance, maintenance-renovation, adu-basics, rental-management, sell-investment-property, 1031-exchange-basics, move-up-planning, holding-costs, home-value-tracking, owner-faq
area（已存在）：fremont-vs-dublin, dublin-vs-pleasanton, sunnyvale-vs-cupertino

## 内容硬规则（违反任何一条都算不合格）
1. 全部原创，不抄袭或改写其他网站文章。
2. 只写查证过的事实。凡州法、税率、金额上限、表格名称、期限，都要用 WebSearch/WebFetch 核对官方或权威来源（DRE、CAR、BOE、FTB、IRS、CFPB、FHFA、HCD、CDI、县估价官/县税务官等）后才能写，并标注"截至 2026 年 X 月"；查不到就写原则、指向官方入口，不写数字。会变的数字（贷款限额、税额门槛）一定带日期。
3. 绝不杜撰陈靖的成绩、经验年限、资格、合作方、成交案例、客户故事。不写"我们保证""最高价""最快""成交率"。
4. 不写服务承诺。陈靖实际包办哪些服务尚未确认，所以不写"陈靖免费提供 staging/专业摄影/装修垫资"之类。写法只能是"可以一起讨论/评估/规划""通常由……负责""是否采用要看房子情况"。唯一例外：可写"可预约免费的房屋估值咨询（CMA 讨论，不是正式估价）"。
5. 不预测房价、不保证学区、不保证投资回报、不推荐具体贷款机构/公司。佣金写"可协商，没有法定标准"。
6. 学校：绝不说某地址一定对应某学校，必须提示通过学区官方渠道按完整地址核实；不做学校优劣排名。
7. 公平住房：不以种族、族裔、宗教、家庭状况等描述或推荐社区；不用"华人多""适合有孩家庭""安全的社区"。
8. 税务、法律、贷款内容要说明一般信息性质（notice 字段由模板生成免责，正文里关键处仍提示咨询 CPA/律师/贷款专业人士）。
9. 陈靖是房地产经纪人，不是律师、CPA、贷款专员。
10. 文风：自然、具体、专业，像懂行的人在讲；避免 AI 腔、排比口号、"不仅……更……"、"在当今……"。中文读者是华人，专有名词保留英文（Escrow、Contingency、Disclosure、CMA、TDS）。
11. 每篇回答"这件事是什么、为什么重要、具体怎么做、常见坑、下一步"。中文约 700–1100 字（FAQ 约 8 问），英文是同内容的地道英文而不是逐字直译，约 450–750 词。
12. 不要在正文里写 CTA，模板会加。可以自然提到"可以和陈靖一起梳理"，每篇最多一次。
