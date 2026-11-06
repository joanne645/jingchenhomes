#!/usr/bin/env python3
"""生成 cities/*.html 城市生活指南页面。

用法（在仓库根目录运行）：
    python3 tools/build_city_guides.py

内容来自 tools/city-content/<slug>.json，共用样式与脚本是 cities/guide.css、cities/guide.js。
改文字只需要改对应的 JSON，然后重新运行本脚本；不需要安装任何依赖。
"""
import json
import sys, re, html, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SJ_SEC = json.loads((ROOT / 'tools/city-content/san-jose-sections.json').read_text(encoding='utf-8'))
SRC = ROOT / 'tools' / 'city-content'
OUT = ROOT / 'cities'
SITE = 'https://www.homesbyjingchen.com'
REVIEWED = '2026年10月'
REVIEWED_ISO = '2026-10-08'
ASSET_VER = '20261107'

CITIES = [  # slug, 名称, 地图初始中心（仅用于边界加载前的初始视野）, 初始缩放
    ('palo-alto', 'Palo Alto', (37.425, -122.140), 12),
    ('cupertino', 'Cupertino', (37.318, -122.045), 13),
    ('sunnyvale', 'Sunnyvale', (37.380, -122.025), 12),
    ('mountain-view', 'Mountain View', (37.395, -122.080), 12),
    ('san-jose', 'San Jose', (37.300, -121.870), 11),
    ('fremont', 'Fremont', (37.530, -121.990), 11),
    ('milpitas', 'Milpitas', (37.432, -121.895), 12),
    ('dublin', 'Dublin', (37.712, -121.905), 12),
    ('pleasanton', 'Pleasanton', (37.665, -121.885), 12),
    ('san-ramon', 'San Ramon', (37.765, -121.945), 12),
]
NAMES = {s: n for s, n, _, _ in CITIES}

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sj_sections
from site_chrome import nav as site_nav, footer as site_footer, font_links, ASSET_VER as SITE_VER, rel  # noqa
SOLD = json.loads((ROOT / 'tools/site-data/sold.json').read_text(encoding='utf-8'))['records']
MK = json.loads((ROOT / 'tools/site-data/market.json').read_text(encoding='utf-8'))
SEO = json.loads((Path(__file__).resolve().parent / 'seo-meta.json').read_text(encoding='utf-8'))
# 与城市相关的比较文章（guides/*.html）
GUIDES = {
    'fremont': [('fremont-vs-dublin', 'Fremont 与 Dublin 买房比较')],
    'dublin': [('fremont-vs-dublin', 'Fremont 与 Dublin 买房比较'), ('dublin-vs-pleasanton', 'Dublin 与 Pleasanton 买房比较')],
    'pleasanton': [('dublin-vs-pleasanton', 'Dublin 与 Pleasanton 买房比较')],
    'sunnyvale': [('sunnyvale-vs-cupertino', 'Sunnyvale 与 Cupertino 买房比较')],
    'cupertino': [('sunnyvale-vs-cupertino', 'Sunnyvale 与 Cupertino 买房比较')],
}


def e(t):
    return html.escape(str(t if t is not None else ''), quote=True)

def paras(ps):
    if isinstance(ps, str):
        ps = [ps]
    return ''.join(f'<p>{e(p)}</p>' for p in ps if p and str(p).strip())

def ext(url, label, cls='btn sm'):
    if not url:
        return ''
    return f'<a class="{cls} ext" href="{e(url)}" target="_blank" rel="noopener">{e(label)}</a>'

def anchor_id(name):
    s = re.sub(r'[（(].*?[)）]', '', name)
    s = re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-').lower()
    return 'd-' + (s or 'area')

def geo_addr(addr):
    """只保留可交给 Census Geocoder 的街道地址（门牌开头）或路口；其他返回空字符串。"""
    if not addr:
        return ''
    a = re.sub(r'[（(].*?[)）]', '', addr).strip()
    parts = [p.strip() for p in a.split(',')]
    for i, p in enumerate(parts):
        if re.match(r'^\d+\s+\S', p):
            return ', '.join(parts[i:])
    if re.search(r'\S\s&\s\S', parts[0]) and len(parts) >= 2 and re.search(r'[A-Za-z]', parts[0]) and not re.search(r'[一-鿿]', a):
        return ', '.join(parts)
    return ''

def short_label(name):
    s = re.sub(r'[（(].*?[)）]', '', name).strip()
    s = re.split(r'[：:]', s)[-1].strip() if '：' in s or ':' in s else s
    return s

def load(slug):
    d = json.loads((SRC / f'{slug}.json').read_text(encoding='utf-8'))
    if slug == 'san-jose':
        x = json.loads((SRC / 'san-jose-districts.json').read_text(encoding='utf-8'))
        d['districts'] = x['districts']
        seen = {p['name'] for p in d['map'].get('pois', [])}
        for p in x['map'].get('pois', []):
            if p['name'] not in seen:
                d['map']['pois'].append(p); seen.add(p['name'])
        detailed = {a['district']: a['anchor'] for a in x['map'].get('district_anchors', [])}
        for a in d['map'].get('district_anchors', []):
            if a['district'] in detailed:
                a['anchor'] = detailed[a['district']]
        have = {s['url'] for s in d['sources']}
        d['sources'] += [s for s in x['sources'] if s['url'] not in have]
    return d

def fix_urls(o):
    if isinstance(o, dict):
        return {k: fix_urls(v) for k, v in o.items()}
    if isinstance(o, list):
        return [fix_urls(v) for v in o]
    if isinstance(o, str) and o.startswith('http'):
        return o.replace('fuhsd.org/about-us/general-information/district-boundary-maps', 'fuhsd.org/about-us/general-information/district-boundry-maps')
    return o

def place_list(places):
    out = []
    for p in places or []:
        note = f'<p>{e(p["note"])}</p>' if p.get('note') else ''
        out.append(f'<div class="place"><b>{e(p["name"])}</b><span class="k">{e(p.get("kind",""))}</span><span class="w">{e(p.get("where",""))}</span>{note}</div>')
    return f'<div class="places">{"".join(out)}</div>' if out else ''

def build(slug, center, zoom):
    d = fix_urls(load(slug))
    name = d['name']
    url = f'{SITE}/cities/{slug}.html'
    sj = slug == 'san-jose'
    dists = d['districts']
    ids = {}
    for x in dists:
        i = anchor_id(x['name']); n = 2
        while i in ids.values():
            i = f'{anchor_id(x["name"])}-{n}'; n += 1
        ids[x['name']] = i

    # ---------- 概览 ----------
    pos = d['position']
    chips = ''.join(f'<span class="chip">{e(n)}</span>' for n in pos.get('neighbors', []))
    bg = d.get('background')
    bg_html = ''
    if bg:
        tl = ''.join(f'<div class="titem"><strong>{e(t["year"])}</strong><p>{e(t["text"])}</p></div>' for t in bg.get('timeline', []))
        bg_html = f'<h3 class="sub">城市背景</h3><div class="prose">{paras(bg.get("paragraphs", []))}</div><div class="timeline">{tl}</div>'
    overview = f'''
<section class="section white" id="overview"><div class="container">
<div class="kicker">01 · 城市生活概览</div><h2 class="title">{e(name)} 在哪里，日常会去到哪里</h2>
<div class="grid2"><div class="prose">{paras(pos['paragraphs'])}{f'<div class="note">{e(pos["note"])}</div>' if pos.get('note') else ''}</div>
<div><div class="factbox"><h3>相邻的城市与地带</h3><p>实际接壤的城市和社区如下。看房时常会跨过市界，城市、邮编和学区要分别核对。</p><div class="chips">{chips.replace('class="chip"','class="chip" style="background:transparent;color:#efe2bd;border-color:rgba(255,255,255,.3)"')}</div></div>{bg_html}</div></div>
</div></section>'''

    # ---------- 地图 ----------
    m = d['map']
    sch = d['schools']
    stations = [{'n': s['name'], 'sys': s['system'], 'a': geo_addr(s.get('address', ''))} for s in m.get('stations', [])]
    pois = [{'n': p['name'], 'c': p.get('category', ''), 'a': geo_addr(p.get('address', '')), 'd': p.get('district', '')} for p in m.get('pois', [])]
    anchors = {a['district']: a['anchor'] for a in m.get('district_anchors', [])}
    dmarks = []
    names_for_marks = [x['name'] for x in dists] + [a for a in anchors if a not in ids]
    for dn in names_for_marks:
        a = geo_addr(anchors.get(dn, ''))
        if not a or '&' in a.split(',')[0]:
            alt = next((p['a'] for p in pois if p['d'] == dn and p['a'] and '&' not in p['a'].split(',')[0]), '')
            a = alt or a
        dmarks.append({'n': dn, 's': short_label(dn), 'a': a, 'id': ids.get(dn, 'districts')})
    sd_js = [{'name': x['name'], 'short': x.get('short', ''), 'url': x.get('locator_url', '')} for x in sch['districts']]
    if sj:
        for x in dists:
            for y in x.get('school_districts', []):
                if y['name'] not in [z['name'] for z in sd_js]:
                    sd_js.append({'name': y['name'], 'short': '', 'url': y.get('locator_url', '')})
    guide = {'slug': slug, 'name': name, 'center': list(center), 'zoom': zoom, 'stations': stations, 'pois': pois, 'districts': dmarks, 'sd': sd_js}

    st_list = ''.join(f'<li><span class="sw sq"></span><span>{e(s["name"])}<br><small class="small">{e(s["system"])}</small></span></li>' for s in m.get('stations', []))
    cats = [('park', '公园与户外', '#2e7d32'), ('trailhead', '步道与保护区入口', '#558b2f'), ('library', '图书馆', '#1565c0'), ('community', '社区与公共设施', '#6a1b9a'), ('grocery', '超市与市集', '#e65100'), ('shopping', '商业中心', '#ad1457'), ('hospital', '医疗', '#c62828'), ('school_admin', '学区与学校', '#455a64')]
    used = {p['c'] for p in pois}
    cat_lg = ''.join(f'<li><span class="sw dot" style="background:{c}"></span><span>{lab}</span></li>' for k, lab, c in cats if k in used)
    om = m.get('official_maps', [])
    def mlinks(items):
        out = []
        for it in items:
            if not it.get('url'):
                continue
            sub = it.get('note') or it.get('what') or ''
            small = f'<small>{e(sub)}</small>' if sub else ''
            out.append(f'<a href="{e(it["url"])}" target="_blank" rel="noopener"><span class="ext">{e(it["label"])}</span>{small}</a>')
        return '<div class="mlinks">' + ''.join(out) + '</div>'
    route_links = []
    seen_u = set()
    for i in (d['commute'].get('links', []) + [x for x in om if x.get('kind') in ('transit', 'bike', 'safe_routes')]):
        if i.get('url') and i['url'] not in seen_u:
            seen_u.add(i['url']); route_links.append(i)
    sr = sch.get('safe_routes') or {}
    if sr.get('url') and sr['url'] not in seen_u:
        route_links.append({'label': f'{name} 建议上学路线（Safe Routes to School）', 'url': sr['url']})
    school_links = []
    for x in sch['districts']:
        if x.get('locator_url'):
            school_links.append({'label': f'{x.get("short") or x["name"]}：按地址查询学校', 'url': x['locator_url'], 'note': f'{x["name"]} · {x.get("grades","")}'})
    other_maps = [x for x in om if x.get('kind') not in ('transit', 'bike', 'safe_routes') and x.get('url') not in {s['url'] for s in school_links}]
    more_maps = ''
    if other_maps:
        cells = []
        for x in other_maps:
            if not x.get('url'):
                continue
            note = f'<p>{e(x["note"])}</p>' if x.get('note') else ''
            cells.append(f'<div class="item"><h4>{e(x["label"])}</h4>{note}{ext(x["url"], "打开官方地图")}</div>')
        more_maps = '<h3 class="sub">更多官方地图</h3><div class="items">' + ''.join(cells) + '</div>'
    maps_html = f'''
<section class="section" id="map"><div class="container">
<div class="kicker">02 · 城市地图</div><h2 class="title">先看清位置，再比较片区</h2>
<p class="lead">地图分成五层，每次只看一类信息：城市范围与轨道站、片区与日常设施、学区范围、上学和通勤路线的官方地图、按地址查询的环境工具。边界来自官方数据，学校招生范围请进入各学区的地址查询。</p>
<div class="maptabs" role="tablist" aria-label="地图图层">
<button type="button" role="tab" data-tab="locate" aria-selected="true">城市定位</button>
<button type="button" role="tab" data-tab="life" aria-selected="false">社区生活</button>
<button type="button" role="tab" data-tab="school" aria-selected="false">学区范围</button>
<button type="button" role="tab" data-tab="routes" aria-selected="false">日常路线</button>
<button type="button" role="tab" data-tab="env" aria-selected="false">环境查询</button>
</div>
<div class="mapwrap">
<div class="mapbox" id="citymap" role="application" aria-label="{e(name)} 地图">
<div class="tiles"></div><svg class="ov" aria-hidden="true"><g></g></svg><div class="mk"></div>
<div class="mapstat" aria-live="polite"></div>
<div class="mapctl"><button type="button" class="zin" aria-label="放大">+</button><button type="button" class="zout" aria-label="缩小">−</button><button type="button" class="zhome" aria-label="回到城市全图" title="回到城市全图">⌂</button></div>
<button type="button" class="maptap"><span>点一下，再用手指拖动和缩放地图</span></button>
<button type="button" class="mapdone">完成，继续浏览页面</button>
<div class="mapattr">底图 © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors · 边界 U.S. Census Bureau</div>
<noscript><p style="padding:20px">地图需要启用 JavaScript。也可以直接使用右侧的官方地图入口。</p></noscript>
</div>
<div class="mapside">
<div class="pane" data-pane="locate"><h3>城市定位</h3>
<p>深蓝色线是 {e(name)} 的城市边界。邮寄地址上的城市名、城市边界和学区范围是三件事，靠近市界的房子要逐项核对。电脑上按住 Ctrl 或 ⌘ 滚动可以缩放。</p>
<ul class="lg"><li><span class="sw" style="background:rgba(198,163,91,.25)"></span><span>{e(name)} 城市边界</span></li>{st_list}</ul>
<p class="small">主干道、高速和轨道线路见底图；相邻城市：{e("、".join(pos.get("neighbors", [])))}。</p></div>
<div class="pane" data-pane="life" hidden><h3>社区生活</h3>
<p>深蓝色标签是各片区内的一个代表性地点，用来帮你找到片区的大致位置，不表示片区边界。点标签可以跳到下面对应的片区介绍；圆点是正文提到的公园、图书馆、商业和医疗设施。</p>
<ul class="lg">{cat_lg}</ul>
<div class="btnrow"><a class="btn sm" href="#districts">看片区比较</a><a class="btn sm" href="#daily">看日常设施清单</a></div></div>
<div class="pane" data-pane="school" hidden><h3>学区范围</h3>
<p>这一层显示覆盖 {e(name)} 的学区范围（District Boundary）。它只能告诉你一个位置属于哪个学区；具体对应哪所小学、初中和高中，要用学区的地址查询工具确认。只占市界极小边角的学区可能不显示。</p>
<ul class="lg" id="sdlegend"></ul>
{mlinks(school_links)}</div>
<div class="pane" data-pane="routes" hidden><h3>日常路线</h3>
<p>通勤和上学路线请直接使用交通机构与市政府的官方地图：车站位置与时刻、公交线路、自行车道，以及各校的建议步行和骑行路线。地图上的红色方块是轨道车站。</p>
{mlinks(route_links)}</div>
<div class="pane" data-pane="env" hidden><h3>环境查询</h3>
<p>洪水、地震和山火等图层都要按具体地址查。一张图说明的是需要继续核实的事项，不能据此判断某套房屋一定安全或一定有问题。</p>
{mlinks(d['environment'].get('tools', []))}</div>
<div class="maperr" id="maperr" hidden></div>
<p class="mapsrc">底图：© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors。城市边界与学区范围：U.S. Census Bureau <a href="https://tigerweb.geo.census.gov/tigerwebmain/TIGERweb_main.html" target="_blank" rel="noopener">TIGERweb</a> 现行图层，打开页面时实时读取。<span id="mapdate"></span> 地点位置由 U.S. Census Geocoder 按官方公布的街道地址换算，与实际入口可能有几十米出入；没有门牌地址的地点不在图上标出。</p>
</div></div>
{more_maps}
</div></section>'''

    # ---------- 片区 ----------
    idx_html = ''
    if sj:
        cells = []
        for x in d.get('district_index', []):
            inner = f'<i>{e(x.get("area",""))}</i><b>{e(x["name"])}</b>{e(x["one_line"])}'
            if x['name'] in ids:
                cells.append(f'<a href="#{ids[x["name"]]}">{inner}</a>')
            else:
                cells.append(f'<div>{inner}</div>')
        idx_html = f'<h3 class="sub" id="district-index">片区索引</h3><p class="small">带箭头的六个片区在下面有详细介绍，其余片区先给出位置和主要特征。</p><div class="dindex">{"".join(cells)}</div><h3 class="sub">六个代表性片区</h3>'
    else:
        cells = ''.join(f'<a href="#{ids[x["name"]]}"><b>{e(x["name"])}</b>{e(x.get("tag",""))}</a>' for x in dists)
        idx_html = f'<div class="dindex">{cells}</div>'
    cards = []
    for n, x in enumerate(dists):
        extra = ''
        btns = ''.join(ext(y.get('locator_url'), f'{y["name"]}（{y.get("grades","")}）地址查询') for y in x.get('school_districts', []))
        btns += ''.join(ext(y.get('url'), y.get('label', '')) for y in x.get('links', []))
        if btns:
            extra = f'<div class="dlinks"><span>官方查询入口：</span>{btns}</div>'
        cards.append(f'''<details class="dist" id="{ids[x['name']]}"{' open' if n == 0 else ''}>
<summary><h3>{e(x['name'])}</h3><span class="tag">{e(x.get('tag',''))}</span><span class="tog"><span class="o">展开</span><span class="c">收起</span></span></summary>
<div class="dbody">
<div class="dcell"><h4>位置与范围</h4><p>{e(x['where'])}</p></div>
<div class="dcell"><h4>住房特点</h4><p>{e(x['housing'])}</p></div>
<div class="dcell"><h4>日常设施与活动</h4><p>{e(x['daily'])}</p></div>
<div class="dcell"><h4>通勤与学校核验</h4><p>{e(x['commute_school'])}</p></div>
<div class="dcell"><h4>需要接受的取舍</h4><p>{e(x['tradeoffs'])}</p></div>
<div class="dcell take"><h4>实地看区时留意</h4><p>{e(x['visit'])}</p></div>
</div>{extra}</details>''')
    districts = f'''
<section class="section cream2" id="districts"><div class="container">
<div class="kicker">03 · 片区比较</div><h2 class="title">同在 {e(name)}，不同片区的日子不一样</h2>
<p class="lead">{e(d['districts_intro'])}</p>
{idx_html}
<div class="btnrow" style="margin:0 0 14px"><button type="button" class="btn sm" id="openall">展开全部片区</button></div>
{''.join(cards)}
</div></section>'''

    # ---------- 日常 ----------
    c = d['commute']
    scen = ''.join(f'<div><h4>{e(s["title"])}</h4><p>{e(s["text"])}</p></div>' for s in c.get('scenarios', []))
    ver = ''.join(f'<li>{e(v)}</li>' for v in c.get('verify', []))
    clinks = ''.join(ext(l['url'], l['label']) for l in c.get('links', []) if l.get('url'))
    daily = f'''
<section class="section white" id="daily"><div class="container">
<div class="kicker">04 · 工作日与周末</div><h2 class="title">上班、接送、买菜和运动，各走一遍</h2>
<h3 class="sub">门到门通勤</h3>
<div class="prose">{paras(c['paragraphs'])}</div>
<div class="scen">{scen}</div>
<div class="two"><div><h4 style="margin:0;font-size:17px;color:var(--navy)">怎样核实自己的通勤</h4><ul class="check">{ver}</ul></div>
<div><h4 style="margin:0;font-size:17px;color:var(--navy)">线路与时刻的官方入口</h4><div class="btnrow">{clinks}</div></div></div>
<h3 class="sub">买菜、用餐与办事</h3>
<div class="prose">{paras(d['errands']['paragraphs'])}</div>{place_list(d['errands'].get('places'))}
<h3 class="sub">公园、运动与周末</h3>
<div class="prose">{paras(d['parks']['paragraphs'])}</div>{place_list(d['parks'].get('places'))}
<h3 class="sub">医疗与行动便利</h3>
<div class="prose">{paras(d['medical']['paragraphs'])}</div>{place_list(d['medical'].get('places'))}
</div></section>'''

    # ---------- 学校 ----------
    sds = []
    for x in sch['districts']:
        b = ext(x.get('locator_url'), x.get('locator_label') or '按地址查询学校', 'btn sm solid')
        if x.get('map_url') and x.get('map_url') != x.get('locator_url'):
            b += ext(x['map_url'], x.get('map_label') or '官方边界图')
        if x.get('enroll_url') and x.get('enroll_url') not in (x.get('locator_url'), x.get('map_url')):
            b += ext(x['enroll_url'], '入学说明')
        short = f'（{e(x["short"])}）' if x.get('short') else ''
        cov = f'<p>{e(x["covers"])}</p>' if x.get('covers') else ''
        note = f'<p>{e(x["note"])}</p>' if x.get('note') else ''
        sds.append(f'<div class="sd"><h4>{e(x["name"])}{short}</h4><div class="g">{e(x.get("grades",""))}</div>{cov}{note}<div class="btnrow">{b}</div></div>')
    progs = ''.join(f'<li>{e(p)}</li>' for p in sch.get('programs', []))
    summary_text = ''.join(sch['summary'])
    closing = '' if '以具体地址、入学学年和学区确认结果为准' in summary_text else '<div class="note">学校边界与安排可能调整，请以具体地址、入学学年和学区确认结果为准。</div>'
    schools = f'''
<section class="section" id="schools"><div class="container">
<div class="kicker">05 · 学校与入学</div><h2 class="title">学校信息按具体地址核实</h2>
<div class="prose">{paras(sch['summary'])}</div>
<div class="bkinds">
<div><b>城市边界</b>决定市政服务和城市税费，与学校安排没有直接对应关系。</div>
<div><b>学区边界</b>District Boundary，决定地址归哪个学区管理。</div>
<div><b>学校招生范围</b>Attendance Boundary，决定地址通常对应哪所学校，按学段分别划定。</div>
<div><b>校董选举区</b>Trustee Area，只用于选举校董，不能用来判断学校。</div>
</div>
<h3 class="sub">相关学区与官方查询</h3>
{''.join(sds)}
{closing}
<div class="two" style="margin-top:34px">
<div><h3 class="sub" style="margin-top:0">课程、照护与学生支持</h3><ul class="dots">{progs}</ul></div>
<div><h3 class="sub" style="margin-top:0">选择性项目与划片学校</h3><div class="prose">{paras(sch.get('choice_note',''))}</div></div>
</div>
<div class="two" style="margin-top:20px">
<div><h3 class="sub" style="margin-top:0">怎样看学校数据</h3><div class="prose">{paras(sch.get('dashboard_note',''))}{paras(sch.get('trustee_note',''))}</div><div class="btnrow">{ext('https://www.caschooldashboard.org/', 'California School Dashboard')}</div></div>
<div><h3 class="sub" style="margin-top:0">上学路线</h3><div class="prose">{paras(sr.get('text',''))}</div><div class="btnrow">{ext(sr.get('url'), '建议上学路线地图')}</div></div>
</div>
</div></section>'''

    # ---------- 住房 ----------
    h = d['housing']
    types = ''.join(f'<div><h4>{e(t["type"])}</h4><p>{e(t["text"])}</p></div>' for t in h.get('types', []))
    cl = ''.join(f'<li>{e(v)}</li>' for v in d['costs'].get('checklist', []))
    tools = ''.join(f'<div class="item"><h4>{e(t["label"])}</h4><p>{e(t.get("what",""))}</p>{ext(t["url"], "打开官方工具")}</div>' for t in d['environment'].get('tools', []) if t.get('url'))
    pl = d['planning']
    pitems = ''.join(f'<div class="item"><h4>{e(i["name"])}</h4><div class="st">{e(i.get("status",""))}</div><p>{e(i.get("text",""))}</p>{ext(i.get("url"), "官方资料")}</div>' for i in pl.get('items', []))
    housing = f'''
<section class="section white" id="housing"><div class="container">
<div class="kicker">06 · 住房与成本</div><h2 class="title">能买到什么房子，住下来还要付什么</h2>
<h3 class="sub">房型与日常使用</h3>
<div class="prose">{paras(h['paragraphs'])}</div>
<div class="scen">{types}</div>
<div class="btnrow"><a class="btn solid" href="../buy.html?city={e(name.replace(' ', '+'))}#search">查看 {e(name)} 在售房源 →</a><a class="btn" href="../contact.html?city={e(name.replace(' ', '+'))}&amp;type=budget#contact">根据我的预算和通勤，缩小看房范围 →</a></div>
<h3 class="sub">房价之外的居住成本</h3>
<div class="two"><div class="prose">{paras(d['costs']['paragraphs'])}</div><div><h4 style="margin:0;font-size:17px;color:var(--navy)">看具体房源时要核对</h4><ul class="check">{cl}</ul></div></div>
<h3 class="sub">气候、噪音与按地址核实的环境因素</h3>
<div class="prose">{paras(d['environment']['paragraphs'])}</div>
<div class="items">{tools}</div>
<h3 class="sub">周边建设与长期适用性</h3>
<div class="prose">{paras(pl['paragraphs'])}</div>
<div class="items">{pitems}</div>
</div></section>'''

    # ---------- 房价数据、近期成交、相关文章 ----------
    mk = MK['cities'][slug]
    local = [r for r in SOLD if r['city'] == name][:4]
    def sold_card(r):
        ph = f'<div class="ph"><img src="{e(r["image"])}" alt="{e(r["address"])}" loading="lazy" referrerpolicy="no-referrer" data-hide-on-error></div>' if r.get('image') else ''
        y, mo, da = r['date'].split('-')
        return (f'<a class="prop" href="{e(r["url"])}" target="_blank" rel="noopener">{ph}<div class="pi"><span class="bd">成交 · {y} 年 {int(mo)} 月 {int(da)} 日</span><h3>{e(r["address"])}</h3>'
                f'<span class="m">{r["beds"]:g} 卧 · {r["baths"]:g} 卫 · {r["sqft"]:,} sqft</span><span class="pr">${r["price"]:,}</span></div></a>')
    sold_html = (f'<h3 class="sub">{e(name)} 的近期真实成交</h3><div class="soldrow">' + ''.join(sold_card(r) for r in local) + f'</div><div class="btnrow" style="margin-top:16px"><a class="btn" href="../sold.html?city={e(name.replace(" ", "+"))}">查看全部成交案例 →</a></div>') if local else f'<h3 class="sub">近期真实成交</h3><div class="prose"><p>目前公开记录里没有陈靖在 {e(name)} 的成交。可以看<a href="../sold.html" style="text-decoration:underline">全部成交案例</a>。</p></div>'
    arts = [('compare-cities', '不同城市与社区怎么比较'), ('school-lookup', '怎样按地址查询学校'), ('holding-costs', '房产持有成本')]
    art_html = ''.join(f'<a href="../insights/{a}.html"><h4>{t}</h4><span class="go">阅读文章 →</span></a>' for a, t in arts)
    market_sec = f'''
<section class="section" id="market"><div class="container">
<div class="kicker">07 · 房价数据与近期成交</div><h2 class="title">{e(name)} 的市场数字怎么看</h2>
<div class="tablebox"><table><thead><tr><th>城市</th><th>近 3 个月成交中位价</th><th>同比变化</th></tr></thead><tbody><tr><td>{e(name)}</td><td>{e(mk['median'])}</td><td>{e(mk['yoy_zh'])}</td></tr></tbody></table></div>
<div class="note">来源：{e(MK['source_zh'])}。统计口径：{e(MK['method_zh'])}更新时间：{e(MK['updated_zh'])}。这是全市概括数字，不是任何一套房屋的估值，也不代表未来走势。十个城市的对比见<a href="../areas.html#market" style="text-decoration:underline">地区与学区</a>。</div>
{sold_html}
<h3 class="sub">相关知识文章</h3><div class="cmp">{art_html}</div>
</div></section>'''

    # ---------- 看区路线 ----------
    t = d['tour']
    stop_prefix = re.compile(r'^第\s*\d+\s*站[\s：:·]*')
    stops = ''.join('<div class="stop"><h4>' + e(stop_prefix.sub('', s['name'])) + '</h4><p>' + e(s['text']) + '</p></div>' for s in t.get('stops', []))
    qs = ''.join(f'<li>{e(q)}</li>' for q in t.get('questions', []))
    tour = f'''
<section class="section dark" id="tour"><div class="container">
<div class="kicker">08 · 实地看区路线</div><h2 class="title">用半天时间，把 {e(name)} 走一遍</h2>
<p class="lead">{e(t['intro'])}</p>
<div class="two" style="margin-top:30px"><div><div class="stops">{stops}</div></div>
<div><h3 style="margin:0 0 4px;font-size:21px;color:var(--gold2)">看房前后要核对的问题</h3><ul class="check">{qs}</ul></div></div>
</div></section>'''

    # ---------- 比较与咨询 ----------
    cmp_cards = []
    for x in d.get('compare', []):
        inner = f'<h4>{e(x["city"])}</h4><p>{e(x["text"])}</p>'
        if x.get('slug') in NAMES and x['slug'] != slug:
            cmp_cards.append(f'<a href="{x["slug"]}.html">{inner}<span class="go">看 {e(NAMES[x["slug"]])} 指南 →</span></a>')
        else:
            cmp_cards.append(f'<div>{inner}</div>')
    allc = ''.join(f'<a href="{s}.html"{" class=cur aria-current=page" if s == slug else ""}>{e(n)}</a>' for s, n, _, _ in CITIES)
    q = name.replace(' ', '+')
    gl = ''.join('<a class="btn" href="../guides/' + g + '.html">' + e(t_) + ' →</a>' for g, t_ in GUIDES.get(slug, []))
    if sj:
        gl = '<a class="btn" href="../areas/san-jose/index.html">San Jose 各邮编市场分析 →</a>' + gl
    glinks = '<div class="btnrow" style="margin-top:20px">' + gl + '<a class="btn" href="../buy.html">湾区买房服务：六个步骤 →</a></div>'
    compare = f'''
<section class="section" id="compare"><div class="container">
<div class="kicker">09 · 城市比较与咨询</div><h2 class="title">还值得一起比较的城市</h2>
<p class="lead">下面的比较都放在同样的预算、房型和通勤条件下来看。城市之间没有高下，差别在于你更看重哪一项。</p>
<div class="cmp">{''.join(cmp_cards)}</div>{glinks}
<div class="cta"><div><h3>把范围缩小到几个片区，再到几套房</h3><p>告诉陈靖你的预算、办公地点、交通方式和对住房的要求，一起比较片区，逐项核对学校、通勤、房屋状况与持有成本。</p><div class="id">Jing Chen 陈靖 · REALTOR® · BQ Realty · DRE #02147119 · <a href="tel:+19259174019">925-917-4019</a></div></div>
<div class="btnrow"><a class="btn gold" href="../contact.html?city={e(q)}&amp;type=compare">让陈靖帮我比较这几个城市 →</a><a class="btn gold" href="../contact.html?city={e(q)}&amp;type=budget">根据我的预算和通勤，缩小看房范围 →</a><a class="btn gold" href="../contact.html?city={e(q)}&amp;type=city">咨询 {e(name)} 的购房选择 →</a></div></div>
<h3 class="sub">十个城市的生活指南</h3><div class="allc">{allc}</div>
</div></section>'''

    if sj:
        sc = sj_sections
        c = sc.Ctx('zh', d, SJ_SEC, '../', lambda z: '../areas/san-jose/index.html' if z == 'index' else f'../areas/san-jose/{z}/index.html')
        c.zip_area = lambda z: (json.loads((ROOT / f'tools/v2-content/zip/{z}.json').read_text(encoding='utf-8'))['area'] if (ROOT / f'tools/v2-content/zip/{z}.json').exists() else '')
        wrap = lambda sid, kick, title, inner: f'<section class="section white" id="{sid}"><div class="container znarrow"><div class="kicker">{kick}</div><h2 class="title">{title}</h2>{inner}</div></section>'
        overview = wrap('overview', '01 · 城市生活概览', f'{e(name)} 在哪里，日常会去到哪里', sc.overview(c))
        maps_html = maps_html.replace('<section class="section" id="map">', '<section class="section white" id="map">', 1)
        districts = wrap('districts', '03 · 片区比较', f'同在 {e(name)}，不同片区的日子不一样', sc.districts(c, ids))
        daily = wrap('daily', '04 · 工作日与周末', '上班、接送、买菜和运动，各走一遍', sc.daily(c))
        schools = wrap('schools', '05 · 学校与入学', '学校信息按具体地址核实', sc.schools(c))
        hcta = f'<p class="zback"><a class="zmore" href="../buy.html?city={e(name.replace(" ", "+"))}#search">查看 San Jose 在售房源 →</a></p>'
        housing = wrap('housing', '06 · 住房与成本', '能买到什么房子，住下来还要付什么', sc.housing(c, hcta))
        src_note = f'来源：{e(MK["source_zh"])}。统计口径：{e(MK["method_zh"])}更新时间：{e(MK["updated_zh"])}。这是全市概括数字，不是任何一套房屋的估值，也不代表未来走势。'
        art_list = '<h3 class="sub">相关知识文章</h3><ul class="zlinks">' + ''.join(f'<li><a href="../insights/{a}.html">{t_}</a></li>' for a, t_ in arts) + '</ul>'
        market_sec = wrap('market', '07 · 房价数据与近期成交', f'{e(name)} 的市场数字怎么看', sc.market(c, mk['median'], mk['yoy_zh'], src_note, sold_html, art_list))
        tour = wrap('tour', '08 · 实地看区路线', f'用半天时间，把 {e(name)} 走一遍', sc.tour(c))
        cta_html = compare[compare.index('<div class="cta">'):compare.rindex('</div></section>')]
        compare = wrap('compare', '09 · 比较与咨询', '把范围缩小到几个片区', sc.compare(c, lambda sl: f'{sl}.html' if sl in NAMES else '', glinks + cta_html))

    # ---------- 来源 ----------
    srcs = ''.join(f'<div class="source"><b>{e(s.get("org",""))}</b><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s.get("label") or s["url"])}</a></div>' for s in d['sources'] if s.get('url'))
    sources = f'''
<section class="section cream2" id="sources"><div class="container">
<div class="kicker">资料来源</div><h2 class="title" style="font-size:clamp(24px,3vw,34px)">这份指南依据的公开资料</h2>
<p class="lead">内容核对时间为{REVIEWED}，以市政府、学区、交通机构、县和州政府等公开资料为主。门店营业、班次、学校安排和建设进度会变化，文中已注明资料日期的地方请以对应机构的最新公告为准。</p>
<details class="src"><summary>查看全部 {len([s for s in d['sources'] if s.get('url')])} 条资料来源</summary><div class="srcl">{srcs}</div></details>
<div class="note" style="margin-top:22px">城市、片区、学校、通勤和环境信息仅供一般了解，不构成估价、投资、税务或法律意见。片区名称是惯称或规划用名，不是法定边界；学校安排以学区对具体地址的确认为准；具体房源请结合最新 MLS 资料、卖方披露、公共记录和独立检查核实。</div>
</div></section>'''

    seo = SEO[slug]
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": seo['h1'], "description": seo['description'], "url": url, "inLanguage": "zh-CN", "dateModified": REVIEWED_ISO,
          "about": {"@type": "City", "name": f"{name}, California"},
          "author": {"@type": "RealEstateAgent", "name": "Jing Chen 陈靖", "telephone": "925-917-4019", "url": SITE + "/"},
          "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Jing Chen Homes", "item": SITE + "/"},
              {"@type": "ListItem", "position": 2, "name": "地区与学区", "item": SITE + "/areas.html"},
              {"@type": "ListItem", "position": 3, "name": f"{name} 城市生活指南", "item": url}]}}
    guide_json = json.dumps(guide, ensure_ascii=False).replace('</', '<' + chr(92) + '/')
    facts = ''.join(f'<div class="fact"><small>{e(f["label"])}</small><strong>{e(f["value"])}</strong></div>' for f in d['facts'][:4])
    page = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(seo['title'])}</title>
<meta name="description" content="{e(seo['description'])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Jing Chen Homes 陈靖">
<meta property="og:title" content="{e(seo['title'])}">
<meta property="og:description" content="{e(seo['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/images/hero.webp">
<meta property="og:locale" content="zh_CN">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="icon" href="../favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<link rel="alternate" hreflang="zh-CN" href="{url}"><link rel="alternate" hreflang="en" href="{SITE}/en/cities/{slug}.html"><link rel="alternate" hreflang="x-default" href="{url}">
{font_links()}
<link rel="stylesheet" href="guide.css?v={ASSET_VER}">
<link rel="stylesheet" href="chrome.css?v={ASSET_VER}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body class="city" data-page="city">
{site_nav("zh", f"cities/{slug}.html", "areas")}
<div class="subnav"><div class="subnav-in"><a href="#overview">概览</a><a href="#map">地图</a><a href="#districts">片区</a><a href="#daily">日常</a><a href="#schools">学校</a><a href="#housing">住房与成本</a><a href="#market">房价与成交</a><a href="#tour">看区路线</a><a href="#compare">比较与咨询</a></div></div>

<header class="hero"><div class="container heroin">
<div class="crumbs"><a href="../index.html">首页</a> / <a href="../areas.html">地区与学区</a> / {e(name)}</div>
<div class="kicker">BAY AREA LIVING GUIDE · {e(d.get('county',''))}</div>
<p class="cityname" aria-hidden="true">{e(name)}<span>城市生活指南</span></p>
<h1 class="cityh1">{e(seo['h1'])}</h1>
<p class="intro lead1">{e(seo['lead'])}</p>
<p class="intro">{e(d['hero']['intro'])}</p>
<div class="herotag">{e(d['hero']['tagline'])}</div>
<div class="facts">{facts}</div>
</div></header>
{overview}{maps_html}{districts}{daily}{schools}{housing}{market_sec}{tour}{compare}{sources}
{site_footer("zh", f"cities/{slug}.html")}
<script>window.GUIDE={guide_json};</script>
<script src="guide.js?v={ASSET_VER}"></script>
<script src="../site.js?v={SITE_VER}" defer></script>
<script>(function(){{var b=document.getElementById('openall');if(!b)return;b.onclick=function(){{var ds=[].slice.call(document.querySelectorAll('details.dist'));var open=ds.some(function(x){{return !x.open}});ds.forEach(function(x){{x.open=open}});b.textContent=open?'收起全部片区':'展开全部片区'}}}})();</script>
</body></html>
'''
    (OUT / f'{slug}.html').write_text(page, encoding='utf-8')
    return d

def main():
    for slug, name, center, zoom in CITIES:
        build(slug, center, zoom)
        print('built', slug, len((OUT / f'{slug}.html').read_text(encoding='utf-8')))

if __name__ == '__main__':
    main()
