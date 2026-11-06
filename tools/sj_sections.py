"""San Jose 地区指南的图文栏目，中英文共用。

结构统一：标题 → 照片（1 张或 3 张）→ 介绍 → 买家需要知道 → 卖家需要知道（适用时）→ 官方入口。
文字来自 tools/city-content（中文）和 tools/v2-content/en-cities（英文），这里不写事实内容。
照片和授权记录在 tools/city-content/san-jose-photos.json。
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
e = lambda s: html.escape(str(s or ''), quote=True)
PHOTOS = json.loads((ROOT / 'tools/city-content/san-jose-photos.json').read_text(encoding='utf-8'))
ZIP_ORDER = ['95129', '95120', '95125', '95124', '95118', '95128', '95131', '95126', '95132', '95135']
AREA_ZIP = {'Willow Glen': '95125', 'Almaden Valley': '95120', 'West San Jose': '95129', 'Cambrian': '95124', 'Berryessa': '95132', 'Evergreen': '95135', 'North San Jose': '95131', 'Rose Garden / Shasta-Hanchett': '95126', 'Blossom Valley': '95118'}

T = {
    'zh': dict(sep='：', full='查看完整地区指南', official='官方网站', view='查看全部照片 · {n} 张', demo='临时演示图 · 上线前替换',
               hospitals='主要医院', malls='主要商业中心', dining='代表性街区', parks='主要公园与步道', lib='馆舍', med_note='医院信息和服务范围以官方资料为准。',
               t_med=('医疗资源', '医院与急诊分布'), t_shop=('购物与采购', '各片区有自己的生活节点'), t_din=('餐饮与街区', 'Downtown 和老街区的生活'),
               t_park=('公园与户外', '山麓、溪流步道和亲子设施'), t_lib=('图书馆与社区', '片区日常生活的线索'), t_tr=('交通与通勤', '门到门走一遍'),
               tr_labels=['开车', '轻轨与公交', 'BART、Caltrain 和机场'], tr_verify='买家需要知道：怎样核实自己的通勤', tr_links='线路与时刻的官方入口',
               nav_daily=['医疗', '购物', '餐饮', '公园', '图书馆', '交通'], nav_school=['学区介绍', '覆盖范围', '边界核实', '关闭与调整', '买家建议', '官方入口'],
               nb='相邻城市', s_zip='ZIP Code 不等于学区边界，也不能仅凭社区名称判断学校归属。',
               s1=('学区介绍', '一座城市，十多个学区'), s2=('主要学区', '覆盖范围'), s3=('边界核实', '分两步查'), s4=('关闭与调整', '按入学学年核对'),
               s5=('课程与选择性项目', '住在附近不等于可以入读'), s6=('学校数据与上学路线', '怎么看'), s7=('买家实用建议', '下 offer 前做这几件事'), s8=('官方查询入口', '各学区'),
               step1='第一步：', step2='第二步：', split='查询分两步：', then='，再到', then2='再到', bounds='四种边界不要混淆',
               b=[('城市边界', '决定市政服务和城市税费，与学校安排没有直接对应关系。'), ('学区边界', '（District Boundary）决定地址归哪个学区管理。'), ('学校招生范围', '（Attendance Boundary）决定地址通常对应哪所学校，按学段分别划定。'), ('校董选举区', '（Trustee Area）只用于选举校董，不能用来判断学校。')],
               decided='决定：', effective='生效：', dash='打开 California School Dashboard', lookup='按地址查询学校', bmap='官方边界图', enroll='入学说明',
               s_note='学校边界与安排可能调整，请以具体地址、入学学年和学区确认结果为准。',
               h1=('住房年代', '老房与翻新要看什么'), h2=('独栋住宅', '各片区年代差别大'), h3=('Townhouse', '楼梯、车库和 HOA'), h4=('Condo', '车位、电梯和 HOA'), h5=('较新社区', '两层独立屋和规划社区'), h6=('山麓住宅', '坡地多看几项'),
               h7=('HOA 与持有成本', '房价之外的账'), h8=('环境与噪音', '按地址核实'), h9=('周边建设', '长期适用性'), h_chk='买家需要知道：看具体房源时要核对', h_tool='打开官方工具', h_src='官方资料',
               m1=('全市数字', '怎么看'), m2=('读懂市场', '这些问题比数字更重要'), m_median='近 3 个月成交中位价', m_yoy='同比', m_zip='查看各 ZIP Code 指南',
               tour_t=('半天看区', '七站路线'), tour_q='看房前后要核对的问题',
               c1=('比较片区', '五个维度'), c2=('相邻城市', '还值得一起比较'), go='查看 {c} 指南', zipline='San Jose 各 ZIP Code 指南', idx='片区索引', idx_note='片区名称是惯称，不是法定边界。下面的链接指向对应的 ZIP Code 图文介绍。'),
    'en': dict(sep=': ', full='Read the full area guide', official='Official site', view='View all {n} photos', demo='Temporary demo photo',
               hospitals='Main hospitals', malls='Main shopping centers', dining='Representative districts', parks='Main parks and trails', lib='Libraries', med_note='Confirm hospital services and coverage with each provider.',
               t_med=('Medical care', 'Hospitals and emergency rooms'), t_shop=('Shopping', 'Every area has its own hub'), t_din=('Dining and streets', 'Downtown and the older districts'),
               t_park=('Parks and outdoors', 'Foothills, creek trails and family spots'), t_lib=('Libraries and community', 'A clue to daily life'), t_tr=('Transit and commuting', 'Test it door to door'),
               tr_labels=['Driving', 'Light rail and buses', 'BART, Caltrain and the airport'], tr_verify='What buyers should know: how to test your commute', tr_links='Official routes and schedules',
               nav_daily=['Medical', 'Shopping', 'Dining', 'Parks', 'Libraries', 'Transit'], nav_school=['Overview', 'Coverage', 'Verify', 'Closures', 'Buyer tips', 'Lookups'],
               nb='Neighboring cities', s_zip='A ZIP code is not a school boundary, and a neighborhood name does not tell you which school serves an address.',
               s1=('School districts', 'One city, many districts'), s2=('Main districts', 'Coverage'), s3=('Verify boundaries', 'Two steps'), s4=('Closures and changes', 'Check by enrollment year'),
               s5=('Programs and choice schools', 'Living nearby is not enrollment'), s6=('School data and routes', 'How to read them'), s7=('Practical tips for buyers', 'Before you write an offer'), s8=('Official lookups', 'By district'),
               step1='Step 1: ', step2='Step 2: ', split='The lookup takes two steps: ', then=', then ', then2='', bounds='Four boundaries not to confuse',
               b=[('City limits', ' determine municipal services and city taxes. They do not map to school assignment.'), ('District boundaries', ' determine which school district an address belongs to.'), ('Attendance boundaries', ' determine which school normally serves an address, set separately by grade level.'), ('Trustee areas', ' are only for electing school board members. Do not use them to look up a school.')],
               decided='Decision: ', effective='Effective: ', dash='Open the California School Dashboard', lookup='Look up a school by address', bmap='Official boundary map', enroll='Enrollment',
               s_note='School boundaries and assignments can change. Confirm by full address and enrollment year with the district.',
               h1=('Home eras', 'What to check in older homes'), h2=('Single-family homes', 'Age varies widely by area'), h3=('Townhomes', 'Stairs, garages and the HOA'), h4=('Condos', 'Parking, elevators and the HOA'), h5=('Newer neighborhoods', 'Two-story homes and planned communities'), h6=('Foothill homes', 'Extra checks on slopes'),
               h7=('HOA and holding costs', 'Beyond the purchase price'), h8=('Environment and noise', 'Check by address'), h9=('Nearby development', 'The long view'), h_chk='What buyers should know: what to confirm for a specific home', h_tool='Open the official tool', h_src='Official source',
               m1=('Citywide numbers', 'How to read them'), m2=('Reading the market', 'Questions that matter more than the number'), m_median='3-month median sale price', m_yoy='year over year', m_zip='See the ZIP code guides',
               tour_t=('Half-day tour', 'Seven stops'), tour_q='Questions to settle before and after a showing',
               c1=('Comparing areas', 'Five factors'), c2=('Neighboring cities', 'Also worth comparing'), go='See the {c} guide', zipline='San Jose ZIP code guides', idx='Neighborhood index', idx_note='These names are common usage, not legal boundaries. Links go to the matching ZIP code guide.'),
}


class Ctx:
    def __init__(self, lang, d, S, prefix, zip_url):
        self.lang, self.d, self.S, self.prefix, self.zip_url = lang, d, S, prefix, zip_url
        self.L = T[lang]

    def label(self, k):
        return self.S['buyer_label' if k == 'buyer' else 'seller_label']


def shots(c, key):
    photos = [x for x in PHOTOS.get(key, []) if (ROOT / x['file']).exists()]
    if not photos:
        return ''
    n = len(photos)
    show = 3 if n >= 3 else 1
    cells = ''
    for k, x in enumerate(photos):
        src = c.prefix + x['file']
        cap = x.get(c.lang) or x.get('zh', '')
        full = cap + (f' · {x["credit"]}' if x.get('credit') else '')
        if k >= show:
            cells += f'<a class="zshot" href="{src}" data-cap="{e(full)}" hidden></a>'
            continue
        more = f'<span class="zall">{c.L["view"].format(n=n)}</span>' if n > 1 and k == show - 1 else ''
        demo = f'<span class="zdemo">{c.L["demo"]}</span>' if x.get('demo') else ''
        cells += f'<a class="zshot" href="{src}" data-cap="{e(full)}"><img src="{src}" alt="{e(cap)}" loading="lazy">{demo}{more}</a>'
    return f'<div class="zgal zgal{show}" data-lb>{cells}</div>'


def ps(x):
    x = x if isinstance(x, list) else [x]
    return ''.join(f'<p>{e(p)}</p>' for p in x if p)


def fac(c, places):
    out = ''
    for p in places or []:
        url = c.S['urls'].get(p['name'])
        link = f' <a href="{e(url)}" target="_blank" rel="noopener">{c.L["official"]}</a>' if url else ''
        stop = '。' if c.lang == 'zh' else '.'
        note = f'{stop}{" " if c.lang == "en" else ""}{e(p["note"].rstrip("。."))}' if p.get('note') else ''
        kind = f'（{e(p.get("kind"))}）{c.L["sep"]}' if c.lang == 'zh' else f' ({e(p.get("kind"))}){c.L["sep"]}'
        out += f'<li><strong>{e(p["name"])}</strong>{kind}{e(p.get("where"))}{note}{stop}{link}</li>'
    return f'<ul class="zfac">{out}</ul>' if out else ''


def li(items):
    return ''.join(f'<li>{e(x)}</li>' for x in items)


def head(pair):
    return f'{e(pair[0])} <span>|</span> {e(pair[1])}'


def strong(label, text, sep):
    return f'<p><strong>{e(label)}{sep}</strong>{e(text)}</p>'


def topic(c, tid, pair, key, intro, buyer='', seller='', after=''):
    b = strong(c.label('buyer'), buyer, c.L['sep']) if buyer else ''
    s = strong(c.label('seller'), seller, c.L['sep']) if seller else ''
    return f'<article class="zblock" id="{tid}"><h3 class="ztitle">{head(pair)}</h3>{shots(c, key)}{intro}{b}{s}{after}</article>'


def overview(c):
    pos, tp = c.d['position'], c.S['overview_topics']
    pairs = [(x['title'], x['sub']) for x in tp]
    nb = f'<p class="zsmall">{c.L["nb"]}{c.L["sep"]}{e(", ".join(pos.get("neighbors", [])))}</p>'
    t = topic(c, 'ov-where', pairs[0], 'overview', ps(pos['paragraphs'][0]), pos.get('note', ''), after=nb)
    t += topic(c, 'ov-roads', pairs[1], 'overview2', ps(pos['paragraphs'][1]))
    t += topic(c, 'ov-rail', pairs[2], 'overview3', ps(pos['paragraphs'][2]))
    return t


def daily(c):
    d, S, L = c.d, c.S, c.L
    m, er, pk, cm = d['medical'], d['errands'], d['parks'], d['commute']
    by = {p['name']: p for p in er['places']}
    pick = lambda k: [by[n] for n in S[k]['names']]
    sub = lambda h, places: f'<h4 class="zh4">{e(h)}</h4>{fac(c, places)}'
    t = topic(c, 'daily-medical', L['t_med'], 'medical', ps(m['paragraphs'][0]), m['paragraphs'][1], after=sub(L['hospitals'], m['places']) + f'<p class="zsmall">{L["med_note"]}</p>')
    t += topic(c, 'daily-shopping', L['t_shop'], 'shopping', ps(S['shopping']['intro']), S['shopping']['buyer'], after=sub(L['malls'], pick('shopping')))
    t += topic(c, 'daily-dining', L['t_din'], 'dining', ps(S['dining']['intro']), S['dining']['buyer'], after=sub(L['dining'], pick('dining')))
    t += topic(c, 'daily-parks', L['t_park'], 'parks', ps(pk['paragraphs'][0]), pk['paragraphs'][1], after=sub(L['parks'], pk['places']))
    libs = [p for p in er['places'] if p['name'] not in S['shopping']['names'] + S['dining']['names']]
    t += topic(c, 'daily-library', L['t_lib'], 'library', ps(S['library']['intro']), S['library']['buyer'], after=sub(L['lib'], libs))
    intro = ''.join(f'<h4 class="zh4">{a}</h4><p>{e(b)}</p>' for a, b in zip(L['tr_labels'], cm['paragraphs']))
    scen = ''.join(f'<h4 class="zh4">{e(x["title"])}</h4><p>{e(x["text"])}</p>' for x in cm.get('scenarios', []))
    links = ''.join(f'<li><a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a></li>' for l in cm.get('links', []) if l.get('url'))
    t += (f'<article class="zblock" id="daily-transit"><h3 class="ztitle">{head(L["t_tr"])}</h3>{shots(c, "transit")}{intro}'
          f'<h4 class="zh4">{L["tr_verify"]}</h4><ul class="zfac">{li(cm.get("verify", []))}</ul>{scen}'
          f'<h4 class="zh4">{L["tr_links"]}</h4><ul class="zlinks">{links}</ul></article>')
    ids = ['medical', 'shopping', 'dining', 'parks', 'library', 'transit']
    nav = ''.join(f'<a href="#daily-{a}">{b}</a>' for a, b in zip(ids, L['nav_daily']))
    return f'<p class="ztopnav">{nav}</p>{t}'


def schools(c):
    S, L = c.S, c.L
    sch = c.d['schools']
    sm = sch['summary']
    sds, links = '', ''
    for x in sch['districts']:
        short = (f'（{e(x["short"])}）' if c.lang == 'zh' else f' ({e(x["short"])})') if x.get('short') else ''
        grades = f' · {e(x["grades"])}' if x.get('grades') else ''
        sds += f'<h4 class="zh4">{e(x["name"])}{short}{grades}</h4>' + ''.join(f'<p>{e(x[k])}</p>' for k in ('covers', 'note') if x.get(k))
        a = []
        lk = lambda u, t: f'<a href="{e(u)}" target="_blank" rel="noopener">{e(t)}</a>'
        if x.get('locator_url'):
            a.append(lk(x['locator_url'], x.get('locator_label') or L['lookup']))
        if x.get('map_url') and x['map_url'] != x.get('locator_url'):
            a.append(lk(x['map_url'], x.get('map_label') or L['bmap']))
        if x.get('enroll_url') and x['enroll_url'] not in (x.get('locator_url'), x.get('map_url')):
            a.append(lk(x['enroll_url'], L['enroll']))
        links += f'<li><strong>{e(x["name"])}</strong>{L["sep"]}{" · ".join(a)}</li>'
    clos = ''.join(f'<h4 class="zh4">{e(x["district"])}</h4><p><strong>{L["decided"]}</strong>{e(x["decided"].rstrip("。."))}{"。" if c.lang == "zh" else "."}</p><p>{e(x["text"])}</p><p><strong>{L["effective"]}</strong>{e(x["effective"].rstrip("。."))}{"。" if c.lang == "zh" else "."}</p>' for x in S['closures'])
    sr = sch.get('safe_routes') or {}
    m1, m2 = sm[1].split(L['split'])
    a2, b2 = m2.split(L['then'], 1)
    cap = (lambda s: s[:1].upper() + s[1:]) if c.lang == 'en' else (lambda s: s)
    stop = '。' if c.lang == 'zh' else '.'
    bs = ''.join(f'<p><strong>{a}</strong>{b}' + (f' {e(sch.get("trustee_note", ""))}' if i == 3 else '') + '</p>' for i, (a, b) in enumerate(L['b']))
    ids = ['intro', 'coverage', 'verify', 'changes', 'tips', 'links']
    nav = ''.join(f'<a href="#schools-{a}">{b}</a>' for a, b in zip(ids, L['nav_school']))
    return f'''<p class="ztopnav">{nav}</p>
<article class="zblock" id="schools-intro"><h3 class="ztitle">{head(L["s1"])}</h3>{shots(c, "schools")}<p>{e(sm[0])}</p><p class="zcall"><strong>{e(L["s_zip"])}</strong></p></article>
<article class="zblock" id="schools-coverage"><h3 class="ztitle">{head(L["s2"])}</h3><p>{e(m1.strip())}</p>{sds}</article>
<article class="zblock" id="schools-verify"><h3 class="ztitle">{head(L["s3"])}</h3><p><strong>{L["step1"]}</strong>{e(cap(a2))}{stop}</p><p><strong>{L["step2"]}</strong>{e(L["then2"])}{e(cap(b2))}</p><h4 class="zh4">{L["bounds"]}</h4>{bs}</article>
<article class="zblock" id="schools-changes"><h3 class="ztitle">{head(L["s4"])}</h3><p>{e(S["closures_intro"])}</p>{clos}</article>
<article class="zblock" id="schools-programs"><h3 class="ztitle">{head(L["s5"])}</h3><p>{e(sch.get("choice_note"))}</p><ul class="zfac">{li(sch.get("programs", []))}</ul></article>
<article class="zblock" id="schools-data"><h3 class="ztitle">{head(L["s6"])}</h3><p>{e(sch.get("dashboard_note"))}</p><p><a class="zmore" href="https://www.caschooldashboard.org/" target="_blank" rel="noopener">{L["dash"]} →</a></p><p>{e(sr.get("text"))}</p></article>
<article class="zblock" id="schools-tips"><h3 class="ztitle">{head(L["s7"])}</h3><ul class="zfac">{li(S["tips"])}</ul>{strong(c.label("seller"), S["schools_seller"], L["sep"])}</article>
<article class="zblock" id="schools-links"><h3 class="ztitle">{head(L["s8"])}</h3><ul class="zlinks">{links}</ul><p class="zsmall">{e(L["s_note"])}</p></article>'''


def housing(c, cta=''):
    d, S, L = c.d, c.S, c.L
    h, co, en, pl = d['housing'], d['costs'], d['environment'], d['planning']
    ty = h.get('types', [])
    tools = ''.join(f'<li><a href="{e(t["url"])}" target="_blank" rel="noopener">{e(t["label"])}</a>{L["sep"]}{e(t.get("what"))}</li>' for t in en.get('tools', []) if t.get('url'))
    items = ''.join(f'<h4 class="zh4">{e(i["name"])}</h4><p class="zsmall">{e(i.get("status"))}</p><p>{e(i.get("text"))}</p>' + (f'<p><a href="{e(i["url"])}" target="_blank" rel="noopener">{L["h_src"]}</a></p>' if i.get('url') else '') for i in pl.get('items', []))
    t = topic(c, 'home-eras', L['h1'], 'housing', ps(h['paragraphs'][0]), seller=S['housing_seller'])
    t += topic(c, 'home-sfh', L['h2'], 'housing2', ps(ty[0]['text']))
    t += topic(c, 'home-th', L['h3'], 'housing3', ps(ty[1]['text']))
    t += topic(c, 'home-condo', L['h4'], 'housing4', ps(ty[2]['text']))
    t += topic(c, 'home-new', L['h5'], 'housing5', ps(h['paragraphs'][1]))
    t += topic(c, 'home-hill', L['h6'], 'housing6', ps(h['paragraphs'][2]))
    t += topic(c, 'home-costs', L['h7'], 'costs', ps(co['paragraphs']), after=f'<h4 class="zh4">{L["h_chk"]}</h4><ul class="zfac">{li(co.get("checklist", []))}</ul>')
    t += topic(c, 'home-env', L['h8'], 'environment', ps(en['paragraphs']), after=f'<ul class="zfac">{tools}</ul>')
    t += topic(c, 'home-plan', L['h9'], 'planning', ps(pl['paragraphs']), after=items)
    return t + cta


def market(c, median, yoy, source, sold_html='', after=''):
    S, L = c.S, c.L
    pills = f'<ul class="zpills"><li>{e(median)} {L["m_median"]}</li><li>{(e(yoy) + " " + L["m_yoy"]) if c.lang == "en" else (L["m_yoy"] + e(yoy))}</li></ul>'
    qa = ''.join(f'<h4 class="zh4">{e(x["q"])}</h4><p>{e(x["a"])}</p>' for x in S['market_q'])
    t = f'<article class="zblock" id="market-city"><h3 class="ztitle">{head(L["m1"])}</h3>{shots(c, "market")}{pills}<p>{e(S["market_intro"])}</p><p class="zsmall">{source}</p><p><a class="zmore" href="{c.zip_url("index")}">{L["m_zip"]} →</a></p></article>'
    t += f'<article class="zblock" id="market-read"><h3 class="ztitle">{head(L["m2"])}</h3>{qa}</article>'
    return t + sold_html + after


def tour(c):
    t, L = c.d['tour'], c.L
    stops = ''.join(f'<h4 class="zh4">{e(s["name"])}</h4><p>{e(s["text"])}</p>' for s in t.get('stops', []))
    return (f'<article class="zblock" id="tour-route"><h3 class="ztitle">{head(L["tour_t"])}</h3>{shots(c, "tour")}<p>{e(t["intro"])}</p>{stops}'
            f'<h4 class="zh4">{L["tour_q"]}</h4><ul class="zfac">{li(t.get("questions", []))}</ul></article>')


def compare(c, city_url, cta=''):
    S, L = c.S, c.L
    dims = ''.join(f'<li><strong>{e(x["k"])}</strong>{L["sep"]}{e(x["t"])}</li>' for x in S['compare_dims'])
    zips = ''.join(f'<li><a href="{c.zip_url(z)}">{z} {e(n)}</a></li>' for z, n in ((z, c.zip_area(z)) for z in ZIP_ORDER if c.zip_area(z)))
    t = f'<article class="zblock" id="compare-dims"><h3 class="ztitle">{head(L["c1"])}</h3>{shots(c, "compare")}<p>{e(S["compare_intro"])}</p><ul class="zfac">{dims}</ul><h4 class="zh4">{L["zipline"]}</h4><ul class="zfac zcols">{zips}</ul></article>'
    rows = ''
    for x in c.d.get('compare', []):
        u = city_url(x['slug']) if x.get('slug') else ''
        go = f'<p><a class="zmore" href="{u}">{L["go"].format(c=e(x["city"]))} →</a></p>' if u else ''
        rows += f'<h4 class="zh4">{e(x["city"])}</h4><p>{e(x["text"])}</p>{go}'
    t += f'<article class="zblock" id="compare-cities"><h3 class="ztitle">{head(L["c2"])}</h3>{rows}</article>'
    return t + cta


def zip_card(c, z, anchor=None):
    """片区块：照片 + 介绍 + 买家 + 卖家 + 完整指南链接。"""
    f = ROOT / f'tools/v2-content/zip/{z}.json'
    if not f.exists():
        return ''
    d = json.loads(f.read_text(encoding='utf-8'))
    sfx = '' if c.lang == 'zh' else '_en'
    url = c.zip_url(z)
    ph = d.get('photos') or []
    img = ''
    if ph and (ROOT / f'images/zip/{z}-1.webp').exists():
        src = f'{c.prefix}images/zip/{z}-1.webp'
        cap = ph[0][c.lang]
        img = f'<div class="zgal zgal1" data-lb><a class="zshot" href="{src}" data-cap="{e(cap)}"><img src="{src}" alt="{e(cap)}" loading="lazy"></a></div>'
    aid = anchor or f'z{z}'
    return (f'<article class="zblock" id="{aid}"><h3 class="ztitle"><a href="{url}">{z} <span>|</span> {e(d["title" + sfx])}</a></h3>{img}<p>{e(d["intro" + sfx][0])}</p>'
            f'{strong(c.label("buyer"), d["buyer" + sfx][0], c.L["sep"])}{strong(c.label("seller"), d["seller" + sfx][0], c.L["sep"])}'
            f'<p><a class="zmore" href="{url}">{c.L["full"]} →</a></p></article>')


def districts(c, ids):
    """片区索引加 10 个 ZIP 图文块。ids：片区名到地图锚点。"""
    L = c.L
    z2name = {v: k for k, v in AREA_ZIP.items()}
    idx = ''
    for x in c.d['district_index']:
        z = AREA_ZIP.get(x['name'])
        name = f'<a href="#{ids.get(x["name"], "z" + z)}">{e(x["name"])}</a>' if z else e(x['name'])
        idx += f'<li><strong>{name}</strong>（{e(x.get("area"))}）{L["sep"]}{e(x["one_line"])}</li>' if c.lang == 'zh' else f'<li><strong>{name}</strong> ({e(x.get("area"))}){L["sep"]}{e(x["one_line"])}</li>'
    cards = ''.join(zip_card(c, z, ids.get(z2name.get(z))) for z in ZIP_ORDER)
    return f'<p>{e(c.d["districts_intro"])}</p><h3 class="ztitle" id="district-index">{L["idx"]}</h3><p class="zsmall">{L["idx_note"]}</p><ul class="zfac">{idx}</ul>{cards}'
