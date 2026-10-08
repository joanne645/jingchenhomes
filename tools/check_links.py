#!/usr/bin/env python3
"""检查城市指南页面里的外部链接是否还能打开。

用法（在仓库根目录运行，需要联网）：
    python3 tools/check_links.py            # 检查全部城市页
    python3 tools/check_links.py dublin     # 只检查一个城市

结果分三类：
  OK        正常打开
  BLOCKED   对方网站拒绝自动访问（401/403/405/429 等），需要用浏览器人工点开确认
  BROKEN    打不开（404、域名失效、超时），需要更换链接
同时会把结果写到 tools/link-report.txt。
"""
import re, sys, ssl, urllib.request, urllib.error, concurrent.futures
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'

def collect(only=None):
    links = {}
    for f in sorted((ROOT / 'cities').glob('*.html')):
        if only and f.stem not in only:
            continue
        for u in re.findall(r'href="(https?://[^"]+)"', f.read_text(encoding='utf-8')):
            u = u.replace('&amp;', '&')
            links.setdefault(u, set()).add(f.stem)
    return links

def check(u):
    ctx = ssl.create_default_context()
    last = ''
    for method in ('HEAD', 'GET'):
        try:
            req = urllib.request.Request(u, method=method, headers={'User-Agent': UA, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
                return 'OK', str(r.status)
        except urllib.error.HTTPError as ex:
            last = str(ex.code)
            if ex.code in (401, 403, 405, 406, 429, 999) or 500 <= ex.code < 600:
                if method == 'HEAD':
                    continue
                return 'BLOCKED', last
            if method == 'HEAD':
                continue
            return 'BROKEN', last
        except Exception as ex:  # 超时、证书、域名等
            last = type(ex).__name__
            if method == 'HEAD':
                continue
            return 'BROKEN', last
    return 'BROKEN', last

def main():
    only = set(sys.argv[1:]) or None
    links = collect(only)
    print(f'共 {len(links)} 个外部链接，开始检查…')
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for u, (st, info) in zip(links, ex.map(check, links)):
            rows.append((st, info, u, ','.join(sorted(links[u]))))
    rows.sort()
    out = [f'{st}\t{info}\t{u}\t[{pages}]' for st, info, u, pages in rows]
    (ROOT / 'tools' / 'link-report.txt').write_text('\n'.join(out) + '\n', encoding='utf-8')
    for st in ('BROKEN', 'BLOCKED'):
        sel = [r for r in rows if r[0] == st]
        print(f'\n{st}: {len(sel)}')
        for _, info, u, pages in sel:
            print(f'  {info}\t{u}\t[{pages}]')
    print(f'\nOK: {len([r for r in rows if r[0] == "OK"])}')
    print('完整结果已写入 tools/link-report.txt')

if __name__ == '__main__':
    main()
