#!/usr/bin/env python3
"""从 Wikimedia Commons 取候选照片和授权记录（在能上网的 Mac 终端运行）。
只保留 CC0、公有领域、CC BY、CC BY-SA，且横向、宽度够大的照片。
结果在 .photo_candidates/：图片和 credits.json。这里只是候选，用之前还要逐张看内容和地点。"""
import json, re, sys, time, html, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '.photo_candidates'
OUT.mkdir(exist_ok=True)
UA = {'User-Agent': 'JingChenHomesPhotoCheck/1.0 (https://github.com/joanne645/jingchenhomes)'}
Q = {
 'medical': ['Santa Clara Valley Medical Center', "O'Connor Hospital San Jose", 'Good Samaritan Hospital San Jose'],
 'shopping': ['Santana Row San Jose', 'Westfield Valley Fair', 'Westgate San Jose', 'Oakridge Mall San Jose'],
 'dining': ['San Pedro Square San Jose', 'Japantown San Jose'],
 'parks': ['Alum Rock Park San Jose', 'Almaden Quicksilver', 'Municipal Rose Garden San Jose', 'Lake Cunningham San Jose', 'Guadalupe River Park San Jose'],
 'library': ['Martin Luther King Jr. Library San Jose'],
 'transit': ['Berryessa North San Jose station', 'San Jose Diridon station', 'VTA light rail San Jose'],
 'schools': ['Lincoln High School San Jose', 'Leland High School San Jose', 'Willow Glen High School San Jose', 'Piedmont Hills High School'],
 'zip95125': ['Willow Glen San Jose', 'Lincoln Avenue Willow Glen'],
 'zip95120': ['Almaden Valley San Jose', 'Almaden Lake Park'],
}
OK = re.compile(r'^(CC0|Public domain|PD\b|CC BY(-SA)? [0-9.]+)', re.I)


def api(**k):
    k.update(format='json', action='query')
    req = urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(k), headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=30))


def clean(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()


recs, seen = [], set()
for topic, qs in Q.items():
    n = 0
    for q in qs:
        try:
            r = api(generator='search', gsrsearch=f'"{q}" filetype:bitmap', gsrnamespace=6, gsrlimit=10, prop='imageinfo', iiprop='url|size|extmetadata', iiurlwidth=1800)
        except Exception as ex:
            print('查询失败', q, ex)
            continue
        got = 0
        for pg in sorted(r.get('query', {}).get('pages', {}).values(), key=lambda x: x.get('index', 0)):
            ii = (pg.get('imageinfo') or [{}])[0]
            m = ii.get('extmetadata', {})
            lic = clean(m.get('LicenseShortName', {}).get('value'))
            t = pg['title']
            if t in seen or not OK.match(lic) or ii.get('width', 0) < 1400 or ii['width'] <= ii.get('height', 0) or got >= 5:
                continue
            seen.add(t)
            n += 1
            got += 1
            name = f'{topic}__{n:02d}.jpg'
            try:
                req = urllib.request.Request(ii['thumburl'], headers=UA)
                (OUT / name).write_bytes(urllib.request.urlopen(req, timeout=60).read())
            except Exception as ex:
                print('下载失败', t, ex)
                continue
            recs.append({'file': name, 'topic': topic, 'query': q, 'title': t, 'page': ii.get('descriptionurl'), 'artist': clean(m.get('Artist', {}).get('value')), 'license': lic, 'license_url': clean(m.get('LicenseUrl', {}).get('value')), 'desc': clean(m.get('ImageDescription', {}).get('value'))[:300], 'date': clean(m.get('DateTimeOriginal', {}).get('value'))[:40], 'size': [ii.get('width'), ii.get('height')]})
            time.sleep(0.4)
        time.sleep(0.4)
    print(topic, n)
(OUT / 'credits.json').write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding='utf-8')
print('完成，共', len(recs), '张')
