#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下载 Redfin 公开的 ZIP 级市场数据，取 San Jose 各邮编同一统计周期的数字。

用法（在项目根目录，Mac 终端运行，需要联网，文件较大，约几分钟）：
    python3 tools/fetch_zip_market.py

结果写入 tools/site-data/sj-zip-market.json。之后运行 python3 tools/build_site.py。
脚本只取同一个 PERIOD_END，某个邮编在该周期没有数据时留空，不会用其他月份补。
可选：python3 tools/fetch_zip_market.py <本地 tsv 或 gz 文件路径>
"""
import csv, gzip, io, json, sys, urllib.request
from pathlib import Path

URL = 'https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/zip_code_market_tracker.tsv000.gz'
ZIPS = ['95118', '95120', '95124', '95125', '95126', '95128', '95129', '95131', '95132', '95135']
ROOT = Path(__file__).resolve().parent.parent
PTYPE = 'All Residential'


def open_stream(src):
    if src:
        raw = open(src, 'rb')
    else:
        print('正在下载 Redfin 数据……')
        raw = urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'}), timeout=120)
    if not src or src.endswith('.gz'):
        raw = gzip.GzipFile(fileobj=raw)
    return io.TextIOWrapper(raw, encoding='utf-8', newline='')


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    csv.field_size_limit(10 ** 7)
    rows, n = [], 0
    r = csv.DictReader(open_stream(sys.argv[1] if len(sys.argv) > 1 else None), delimiter='\t')
    r.fieldnames = [f.strip().strip('"').upper() for f in r.fieldnames]
    for k in ('PERIOD_BEGIN', 'PERIOD_END', 'REGION', 'PROPERTY_TYPE', 'MEDIAN_SALE_PRICE', 'HOMES_SOLD', 'MEDIAN_DOM'):
        if k not in r.fieldnames:
            sys.exit(f'数据格式变了，缺少字段 {k}，已停止，没有写入文件。')
    for row in r:
        n += 1
        if row['PROPERTY_TYPE'].strip('"') != PTYPE:
            continue
        z = row['REGION'].strip('"').replace('Zip Code: ', '')
        if z in ZIPS:
            rows.append((z, row))
    if not rows:
        sys.exit(f'读了 {n} 行，没有找到目标邮编，已停止，没有写入文件。')
    # 选 10 个邮编都有成交中位价的最新周期；都不全时选覆盖最多的最新周期
    cover = {}
    for z, row in rows:
        if num(row['MEDIAN_SALE_PRICE']):
            cover.setdefault(row['PERIOD_END'].strip('"'), set()).add(z)
    end = max(cover, key=lambda e: (len(cover[e]), e))
    out = {}
    begin = ''
    for z, row in rows:
        if row['PERIOD_END'].strip('"') == end:
            begin = row['PERIOD_BEGIN'].strip('"')
            price, sold, dom = num(row['MEDIAN_SALE_PRICE']), num(row['HOMES_SOLD']), num(row['MEDIAN_DOM'])
            out[z] = {k: int(round(v)) for k, v in (('price', price), ('sold', sold), ('dom', dom)) if v is not None}
    data = {'status': 'verified', 'period_begin': begin, 'period_end': end, 'property_type': PTYPE, 'source': 'Redfin Data Center', 'source_url': 'https://www.redfin.com/news/data-center/', 'file': URL, 'zips': out}
    p = ROOT / 'tools/site-data/sj-zip-market.json'
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'完成：统计周期 {begin} 至 {end}，覆盖 {len(out)} 个邮编')
    for z in ZIPS:
        print(z, out.get(z, '没有数据'))
    miss = [z for z in ZIPS if z not in out]
    if miss:
        print('这些邮编在该周期没有数据，页面会显示“待核实”：', miss)


if __name__ == '__main__':
    main()
