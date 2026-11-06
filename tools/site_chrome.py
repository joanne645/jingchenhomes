#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全站公共导航、页脚（build_site.py 和 build_city_guides.py 共用）。"""
import posixpath

SITE = 'https://www.homesbyjingchen.com'
ASSET_VER = '20261106'
PHONE = '925-917-4019'
TEL = 'tel:+19259174019'
DRE = '02147119'
BROKER = 'BQ Realty'
BROKER_DRE = None   # 拿到 BQ Realty 经纪公司 DRE 号后填在这里，页脚会自动显示

NAV = {
    'zh': [('buy', 'buy.html', '买房指南'), ('sell', 'sell.html', '卖房服务'), ('areas', 'areas.html', '地区与学区'),
           ('homeowner', 'homeowner.html', '房主之家'), ('sold', 'sold.html', '成交案例'),
           ('insights', 'insights.html', '地产知识'), ('about', 'about.html', '关于陈靖')],
    'en': [('buy', 'buy.html', 'Buy a Home'), ('sell', 'sell.html', 'Sell a Home'), ('areas', 'areas.html', 'Areas & Schools'),
           ('homeowner', 'homeowner.html', 'Homeowner Resources'), ('sold', 'sold.html', 'Sold'),
           ('insights', 'insights.html', 'Insights'), ('about', 'about.html', 'About Jing')],
}


def esc(t):
    return (str(t) if t is not None else '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def rel(frm, to):
    """从输出文件 frm 到站点路径 to 的相对链接。"""
    base = posixpath.dirname(frm)
    frag = ''
    if '#' in to:
        to, frag = to.split('#', 1)
        frag = '#' + frag
    q = ''
    if '?' in to:
        to, q = to.split('?', 1)
        q = '?' + q
    return posixpath.relpath(to, base or '.') + q + frag


def path(lang, p):
    return ('en/' + p) if lang == 'en' else p


def alt_out(out):
    return out[3:] if out.startswith('en/') else 'en/' + out


def asset(out, name):
    return rel(out, name) + '?v=' + ASSET_VER


def font_links():
    return ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Noto+Serif+SC:wght@500&display=swap" rel="stylesheet">')


def nav(lang, out, key=''):
    r = lambda p: esc(rel(out, path(lang, p)))
    items = ''.join(f'<a href="{r(p)}"' + (' aria-current="page"' if k == key else '') + f'>{esc(t)}</a>' for k, p, t in NAV[lang])
    cta = '预约咨询' if lang == 'zh' else 'Contact'
    other = alt_out(out)
    sw = ('<a class="slang" lang="en" hreflang="en" href="%s">EN</a>' if lang == 'zh' else '<a class="slang" lang="zh-CN" hreflang="zh-CN" href="%s">中文</a>') % esc(rel(out, other))
    label = '主导航' if lang == 'zh' else 'Main navigation'
    skip = '跳到正文' if lang == 'zh' else 'Skip to content'
    menu = '打开菜单' if lang == 'zh' else 'Open menu'
    return (f'<a class="skip" href="#main">{skip}</a><header class="snav"><div class="snav-in">'
            f'<a class="sbrand" href="{r("index.html")}"><img src="{esc(rel(out, "images/logo-nav.png"))}" alt="JC Team" width="60" height="48"><span><b>Jing Chen</b><small>REALTOR® · {BROKER} · DRE #{DRE}</small></span></a>'
            f'<button class="sburger" type="button" aria-label="{menu}" aria-expanded="false" aria-controls="slinks">☰</button>'
            f'<nav class="slinks" id="slinks" aria-label="{label}">{items}'
            f'<a class="scta"' + (' aria-current="page"' if key == 'contact' else '') + f' href="{r("contact.html")}">{cta}</a>{sw}</nav>'
            '</div></header>')


EHO = ('<svg viewBox="0 0 40 40" role="img" aria-label="Equal Housing Opportunity"><path fill="none" stroke="currentColor" stroke-width="3" d="M4 18 20 5l16 13M8 16v19h24V16"/>'
       '<path fill="currentColor" d="M14 20h12v3H14zm0 6h12v3H14z"/></svg>')


def footer(lang, out):
    r = lambda p: esc(rel(out, path(lang, p)))
    broker = BROKER + (f' · DRE #{BROKER_DRE}' if BROKER_DRE else '')
    z = lang == 'zh'
    cols = [
        ('服务' if z else 'Services', [('buy.html', '买房指南' if z else 'Buy a Home'), ('sell.html', '卖房服务' if z else 'Sell a Home'),
                                       ('homeowner.html', '房主之家' if z else 'Homeowner Resources'), ('calculators/buyer-costs.html', '买房费用计算器' if z else 'Buyer Cost Calculator'),
                                       ('calculators/net-proceeds.html', '卖房净收益估算' if z else 'Seller Net Proceeds')]),
        ('了解' if z else 'Explore', [('areas.html', '地区与学区' if z else 'Areas & Schools'), ('sold.html', '成交案例' if z else 'Sold Properties'),
                                      ('insights.html', '地产知识' if z else 'Insights'), ('about.html', '关于陈靖' if z else 'About Jing'),
                                      ('contact.html', '预约咨询' if z else 'Contact'), ('privacy.html', '隐私说明' if z else 'Privacy')]),
    ]
    colhtml = ''.join(f'<div><h2>{esc(h)}</h2><ul>' + ''.join(f'<li><a href="{r(p)}">{esc(t)}</a></li>' for p, t in ls) + '</ul></div>' for h, ls in cols)
    if z:
        lg = (f'<p>© 2026 Jing Chen 陈靖 · REALTOR® · {broker} · 持牌人 CA DRE #{DRE}。房地产信息仅供一般参考，房源状态、价格、面积、学校及市场数据应在交易前独立核实。'
              '成交案例信息来自 MLSListings 公开记录及公开房源页面；客户评价引用自陈靖的 Zillow 认证评价，版权归原平台及作者所有。</p>'
              '<p>本网站内容不构成法律、税务、贷款或投资建议。公平住房：我们遵守联邦和加州公平住房法律，向所有人提供平等的住房机会。</p>')
    else:
        lg = (f'<p>© 2026 Jing Chen · REALTOR® · {broker} · CA DRE #{DRE}. Real estate information is for general reference only. Listing status, prices, square footage, schools and market data should be independently verified before any transaction. '
              'Sales information comes from public MLSListings records and public listing pages. Client reviews are quoted from Jing Chen’s verified Zillow reviews; copyright belongs to the original platform and authors.</p>'
              '<p>Nothing on this site is legal, tax, lending or investment advice. Fair housing: we follow federal and California fair housing laws and support equal housing opportunity for everyone.</p>')
    area = '服务区域：硅谷 · 东湾 · 三谷' if z else 'Serving Silicon Valley, the East Bay and the Tri-Valley'
    langs = '中文 · English'
    return (f'<footer class="sfoot"><div class="sfoot-in"><div class="sfoot-grid"><div class="sf-brand"><b>Jing Chen 陈靖</b>'
            f'REALTOR® · {broker}<br>CA DRE #{DRE}<br><a href="{TEL}">{PHONE}</a><br>{area}<br>{langs}</div>{colhtml}</div>'
            f'<div class="sf-legal">{EHO}<div>{lg}</div></div></div></footer>')
