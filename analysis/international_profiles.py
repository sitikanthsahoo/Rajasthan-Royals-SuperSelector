"""Verified ICC profile references for shortlist players outside the IPL roster feed."""
from .enrich_profiles import ROOT,fetch,clean,key
import re,json,html
from datetime import date
from concurrent.futures import ThreadPoolExecutor
PAGES=[('Najibullah Zadran','57991/najibullah-zadran'),('Nurul Hasan','10219/nurul-hasan'),('Mohammad Nawaz','57935/mohammad-nawaz'),('Sufiyan Muqeem','97317/sufyan-moqim'),('Shadab Khan','65739/shadab-khan'),('Craig Young','59442/craig-young'),('Joshua Little','66081/josh-little'),('Babar Azam','59429/babar-azam')]
def main():
    d=json.loads((ROOT/'web/data/dashboard.json').read_text());p=json.loads((ROOT/'web/data/profiles.json').read_text())
    names={key(v['name']):k for k,v in d['players'].items()}
    def read(item):
        name,path=item;url='https://www.icc-cricket.com/rankings/'+path;s=fetch(url)
        imgs=[html.unescape(x) for x in re.findall(r'<img[^>]+src="([^"]+)"',s) if '/players/generic/' in x]
        year=re.search(r'Last Match(?:<!--.*?-->|\s|-)*(\d{4})',s)
        return names[key(name)],dict(name=name,source=url,source_label='Official ICC player profile',photo=imgs[0] if imgs else None,checked=str(date.today()),status='ICC profile records appearances through '+year[1] if year else 'International profile available; current match availability unverified')
    with ThreadPoolExecutor(max_workers=4) as pool:
        for pid,record in pool.map(read,PAGES):p['players'][pid]=record
    url='https://www.cricbuzz.com/profiles/12555/abrar-ahmed';s=fetch(url)
    imgs=[]
    for tag in re.findall('<img[^>]*>',s):
        if 'abrar' in tag.lower():
            m=re.search(r'src="([^"]+)"',tag)
            if m:imgs.append(html.unescape(m[1]))
    p['players'][names[key('Abrar Ahmed')]]=dict(name='Abrar Ahmed',source=url,source_label='Cricbuzz player profile',photo=imgs[0] if imgs else None,checked=str(date.today()),status='International profile available; current match availability unverified')
    (ROOT/'web/data/profiles.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8')
    print('Profiles',len(p['players']),'Photos',sum(bool(x.get('photo')) for x in p['players'].values()))
if __name__=='__main__':main()
