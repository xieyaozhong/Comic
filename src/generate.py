import json, random, shutil, hashlib, re, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
import yaml
from PIL import Image, ImageDraw, ImageFont

R=Path('.'); CFG=R/'config.yaml'; D=R/'docs'; C=D/'comics'; H=R/'data/history.json'; TZ=timezone(timedelta(hours=8))
W,PH,GAP,HEAD,FOOT=1080,860,38,230,100

STORIES=[
 {'theme':'校園祕密直播','keys':['thriller','school','drama'],'title':'凌晨 2:13 的直播間','summary':'轉學生誤入一場只有被點名者才能看見的直播，而下一個名字竟然是她。','tags':['校園','懸疑','直播','反轉'],'p':[
 ('night','徐允：這不是我們學校的社群嗎…？','午夜，手機突然跳出未訂閱直播'),('phone','直播標題：今晚會消失的人','觀眾名單一個個亮起'),('hall','閔夏：妳也收到了？千萬別留言。','只有少數學生看得見'),('stairs','徐允：等等，最後那個名字是我？','畫面切到空無一人的樓梯間'),('hook','匿名訊息：2:30 前，找到「第二支手機」。','下一秒，直播鏡頭對準了徐允身後')]},
 {'theme':'職場偽戀愛','keys':['romance','drama'],'title':'簽下去就要假裝交往','summary':'普通企劃為了保住工作答應三個月假戀愛，卻在合約最後一頁看到父親的名字。','tags':['職場','戀愛','契約','祕密'],'p':[
 ('office','海準：三個月，妳會得到升職。','他遞來一份奇怪的合約'),('paper','閔夏：假裝交往也寫進 KPI？','條款 7：不得對外否認關係'),('lift','同事：你們真的在一起了？','消息比公告更快傳遍公司'),('roof','海準：如果現在反悔，已經來不及。','樓下停著三台記者車'),('hook','閔夏：為什麼我爸也簽過這份合約？','最後一頁夾著十五年前的照片')]},
 {'theme':'迴歸倒數','keys':['action','fantasy','thriller'],'title':'我又回到出事前三天','summary':'事故後醒來，時間回到三天前；唯一記得真相的人，是曾經最討厭他的女孩。','tags':['回歸','懸疑','命運','救贖'],'p':[
 ('rain','海準：我不是已經死了嗎？','煞車聲仍在耳邊'),('room','手機日期：10 月 14 日','事故前三天'),('cafe','徐允：這次你總算記得我了？','她推出一張車禍照片'),('alley','徐允：第三天，你會害死一個人。','而那個人不是你'),('hook','徐允：今晚 11 點，不要回家。','門外卻站著另一個海準')]},
 {'theme':'偶像生存戰','keys':['drama','thriller','romance'],'title':'第 7 名不准出道','summary':'練習生在最終排名前收到匿名規則：成為第 7 名的人，會被節目抹去存在。','tags':['偶像','生存賽','競爭','懸念'],'p':[
 ('stage','導演：最終排名五分鐘後公開。','候場區安靜得異常'),('phone','匿名訊息：別拿第 7 名。','上一個第 7 名已不存在'),('hall','閔夏：妳也看到那條規則？','她的名牌有被撕掉的痕跡'),('stage','徐允：如果故意失誤呢？','耳機傳來自己的聲音：太晚了'),('hook','主持人：第 7 名——','全場燈光突然熄滅')]}
]
COL={'night':((26,30,57),(76,88,137)),'phone':((20,22,34),(67,75,96)),'hall':((99,120,147),(190,203,218)),'stairs':((51,54,72),(118,125,149)),'hook':((78,50,88),(164,113,169)),'office':((230,235,246),(199,214,235)),'paper':((225,229,239),(248,233,240)),'lift':((168,173,184),(224,229,239)),'roof':((108,130,166),(204,217,234)),'rain':((48,57,81),(103,117,149)),'room':((215,220,232),(250,245,250)),'cafe':((207,181,154),(248,237,218)),'alley':((75,83,104),(148,160,185)),'stage':((54,38,70),(132,98,171))}

def f(n,b=False):
 p='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc' if b else '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'; return ImageFont.truetype(p,n)
def rr(d,b,r,fill=None,outline=None,w=1): d.rounded_rectangle(b,radius=r,fill=fill,outline=outline,width=w)
def grad(sz,a,b):
 im=Image.new('RGB',sz); px=im.load(); w,h=sz
 for y in range(h):
  t=y/max(1,h-1); c=tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
  for x in range(w): px[x,y]=c
 return im
def wrap(d,s,font,m):
 out=[]; cur=''
 for ch in s:
  if d.textbbox((0,0),cur+ch,font=font)[2]<=m: cur+=ch
  else: out.append(cur); cur=ch
 if cur: out.append(cur)
 return out
def seed(s): return random.Random(int(hashlib.sha256(s.encode()).hexdigest()[:16],16))
def history():
 try:return json.loads(H.read_text(encoding='utf-8'))
 except:return []

def trends():
 score={k:1 for k in ['romance','thriller','action','fantasy','drama','school']}; terms={'romance':['romance','로맨스','학원로맨스'],'thriller':['thriller','스릴러'],'action':['action','액션','먼치킨'],'fantasy':['fantasy','판타지','로판','게임판타지'],'drama':['drama','드라마','학원물'],'school':['school','학원','학원로맨스']}
 for url in ['https://www.webtoons.com/en/ranking/popular','https://comic.naver.com/webtoon?tab=genre']:
  try:
   q=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 DailyComicBot/1.0'}); text=urllib.request.urlopen(q,timeout=8).read(450000).decode('utf-8','ignore').lower(); text=re.sub(r'<[^>]+>',' ',text)
   for k,ws in terms.items(): score[k]+=sum(text.count(w.lower()) for w in ws)
  except Exception as e: print('trend fallback',type(e).__name__)
 return score
def choose(day,hist):
 used={x.get('theme') for x in hist[-8:]}; pool=[s for s in STORIES if s['theme'] not in used] or STORIES; sc=trends(); weighted=[]
 for s in pool: weighted += [s]*min(80,1+sum(sc.get(k,1) for k in s['keys']))
 pick=seed(day).choice(weighted); print('trend',sc,'=>',pick['theme']); return pick

def person(d,x,y,skin=(247,219,198),hair=(48,43,58),clothes=(218,226,242),mood='calm'):
 d.line((x-22,y+260,x-28,y+420),fill=(55,61,81),width=20); d.line((x+22,y+260,x+28,y+420),fill=(55,61,81),width=20)
 rr(d,(x-72,y+105,x+72,y+285),30,clothes); d.rectangle((x-13,y+86,x+13,y+122),fill=skin); d.ellipse((x-60,y-20,x+60,y+108),fill=skin); d.pieslice((x-68,y-32,x+68,y+95),180,360,fill=hair); d.rounded_rectangle((x-64,y-4,x+64,y+38),radius=18,fill=hair)
 ey=y+48
 if mood=='shock':
  d.ellipse((x-32,ey-5,x-14,ey+14),fill='white',outline=(20,20,28),width=2); d.ellipse((x+14,ey-5,x+32,ey+14),fill='white',outline=(20,20,28),width=2)
 else:
  d.line((x-32,ey+4,x-14,ey+4),fill=(20,20,28),width=3); d.line((x+14,ey+4,x+32,ey+4),fill=(20,20,28),width=3)
 d.line((x-12,y+78,x+12,y+78),fill=(30,30,35),width=3); d.line((x-70,y+155,x-120,y+215),fill=clothes,width=15); d.line((x+70,y+155,x+120,y+215),fill=clothes,width=15)

def panel(story,i,out,day):
 scene,dialog,cap=story['p'][i-1]; im=grad((W,PH),*COL[scene]); d=ImageDraw.Draw(im,'RGBA'); r=seed(day+str(i)); dark=i==5
 if scene in {'night','hall','stairs','office','lift','room'}:
  for x in (90,330,570,810): d.rectangle((x,120,x+170,350),outline=(255,255,255,95),width=4)
 if scene in {'rain','alley'}:
  for _ in range(80):
   x=r.randint(0,W); y=r.randint(0,PH); d.line((x,y,x-12,y+30),fill=(225,235,255,90),width=2)
 if scene=='stage':
  for x in (180,420,660,900): d.polygon([(x,80),(x-55,360),(x+55,360)],fill=(255,255,255,28))
 if dark: d.rectangle((0,0,W,PH),fill=(55,15,42,55))
 person(d,300,255,hair=(58,44,62),clothes=(222,227,242),mood='shock' if i in (2,4,5) else 'calm'); person(d,760,275,hair=(46,53,75),clothes=(164,190,222),mood='calm')
 rr(d,(36,30,235,82),20,(20,22,32,230)); d.text((54,42),f'EP {day[5:].replace("-",".")} · {i}',font=f(24,1),fill='white')
 rr(d,(46,105,46+d.textbbox((0,0),cap,font=f(25,1))[2]+34,153),20,(255,255,255,235)); d.text((63,116),cap,font=f(25,1),fill=(39,43,57))
 who,said=dialog.split('：',1) if '：' in dialog else ('旁白',dialog); y1=PH-225; rr(d,(48,y1,W-48,PH-44),26,(29,31,43) if dark else (255,255,255),outline=(80,85,105),w=2); color='white' if dark else (28,30,38); d.text((72,y1+18),who,font=f(28,1),fill=color); yy=y1+58
 for line in wrap(d,said,f(27),W-150): d.text((72,yy),line,font=f(27),fill=color); yy+=36
 if dark: d.text((W-250,40),'TO BE\nCONTINUED',font=f(26,1),fill=(255,255,255,210),align='right')
 im.save(out)

def compose(cfg,story,paths,out,day):
 total=HEAD+FOOT+len(paths)*PH+(len(paths)-1)*GAP; im=Image.new('RGB',(W,total),(247,247,250)); d=ImageDraw.Draw(im,'RGBA'); h=grad((W,HEAD),(31,34,50),(89,60,108)); im.paste(h,(0,0)); d.text((52,36),cfg['comic']['title'],font=f(48,1),fill='white'); d.text((52,96),story['title'],font=f(38,1),fill=(249,228,255)); d.text((52,150),story['summary'],font=f(23),fill=(238,238,245)); d.text((W-355,38),'  '.join('#'+x for x in story['tags']),font=f(20,1),fill=(232,216,247)); y=HEAD
 for p in paths: im.paste(Image.open(p).convert('RGB'),(0,y)); y+=PH+GAP
 d.rectangle((0,total-FOOT,W,total),fill=(20,23,33)); d.text((52,total-66),'短篇只揭露一小段，但每天留下下一個鉤子',font=f(22),fill=(220,225,240)); d.text((W-220,total-66),day,font=f(23,1),fill=(255,220,238)); im.save(out)
def index(cfg,meta):
 cards=[]
 for p in sorted(C.glob('*.png'),reverse=True)[:40]:
  try:m=json.loads(p.with_suffix('.json').read_text(encoding='utf-8'))
  except:m={}
  tags=''.join(f'<i>#{x}</i>' for x in m.get('tags',[])[:3]); cards.append(f'<a class="c" href="comics/{p.name}"><img src="comics/{p.name}"><div><b>{m.get("title",p.stem)}</b><small>{p.stem}</small><p>{m.get("summary","")}</p>{tags}</div></a>')
 n=len(list(C.glob('*.png'))); title=cfg['comic']['title']; sub=cfg['comic'].get('subtitle','')
 css='*{box-sizing:border-box}body{margin:0;background:linear-gradient(#161522,#0b0d14 35%,#11131c);color:#f2f4fb;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",sans-serif}.w{max-width:1180px;margin:auto;padding:40px 20px 80px}.hero{display:grid;grid-template-columns:1.05fr .95fr;gap:20px}.b{background:#ffffff08;border:1px solid #ffffff14;border-radius:28px;box-shadow:0 18px 55px #0005}.intro{padding:34px}h1{font-size:clamp(44px,7vw,76px);line-height:.95;margin:0}.m{color:#adb6ce;line-height:1.75}.bad{display:flex;gap:9px;flex-wrap:wrap}.bad span,i{background:#efe7ff;color:#352c4d;border-radius:999px;padding:8px 12px;font-size:13px;font-style:normal;font-weight:700}.stat{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:24px}.stat div{background:#ffffff08;border-radius:18px;padding:17px}.stat b{font-size:30px;display:block}.latest{display:block;color:inherit;text-decoration:none;padding:14px}.latest img{width:100%;border-radius:20px}.latest h2{margin:14px 8px 4px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px;padding:16px}.c{color:inherit;text-decoration:none;background:#ffffff08;border:1px solid #ffffff10;border-radius:20px;overflow:hidden}.c img{width:100%;height:330px;object-fit:cover;object-position:top}.c div{padding:13px}.c small{display:block;color:#9ea8c1;margin:5px 0}.c p{font-size:14px;line-height:1.55}.c i{display:inline-block;margin:3px;padding:5px 8px;background:#ffffff10;color:#dbe2f5}@media(max-width:850px){.hero{grid-template-columns:1fr}.stat{grid-template-columns:1fr}}'
 html=f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{css}</style><main class="w"><section class="hero"><div class="b intro"><h1>{title}</h1><p class="m">{sub}<br>每天讀取公開熱門頁面，讓題材偏向當下常見的韓國網漫類型；抓不到網路時自動使用本地趨勢池。</p><div class="bad"><span>K-Webtoon Inspired</span><span>Trend-aware</span><span>API 成本 0</span></div><div class="stat"><div><b>{n}</b>連載篇數</div><div><b>5</b>每篇分鏡</div><div><b>0</b>API 花費</div></div></div><a class="b latest" href="latest.png"><img src="latest.png"><h2>{meta["title"]}</h2><p class="m">{meta["summary"]}</p></a></section><h2>最新連載</h2><section class="b grid">{"".join(cards)}</section></main>'; (D/'index.html').write_text(html,encoding='utf-8')

def main():
 cfg=yaml.safe_load(CFG.read_text(encoding='utf-8')); day=datetime.now(TZ).strftime('%Y-%m-%d'); hist=history(); story=choose(day,hist); C.mkdir(parents=True,exist_ok=True); tmp=R/'.tmp_panels'; shutil.rmtree(tmp,ignore_errors=True); tmp.mkdir(); paths=[]
 for i in range(1,6): p=tmp/f'{i}.png'; panel(story,i,p,day); paths.append(p)
 out=C/f'{day}.png'; compose(cfg,story,paths,out,day); meta={'title':story['title'],'theme':story['theme'],'summary':story['summary'],'tags':story['tags'],'date':day,'generator':'k-webtoon-trend-v2','api_cost':0,'dry_run':False}; (C/f'{day}.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8'); shutil.copyfile(out,D/'latest.png'); (D/'latest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8'); hist.append({'date':day,'title':meta['title'],'theme':meta['theme']}); H.parent.mkdir(parents=True,exist_ok=True); H.write_text(json.dumps(hist[-120:],ensure_ascii=False,indent=2),encoding='utf-8'); index(cfg,meta); shutil.rmtree(tmp,ignore_errors=True); print('generated',out)
if __name__=='__main__': main()
