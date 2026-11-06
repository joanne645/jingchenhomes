#!/usr/bin/env python3
"""检查文章批次文件是否齐全、格式是否合规。用法：python3 tools/v2-content/check_articles.py [slug前缀...]"""
import json,re,sys
from pathlib import Path
D=Path(__file__).parent/'articles'
bad=0
for j in sorted(D.glob('*.json')):
    s=j.stem; m=json.loads(j.read_text(encoding='utf8'))
    for l in('zh','en'):
        f=D/f'{s}.{l}.html'
        if not f.exists(): print('MISSING',f.name);bad+=1;continue
        t=f.read_text(encoding='utf8')
        n=len(re.sub(r'<[^>]+>','',t))
        tags=set(re.findall(r'<([a-z0-9]+)',t))-set('h2 h3 p ul ol li strong em a div table thead tbody tr th td aside'.split())
        if tags: print(s,l,'BAD TAGS',tags);bad+=1
        if 'style=' in t: print(s,l,'INLINE STYLE');bad+=1
        print(f'{s:32}{l} {n}')
    for k in('title','seo_title','description','lead'):
        for l in('zh','en'):
            if not m[l].get(k): print(s,'NO',l,k);bad+=1
    if not m.get('sources') and m['category']!='area': print(s,'NO SOURCES')
print('problems:',bad)
