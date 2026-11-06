#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成买房 / 卖房服务页与城市比较文章。

用法（在项目根目录执行）：
    python3 tools/build_pages.py

读取：
    tools/seo-meta.json            各页面的 title / description / H1 / 导语
    tools/page-content/<key>.html  正文片段（原文成稿，改文案改这里）
输出：
    buy.html  sell.html  guides/<key>.html

兼容 Python 3.8+，不依赖第三方库。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://www.homesbyjingchen.com'
ASSET_VER = '20261009'
PUBLISHED = '2026-10-09'   # 页面发布日期
REVIEWED = '2026-10-08'    # 正文资料核查日期（写在正文里）

# key -> (输出路径, 类型, 咨询参数 ask, 咨询主题, 面包屑上级)
PAGES = [
    ('buy', 'buy.html', 'service', 'buy', '', None),
    ('sell', 'sell.html', 'service', 'sell', '', None),
    ('fremont-vs-dublin', 'guides/fremont-vs-dublin.html', 'article', 'compare', 'Fremont 与 Dublin', ['fremont', 'dublin']),
    ('dublin-vs-pleasanton', 'guides/dublin-vs-pleasanton.html', 'article', 'compare', 'Dublin 与 Pleasanton', ['dublin', 'pleasanton']),
    ('sunnyvale-vs-cupertino', 'guides/sunnyvale-vs-cupertino.html', 'article', 'compare', 'Sunnyvale 与 Cupertino', ['sunnyvale', 'cupertino']),
]
CITY_NAMES = {'fremont': 'Fremont', 'dublin': 'Dublin', 'pleasanton': 'Pleasanton', 'sunnyvale': 'Sunnyvale',
              'cupertino': 'Cupertino', 'palo-alto': 'Palo Alto'}
# 成稿里的站内锚点 -> 真实路径（相对网站根目录）
ANCHORS = {
    '#buy': 'buy.html', '#sell': 'sell.html',
    '#fremont-vs-dublin': 'guides/fremont-vs-dublin.html',
    '#dublin-vs-pleasanton': 'guides/dublin-vs-pleasanton.html',
    '#sunnyvale-vs-cupertino': 'guides/sunnyvale-vs-cupertino.html',
    '#palo-alto': 'cities/palo-alto.html',
}
# 已确认失效、需要替换的外部链接
URL_FIX = {
    'https://www.fuhsd.org/about-us/general-information/district-boundary-maps':
        'https://www.fuhsd.org/about-us/general-information/district-boundry-maps',
}
ARTICLE_TITLES = {
    'fremont-vs-dublin': 'Fremont 与 Dublin 比较',
    'dublin-vs-pleasanton': 'Dublin 与 Pleasanton 比较',
    'sunnyvale-vs-cupertino': 'Sunnyvale 与 Cupertino 比较',
}


def esc(t):
    return (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def nav(pre, key):
    def cur(k):
        return ' class="on" aria-current="page"' if k == key else ''
    return ('<nav class="nav"><div class="navin"><a class="brand" href="' + pre + 'index.html">'
            '<img class="navlogo" src="' + pre + 'images/logo-nav.png" alt="JC Team">JING CHEN HOMES</a>'
            '<div class="navlinks">'
            '<a href="' + pre + 'buy.html"' + cur('buy') + '>买房</a>'
            '<a href="' + pre + 'sell.html"' + cur('sell') + '>卖房</a>'
            '<a href="' + pre + 'index.html#homes">找房</a>'
            '<a href="' + pre + 'index.html#market-cities">城市指南</a>'
            '<a href="' + pre + 'index.html#compare-guides">城市比较</a>'
            '<a href="' + pre + 'index.html#sold">成交案例</a>'
            '<a href="' + pre + 'index.html#about">关于陈靖</a>'
            '<a class="navcta" href="{CONTACT}">咨询陈靖</a>'
            '</div></div></nav>')


def build(key, out, kind, ask, topic, cities, meta):
    m = meta[key]
    depth = out.count('/')
    pre = '../' * depth
    url = SITE + '/' + out
    contact = pre + 'index.html?ask=' + ask + ('&amp;topic=' + topic.replace(' ', '+') if topic else '') + '#contact'
    body = (ROOT / 'tools' / 'page-content' / (key + '.html')).read_text(encoding='utf-8')

    for a, b in URL_FIX.items():
        body = body.replace(a, b)
    for a, b in ANCHORS.items():
        body = body.replace('href="' + a + '"', 'href="' + pre + b + '"')
    body = body.replace('<div class="table-wrap">', '<div class="tablewrap" role="region" aria-label="比较表，可左右滑动" tabindex="0">')

    # 咨询模块：沿用成稿文案，接入现有联系表单与电话
    def cta(mo):
        inner = mo.group(1)
        h3 = re.search(r'<h3>(.*?)</h3>', inner, re.S).group(1).strip()
        p = re.search(r'<p>(.*?)</p>', inner, re.S).group(1).strip()
        label = re.search(r'<a class="button"[^>]*>(.*?)</a>', inner, re.S).group(1).strip()
        return ('<aside class="cta"><div><h3>' + h3 + '</h3><p>' + p + '</p>'
                '<div class="id">陈靖 Jing Chen · REALTOR® · BQ Realty · DRE #02147119</div></div>'
                '<div class="btnrow"><a class="btn gold" href="' + contact + '">' + label + ' →</a>'
                '<a class="btn gold" href="tel:+19259174019">电话 925-917-4019</a></div></aside>')
    body, n = re.subn(r'<aside class="cta">(.*?)</aside>', cta, body, flags=re.S)
    assert n == 1, key
    assert 'homesbyjingchen.com/#contact' not in body and 'href="#' not in body, key

    # 比较文章：补上两座城市的完整指南入口
    if cities:
        links = ' · '.join('<a href="' + pre + 'cities/' + s + '.html">' + CITY_NAMES[s] + ' 城市生活指南</a>' for s in cities)
        extra = '<p class="related">相关城市指南：' + links + '</p>'
        assert '<div class="sources">' in body, key
        body = body.replace('<div class="sources">', extra + '\n<div class="sources">', 1)

    if kind == 'article':
        crumbs = [('首页', pre + 'index.html', SITE + '/'), ('城市比较', pre + 'index.html#compare-guides', SITE + '/#compare-guides'), (ARTICLE_TITLES[key], None, url)]
        kicker = '城市比较 · BAY AREA CITY COMPARISON'
        ld_type = 'Article'
    else:
        label = '湾区买房服务' if key == 'buy' else '湾区卖房服务'
        crumbs = [('首页', pre + 'index.html', SITE + '/'), (label, None, url)]
        kicker = ('BUYING IN THE BAY AREA · 买房服务' if key == 'buy' else 'SELLING IN THE BAY AREA · 卖房服务')
        ld_type = 'WebPage'
    crumb_html = ' / '.join(('<a href="' + h + '">' + esc(n_) + '</a>') if h else esc(n_) for n_, h, _ in crumbs)

    agent = {"@type": "RealEstateAgent", "name": "Jing Chen 陈靖", "telephone": "+1-925-917-4019", "url": SITE + "/"}
    ld = {"@context": "https://schema.org", "@type": ld_type, "url": url, "inLanguage": "zh-CN",
          "description": m['description'], "datePublished": PUBLISHED, "dateModified": PUBLISHED,
          "publisher": agent}
    if ld_type == 'Article':
        ld["headline"] = m['h1']
        ld["mainEntityOfPage"] = url
        ld["image"] = SITE + "/images/hero.webp"
    else:
        ld["name"] = m['h1']
        ld["about"] = agent
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n_, "item": abs_} for i, (n_, _, abs_) in enumerate(crumbs)]}

    foot_extra = '买房服务' if key != 'buy' else '卖房服务'
    foot_href = 'buy.html' if key != 'buy' else 'sell.html'
    page = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="Jing Chen Homes 陈靖">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/images/hero.webp">
<meta property="og:locale" content="zh_CN">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{pre}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{pre}favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="{pre}apple-touch-icon.png">
<link rel="stylesheet" href="{pre}cities/guide.css?v={ver}">
<link rel="stylesheet" href="{pre}pages.css?v={ver}">
<script type="application/ld+json">{ld}</script>
<script type="application/ld+json">{bc}</script>
</head>
<body class="page">
{nav}
<header class="hero"><div class="container heroin">
<div class="crumbs">{crumbs}</div>
<div class="kicker">{kicker}</div>
<h1 class="pageh1">{h1}</h1>
<p class="intro">{lead}</p>
<div class="heroid">陈靖 Jing Chen · REALTOR® · BQ Realty · DRE #02147119 · <a href="tel:+19259174019">925-917-4019</a></div>
</div></header>
<main class="section white"><div class="container"><article class="art">
{body}
</article></div></main>
<footer><div class="container footer"><div><strong>Jing Chen 陈靖</strong><br>REALTOR® · BQ Realty · DRE #02147119 · <a href="tel:+19259174019">925-917-4019</a></div><div>© 2026 Jing Chen · 内容仅供一般参考，不构成估价、贷款、税务或法律意见<br><a href="{pre}index.html">返回首页</a> · <a href="{pre}{foot_href}">{foot_extra}</a> · <a href="{pre}index.html#market-cities">城市指南</a> · <a href="{contact}">预约咨询</a></div></div></footer>
</body></html>
'''.format(title=esc(m['title']), desc=esc(m['description']), url=url, site=SITE, pre=pre, ver=ASSET_VER,
           ogtype='article' if kind == 'article' else 'website',
           ld=json.dumps(ld, ensure_ascii=False), bc=json.dumps(bc, ensure_ascii=False),
           nav=nav(pre, key).replace('{CONTACT}', contact), crumbs=crumb_html, kicker=kicker,
           h1=esc(m['h1']), lead=m['lead'], body=body.strip(), contact=contact,
           foot_href=foot_href, foot_extra=foot_extra)
    dest = ROOT / out
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding='utf-8')
    return len(page)


def main():
    meta = json.loads((ROOT / 'tools' / 'seo-meta.json').read_text(encoding='utf-8'))
    for key, out, kind, ask, topic, cities in PAGES:
        print('built', out, build(key, out, kind, ask, topic, cities, meta))


if __name__ == '__main__':
    main()
