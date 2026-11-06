#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 V2 全站页面（城市中文页除外，由 build_city_guides.py 生成）。

用法（在项目根目录）：python3 tools/build_site.py

内容来源：
  tools/site-data/sold.json        成交记录
  tools/site-data/market.json      市场数据
  tools/v2-content/articles/       文章（<slug>.json + .zh.html + .en.html）
  tools/v2-content/en-cities/      英文城市页
  tools/v2-content/pages/          买房、卖房六步正文的英文
  tools/page-content/              买房、卖房正文的中文
  tools/v2-content/transfer-tax.json  卖房计算器用的转让税
本文件里的文案是各栏目首页、关于、联系等页面的文字。
只用 Python 自带库。
"""
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from site_chrome import SITE, ASSET_VER, PHONE, TEL, DRE, BROKER, esc, rel, path, alt_out, asset, font_links, nav, footer  # noqa

ROOT = Path(__file__).resolve().parent.parent
C = ROOT / 'tools' / 'v2-content'
TODAY = '2026-11-05'
SOLD = json.loads((ROOT / 'tools/site-data/sold.json').read_text(encoding='utf-8'))['records']
MK = json.loads((ROOT / 'tools/site-data/market.json').read_text(encoding='utf-8'))
SEO = json.loads((ROOT / 'tools/seo-meta.json').read_text(encoding='utf-8'))
_tt = C / 'transfer-tax.json'
TT = json.loads(_tt.read_text(encoding='utf-8')) if _tt.exists() else {'county_rate_per_1000': 1.10, 'cities': {}}

CITIES = [('palo-alto', 'Palo Alto'), ('cupertino', 'Cupertino'), ('sunnyvale', 'Sunnyvale'), ('mountain-view', 'Mountain View'), ('san-jose', 'San Jose'),
          ('fremont', 'Fremont'), ('milpitas', 'Milpitas'), ('dublin', 'Dublin'), ('pleasanton', 'Pleasanton'), ('san-ramon', 'San Ramon')]
CITY_CARD = {
    'zh': {'palo-alto': '两个 Caltrain 站和两条步行商业街，老街区、Eichler 社区与 Baylands 湿地同在一城。', 'cupertino': '背靠山麓、城内没有轨道站，日常沿 Stevens Creek Blvd 展开，以开车为主。',
           'sunnyvale': '两个 Caltrain 站加北部轻轨；南北片区的学区和通勤方向不同。', 'mountain-view': '两座 Caltrain 站和轻轨起点，Castro St 步行街，101 以北是 Shoreline 和办公园区。',
           'san-jose': '城市大、片区差别明显，先按办公地点和房型选定片区，再比较街道。', 'fremont': '两座 BART 站加 Dumbarton Bridge，七个片区的通勤方向各不相同。',
           'milpitas': 'BART 与轻轨同站换乘，站区新联排、老独立屋街区和东侧山麓并存。', 'dublin': 'I-580 北侧，两个 BART 站；西边是老城区，东边是带大型公园的新社区。',
           'pleasanton': 'Main Street 老城和周六农夫市集，北缘两座 BART 站，另有 ACE 火车。', 'san-ramon': '沿 I-680 展开，Bishop Ranch 是办公与商业核心；城内没有 BART 站。'},
    'en': {'palo-alto': 'Two Caltrain stations and two walkable main streets, with older neighborhoods, Eichler tracts and the Baylands in one city.', 'cupertino': 'Against the foothills with no rail station; daily life runs along Stevens Creek Blvd, mostly by car.',
           'sunnyvale': 'Two Caltrain stations plus light rail in the north; school districts and commute directions differ from north to south.', 'mountain-view': 'Two Caltrain stations and the light-rail terminus, pedestrian Castro Street, with Shoreline and office campuses north of 101.',
           'san-jose': 'Large and varied: choose a living area by office location and home type first, then compare streets.', 'fremont': 'Two BART stations and the Dumbarton Bridge; each of its seven areas commutes in a different direction.',
           'milpitas': 'BART and light rail share one station; newer townhomes near it, older single-family streets, and the east foothills.', 'dublin': 'North of I-580 with two BART stations; older neighborhoods to the west, newer communities with large parks to the east.',
           'pleasanton': 'Historic Main Street and a Saturday farmers’ market, two BART stations on the north edge, plus ACE trains.', 'san-ramon': 'Along I-680 with Bishop Ranch as its office and retail core; there is no BART station inside the city.'},
}
REVIEWS = [('shirleysh06', 'Jing is a very professional and reliable agent. She is also a very knowledgeable agent. She recently helped us selling our house in one week...'),
           ('Nidhi Palta', 'Jing has been nothing short of amazing throughout my home buying journey. As a first-time buyer in the US...'),
           ('Lei Qiao', 'I recently worked with Jing Chen for the purchase and leasing of my investment property on San Pablo Ave in Sunnyvale...'),
           ('sandygao33', 'I had a wonderful experience working with Jing as my real estate agent. She is incredibly professional, knowledgeable, and dedicated...'),
           ('Leo Wu', 'Jing Chen is an exceptional real estate agent with a proven track record of success. Her 5.0-star rating across 13 reviews is a testament to her dedication...'),
           ('Kim Lee', 'Unfortunately Zillow provide only a max of 5 star rating, that said I would have rated a 10 :-). On a more serious note, I first got to know Chen Jing last year...')]
ZILLOW = 'https://www.zillow.com/profile/Jing727'
MLS = 'https://www.mlslistings.com/FindAnAgent/Profile/ClosedListings/02147119'
BUY_ORDER = ['first-time-buyer-process', 'budget-preapproval', 'home-search', 'compare-cities', 'school-lookup', 'home-inspection', 'read-disclosures', 'cma-home-value', 'offer-strategy', 'escrow-closing', '@buyer-costs', 'buyer-faq']
SELL_ORDER = ['home-value-consultation', 'pre-listing-analysis', 'prep-and-repairs', 'staging-photography', 'marketing-plan', 'mls-online-exposure', 'open-house', 'offers-negotiation', 'seller-escrow-closing', '@net-proceeds', 'sell-rental-property', 'seller-faq']
OWNER_ORDER = ['property-tax-insurance', 'maintenance-renovation', 'adu-basics', 'rental-management', 'sell-investment-property', '1031-exchange-basics', 'move-up-planning', 'holding-costs', 'home-value-tracking', 'owner-faq']
GUIDES = ['fremont-vs-dublin', 'dublin-vs-pleasanton', 'sunnyvale-vs-cupertino']
CAT = {'zh': {'buy': '买房', 'sell': '卖房', 'owner': '房主', 'area': '城市比较'}, 'en': {'buy': 'Buying', 'sell': 'Selling', 'owner': 'Homeowners', 'area': 'City comparisons'}}
HUB = {'buy': 'buy.html', 'sell': 'sell.html', 'owner': 'homeowner.html', 'area': 'areas.html'}
HUBN = {'zh': {'buy': '买房指南', 'sell': '卖房服务', 'owner': '房主之家', 'area': '地区与学区'}, 'en': {'buy': 'Buy a Home', 'sell': 'Sell a Home', 'owner': 'Homeowner Resources', 'area': 'Areas & Schools'}}
TOOLS = {'buyer-costs': {'zh': ('买房费用计算器', '输入房价、首付、利率和税险，估算首付与交割所需现金，以及每月住房支出。'), 'en': ('Buyer Cost Calculator', 'Enter price, down payment, rate, tax and insurance to estimate cash to close and monthly housing cost.')},
         'net-proceeds': {'zh': ('Seller Net Proceeds 估算', '输入预计成交价和各项费用，估算卖房后的税前到手金额。'), 'en': ('Seller Net Proceeds Estimator', 'Enter an expected sale price and costs to estimate your pre-tax proceeds.')}}
NOTICE = {
    'zh': {'tax': '本文是一般信息，不构成税务建议。税务处理取决于个人情况，请咨询 CPA 或税务专业人士。', 'legal': '本文是一般信息，不构成法律建议。具体权利和义务以合同及适用法律为准，请咨询律师。',
           'loan': '本文是一般信息，不构成贷款建议或贷款承诺。利率、额度和条件以贷款机构为准，请咨询贷款专业人士。', 'tax-legal': '本文是一般信息，不构成税务或法律建议。具体情况请咨询 CPA、税务专业人士或律师。'},
    'en': {'tax': 'General information only, not tax advice. Tax treatment depends on your situation; please consult a CPA or tax professional.', 'legal': 'General information only, not legal advice. Your rights and duties depend on your contract and applicable law; please consult an attorney.',
           'loan': 'General information only, not lending advice or a loan commitment. Rates, amounts and terms are set by lenders; please consult a lending professional.', 'tax-legal': 'General information only, not tax or legal advice. Please consult a CPA, tax professional or attorney about your situation.'},
}


def load_articles():
    arts = {}
    for j in sorted((C / 'articles').glob('*.json')):
        s = j.stem
        m = json.loads(j.read_text(encoding='utf-8'))
        ok = all((C / 'articles' / f'{s}.{l}.html').exists() for l in ('zh', 'en'))
        if not ok:
            print('跳过（缺正文）:', s)
            continue
        m['slug'] = s
        arts[s] = m
    return arts


ARTS = load_articles()


def art_path(slug):
    return ('guides/' if ARTS.get(slug, {}).get('category') == 'area' else 'insights/') + slug + '.html'


def resolve(html, lang, out):
    def sub(m):
        kind, tail = m.group(1), m.group(2)
        frag = ''
        if kind == 'article':
            t = art_path(tail)
            if tail not in ARTS:
                print('  未知文章链接:', tail, 'in', out)
        elif kind == 'tool':
            t = f'calculators/{tail}.html'
        elif kind == 'city':
            t = f'cities/{tail}.html'
        elif kind == 'zip':
            t = 'areas/san-jose/index.html' if tail == 'index' else f'areas/san-jose/{tail}/index.html'
        else:
            q = ''
            for sep in ('?', '#'):
                if sep in tail:
                    tail, rest = tail.split(sep, 1)
                    q = sep + rest
                    break
            t = ('index' if tail == 'home' else tail) + '.html' + q
        return 'href="' + esc(rel(out, path(lang, t))).replace('&amp;amp;', '&amp;') + frag + '"'
    return re.sub(r'href="@(article|tool|city|page|zip)/([^"]+)"', sub, html)


def page(lang, out, title, desc, body, key='', ld=None, kind='website', noindex=False, image='images/about-agent.webp', pagekey='', has_alt=True):
    url = f'{SITE}/{out}'.replace('/index.html', '/')
    alt = f'{SITE}/{alt_out(out)}'.replace('/index.html', '/')
    zh_url, en_url = (url, alt) if lang == 'zh' else (alt, url)
    lds = ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False).replace('</', '<\\/') + '</script>' for x in (ld or []))
    hl = f'<link rel="alternate" hreflang="zh-CN" href="{zh_url}"><link rel="alternate" hreflang="en" href="{en_url}"><link rel="alternate" hreflang="x-default" href="{zh_url}">' if has_alt else ''
    html = f'''<!doctype html>
<html lang="{'zh-CN' if lang == 'zh' else 'en'}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="canonical" href="{url}">{hl}
<meta property="og:type" content="{kind}"><meta property="og:site_name" content="Jing Chen Homes 陈靖"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/{image}"><meta property="og:locale" content="{'zh_CN' if lang == 'zh' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{esc(rel(out, 'favicon.svg'))}" type="image/svg+xml"><link rel="icon" href="{esc(rel(out, 'favicon.ico'))}" sizes="any"><link rel="apple-touch-icon" href="{esc(rel(out, 'apple-touch-icon.png'))}">
{font_links()}
<link rel="stylesheet" href="{esc(asset(out, 'site.css'))}">
{lds}
</head>
<body class="v2" data-page="{esc(pagekey or key)}">
{nav(lang, out, key)}
<main id="main">
{resolve(body, lang, out)}
</main>
{footer(lang, out)}
<script src="{esc(asset(out, 'site.js'))}" defer></script>
</body></html>
'''
    f = ROOT / out
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(html, encoding='utf-8')
    PAGES.append(out)


PAGES = []


def hero(crumbs, h1, lead, kick='', btns='', meta=''):
    c = ''
    if crumbs:
        c = '<p class="crumb">' + ' / '.join(f'<a href="{h}">{esc(t)}</a>' if h else esc(t) for t, h in crumbs) + '</p>'
    k = f'<p class="kick">{esc(kick)}</p>' if kick else ''
    return f'<section class="vhero"><div class="wrap">{c}{k}<h1>{esc(h1)}</h1><p class="lead">{esc(lead)}</p>{btns}{meta}</div></section>'


def crumbs(lang, *items):
    home = ('首页' if lang == 'zh' else 'Home', '@HOME')
    return [home] + list(items)


def fix_home(html):
    return html.replace('href="@HOME"', 'href="@page/home"')


def cta(lang, h, p, ask='general', extra=''):
    label = '预约咨询' if lang == 'zh' else 'Contact Jing'
    return (f'<section class="ctaband"><div class="wrap"><div><h2>{esc(h)}</h2><p>{esc(p)}</p></div><div class="btns"><a class="b gold" href="@page/contact?type={ask}{extra}">{label} →</a>'
            f'<a class="b ghost" href="{TEL}">{PHONE}</a></div></div></section>')


def module_card(lang, slug, i):
    go = '阅读详情 →' if lang == 'zh' else 'Read more →'
    if slug.startswith('@'):
        k = slug[1:]
        t, d = TOOLS[k][lang]
        return f'<a class="card tool" href="@tool/{k}"><div class="no">{i:02d}</div><h3>{esc(t)}</h3><p>{esc(d)}</p><span class="go">{"打开工具 →" if lang == "zh" else "Open tool →"}</span></a>'
    if slug not in ARTS:
        print('  缺文章:', slug)
        return ''
    m = ARTS[slug][lang]
    return f'<a class="card" href="@article/{slug}"><div class="no">{i:02d}</div><h3>{esc(m["title"])}</h3><p>{esc(m["description"])}</p><span class="go">{go}</span></a>'


def fragment(name, lang):
    if lang == 'zh':
        t = (ROOT / 'tools/page-content' / f'{name}.html').read_text(encoding='utf-8')
        t = re.sub(r'<aside class="cta">.*?</aside>', '', t, flags=re.S)
        for g in GUIDES:
            t = t.replace(f'href="#{g}"', f'href="@article/{g}"')
        t = t.replace('href="#buy"', 'href="@page/buy"').replace('href="#sell"', 'href="@page/sell"').replace('href="#palo-alto"', 'href="@city/palo-alto"')
        return t
    return (C / 'pages' / f'{name}.en.html').read_text(encoding='utf-8')


def fmt_date(d, lang):
    y, m, day = d.split('-')
    if lang == 'zh':
        return f'{y} 年 {int(m)} 月 {int(day)} 日'
    return datetime.date(int(y), int(m), int(day)).strftime('%b %-d, %Y')


def prop_card(r, lang, out_attrs=True):
    z = lang == 'zh'
    meta = f'{r["beds"]:g} {"卧" if z else "bd"} · {r["baths"]:g} {"卫" if z else "ba"} · {r["sqft"]:,} sqft'
    side = {'buyer': '代表买方' if z else 'Represented buyer', 'seller': '代表卖方' if z else 'Represented seller'}.get(r['side'], '')
    img = (f'<div class="ph"><img src="{esc(r["image"])}" alt="{esc(r["address"])}" loading="lazy" referrerpolicy="no-referrer" data-hide-on-error></div>' if r['image'] else '')
    attrs = f' data-city="{esc(r["city"])}" data-year="{r["date"][:4]}" data-price="{r["price"]}" data-side="{r["side"] or "unknown"}"'
    return (f'<a class="prop" href="{esc(r["url"])}" target="_blank" rel="noopener"{attrs}>{img}<div class="pi"><span class="bd">{"成交" if z else "SOLD"} · {esc(fmt_date(r["date"], lang))}</span>'
            f'<h3>{esc(r["address"])}</h3><span class="m">{esc(meta)}</span>' + (f'<span class="side">{esc(side)}</span>' if side else '') + f'<span class="pr">${r["price"]:,}</span></div></a>')


def review_cards(lang, items):
    src = 'Zillow 认证评价' if lang == 'zh' else 'Verified on Zillow'
    return ''.join(f'<a class="rv" href="{ZILLOW}" target="_blank" rel="noopener"><span class="st" aria-label="5 stars">★★★★★</span><p>“{esc(q)}”</p><span class="who">{esc(n)} · {src} ↗</span></a>' for n, q in items)


def city_cards(lang, price=False):
    z = lang == 'zh'
    out = ''
    for s, n in CITIES:
        pm = ''
        if price:
            c = MK['cities'][s]
            med = c.get('median_en', c['median']) if not z else c['median']
            pm = f'<span class="pm">{"成交中位价" if z else "Median sale"} {esc(med)}</span>'
        out += f'<a class="cityc" href="@city/{s}"><h3>{esc(n)}</h3><p>{esc(CITY_CARD[lang][s])}</p>{pm}</a>'
    return out


def market_table(lang):
    z = lang == 'zh'
    order = sorted(MK['cities'], key=lambda k: list(MK['cities']).index(k))
    names = dict(CITIES)
    rows = ''
    for s in order:
        c = MK['cities'][s]
        med = c['median'] if z else c.get('median_en', c['median'])
        yoy = c['yoy_zh'] if z else c['yoy_en']
        rows += f'<tr><td><a href="@city/{s}">{esc(names[s])}</a></td><td>{esc(med)}</td><td class="{c["dir"]}">{esc(yoy)}</td></tr>'
    th = ('城市', '近 3 个月成交中位价', '同比变化') if z else ('City', '3-month median sale price', 'Year over year')
    return f'<div class="tablewrap"><table><thead><tr><th>{th[0]}</th><th>{th[1]}</th><th>{th[2]}</th></tr></thead><tbody>{rows}</tbody></table></div>'


def market_note(lang):
    if lang == 'zh':
        return f'<p class="src-note">来源：{esc(MK["source_zh"])}。统计口径：{esc(MK["method_zh"])}更新时间：{esc(MK["updated_zh"])}。这是城市层面的概括数字，不是任何一套房屋的估值，也不代表未来走势。</p>'
    return f'<p class="src-note">Source: {esc(MK["source_en"])}. Method: {esc(MK["method_en"])} Updated: {esc(MK["updated_en"])}. These are citywide summaries, not a valuation of any home or a forecast.</p>'


def lead_form(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    entries = [('买房', L('我要买房', 'Buy a home'), L('预算、城市和看房计划', 'Budget, cities and tours')), ('卖房', L('我要卖房', 'Sell a home'), L('定价、准备和上市安排', 'Pricing, prep and listing')),
               ('估值', L('免费房屋估值', 'Free home value consultation'), L('讨论可比成交，不是正式估价', 'A comparable-sales talk, not an appraisal')), ('换房', L('换房规划', 'Plan a move'), L('两笔交易的顺序和资金', 'Sequence and funds for two deals')),
               ('投资', L('投资咨询', 'Investment property'), L('区域、租金和持有成本', 'Area, rent and holding costs')), ('其他', L('一般咨询', 'General question'), L('想先了解市场或流程', 'Market or process questions'))]
    btn = ''.join(f'<button class="entry" type="button" data-intent="{v}" aria-pressed="false"><strong>{esc(t)}</strong><span>{esc(d)}</span></button>' for v, t, d in entries)
    opts = f'<option value="">{L("请选择", "Please choose")}</option>' + ''.join(f'<option value="{v}">{esc(t)}</option>' for v, t, _ in entries)
    copt = f'<option value="">{L("未确定", "Not sure yet")}</option>' + ''.join(f'<option>{n}</option>' for _, n in CITIES) + f'<option>{L("其他城市", "Other")}</option>'
    return f'''<div class="grid g3" style="margin-bottom:26px" role="group" aria-label="{L('选择咨询类型', 'Choose a topic')}">{btn}</div>
<div class="formbox">
<div class="okbox" id="formOk" hidden><h2>{L('已收到你的咨询', 'We received your message')}</h2><p>{L('陈靖会尽快与你联系。如果比较急，可以直接拨打 ', 'Jing will get back to you soon. If it is urgent, call ')}<a href="{TEL}">{PHONE}</a>{'。' if z else '.'}</p></div>
<form id="leadForm" novalidate>
<div class="alert" id="formAlert" role="alert" tabindex="-1" hidden></div>
<div class="form-grid">
<div class="field"><label for="fName">{L('姓名', 'Name')} <i>*</i></label><input id="fName" name="name" autocomplete="name" required maxlength="100"><span class="err"></span></div>
<div class="field"><label for="fIntent">{L('需求类型', 'Topic')} <i>*</i></label><select id="fIntent" name="intent" required>{opts}</select><span class="err"></span></div>
<div class="field"><label for="fPhone">{L('电话', 'Phone')}</label><input id="fPhone" name="phone" type="tel" autocomplete="tel" maxlength="40"><span class="err"></span></div>
<div class="field"><label for="fEmail">Email</label><input id="fEmail" name="email" type="email" autocomplete="email" maxlength="160"><span class="err"></span></div>
<div class="field full"><label for="fCity">{L('意向城市', 'City of interest')}</label><select id="fCity" name="city">{copt}</select></div>
<div class="field full"><label for="fMsg">{L('留言', 'Message')}</label><textarea id="fMsg" name="message" maxlength="3000"></textarea></div>
<input class="hp" type="text" name="company_website" tabindex="-1" autocomplete="off" aria-hidden="true">
</div>
<p class="fnote">{L('电话和 Email 至少填写一项。', 'Please give a phone number or an email.')}</p>
<button class="b fill" id="leadSubmit" type="submit" style="width:100%;margin-top:14px">{L('提交咨询', 'Send message')}</button>
<p class="fnote">{L('提交即表示你同意陈靖通过你留下的方式联系你。信息只用于跟进你的房地产咨询，详见', 'By sending this form you agree that Jing may contact you using the details provided. Your information is used only to follow up on your inquiry. See the')}<a href="@page/privacy">{L('隐私说明', 'privacy notice')}</a>{'。' if z else '.'}</p>
</form></div>'''


# ---------- 各页面 ----------
def build_home(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    out = path(lang, 'index.html')
    feat = [r for r in SOLD if r['image']][:4]
    latest = [s for s in ['first-time-buyer-process', 'home-value-consultation', 'adu-basics'] if s in ARTS]
    entries = [('buy', L('买房指南', 'Buy a Home'), L('从预算、城市和学校查询开始，一步步走到 Escrow 和入住。', 'From budget, cities and school lookup through escrow and move-in.')),
               ('sell', L('卖房服务', 'Sell a Home'), L('把定价依据、上市准备、Offer 比较和时间表连起来。', 'Connect pricing, preparation, offer review and timing.')),
               ('areas', L('地区与学区', 'Areas & Schools'), L('10 个城市的片区、通勤、官方学校查询入口和市场数据。', 'Neighborhoods, commutes, official school lookups and market data for 10 cities.')),
               ('homeowner', L('房主之家', 'Homeowner Resources'), L('房产税、保险、维护、ADU、出租和 1031 基础知识。', 'Property tax, insurance, upkeep, ADUs, rentals and 1031 basics.')),
               ('insights', L('地产知识', 'Insights'), L('按主题查找文章，所有内容标明更新日期。', 'Search articles by topic, each with its review date.'))]
    cards = ''.join(f'<a class="card" href="@page/{k}"><h3>{esc(t)}</h3><p>{esc(d)}</p><span class="go">{L("进入", "Explore")} →</span></a>' for k, t, d in entries)
    ld = {"@context": "https://schema.org", "@type": "RealEstateAgent", "name": "Jing Chen 陈靖", "url": SITE + '/', "image": SITE + "/images/about-agent.webp", "telephone": "+1-925-917-4019",
          "areaServed": [n for _, n in CITIES] + ["Silicon Valley", "East Bay", "Tri-Valley"], "worksFor": {"@type": "Organization", "name": BROKER}, "identifier": f"CA DRE #{DRE}"}
    h1 = '湾区买房与卖房，<br><span>从看懂城市和房子开始</span>' if z else 'Buying and selling in the Bay Area <span>starts with understanding the city and the home</span>'
    lead = L('同样的预算，不同的城市、社区和房屋类型，会带来不同的日常生活。陈靖提供加州湾区买房、卖房与换房服务，陪你把通勤、学校、居住空间和持有成本放在一起比较。',
             'The same budget buys a different daily life in each city, neighborhood and home type. Jing helps Bay Area buyers, sellers and movers weigh commute, schools, space and holding costs together.')
    body = f'''<section class="home-hero"><div class="wrap hh-grid"><div class="hh-copy">
<p class="hh-name">陈靖 Jing Chen<span>{L('加州湾区买房、卖房与城市选择', 'Bay Area home buying, selling and city selection')}</span></p>
<h1>{h1}</h1><p class="hh-lead">{esc(lead)}</p>
<div class="btns"><a class="b gold" href="@page/buy">{L('我想在湾区买房', 'I want to buy')} →</a><a class="b ghost" href="@page/sell">{L('我准备卖房', 'I plan to sell')} →</a><a class="b ghost" href="@page/contact">{L('聊聊我的计划', 'Talk about my plan')} →</a></div>
<div class="hh-meta"><span>REALTOR® · {BROKER}</span><span>DRE #{DRE}</span><span>Silicon Valley · East Bay · Tri-Valley</span></div>
</div><div class="hh-photo"><img src="{esc(rel(out, 'images/hero.webp'))}" alt="{L('陈靖 Jing Chen 肖像', 'Portrait of Jing Chen')}" width="1199" height="1800" fetchpriority="high"></div></div></section>

<section class="band"><div class="wrap"><p class="kick">START HERE</p><h2 class="h2">{L('先明确你的下一步', 'Start with your next step')}</h2>
<p class="sub">{L('每个栏目都有独立页面，先进入你现在最需要的那一部分。', 'Each topic has its own section. Go straight to what you need now.')}</p><div class="grid g5">{cards}</div></div></section>

<section class="band white"><div class="wrap"><div class="head-row"><div><p class="kick">REAL TRANSACTIONS</p><h2 class="h2">{L('精选真实成交', 'Selected real sales')}</h2>
<p class="sub">{L(f'近 3 年公开可查的 {len(SOLD)} 笔成交记录，数据来自 MLSListings 和公开房源页面。', f'{len(SOLD)} publicly verifiable sales over about three years, from MLSListings and public listing pages.')}</p></div>
<a class="b line" href="@page/sold">{L('查看全部成交', 'See all sales')} →</a></div><div class="grid g4">{''.join(prop_card(r, lang) for r in feat)}</div></div></section>

<section class="band"><div class="wrap"><div class="head-row"><div><p class="kick">CLIENT REVIEWS</p><h2 class="h2">{L('客户怎么说', 'What clients say')}</h2>
<p class="sub">{L('摘自陈靖在 Zillow 上的认证评价（5.0 分，15 条），点击可查看原文。', 'Excerpts from Jing’s verified Zillow reviews (5.0 from 15 reviews). Click to read the originals.')}</p></div>
<a class="b line" href="@page/about#reviews">{L('更多评价', 'More reviews')} →</a></div><div class="grid g3">{review_cards(lang, REVIEWS[:3])}</div></div></section>

<section class="band white"><div class="wrap"><div class="head-row"><div><p class="kick">AREAS &amp; SCHOOLS</p><h2 class="h2">{L('认识城市，也认识你未来的一周', 'Know the city and your future week')}</h2></div>
<a class="b line" href="@page/areas">{L('地区与学区总览', 'All areas and schools')} →</a></div><div class="grid g5">{city_cards(lang)}</div></div></section>

{('<section class="band"><div class="wrap"><div class="head-row"><div><p class="kick">INSIGHTS</p><h2 class="h2">' + L('从这几篇开始', 'Good places to start') + '</h2></div><a class="b line" href="@page/insights">' + L('全部文章', 'All articles') + ' →</a></div><div class="grid g3">' + ''.join(module_card(lang, s, i + 1) for i, s in enumerate(latest)) + '</div></div></section>') if latest else ''}

<section class="band tint"><div class="wrap split"><img src="{esc(rel(out, 'images/value.webp'))}" alt="{L('陈靖 Jing Chen', 'Jing Chen')}" width="960" height="1440" loading="lazy"><div>
<p class="kick">ABOUT JING</p><h2 class="h2">{L('关于陈靖', 'About Jing')}</h2>
<p class="quote">{L('“房地产交易，不只是找到一套房子。真正重要的是，在信息复杂、金额巨大的决定面前，把风险、机会与选择讲清楚。”', '“A real estate transaction is more than finding a house. What really matters is making the risks, opportunities and choices clear when you face a complex, high-stakes decision.”')}</p>
<a class="b line" href="@page/about">{L('了解陈靖', 'Meet Jing')} →</a></div></div></section>
{cta(lang, L('你的下一步是什么？', 'What is your next step?'), L('已经准备开始，或者只是想了解市场，都可以先告诉陈靖你的情况。', 'Whether you are ready to start or just want to understand the market, tell Jing about your situation.'))}'''
    title = SEO['home']['title'] if z else 'Jing Chen | Bay Area Realtor | Buy and Sell in Silicon Valley'
    desc = SEO['home']['description'] if z else f'Jing Chen, REALTOR® with BQ Realty, DRE #{DRE}. Bay Area home buying and selling service in English and Chinese, built around cities, schools and commutes.'
    page(lang, out, title, desc, body, key='', pagekey='home', ld=[ld])


def hub(lang, name, key, title, desc, h1, lead, kick, body, ask, btn_label):
    z = lang == 'zh'
    out = path(lang, name)
    btns = f'<div class="btns"><a class="b gold" href="@page/contact?type={ask}">{esc(btn_label)} →</a><a class="b ghost" href="{TEL}">{PHONE}</a></div>'
    h = fix_home(hero(crumbs(lang, (HUBN[lang].get({'homeowner': 'owner', 'areas': 'area'}.get(key, key), ''), None)), h1, lead, kick, btns))
    page(lang, out, title, desc, h + body, key=key, ld=[breadcrumb(lang, [(HUBN[lang].get({'homeowner': 'owner', 'areas': 'area'}.get(key, key), ''), out)])])


def breadcrumb(lang, items):
    lst = [{"@type": "ListItem", "position": 1, "name": '首页' if lang == 'zh' else 'Home', "item": f'{SITE}/{path(lang, "")}'}]
    for i, (n, p) in enumerate(items):
        lst.append({"@type": "ListItem", "position": i + 2, "name": n, "item": f'{SITE}/{p}'})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": lst}


def build_buy(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    cards = ''.join(module_card(lang, s, i + 1) for i, s in enumerate(BUY_ORDER))
    copt = ''.join(f'<option>{n}</option>' for _, n in CITIES)
    body = f'''<section class="band"><div class="wrap"><p class="kick">BUYER GUIDE</p><h2 class="h2">{L('买房 12 个模块', '12 topics for buyers')}</h2><p class="sub">{L('按流程排列。每个模块都有一篇详细说明，也可以直接打开费用计算器。', 'Listed in the order you are likely to need them. Each topic links to a full guide, and the cost calculator is ready to use.')}</p><div class="grid g3">{cards}</div></div></section>
<section class="band dark" id="search"><div class="wrap"><div class="grid g2" style="align-items:center"><div><p class="kick">HOME SEARCH</p><h2 class="h2">{L('开始看房源', 'Start looking at homes')}</h2><p class="sub">{L('先按城市看在售房源，点击后会打开 Zillow 对应城市的搜索页，可以在页面内继续按预算和房型筛选。想要按你的条件整理的 MLS 房源清单，可以直接联系陈靖。', 'Browse by city. The button opens the Zillow search page for that city, where you can filter by budget and home type. For a tailored MLS list, contact Jing directly.')}</p></div>
<div class="formbox" style="color:var(--ink)"><div class="field"><label for="searchCity">{L('城市', 'City')}</label><select id="searchCity">{copt}</select></div><button class="b fill" id="searchGo" type="button" style="width:100%;margin-top:14px">{L('打开 Zillow 查看在售房源', 'Open homes on Zillow')} ↗</button><p class="fnote">{L('外部网站，房源信息由 Zillow 提供，不代表陈靖或 BQ Realty 的房源。', 'External site. Listings are provided by Zillow and are not necessarily listed by Jing or BQ Realty.')}</p></div></div></div></section>
<section class="band white"><div class="narrow"><p class="kick">{L('六个步骤', 'SIX STEPS')}</p><h2 class="h2">{L('在湾区买房，可以这样走', 'A practical path to buying in the Bay Area')}</h2><div class="prose" style="margin-top:28px">{fragment('buy', lang)}</div></div></section>
{cta(lang, L('从你的预算、工作地点和入住时间开始', 'Start with your budget, work location and move-in time'), L('告诉陈靖你的预算范围、工作地点、意向城市和时间安排，一起确定下一步需要比较的社区或房源。', 'Share your budget range, work location, cities of interest and timing, and decide together which neighborhoods or homes to compare next.'), 'buy')}'''
    hub(lang, 'buy.html', 'buy', SEO['buy']['title'] if z else 'Bay Area Home Buying Guide | Jing Chen', SEO['buy']['description'] if z else 'A step-by-step Bay Area buyer guide: budget, pre-approval, cities, school lookup, inspections, disclosures, offers and closing.',
        SEO['buy']['h1'] if z else 'Buying a home in the Bay Area', SEO['buy']['lead'] if z else 'From budget and city choice through inspections, offers and closing, with practical guides for each step.', 'BUY A HOME', body, 'buy', L('讨论我的买房计划', 'Talk about buying'))


def build_sell(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    cards = ''.join(module_card(lang, s, i + 1) for i, s in enumerate(SELL_ORDER))
    steps = [(L('了解目标', 'Understand your goals'), L('房屋、时间和优先顺序', 'The home, timing and priorities')), (L('定价分析', 'Pricing analysis'), L('可比成交和当前竞争', 'Comparable sales and competition')), (L('上市准备', 'Preparation'), L('按影响和预算排序', 'Ranked by impact and budget')),
             (L('上市展示', 'Listing and showings'), L('MLS、线上信息和看房', 'MLS, online exposure and showings')), (L('比较 Offer', 'Offer review'), L('价格和执行条件一起看', 'Price and terms together')), (L('Escrow 到交割', 'Escrow to closing'), L('按合同节点推进', 'Contract milestones')) ]
    st = ''.join(f'<div class="card"><div class="no">{i + 1:02d}</div><h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for i, (a, b) in enumerate(steps))
    body = f'''<section class="band"><div class="wrap"><p class="kick">THE PROCESS</p><h2 class="h2">{L('卖房的六个阶段', 'Six stages of selling')}</h2><p class="sub">{L('每一步都要有依据：先把信息讲清楚，再决定投入和时间。', 'Each step should rest on facts: get the information clear, then decide what to spend and when.')}</p><div class="grid g3">{st}</div></div></section>
<section class="band white"><div class="wrap"><p class="kick">SELLER GUIDE</p><h2 class="h2">{L('卖房 12 个模块', '12 topics for sellers')}</h2><p class="sub">{L('包含免费房屋估值咨询、上市准备、营销、Offer 比较、出租房出售等内容，以及净收益估算工具。', 'Including free home value consultation, preparation, marketing, offer review, selling a rental and a net proceeds estimator.')}</p><div class="grid g3">{cards}</div></div></section>
<section class="band"><div class="narrow"><p class="kick">{L('详细说明', 'IN DETAIL')}</p><h2 class="h2">{L('卖房时要想清楚的事', 'What to think through when selling')}</h2><div class="prose" style="margin-top:28px">{fragment('sell', lang)}</div></div></section>
{cta(lang, L('让上市计划配合你的下一步', 'Fit the listing plan to your next step'), L('提供房屋地址、预计出售时间和目前最关心的问题，与陈靖讨论定价依据和上市准备的顺序。', 'Share your address, expected timing and main concerns, and talk through the basis for pricing and the order of preparation.'), 'valuation')}'''
    hub(lang, 'sell.html', 'sell', SEO['sell']['title'] if z else 'Bay Area Home Selling Guide | Jing Chen', SEO['sell']['description'] if z else 'Bay Area seller guide: home value consultation, market analysis, preparation, marketing, offer review, escrow and net proceeds.',
        SEO['sell']['h1'] if z else 'Selling a home in the Bay Area', SEO['sell']['lead'] if z else 'Connect pricing, preparation, marketing and timing so each decision has a clear basis.', 'SELL A HOME', body, 'valuation', L('预约免费房屋估值咨询', 'Book a free home value consultation'))


def build_areas(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    tiers = [('$1.3M – $1.6M', L('San Jose、Milpitas、Dublin、Fremont、San Ramon、Pleasanton 等城市的成交中位价大致落在这个区间。', 'Median sale prices in San Jose, Milpitas, Dublin, Fremont, San Ramon and Pleasanton fall roughly in this range.')),
             ('$1.7M – $2M', L('Sunnyvale、Mountain View 的成交中位价在这个区间。', 'Sunnyvale and Mountain View medians fall in this range.')),
             (L('$3M 以上', '$3M and above'), L('Cupertino、Palo Alto 的成交中位价在 $3M 以上。', 'Cupertino and Palo Alto medians are above $3M.'))]
    t = ''.join(f'<div class="card"><h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for a, b in tiers)
    guides = ''.join(module_card(lang, g, i + 1) for i, g in enumerate(GUIDES))
    extra = ''.join(module_card(lang, s, i + 4) for i, s in enumerate(['compare-cities', 'school-lookup']))
    body = f'''<section class="band" id="cities"><div class="wrap"><p class="kick">10 CITIES</p><h2 class="h2">{L('十个城市，各有一份指南', 'A guide for each of 10 cities')}</h2><p class="sub">{L('每个城市都包括城市简介、片区特点、房屋类型、房价数据、交通通勤、学校查询入口、生活配套、近期真实成交和相关文章。', 'Each guide covers the city, neighborhoods, home types, price data, commuting, official school lookups, daily life, recent sales and related articles.')}{'' if z else ' English guides are concise editions; the most detailed versions are in Chinese.'}</p><div class="grid g4">{city_cards(lang, True)}</div></div></section>
<section class="band tint" id="san-jose-zip"><div class="wrap"><div class="head-row"><div><p class="kick">SAN JOSE BY ZIP CODE</p><h2 class="h2">{L('San Jose 各邮编市场分析', 'San Jose by ZIP code')}</h2><p class="sub">{L('San Jose 城市大、差异明显。按邮编了解 Berryessa、Cambrian、Almaden Valley 等地区的房屋特点和买卖要点。', 'San Jose is large and varied. Read what buyers and sellers should know, ZIP code by ZIP code, in Berryessa, Cambrian, Almaden Valley and more.')}</p></div><a class="b fill" href="@zip/index">{L('查看邮编分析', 'See ZIP code analysis')} →</a></div></div></section>
<section class="band white" id="schools"><div class="narrow"><p class="kick">SCHOOLS</p><h2 class="h2">{L('学校要按完整地址查询', 'Check schools by full address')}</h2><div class="note">{L('本网站不保证任何地址对应特定学校。城市、邮编、学区和招生范围是不同的边界，学校安排也可能调整。请按完整地址在学区官方渠道查询，并向学区确认入学和实际安置。各学区官方入口列在对应城市页。', 'This site does not guarantee that any address is assigned to a particular school. City limits, ZIP codes, districts and attendance boundaries differ, and assignments can change. Look up the full address through official district channels and confirm enrollment and placement with the district. Official links are on each city page.')}</div></div></section>
<section class="band" id="market"><div class="wrap"><p class="kick">MARKET DATA</p><h2 class="h2">{L('各城市成交中位价', 'Median sale prices by city')}</h2>{market_table(lang)}{market_note(lang)}</div></section>
<section class="band white" id="budget"><div class="wrap"><p class="kick">BUDGET</p><h2 class="h2">{L('预算可以买哪里', 'Where a budget can go')}</h2><div class="grid g3">{t}</div><p class="src-note" style="margin-top:16px">{L('以上区间根据上表的成交中位价粗略归纳。同一城市内不同社区、地块大小、房屋新旧的价格差异仍然很大，不能代替针对具体预算和目标区域的规划。', 'These ranges are a rough summary of the medians above. Prices vary widely within a city by neighborhood, lot size and age, so this is no substitute for planning around your own budget and target areas.')}</p></div></section>
<section class="band" id="compare"><div class="wrap"><p class="kick">COMPARE</p><h2 class="h2">{L('两座城市之间，怎么做选择？', 'How to choose between two cities')}</h2><div class="grid g3">{guides}{extra}</div></div></section>
{cta(lang, L('把范围缩小到几个片区，再到几套房', 'Narrow it to a few neighborhoods, then a few homes'), L('告诉陈靖你的预算、办公地点、交通方式和住房要求，一起比较。', 'Share your budget, office location, commute and housing needs, and compare together.'), 'compare')}'''
    hub(lang, 'areas.html', 'areas', L('湾区地区与学区指南｜10 个城市｜陈靖', 'Bay Area Cities and Schools Guide | Jing Chen'), L('湾区 10 个城市的片区、通勤、学校官方查询入口、成交中位价和近期成交。学校信息请按完整地址向学区核实。', 'Neighborhoods, commutes, official school lookups, median prices and recent sales for 10 Bay Area cities. Always verify schools by full address.'),
        L('地区与学区资源中心', 'Areas and schools resource center'), L('城市名只是起点。这里把片区、通勤、学校查询和市场数据放在一起，帮你判断哪里值得实地看。', 'A city name is only a starting point. Here neighborhoods, commutes, school lookup and market data sit together so you can decide where to visit.'), 'AREAS & SCHOOLS', body, 'compare', L('让陈靖帮我比较城市', 'Compare cities with Jing'))


def build_owner(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    cards = ''.join(module_card(lang, s, i + 1) for i, s in enumerate(OWNER_ORDER))
    body = f'''<section class="band"><div class="wrap"><p class="kick">HOMEOWNER RESOURCES</p><h2 class="h2">{L('10 个房主专题', '10 topics for homeowners')}</h2><div class="note" style="max-width:820px">{L('税务、法律和贷款相关内容仅供一般信息参考，具体事项请咨询 CPA、律师或贷款专业人士。', 'Tax, legal and lending topics are for general information only. Please consult a CPA, attorney or lending professional about your situation.')}</div><div class="grid g3" style="margin-top:24px">{cards}</div></div></section>
{cta(lang, L('想知道现在的房子适合继续持有、出租还是换房？', 'Wondering whether to hold, rent out or move?'), L('把房屋情况和接下来几年的计划告诉陈靖，一起梳理可以考虑的方向。', 'Share your home and your plans for the next few years, and sort through the options together.'), 'swap')}'''
    hub(lang, 'homeowner.html', 'homeowner', L('房主之家｜房产税、保险、ADU、出租与 1031｜陈靖', 'Homeowner Resources: Tax, ADU, Rentals, 1031 | Jing Chen'), L('加州房主常用知识：房产税与保险、维护装修、ADU、出租管理、投资房出售、1031、换房规划、持有成本和房屋估值。', 'Practical guides for California homeowners: property tax, insurance, upkeep, ADUs, rentals, selling investment property, 1031 basics and holding costs.'),
        L('房主之家', 'Homeowner resources'), L('买下房子以后，还有税、保险、维护、出租和换房这些事。这里按主题整理成可以随时查的资料。', 'After you buy, there are still taxes, insurance, upkeep, rentals and future moves. These guides are organized so you can look things up when you need them.'), 'HOMEOWNERS', body, 'swap', L('讨论换房或持有计划', 'Talk about my plans'))


def build_sold(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    cities = sorted({r['city'] for r in SOLD})
    years = sorted({r['date'][:4] for r in SOLD}, reverse=True)
    nb = sum(r['side'] == 'buyer' for r in SOLD)
    ns = sum(r['side'] == 'seller' for r in SOLD)
    prices = [('', L('全部价格', 'Any price')), ('0-1000000', L('$100 万以下', 'Under $1M')), ('1000000-1500000', '$1M – $1.5M'), ('1500000-2000000', '$1.5M – $2M'), ('2000000-3000000', '$2M – $3M'), ('3000000-', L('$300 万以上', '$3M and up'))]
    fopt = lambda ls: ''.join(f'<option value="{esc(v)}">{esc(t)}</option>' for v, t in ls)
    body = fix_home(hero(crumbs(lang, (L('成交案例', 'Sold Properties'), None)), L('陈靖的真实成交记录', 'Jing Chen’s real sales record'), L(f'{len(SOLD)} 笔公开可查的成交，可按城市、年份、价格和交易类型筛选。每张卡片都链接到公开来源，方便你核实。', f'{len(SOLD)} publicly verifiable sales you can filter by city, year, price and transaction type. Each card links to a public source.'), 'SOLD PROPERTIES')) + f'''
<section class="band"><div class="wrap"><div class="filters" role="search" aria-label="{L('筛选成交', 'Filter sales')}">
<label>{L('城市', 'City')}<select id="fCity">{fopt([('', L('全部城市', 'All cities'))] + [(c, c) for c in cities])}</select></label>
<label>{L('年份', 'Year')}<select id="fYear">{fopt([('', L('全部年份', 'All years'))] + [(y, y) for y in years])}</select></label>
<label>{L('价格', 'Price')}<select id="fPrice">{fopt(prices)}</select></label>
<label>{L('交易类型', 'Transaction type')}<select id="fSide">{fopt([('', L('全部类型', 'All types')), ('buyer', L(f'代表买方（已标注 {nb} 笔）', f'Represented buyer ({nb} labeled)')), ('seller', L(f'代表卖方（已标注 {ns} 笔）', f'Represented seller ({ns} labeled)'))])}</select></label>
</div><p class="count" id="soldCount" aria-live="polite"></p><div class="grid g4" id="soldGrid">{''.join(prop_card(r, lang) for r in SOLD)}</div><p class="note" id="soldEmpty" hidden>{L('没有符合条件的成交，请放宽筛选条件。', 'No sales match. Try broader filters.')}</p>
<p class="src-note" style="margin-top:20px">{L('数据来自', 'Data from')} <a href="{MLS}" target="_blank" rel="noopener">{L('MLSListings 经纪人主页公开成交记录', 'MLSListings public agent closed listings')}</a>{L('及公开房源页面，采集于 2026 年 9 月，一条明显属于租赁的记录未列入。“交易类型”目前只标注了已确认的记录，其余记录仍在核对。房屋照片版权归原房源页所有。', ' and public listing pages, collected September 2026. One record that was clearly a lease was left out. Transaction type is shown only where confirmed. Photo rights belong to the original listing pages.')}</p></div></section>
<section class="band white"><div class="wrap"><p class="kick">CLIENT REVIEWS</p><h2 class="h2">{L('客户评价', 'Client reviews')}</h2><div class="grid g3">{review_cards(lang, REVIEWS[:3])}</div><div class="btns" style="margin-top:20px"><a class="b line" href="{ZILLOW}" target="_blank" rel="noopener">{L('查看全部 15 条 Zillow 评价', 'See all 15 Zillow reviews')} ↗</a></div></div></section>
{cta(lang, L('想了解类似房子的成交情况？', 'Curious about sales like yours?'), L('告诉陈靖你的城市和房型，一起看可比成交。', 'Share your city and home type and look at comparable sales together.'), 'valuation')}'''
    page(lang, path(lang, 'sold.html'), L('陈靖成交案例｜湾区真实成交记录｜Jing Chen', 'Sold Properties | Jing Chen Bay Area Sales'), L(f'陈靖 Jing Chen 的 {len(SOLD)} 笔公开成交记录，可按城市、年份、价格和交易类型筛选，并附公开来源链接。', f'{len(SOLD)} public sales records for Jing Chen, filterable by city, year, price and transaction type, with source links.'), body, key='sold', ld=[breadcrumb(lang, [(L('成交案例', 'Sold Properties'), path(lang, 'sold.html'))])])


def build_insights(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    order = [s for s in BUY_ORDER + SELL_ORDER + OWNER_ORDER + GUIDES if s in ARTS]
    cards = ''
    for s in order:
        m = ARTS[s]
        cards += (f'<a class="card" data-cat="{m["category"]}" href="@article/{s}"><span class="dates">{esc(CAT[lang][m["category"]])} · {L("更新", "Updated")} {esc(fmt_date(m["reviewed"], lang))}</span><h3>{esc(m[lang]["title"])}</h3><p>{esc(m[lang]["description"])}</p><span class="go">{L("阅读", "Read")} →</span></a>')
    chips = f'<button class="chip" type="button" data-f="" aria-pressed="true">{L("全部", "All")}</button>' + ''.join(f'<button class="chip" type="button" data-f="{k}" aria-pressed="false">{esc(v)}</button>' for k, v in CAT[lang].items())
    tools = ''.join(f'<a class="card tool" href="@tool/{k}"><h3>{esc(v[lang][0])}</h3><p>{esc(v[lang][1])}</p><span class="go">{L("打开工具", "Open tool")} →</span></a>' for k, v in TOOLS.items())
    body = fix_home(hero(crumbs(lang, (L('地产知识', 'Insights'), None)), L('地产知识中心', 'Real estate insights'), L('按买房、卖房、房主和城市比较分类。文章都标明核对日期和主要来源。', 'Organized by buying, selling, homeownership and city comparisons, with review dates and main sources.'), 'INSIGHTS')) + f'''
<section class="band"><div class="wrap"><div class="chips" role="group" aria-label="{L('文章分类', 'Categories')}">{chips}</div>
<div class="filters"><label>{L('搜索文章', 'Search articles')}<input id="artQ" type="search" placeholder="{L('例如 Escrow、ADU、学区', 'For example escrow, ADU, schools')}"></label></div>
<p class="count" id="artCount" aria-live="polite"></p><div class="grid g3" id="artGrid">{cards}</div><p class="note" id="artEmpty" hidden>{L('没有找到相关文章，换个关键词试试。', 'No articles found. Try another word.')}</p></div></section>
<section class="band white"><div class="wrap"><p class="kick">TOOLS</p><h2 class="h2">{L('计算工具', 'Calculators')}</h2><div class="grid g2">{tools}</div></div></section>'''
    page(lang, path(lang, 'insights.html'), L('湾区地产知识｜买房、卖房与房主指南｜陈靖', 'Bay Area Real Estate Insights | Jing Chen'), L('湾区买房、卖房、房主和城市比较文章，支持分类和搜索，每篇标明核对日期和来源。', 'Bay Area articles on buying, selling, homeownership and comparing cities, with search, categories, review dates and sources.'), body, key='insights', ld=[breadcrumb(lang, [(L('地产知识', 'Insights'), path(lang, 'insights.html'))])])


def build_article(slug, lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    a = ARTS[slug]
    m = a[lang]
    out = path(lang, art_path(slug))
    raw = (C / 'articles' / f'{slug}.{lang}.html').read_text(encoding='utf-8')
    heads = []

    def addid(mm):
        i = f's{len(heads) + 1}'
        heads.append((i, re.sub(r'<[^>]+>', '', mm.group(1))))
        return f'<h2 id="{i}">{mm.group(1)}</h2>'
    bodyh = re.sub(r'<h2[^>]*>(.*?)</h2>', addid, raw, flags=re.S)
    bodyh = re.sub(r'<a href="(https?://[^"]+)"(?![^>]*target)', r'<a href="\1" target="_blank" rel="noopener"', bodyh)
    cat = a['category']
    toc = ''.join(f'<a href="#{i}">{esc(t)}</a>' for i, t in heads)
    notice = f'<p class="legal">{esc(NOTICE[lang][a["notice"]])}</p>' if a.get('notice') else ''
    src = ''
    if a.get('sources'):
        src = f'<section class="sources"><h2>{L("主要资料来源", "Main sources")}</h2><ul>' + ''.join(f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])}</a></li>' for s in a['sources']) + '</ul></section>'
    rel_slugs = [s for s in a.get('related', []) if s in ARTS and s != slug][:3]
    related = ''
    if rel_slugs:
        related = f'<section class="band white"><div class="wrap"><p class="kick">{L("相关文章", "RELATED")}</p><h2 class="h2">{L("接着看", "Keep reading")}</h2><div class="grid g3">' + ''.join(module_card(lang, s, i + 1) for i, s in enumerate(rel_slugs)) + '</div></div></section>'
    ask = {'buy': 'buy', 'sell': 'sell', 'owner': 'general', 'area': 'compare'}[cat]
    extra = f'&topic={esc(m["title"])}' if cat == 'area' else ''
    h = fix_home(hero(crumbs(lang, (HUBN[lang][cat], f'@page/{HUB[cat][:-5]}'), (m['title'], None)), m['title'], m['lead'], CAT[lang][cat].upper() if not z else CAT[lang][cat], meta=f'<p class="hmeta">{L("核对日期", "Reviewed")} {esc(fmt_date(a["reviewed"], lang))} · {L("作者", "By")} Jing Chen {L("陈靖", "")}</p>'))
    side = (f'<aside class="art-side">' + (f'<nav class="toc" aria-label="{L("本文目录", "On this page")}"><h2>{L("本文目录", "On this page")}</h2>{toc}</nav>' if toc else '') +
            f'<div class="side-cta"><h2>{L("想结合自己的情况聊聊？", "Want to talk about your situation?")}</h2><p>{L("把你的情况告诉陈靖，一起梳理下一步。", "Tell Jing your situation and map out the next step.")}</p><a class="b gold" style="width:100%" href="@page/contact?type={ask}">{L("预约咨询", "Contact Jing")}</a><a class="tel" href="{TEL}">{PHONE}</a></div></aside>')
    body = h + f'<section class="band"><div class="wrap art-grid"><article class="prose">{notice}{bodyh}{src}</article>{side}</div></section>{related}'
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": m['title'], "description": m['description'], "inLanguage": 'zh-CN' if z else 'en', "datePublished": a.get('published', a['reviewed']), "dateModified": a['reviewed'],
          "author": {"@type": "Person", "name": "Jing Chen"}, "publisher": {"@type": "Organization", "name": "Jing Chen Homes"}, "mainEntityOfPage": f'{SITE}/{out}'}
    page(lang, out, m['seo_title'], m['description'], body, key='insights', kind='article', ld=[ld, breadcrumb(lang, [(HUBN[lang][cat], path(lang, HUB[cat])), (m['title'], out)])])


def field(i, label, val, hint='', step='any'):
    h = f'<small class="fnote" style="margin:0">{esc(hint)}</small>' if hint else ''
    return f'<div class="field"><label for="{i}">{esc(label)}</label><input id="{i}" type="number" inputmode="decimal" min="0" step="{step}" value="{val}">{h}</div>'


def build_calcs(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    t, d = TOOLS['buyer-costs'][lang]
    disc = L('这是粗略估算，不是贷款报价或承诺。默认数字只是示例，请换成贷款机构、保险公司和具体房源的实际数字。', 'This is a rough estimate, not a loan quote or commitment. Default numbers are only examples; replace them with figures from your lender, insurer and the specific home.')
    b = fix_home(hero(crumbs(lang, (HUBN[lang]['buy'], '@page/buy'), (t, None)), t, d, 'CALCULATOR')) + f'''
<section class="band"><div class="wrap"><div class="legal">{disc}</div><div class="calc"><form id="buyerCalc" class="formbox" onsubmit="return false"><div class="form-grid">
{field('bPrice', L('房价 ($)', 'Home price ($)'), 1500000)}{field('bDown', L('首付比例 (%)', 'Down payment (%)'), 20)}
{field('bRate', L('贷款年利率 (%)', 'Interest rate (%)'), 6.5, L('示例，请用贷款报价', 'Example; use your quote'))}{field('bTerm', L('贷款年限', 'Loan term (years)'), 30)}
{field('bTax', L('房产税率 (% / 年)', 'Property tax (% / year)'), 1.2, L('示例，实际税率按房源税单核对', 'Example; check the actual tax bill'))}{field('bIns', L('房屋保险 ($ / 年)', 'Home insurance ($ / year)'), 2400, L('示例，请向保险公司询价', 'Example; get a quote'))}
{field('bHoa', L('HOA ($ / 月)', 'HOA ($ / month)'), 0)}{field('bMello', L('Mello-Roos 等特别税 ($ / 年)', 'Mello-Roos and special taxes ($ / year)'), 0)}
{field('bClose', L('买方交割费用 (% 房价)', 'Buyer closing costs (% of price)'), 1, L('示例，以 Loan Estimate 为准', 'Example; see your Loan Estimate'))}
</div></form><div class="res" aria-live="polite"><h2>{L('估算结果', 'Estimate')}</h2><dl>
<dt>{L('首付', 'Down payment')}</dt><dd id="rDown"></dd><dt>{L('买方交割费用', 'Closing costs')}</dt><dd id="rClose"></dd><dt>{L('贷款金额', 'Loan amount')}</dt><dd id="rLoan"></dd>
<div class="big"><span>{L('需要准备的现金', 'Cash to close')}</span><b id="rCash"></b></div>
<dt>{L('本金和利息 / 月', 'Principal and interest / mo')}</dt><dd id="rPI"></dd><dt>{L('房产税 / 月', 'Property tax / mo')}</dt><dd id="rTax"></dd><dt>{L('保险 / 月', 'Insurance / mo')}</dt><dd id="rIns"></dd><dt>{L('HOA 和特别税 / 月', 'HOA and special taxes / mo')}</dt><dd id="rHoa"></dd>
<div class="big"><span>{L('每月住房支出', 'Monthly housing cost')}</span><b id="rMonth"></b></div></dl>
<p class="fnote" id="pmiNote" style="color:rgba(255,255,255,.8)" hidden>{L('首付低于 20% 时，贷款可能需要贷款保险（PMI），未计入上面的结果。', 'With less than 20% down, a loan may require mortgage insurance, which is not included above.')}</p></div></div>
<div class="prose" style="margin-top:32px"><p>{L('还需要留出搬家、维修和应急资金。了解预算怎么定，可以看', 'Also leave room for moving, repairs and reserves. To learn how to set a budget, read')} <a href="@article/budget-preapproval">{L('预算与贷款预批准', 'budget and pre-approval')}</a>{L('。', '.')}</p></div></div></section>'''
    out = path(lang, 'calculators/buyer-costs.html')
    page(lang, out, t + L('｜陈靖', ' | Jing Chen'), d, b, key='buy', ld=[breadcrumb(lang, [(HUBN[lang]['buy'], path(lang, 'buy.html')), (t, out)])])

    t, d = TOOLS['net-proceeds'][lang]
    copt = ''.join(f'<option value="{s}">{esc(n)}</option>' for s, n in CITIES) + f'<option value="other">{L("其他城市", "Other city")}</option>'
    tt = json.dumps(TT, ensure_ascii=False).replace('</', '<\\/')
    disc = L('这是粗略估算，不是交割结算单，也不含资本利得税和预扣。佣金可协商，没有法定标准；买方经纪报酬由合同约定，下面的数字只是示例。转让税由谁支付按合同和当地习惯确定，请向 Title 或 Escrow 公司确认。', 'This is a rough estimate, not a closing statement, and it leaves out capital gains tax and withholding. Commissions are negotiable with no legal standard, and any buyer-agent compensation is set by agreement; the numbers below are only examples. Who pays transfer tax depends on the contract and local custom, so confirm with your title or escrow company.')
    b = fix_home(hero(crumbs(lang, (HUBN[lang]['sell'], '@page/sell'), (t, None)), t, d, 'CALCULATOR')) + f'''
<section class="band"><div class="wrap"><div class="legal">{disc}</div><div class="calc"><form id="netCalc" class="formbox" onsubmit="return false"><div class="form-grid">
{field('nPrice', L('预计成交价 ($)', 'Expected sale price ($)'), 1500000)}{field('nPayoff', L('贷款余额 ($)', 'Loan payoff ($)'), 500000)}
{field('nList', L('挂牌方经纪佣金 (%)', 'Listing brokerage fee (%)'), 2.5, L('示例，可协商', 'Example; negotiable'))}{field('nBuyer', L('买方经纪报酬 (%)', 'Buyer-agent compensation (%)'), 2.5, L('示例，如约定才有', 'Example; only if agreed'))}
<div class="field full"><label for="nCity">{L('城市', 'City')}</label><select id="nCity">{copt}</select><small class="fnote" id="nCityNote" style="margin:0"></small></div>
{field('nTransfer', L('转让税 ($)', 'Transfer tax ($)'), 0, L('按城市自动估算，可手动修改', 'Estimated by city; you can edit'))}{field('nEscrow', L('Escrow 和 Title 费用 ($)', 'Escrow and title fees ($)'), 4000, L('示例，请向 Escrow 询价', 'Example; ask escrow for a quote'))}
{field('nPrep', L('上市准备和维修 ($)', 'Preparation and repairs ($)'), 10000)}{field('nCredit', L('给买方的 Credit ($)', 'Credits to buyer ($)'), 0)}{field('nOther', L('其他（HOA 过户、搬家等） ($)', 'Other (HOA transfer, moving, etc.) ($)'), 0)}
</div></form><div class="res" aria-live="polite"><h2>{L('估算结果', 'Estimate')}</h2><dl>
<dt>{L('预计成交价', 'Sale price')}</dt><dd id="rPrice"></dd><dt>{L('贷款余额', 'Loan payoff')}</dt><dd id="rPay"></dd><dt>{L('经纪佣金和报酬', 'Brokerage fees')}</dt><dd id="rComm"></dd><dt>{L('转让税', 'Transfer tax')}</dt><dd id="rTrans"></dd><dt>{L('Escrow 和 Title', 'Escrow and title')}</dt><dd id="rEsc"></dd><dt>{L('准备、Credit 和其他', 'Prep, credits, other')}</dt><dd id="rPrep"></dd>
<div class="big"><span>{L('税前到手金额', 'Pre-tax proceeds')}</span><b id="rNet"></b></div></dl></div></div>
<script type="application/json" id="transferTax">{tt}</script>
<div class="prose" style="margin-top:32px"><p>{L('想让数字更接近实际，可以先了解', 'For more realistic numbers, read about')} <a href="@article/seller-escrow-closing">{L('卖方 Escrow 与 Closing', 'seller escrow and closing')}</a>{L('，或者', ', or')} <a href="@page/contact?type=valuation">{L('预约免费房屋估值咨询', 'book a free home value consultation')}</a>{L('。', '.')}</p></div></div></section>'''
    out = path(lang, 'calculators/net-proceeds.html')
    page(lang, out, t + L('｜陈靖', ' | Jing Chen'), d, b, key='sell', ld=[breadcrumb(lang, [(HUBN[lang]['sell'], path(lang, 'sell.html')), (t, out)])])


def build_about(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    out = path(lang, 'about.html')
    n = len(SOLD)
    cities = len({r['city'] for r in SOLD})
    first = SOLD[-1]['date'][:4]
    last = SOLD[0]['date'][:4]
    adv = [(L('看懂市场', 'Read the market'), L('Comparable Sales、库存、DOM、每平方英尺成交价与竞争强度，帮助你理解“这套房到底值多少”。', 'Comparable sales, inventory, days on market, price per square foot and competition help you understand what a home is really worth.')),
           (L('做对策略', 'Build the right strategy'), L('买方如何组织 Offer；卖方如何定价、准备、上市，都不是照模板走。', 'How a buyer structures an offer and how a seller prices, prepares and lists should never come from a template.')),
           (L('推进交易', 'Keep the deal moving'), L('贷款、Inspection、Escrow、Contractor、Staging、摄影与物业管理等环节统一协调。', 'Lending, inspections, escrow, contractors, staging, photography and property management stay coordinated.'))]
    ad = ''.join(f'<div class="card"><div class="no">{i + 1:02d}</div><h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for i, (a, b) in enumerate(adv))
    wor = [L('先把问题讲清楚，再做决定。', 'Get the questions clear before deciding.'), L('看具体的房子和地址，不只看城市平均数。', 'Look at the specific home and address, not only citywide averages.'), L('学校、税务、法律和贷款问题，指向官方渠道和相应专业人士核实。', 'For schools, tax, legal and lending questions, go to official channels and the right professionals.'), L('不承诺未来价格，把取舍和风险摆在桌面上。', 'No promises about future prices; trade-offs and risks stay on the table.')]
    wl = ''.join(f'<li>{esc(w)}</li>' for w in wor)
    res = [L('贷款专业人士', 'Lending professionals'), L('房屋检查人员', 'Home inspectors'), L('Escrow 和 Title 公司', 'Escrow and title companies'), L('承包商和维修人员', 'Contractors and repair trades'), L('Staging 和摄影', 'Staging and photography'), L('物业管理', 'Property management')]
    rl = ''.join(f'<div class="card"><h3>{esc(r)}</h3></div>' for r in res)
    cl = ''.join(f'<a class="chip" href="@city/{s}">{esc(c)}</a>' for s, c in CITIES)
    body = fix_home(hero(crumbs(lang, (L('关于陈靖', 'About Jing'), None)), L('关于陈靖 Jing Chen', 'About Jing Chen'), L('湾区 REALTOR®，提供中英文房地产服务，服务硅谷、东湾与三谷的买家、卖家和房主。', 'A Bay Area REALTOR® serving buyers, sellers and homeowners across Silicon Valley, the East Bay and the Tri-Valley, in English and Chinese.'), 'ABOUT JING')) + f'''
<section class="band white"><div class="wrap split"><img src="{esc(rel(out, 'images/about-agent.webp'))}" alt="{L('陈靖 Jing Chen 肖像', 'Portrait of Jing Chen')}" width="1200" height="1800"><div>
<p class="quote">{L('“房地产交易，不只是找到一套房子。真正重要的是，在信息复杂、金额巨大的决定面前，把风险、机会与选择讲清楚。”', '“A real estate transaction is more than finding a house. What really matters is making the risks, opportunities and choices clear when you face a complex, high-stakes decision.”')}</p>
<p>{L('陈靖希望做的，不只是帮客户完成一笔交易，而是在买房、卖房与投资过程中，帮助客户理解市场、判断价值、组织策略，并把每一个关键环节推进到位。', 'Jing’s aim is not just to help clients close a transaction. Whether buying, selling or investing, she helps them understand the market, judge value, build a strategy and see every key step through.')}</p>
<div class="cred"><div><small>Brokerage</small><strong>{BROKER}</strong></div><div><small>California DRE</small><strong>#{DRE}</strong></div><div><small>Languages</small><strong>中文 · English</strong></div><div><small>Phone</small><strong><a href="{TEL}">{PHONE}</a></strong></div></div>
<a class="b fill" href="@page/contact">{L('预约与陈靖聊聊', 'Talk with Jing')} →</a></div></div></section>
<section class="band" id="area"><div class="wrap"><p class="kick">SERVICE AREA</p><h2 class="h2">{L('服务区域', 'Service area')}</h2><p class="sub">{L('硅谷、南湾、东湾与三谷，包括以下城市。', 'Silicon Valley, the South Bay, the East Bay and the Tri-Valley, including these cities.')}</p><div class="chips">{cl}</div></div></section>
<section class="band white"><div class="wrap"><p class="kick">HOW JING HELPS</p><h2 class="h2">{L('专业优势', 'How Jing helps')}</h2><div class="grid g3">{ad}</div></div></section>
<section class="band"><div class="wrap split" style="align-items:start"><div><p class="kick">PHILOSOPHY</p><h2 class="h2">{L('工作理念', 'How Jing works')}</h2><div class="prose"><ul>{wl}</ul></div></div>
<div><p class="kick">TRACK RECORD</p><h2 class="h2">{L('真实成交经验', 'Real transaction experience')}</h2><div class="stats" style="grid-template-columns:1fr 1fr"><div class="stat"><b>{n}</b><span>{L('笔公开可查成交', 'public sales on record')}</span></div><div class="stat"><b>{cities}</b><span>{L('个城市', 'cities')}</span></div></div>
<p class="src-note">{L(f'统计范围：{first}–{last} 年 MLSListings 公开成交记录及公开房源页面，2026 年 9 月采集。', f'Based on public MLSListings records and public listing pages, {first}–{last}, collected September 2026.')}</p><a class="b line" href="@page/sold">{L('查看全部成交', 'See all sales')} →</a></div></div></section>
<section class="band white"><div class="wrap split"><div><p class="kick">ENGLISH · 中文</p><h2 class="h2">{L('中英文服务', 'Service in English and Chinese')}</h2><p>{L('看房讨论、合同解读和与各方沟通都可以用中文或英文进行。合同文件以英文正式文本为准，遇到不理解的条款可以逐项讨论，法律问题请咨询律师。', 'Home tours, document reviews and communication can all happen in English or Chinese. Contracts are in English, and any term you do not understand can be discussed item by item. For legal questions, please consult an attorney.')}</p></div><img src="{esc(rel(out, 'images/lifestyle.webp'))}" alt="{L('陈靖 Jing Chen 生活照', 'Jing Chen lifestyle portrait')}" width="1350" height="1800" loading="lazy"></div></section>
<section class="band" id="reviews"><div class="wrap"><p class="kick">CLIENT REVIEWS</p><h2 class="h2">{L('客户评价', 'Client reviews')}</h2><p class="sub">{L('以下内容节选自陈靖 Zillow 认证客户评价（5.0 分，15 条），版权归原平台及作者所有。', 'Excerpts from Jing’s verified Zillow reviews (5.0 from 15 reviews). Copyright belongs to the original platform and authors.')}</p><div class="grid g3">{review_cards(lang, REVIEWS)}</div><div class="btns" style="margin-top:20px"><a class="b line" href="{ZILLOW}" target="_blank" rel="noopener">{L('查看全部 15 条 Zillow 评价', 'See all 15 Zillow reviews')} ↗</a></div></div></section>
<section class="band white"><div class="wrap"><p class="kick">NETWORK</p><h2 class="h2">{L('专业合作资源', 'Professional resources')}</h2><p class="sub">{L('一笔交易通常会涉及下面这些专业角色，可以和陈靖讨论怎样配合。你可以自由选择任何服务提供方。', 'A transaction usually involves these professionals, and you can talk with Jing about how they fit in. You are always free to choose any provider.')}</p><div class="grid g3">{rl}</div></div></section>
{cta(lang, L('一次有准备的沟通，可以从这四件事开始', 'A prepared conversation can start with four things'), L('你考虑买房还是卖房？希望什么时候完成？预算或价格预期是什么？哪些生活需求最不能妥协？', 'Are you buying or selling? When do you hope to finish? What is your budget or price expectation? What can you not compromise on?'))}'''
    ld = {"@context": "https://schema.org", "@type": "RealEstateAgent", "name": "Jing Chen 陈靖", "url": f'{SITE}/{out}', "image": SITE + "/images/about-agent.webp", "telephone": "+1-925-917-4019", "worksFor": {"@type": "Organization", "name": BROKER}, "identifier": f"CA DRE #{DRE}", "knowsLanguage": ["zh", "en"]}
    page(lang, out, L('关于陈靖｜湾区 REALTOR® 中英文服务｜Jing Chen', 'About Jing Chen | Bay Area REALTOR®'), L(f'陈靖 Jing Chen，BQ Realty 房地产经纪人，DRE #{DRE}。服务硅谷、东湾与三谷，提供中英文买房、卖房服务。', f'Jing Chen, REALTOR® with BQ Realty, DRE #{DRE}, serves Silicon Valley, the East Bay and the Tri-Valley in English and Chinese.'), body, key='about', ld=[ld, breadcrumb(lang, [(L('关于陈靖', 'About Jing'), out)])])


def build_contact(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    out = path(lang, 'contact.html')
    body = fix_home(hero(crumbs(lang, (L('预约咨询', 'Contact'), None)), L('你的下一步是什么？', 'What is your next step?'), L('已经准备开始，或者只是想了解市场，都可以先告诉陈靖你的情况。', 'Whether you are ready to start or just want to understand the market, tell Jing about your situation.'), 'CONTACT',
                         meta=f'<p class="hmeta">{L("电话", "Phone")} <a href="{TEL}" style="text-decoration:underline">{PHONE}</a> · REALTOR® · {BROKER} · DRE #{DRE}</p>')) + f'''
<section class="band"><div class="narrow" style="width:min(960px,calc(100% - 48px))"><h2 class="h2">{L('选择你想咨询的内容', 'Choose what you would like to discuss')}</h2>{lead_form(lang)}</div></section>'''
    page(lang, out, L('预约咨询陈靖｜湾区买房卖房｜Jing Chen', 'Contact Jing Chen | Bay Area Real Estate'), L('咨询湾区买房、卖房、免费房屋估值、换房规划或投资房。可在线留言，也可致电 925-917-4019。', 'Ask about buying, selling, a free home value consultation, planning a move or investment property. Message online or call 925-917-4019.'), body, key='contact')


def build_privacy(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    txt = L(f'''<h2>我们收集什么</h2><p>当你提交咨询表单时，我们会收到你填写的姓名、电话、Email、需求类型、意向城市和留言，以及提交时所在的页面地址和来源页面。</p>
<h2>怎样使用</h2><p>这些信息只用于联系你、跟进你的房地产咨询。我们不会出售你的个人信息。</p>
<h2>存放和第三方服务</h2><p>表单内容保存在 Supabase 数据库，并通过邮件服务发送给陈靖。网站部署在 Vercel，字体来自 Google Fonts；城市页地图会从 OpenStreetMap 和 U.S. Census Bureau 读取数据，这些服务在你访问时可能获得你的 IP 地址等技术信息。成交卡片的部分图片来自第三方房源网站。</p>
<h2>删除或更正</h2><p>如果想查看、更正或删除你提交的信息，请致电 {PHONE}。</p>
<h2>更新</h2><p>本说明可能调整，页面日期为最近更新时间：2026 年 11 月。</p>''', f'''<h2>What we collect</h2><p>When you send the contact form, we receive the name, phone, email, topic, city of interest and message you enter, plus the page address and referring page.</p>
<h2>How we use it</h2><p>We use this information only to contact you and follow up on your real estate inquiry. We do not sell your personal information.</p>
<h2>Storage and third parties</h2><p>Form submissions are stored in a Supabase database and sent to Jing through an email service. The site is hosted on Vercel and uses Google Fonts. City page maps load data from OpenStreetMap and the U.S. Census Bureau, and these services may receive technical information such as your IP address. Some sold-home images load from third-party listing sites.</p>
<h2>Changes or deletion</h2><p>To review, correct or delete information you sent, call {PHONE}.</p>
<h2>Updates</h2><p>This notice may change. Last updated November 2026.</p>''')
    body = fix_home(hero(crumbs(lang, (L('隐私说明', 'Privacy'), None)), L('隐私说明', 'Privacy notice'), L('我们怎样处理你在本网站提交的信息。', 'How we handle information you send through this site.'))) + f'<section class="band"><div class="narrow"><div class="prose">{txt}</div></div></section>'
    page(lang, path(lang, 'privacy.html'), L('隐私说明｜Jing Chen Homes', 'Privacy Notice | Jing Chen Homes'), L('Jing Chen Homes 网站如何收集和使用咨询表单信息。', 'How the Jing Chen Homes site collects and uses contact form information.'), body)


def build_en_city(slug, name):
    f = C / 'en-cities' / f'{slug}.json'
    if not f.exists():
        print('缺英文城市页:', slug)
        return
    d = json.loads(f.read_text(encoding='utf-8'))
    zh = json.loads((ROOT / 'tools/city-content' / f'{slug}.json').read_text(encoding='utf-8'))
    lang = 'en'
    out = f'en/cities/{slug}.html'
    p = lambda ls: ''.join(f'<p>{esc(x)}</p>' for x in (ls if isinstance(ls, list) else [ls]))
    nb = ''.join(f'<h3>{esc(x["name"])}</h3><p>{esc(x["summary"])}</p>' for x in d['neighborhoods'])
    types = ''.join(f'<div class="card"><h3>{esc(t["type"])}</h3><p>{esc(t["text"])}</p></div>' for t in d['housing'].get('types', []))
    sds = ''
    for x in zh['schools']['districts']:
        url = x.get('locator_url') or x.get('map_url') or x.get('enroll_url')
        sds += f'<li>{esc(x["name"])}' + (f' ({esc(x["grades"])})' if x.get('grades') else '') + (f': <a href="{esc(url)}" target="_blank" rel="noopener">official address lookup</a>' if url else '') + '</li>'
    if slug == 'san-jose':
        seen = {x['name'] for x in zh['schools']['districts']}
        dist = json.loads((ROOT / 'tools/city-content/san-jose-districts.json').read_text(encoding='utf-8'))
        lst = dist if isinstance(dist, list) else dist.get('districts', [])
        for a in lst:
            for y in a.get('school_districts', []):
                if y['name'] not in seen and y.get('locator_url'):
                    seen.add(y['name'])
                    sds += f'<li>{esc(y["name"])}: <a href="{esc(y["locator_url"])}" target="_blank" rel="noopener">official address lookup</a></li>'
    c = MK['cities'][slug]
    med = c.get('median_en', c['median'])
    sold = [r for r in SOLD if r['city'] == name][:4]
    sold_html = (f'<h2 id="sold">Recent real sales in {esc(name)}</h2><div class="grid g2" style="margin:16px 0">' + ''.join(prop_card(r, lang) for r in sold) + f'</div><p><a href="@page/sold?city={name.replace(" ", "+")}">See all sales</a></p>') if sold else ''
    rel_a = ['compare-cities', 'school-lookup', 'home-search']
    h = fix_home(hero(crumbs(lang, ('Areas & Schools', '@page/areas'), (name, None)), d['h1'], d['lead'], d.get('county', ''), meta=f'<p class="hmeta">{esc(d.get("tagline", ""))}</p>'))
    links = ''.join(module_card(lang, s, i + 1) for i, s in enumerate(rel_a) if s in ARTS)
    body = h + f'''<section class="band"><div class="wrap art-grid"><article class="prose">
<div class="note">This is a concise English edition. The <a href="{esc(rel(out, f'cities/{slug}.html'))}" hreflang="zh-CN">full guide in Chinese</a> includes maps, more detail and a half-day tour route.</div>
<h2 id="overview">City overview</h2>{p(d['overview'])}
<h2 id="neighborhoods">Neighborhoods</h2><p>These names are common usage, not legal boundaries.</p>{nb}
<h2 id="housing">Home types</h2>{p(d['housing']['intro'])}<div class="grid g2" style="margin:16px 0">{types}</div>
{'<p><a href="@zip/index">See San Jose market analysis by ZIP code</a></p>' if slug == 'san-jose' else ''}<h2 id="market">Price data</h2><div class="tablewrap"><table><thead><tr><th>City</th><th>3-month median sale price</th><th>Year over year</th></tr></thead><tbody><tr><td>{esc(name)}</td><td>{esc(med)}</td><td class="{c['dir']}">{esc(c['yoy_en'])}</td></tr></tbody></table></div>{market_note(lang)}
<h2 id="commute">Transit and commuting</h2>{p(d['commute'])}
<h2 id="schools">Schools and official lookups</h2>{p(d['schools'])}<ul>{sds}</ul><div class="note">No address is guaranteed a particular school. Verify the full address and enrollment through the district’s official channels.</div>
<h2 id="daily">Daily life</h2>{p(d['daily_life'])}
<h2 id="environment">Environment checks</h2>{p(d['environment'])}
{sold_html}</article>
<aside class="art-side"><div class="side-cta"><h2>Compare {esc(name)} with other cities</h2><p>Share your budget, office location and housing needs with Jing.</p><a class="b gold" style="width:100%" href="@page/contact?type=compare&city={name.replace(' ', '+')}">Contact Jing</a><a class="tel" href="{TEL}">{PHONE}</a></div></aside></div></section>
<section class="band white"><div class="wrap"><p class="kick">RELATED</p><h2 class="h2">Related articles</h2><div class="grid g3">{links}</div></div></section>'''
    page(lang, out, d['seo_title'], d['description'], body, key='areas', kind='article', ld=[breadcrumb(lang, [('Areas & Schools', 'en/areas.html'), (name, out)])])


# ---------- San Jose 邮编 ----------
REF = json.loads((ROOT / 'tools/site-data/sj-zip-reference.json').read_text(encoding='utf-8'))
_mk = ROOT / 'tools/site-data/sj-zip-market.json'
ZM = json.loads(_mk.read_text(encoding='utf-8')) if _mk.exists() else None   # 同周期核实数据，运行 tools/fetch_zip_market.py 生成
ZC = {f.stem: json.loads(f.read_text(encoding='utf-8')) for f in sorted((C / 'zip').glob('*.json'))}
ZIPS_ALL = list(REF['zips'])
SHOW_REFERENCE = False   # True 时显示未核实的历史参考数字并加提示；默认不发布
SHOW_NUMBERS = bool(ZM) or SHOW_REFERENCE


def zmarket(z):
    return (ZM['zips'] if ZM else REF['zips']).get(z, {})


def money_short(v):
    if not v:
        return ''
    return f'${v / 1e6:.2f}M' if v >= 1e6 else f'${round(v / 1000):,}K'


def zperiod(lang):
    if ZM:
        fmt = lambda d: fmt_date(d, lang)
        return (f'{fmt(ZM["period_begin"])} 至 {fmt(ZM["period_end"])}' if lang == 'zh' else f'{fmt(ZM["period_begin"])} to {fmt(ZM["period_end"])}')
    return REF['period_' + lang]


def zmeta(lang):
    z = lang == 'zh'
    L = (lambda a, b: a if z else b)
    if ZM:
        return f'''<dl class="zsrc"><dt>{L('数据来源', 'Source')}</dt><dd><a href="{esc(ZM['source_url'])}" target="_blank" rel="noopener">Redfin Data Center</a></dd><dt>{L('统计周期', 'Period')}</dt><dd>{esc(zperiod(lang))}</dd><dt>{L('住宅类型', 'Home types')}</dt><dd>{L('所有住宅类型混合（All Residential）', 'All Residential (all home types combined)')}</dd><dt>{L('数据更新', 'Updated')}</dt><dd>{esc(fmt_date(TODAY, lang))}</dd></dl>'''
    return f'''<dl class="zsrc"><dt>{L('数据来源', 'Source')}</dt><dd>{esc(REF['source_' + lang])}</dd><dt>{L('统计周期', 'Period')}</dt><dd>{esc(REF['period_' + lang])}</dd><dt>{L('住宅类型', 'Home types')}</dt><dd>{esc(REF['types_' + lang])}</dd><dt>{L('数据更新', 'Updated')}</dt><dd>{L('尚未重新核实', 'Not yet re-verified')}</dd></dl>'''


def zbanner(lang):
    if ZM or not SHOW_REFERENCE:
        return ''
    return '<p class="zwarn">' + ('预览版：以下数字沿用 2026 年 8–10 月的历史参考数据，尚未重新核实，不代表实时行情。95132 暂不填写未经确认的数字。' if lang == 'zh' else 'Preview: these figures are historical reference data from August to October 2026. They have not been re-verified and are not live market data. 95132 stays blank until confirmed.') + '</p>'


def zpills(lang, z):
    if not SHOW_NUMBERS:
        return ''
    m = zmarket(z)
    zh = lang == 'zh'
    pend = '待核实' if zh else 'Pending'
    a = f'{money_short(m.get("price"))} {"成交中位价" if zh else "median sale price"}' if m.get('price') else f'{"成交中位价" if zh else "Median sale price"} {pend}'
    b = (f'{m["dom"]} {"天 DOM" if zh else "days on market"}') if m.get('dom') is not None else f'DOM {pend}'
    c = (f'{m["sold"]} {"笔成交" if zh else "sales"}') if m.get('sold') is not None else f'{"成交数" if zh else "Sales"} {pend}'
    return f'<ul class="zpills"><li>{esc(a)}</li><li>{esc(b)}</li><li>{esc(c)}</li></ul>'


def zgallery(lang, z, out, eager=False):
    """相册：显示 1 张或 3 张，其余照片隐藏，点击由 site.js 打开 Lightbox。没有授权照片时不显示图片区。"""
    photos = [(i, ph) for i, ph in enumerate(ZC[z].get('photos', [])) if (ROOT / f'images/zip/{z}-{i + 1}.webp').exists()]
    if not photos:
        return ''
    n = len(photos)
    show = 3 if n >= 3 else 1
    cells = ''
    for k, (i, ph) in enumerate(photos):
        src = esc(rel(out, f'images/zip/{z}-{i + 1}.webp'))
        cap = ph[lang] + (f' · {ph["credit"]}' if ph.get('credit') else '')
        if k >= show:
            cells += f'<a class="zshot" href="{src}" data-cap="{esc(cap)}" hidden></a>'
            continue
        more = ''
        if n > 1 and k == show - 1:
            more = f'<span class="zall">{"查看全部照片 · " + str(n) + " 张" if lang == "zh" else "View all " + str(n) + " photos"}</span>'
        load = 'eager' if eager and k == 0 else 'lazy'
        cells += f'<a class="zshot" href="{src}" data-cap="{esc(cap)}"><img src="{src}" alt="{esc(ph.get("alt_" + lang) or ph[lang])}" loading="{load}">{more}</a>'
    return f'<div class="zgal zgal{show}" data-lb>{cells}</div>'


# 视觉样板：先只有这两个邮编使用新组件的深度阅读，确认后再加其他邮编
_dist = json.loads((ROOT / 'tools/city-content/san-jose-districts.json').read_text(encoding='utf-8'))['districts']
ZGUIDE = {z: next(x for x in _dist if x['name'] == n) for z, n in {'95125': 'Willow Glen', '95120': 'Almaden Valley'}.items()}


def zdeep(lang, z):
    """详情页的市场数据来源、深度阅读和官方入口。"""
    zh = lang == 'zh'
    L = (lambda a, b: a if zh else b)
    out = f'<h2 class="zh2">{L("市场数据来源", "Market data source")}</h2>'
    if SHOW_NUMBERS:
        out += zmeta(lang)
    else:
        out += '<p class="zsrcnote">' + L('成交中位价、DOM 和成交数量尚未按同一统计周期核实，暂不显示。核实后会在这里注明来源、统计周期、住宅类型和更新日期。', 'Median sale price, days on market and sales are not shown until they are verified for a single period. The source, period, home types and update date will appear here at that time.') + '</p>'
    x = ZGUIDE[z]
    links = ''
    if zh:
        secs = [('位置与范围', 'where'), ('住房特点', 'housing'), ('日常设施', 'daily'), ('通勤与学校', 'commute_school'), ('需要接受的取舍', 'tradeoffs'), ('实地看区时留意', 'visit')]
        out += f'<h2 class="zh2">{esc(x["name"])} 深度阅读</h2>' + ''.join(f'<h3 class="zh3">{t}</h3><p>{esc(x[k])}</p>' for t, k in secs)
        links = ''.join(f'<li><a href="{esc(y["locator_url"])}" target="_blank" rel="noopener">{esc(y["name"])}（{esc(y.get("grades", ""))}）地址查询</a></li>' for y in x.get('school_districts', []))
        links += ''.join(f'<li><a href="{esc(y["url"])}" target="_blank" rel="noopener">{esc(y["label"])}</a></li>' for y in x.get('links', []))
    links += ''.join(f'<li><a href="{esc(k["url"])}" target="_blank" rel="noopener">{esc(k["zh" if zh else "en"])}</a></li>' for k in ZC[z].get('links', []))
    if links:
        out += f'<h2 class="zh2">{L("官方查询入口", "Official resources")}</h2><ul class="zlinks">{links}</ul>'
    return out


def zblock(lang, z, out, h='h2', full=True):
    d = ZC[z]
    zh = lang == 'zh'
    sfx = '' if zh else '_en'
    title = f'{z} <span>|</span> {esc(d["title" + sfx])}'
    head = f'<{h} class="ztitle">{title}</{h}>' if full else f'<{h} class="ztitle"><a href="@zip/{z}">{title}</a></{h}>'
    p = lambda ls: ''.join(f'<p>{esc(x)}</p>' for x in ls)
    rich = lambda lab, ls: f'<p><strong>{lab}：</strong>{esc(ls[0])}</p>' + p(ls[1:]) if zh else f'<p><strong>{lab}:</strong> {esc(ls[0])}</p>' + p(ls[1:])
    buy, sell = d['buyer' + sfx], d['seller' + sfx]
    if not full:
        more_label = ('查看完整地区指南' if zh else 'Read the full area guide') if z in ZGUIDE else ('查看 ' + z + ' 详情' if zh else 'See ' + z + ' details')
        return (f'<article class="zblock" id="z{z}">{head}{zgallery(lang, z, out)}{zpills(lang, z)}<p>{esc(d["intro" + sfx][0])}</p>{rich("买家需要知道" if zh else "What buyers should know", buy[:1])}{rich("卖家需要知道" if zh else "What sellers should know", sell[:1])}'
                f'<p><a class="zmore" href="@zip/{z}">{more_label} →</a></p></article>')
    if z in ZGUIDE:
        return f'<article class="zblock">{head}{zgallery(lang, z, out, True)}{zpills(lang, z)}{p(d["intro" + sfx])}{rich("买家需要知道" if zh else "What buyers should know", buy)}{rich("卖家需要知道" if zh else "What sellers should know", sell)}{zdeep(lang, z)}</article>'
    note = d.get('note')
    nt = ''
    if note and note.get('checked'):   # 未核实的引用不发布
        nt = f'<p class="znote">{esc(note["zh" if zh else "en"])} <a class="zcite" href="{esc(note["url"])}" target="_blank" rel="noopener">{esc(note["src"])}</a></p>'
    links = ''.join(f'<li><a href="{esc(k["url"])}" target="_blank" rel="noopener">{esc(k["zh" if zh else "en"])}</a></li>' for k in d.get('links', []))
    srcs = ''
    if SHOW_NUMBERS or links:
        srcs = f'<h2 class="zh2">{("数据来源" if SHOW_NUMBERS else "官方资料") if zh else ("Data sources" if SHOW_NUMBERS else "Official resources")}</h2>' + (zmeta(lang) if SHOW_NUMBERS else '') + (f'<ul class="zlinks">{links}</ul>' if links else '')
    return f'<article class="zblock">{zbanner(lang)}{head}{zgallery(lang, z, out)}{zpills(lang, z)}{p(d["intro" + sfx])}{rich("买家需要知道" if zh else "What buyers should know", buy)}{rich("卖家需要知道" if zh else "What sellers should know", sell)}{nt}{srcs}</article>'


def zchart(lang):
    zh = lang == 'zh'
    have = sorted([(z, zmarket(z)['price']) for z in ZIPS_ALL if zmarket(z).get('price')], key=lambda x: -x[1])
    top = max(v for _, v in have) * 1.05
    bars = ''.join(f'<div class="zbar"><span class="zv">{money_short(v)}</span><i style="--v:{v / top * 100:.1f}%"></i><a href="@zip/{z}">{z}</a></div>' if z in ZC else f'<div class="zbar"><span class="zv">{money_short(v)}</span><i style="--v:{v / top * 100:.1f}%"></i><b>{z}</b></div>' for z, v in have)
    miss = [z for z in ZIPS_ALL if not zmarket(z).get('price')]
    mt = f'<p class="src-note">{"尚未核实、未列入图表：" if zh else "Not yet verified, so not charted: "}{", ".join(miss)}</p>' if miss else ''
    sub = f'{esc(zperiod(lang))}；{esc(REF["types_zh"])}' if zh else f'{esc(zperiod(lang))}; {esc(REF["types_en"])}'
    label = '各邮编成交中位价柱状图，数据见上表' if zh else 'Bar chart of median sale price by ZIP code; the data is in the table above'
    return f'<h2 class="zh2">{"核心邮编成交中位价比较" if zh else "Median sale price by ZIP code"}</h2><p class="zsub">{sub}</p><div class="zbars" role="img" aria-label="{label}">{bars}</div>{mt}', have


def build_zip_overview(lang):
    zh = lang == 'zh'
    L = (lambda a, b: a if zh else b)
    out = path(lang, 'areas/san-jose/index.html')
    pend = L('待核实', 'Pending')
    if SHOW_NUMBERS:
        order = sorted(ZIPS_ALL, key=lambda z: -(zmarket(z).get('price') or 0))
    else:
        order = sorted(ZIPS_ALL)
    rows = ''
    for z in order:
        m = zmarket(z)
        area = REF['areas'][z][0 if zh else 1]
        link = f'<a href="@zip/{z}">{z}</a>' if z in ZC else z
        nums = f'<td>{money_short(m.get("price")) or pend}</td><td>{m.get("sold", pend)}</td><td>{m.get("dom", pend)}</td>' if SHOW_NUMBERS else ''
        rows += f'<tr><td>{link}</td><td>{esc(area)}</td>{nums}</tr>'
    numh = f'<th>{L("成交中位价", "Median sale price")}</th><th>{L("成交数", "Sales")}</th><th>DOM</th>' if SHOW_NUMBERS else ''
    if SHOW_NUMBERS:
        chart, have = zchart(lang)
        hi, lo = have[0], have[-1]
        x = hi[1] / lo[1]
        an = (f'<p>这些数字揭示了一个重要事实：<strong>San Jose 并不是一个统一的房地产市场。</strong></p><p>例如，{hi[0]} 的成交中位价约为 {lo[0]} 的 {x:.1f} 倍，但两者在房屋类型、地块、学区边界和买家需求方面都有差异。这些数字混合了独栋、Townhouse 和 Condo，看懂差异从哪里来，比看价格排名更有用。</p>' if zh else
              f'<p>These numbers point to one important fact: <strong>San Jose is not a single real estate market.</strong></p><p>The median in {hi[0]} is about {x:.1f} times the median in {lo[0]}, but the two differ in home types, lots, school boundaries and buyer demand. The figures mix single-family homes, townhomes and condos, so understanding where the gap comes from matters more than the ranking.</p>')
        meta_block = zmeta(lang)
    else:
        chart = ''
        an = ('<p><strong>San Jose 并不是一个统一的房地产市场。</strong>不同邮编在房屋类型、地块、学区边界和买家需求方面都有差异，看懂差异从哪里来，比看价格排名更有用。</p><p class="src-note">各邮编的成交中位价、成交数和 DOM 正在按同一统计周期核实，核实后发布。</p>' if zh else
              '<p><strong>San Jose is not a single real estate market.</strong> ZIP codes differ in home types, lots, school boundaries and buyer demand, and understanding those differences matters more than a price ranking.</p><p class="src-note">Median price, sales and days on market for each ZIP code are being verified for a single period and will be published once confirmed.</p>')
        meta_block = ''
    blocks = ''.join(zblock(lang, z, out, 'h3', False) for z in order if z in ZC)
    no = [z for z in order if z not in ZC]
    body = f'''<div class="zpage"><p class="crumb2"><a href="@page/home">{L('首页', 'Home')}</a> / <a href="@page/areas">{L('地区与学区', 'Areas & Schools')}</a> / San Jose</p>
<h1 class="zh1">San Jose Real Estate Market by ZIP Code{'<small>圣何塞各邮编房地产市场分析</small>' if zh else ''}</h1>
{zbanner(lang)}
<div class="tablewrap ztable"><table><thead><tr><th>ZIP Code</th><th>{L('主要地区', 'Main area')}</th>{numh}</tr></thead><tbody>{rows}</tbody></table></div>
{meta_block}
{chart}
<h2 class="zh2">{L('不同 ZIP Code 的价格差异', 'Why prices differ by ZIP code')}</h2>{an}
<h2 class="zh2">{L('各邮编地区介绍', 'ZIP code guides')}</h2>
{blocks}
<p class="src-note">{L('学校信息请按完整地址向学区官方渠道核实。本页不保证任何地址对应特定学校，市场数字也不是任何一套房屋的估值。', 'Verify schools by full address through official district channels. This page does not guarantee any school assignment, and market figures are not a valuation of any home.')}</p>
<p class="zback"><a href="@city/san-jose">{L('查看 San Jose 城市生活指南', 'See the San Jose city guide')} →</a></p></div>
{cta(lang, L('想知道哪个邮编适合你？', 'Which ZIP code fits you?'), L('把预算、工作地点和房型要求告诉陈靖，一起比较。', 'Share your budget, work location and home type with Jing and compare together.'), 'compare', '&city=San+Jose')}'''
    t = L('San Jose 各邮编房地产市场分析｜陈靖', 'San Jose Real Estate Market by ZIP Code | Jing Chen')
    dsc = L('按 ZIP Code 了解 San Jose 各地区的房屋特点和买卖要点，包括 Berryessa、Cambrian、Almaden Valley、Willow Glen 等。', 'A ZIP code guide to San Jose areas, including what buyers and sellers should know in Berryessa, Cambrian, Almaden Valley and Willow Glen.')
    page(lang, out, t, dsc, body, key='areas', ld=[breadcrumb(lang, [(L('地区与学区', 'Areas & Schools'), path(lang, 'areas.html')), ('San Jose', out.replace('index.html', ''))])])
    if no:
        print('邮编缺正文，未生成详情页:', no)


def build_zip_page(lang, z):
    zh = lang == 'zh'
    L = (lambda a, b: a if zh else b)
    d = ZC[z]
    out = path(lang, f'areas/san-jose/{z}/index.html')
    area = d['area'] if zh else d['area_en']
    others = [x for x in sorted(ZC) if x != z]
    ol = ''.join(f'<a class="chip" href="@zip/{x}">{x} {esc((ZC[x]["area"] if zh else ZC[x]["area_en"]))}</a>' for x in others)
    body = f'''<div class="zpage"><p class="crumb2"><a href="@page/home">{L('首页', 'Home')}</a> / <a href="@page/areas">{L('地区与学区', 'Areas & Schools')}</a> / <a href="@zip/index">San Jose</a> / {z}</p>
{zblock(lang, z, out, 'h1', True)}
<h2 class="zh2">{L('继续比较', 'Keep comparing')}</h2><div class="chips">{ol}</div>
<p class="zback"><a href="@zip/index">{L('返回 San Jose 邮编总览', 'Back to San Jose ZIP code overview')} →</a></p>
<p class="src-note">{L('学校信息请按完整地址向学区官方渠道核实，本页不保证任何地址对应特定学校。', 'Verify schools by full address through official district channels. This page does not guarantee any school assignment.')}</p></div>
{cta(lang, L(f'想深入了解 {z}？', f'Want to look closer at {z}?'), L('告诉陈靖你的预算和房型要求，一起看同类房屋的近期成交。', 'Share your budget and home type with Jing and review recent sales of similar homes.'), 'compare', '&city=San+Jose')}'''
    t = f'{z} {area} 买房卖房指南｜陈靖' if zh else f'{z} {area} Real Estate Guide | Jing Chen'
    dsc = (d['intro'][0] if zh else d['intro_en'][0])[:150]
    url = out.replace('index.html', '')
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": f'{z} {d["title" if zh else "title_en"]}', "inLanguage": 'zh-CN' if zh else 'en', "dateModified": TODAY, "author": {"@type": "Person", "name": "Jing Chen"}, "about": {"@type": "Place", "name": f'{area}, San Jose, CA {z}'}, "mainEntityOfPage": f'{SITE}/{url}'}
    page(lang, out, t, dsc, body, key='areas', kind='article', ld=[ld, breadcrumb(lang, [(L('地区与学区', 'Areas & Schools'), path(lang, 'areas.html')), ('San Jose', path(lang, 'areas/san-jose/')), (z, url)])])


def sitemap():
    extra = [f'cities/{s}.html' for s, _ in CITIES]
    urls = sorted(set(PAGES + extra), key=lambda p: (p.startswith('en/'), p.count('/'), p))
    x = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        loc = f'{SITE}/{u}'.replace('/index.html', '/')
        x.append(f'  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod></url>')
    x.append('</urlset>\n')
    (ROOT / 'sitemap.xml').write_text('\n'.join(x), encoding='utf-8')
    print('sitemap', len(urls))


def main():
    for lang in ('zh', 'en'):
        build_home(lang); build_buy(lang); build_sell(lang); build_areas(lang); build_owner(lang)
        build_sold(lang); build_insights(lang); build_about(lang); build_contact(lang); build_privacy(lang); build_calcs(lang)
        for s in ARTS:
            build_article(s, lang)
        build_zip_overview(lang)
        for z in ZC:
            build_zip_page(lang, z)
    for s, n in CITIES:
        build_en_city(s, n)
    sitemap()
    print('pages', len(PAGES))


if __name__ == '__main__':
    main()
