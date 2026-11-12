"""Refresh public profile references; no ranking or nationality inference from names.
Remote portraits are referenced, not redistributed. All requests are public and cached.
Run: python -m analysis.enrich_profiles
"""
import concurrent.futures as futures
import html,json,re,unicodedata,urllib.request,time
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'tmp'/'profile-sources'
CACHE.mkdir(parents=True,exist_ok=True)
def fetch(url):
    import hashlib
    path=CACHE/(hashlib.sha256(url.encode()).hexdigest()+'.html')
    if path.exists() and time.time()-path.stat().st_mtime < 6*3600:
        return path.read_text(encoding='utf8')
    req=urllib.request.Request(url,headers={'User-Agent':'SupeRR-Student-Research/1.0'})
    s=urllib.request.urlopen(req,timeout=25).read().decode('utf8')
    path.write_text(s,encoding='utf8');return s
def clean(s):return html.unescape(re.sub('<[^>]+>',' ',s)).strip()
def norm(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
ALIASES={'Josh Little':'Joshua Little','Varun Chakaravarthy':'Varun Chakravarthy','R Sai Kishore':'Sai Kishore','Yudhvir Singh Charak':'Yudhvir Singh','Sufyan Moqim':'Sufiyan Muqeem','Ravindra Jadeja':'Ravindra Jadeja'}
def key(s):return norm(ALIASES.get(s,s))
def links(s):return set(html.unescape(x) for x in re.findall(r'href="(/players/[^"?#]+)',s))
def img_for(s,name):
    for tag in re.findall(r'<img\b[^>]*>',s):
        alt=re.search(r'alt="([^"]*)',tag)
        src=re.search(r'\bsrc="([^"]+)',tag)
        if alt and src and key(clean(alt[1]))==key(name):
            src=html.unescape(src[1]);return 'https://www.iplt20.com'+src if src.startswith('/') else src
    return None
def main():
    data=json.loads((ROOT/'web/data/dashboard.json').read_text())
    wanted={key(p['name']):str(p['id']) for scope in data['rankings'].values() for rows in scope.values() for p in rows}
    teams=['chennai-super-kings','delhi-capitals','gujarat-titans','kolkata-knight-riders','lucknow-super-giants','mumbai-indians','punjab-kings','rajasthan-royals','royal-challengers-bengaluru','sunrisers-hyderabad']
    def team(slug):
        s=fetch('https://www.iplt20.com/teams/'+slug); ls=links(s)
        # Player pages expose the complete Rest of Squad list, even when team HTML has only four cards.
        if ls:ls |= links(fetch('https://www.iplt20.com'+sorted(ls)[0]))
        return ls
    all_links=set()
    with futures.ThreadPoolExecutor(max_workers=4) as pool:
        for slug,result in zip(teams,pool.map(team,teams)):
            all_links |= result;print(slug,len(result),flush=True)
    chosen=[l for l in all_links if key(l.rsplit('/',1)[-1].replace('-',' ')) in wanted]
    records={}; errors=[]
    def profile(link):
        try:
            url='https://www.iplt20.com'+link;s=fetch(url)
            name=clean(re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S)[1])
            facts={clean(k):clean(v) for k,v in re.findall(r'<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>',s,re.S)}
            title=clean(re.search(r'<title>(.*?)</title>',s,re.S)[1])
            team=title.split('|')[1].replace('Profile','').strip()
            return wanted.get(key(name)),dict(name=name,country=facts.get('Nationality'),role=facts.get('Role'),born=facts.get('Born'),ipl_team=team,source=url,photo=img_for(s,name),checked=str(date.today()),source_label='Official IPL player profile',status='Listed on IPL team roster; match fitness and future selection not verified')
        except Exception as e:return None,{'error':str(e),'url':link}
    with futures.ThreadPoolExecutor(max_workers=4) as pool:
        for pid,p in pool.map(profile,chosen):
            if pid:records[pid]=p
            else:errors.append(p)
    out={'checked':str(date.today()),'players':records,'errors':errors,'policy':{'source':'https://www.cricbuzz.com/cricket-news/140773/mohammad-amir-rules-out-entering-ipl-auction','label':'Pakistan representation - IPL availability review','note':'Pakistan representatives remain in the research rankings. IPL participation has been restricted in practice; nationality or passport exceptions exist. Verify registration, board clearance and current eligibility individually. This is not a legal determination or a performance penalty.'}}
    (ROOT/'web/data/profiles.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    print('Profiles:',len(records),'photos:',sum(bool(p.get('photo')) for p in records.values()),'errors:',len(errors),flush=True)
if __name__=='__main__':main()
