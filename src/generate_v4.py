from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, random, re, shutil, urllib.request
import yaml
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R=Path('.'); CFG=R/'config.yaml'; D=R/'docs'; C=D/'comics'; E=D/'episodes'; H=R/'data/history.json'; TZ=timezone(timedelta(hours=8))
W,HGT=1080,760
LAY=[('hero',1080,760,'center',90),('support',820,650,'left',150),('clue',650,610,'right',95),('tension',880,680,'center',180),('reveal',1080,820,'center',0)]
ST=[
 {'theme':'校園祕密直播','keys':['thriller','school','drama'],'title':'凌晨 2:13 的直播間','summary':'轉學生誤入只有被點名者才能看見的直播，而下一個名字竟然是她。','tags':['校園','懸疑','直播','反轉'],'p':[('night','徐允：這不是我們學校的社群嗎…？','午夜，手機突然跳出未訂閱直播'),('phone','畫面：今晚會消失的人','觀眾名單一個個亮起'),('hall','閔夏：妳也收到了？千萬別留言。','只有少數學生看得見'),('stairs','徐允：等等，最後那個名字是我？','畫面切到空無一人的樓梯間'),('hook','匿名訊息：2:30 前，找到「第二支手機」。','下一秒，鏡頭對準徐允身後')]},
 {'theme':'職場偽戀愛','keys':['romance','drama'],'title':'簽下去就要假裝交往','summary':'普通企劃答應三個月假戀愛，卻在合約最後一頁看到父親的名字。','tags':['職場','戀愛','契約','祕密'],'p':[('office','海準：三個月，妳會得到升職。','他遞來一份奇怪合約'),('paper','閔夏：假裝交往也寫進 KPI？','條款 7：不得對外否認關係'),('lift','同事：你們真的在一起了？','消息比公告更快傳遍公司'),('roof','海準：現在反悔，已經來不及。','樓下停著三台記者車'),('hook','閔夏：為什麼我爸也簽過這份合約？','最後一頁夾著十五年前的照片')]},
 {'theme':'迴歸倒數','keys':['action','fantasy','thriller'],'title':'我又回到出事前三天','summary':'事故後醒來，時間回到三天前；唯一記得真相的人，是最討厭他的女孩。','tags':['回歸','懸疑','命運','救贖'],'p':[('rain','海準：我不是已經死了嗎？','煞車聲仍在耳邊'),('room','手機日期：10 月 14 日','事故前三天'),('cafe','徐允：這次你總算記得我了？','她推出一張車禍照片'),('alley','徐允：第三天，你會害死一個人。','而那個人不是你'),('hook','徐允：今晚 11 點，不要回家。','門外卻站著另一個海準')]},
 {'theme':'偶像生存戰','keys':['drama','thriller','romance'],'title':'第 7 名不准出道','summary':'練習生在最終排名前收到匿名規則：成為第 7 名的人，會被節目抹去存在。','tags':['偶像','生存賽','競爭','懸念'],'p':[('stage','導演：最終排名五分鐘後公開。','候場區安靜得異常'),('phone','匿名訊息：別拿第 7 名。','上一個第 7 名已不存在'),('hall','閔夏：妳也看到那條規則？','她的名牌有被撕掉的痕跡'),('stage','徐允：如果故意失誤呢？','耳機傳來自己的聲音：太晚了'),('hook','主持人：第 7 名——','全場燈光突然熄滅')]}
]
COL={'night':((30,34,68),(93,108,165)),'phone':((19,22,34),(68,77,102)),'hall':((117,137,164),(199,212,227)),'stairs':((51,56,79),(119,128,156)),'hook':((80,53,92),(170,117,176)),'office':((230,235,245),(198,213,234)),'paper':((226,230,239),(247,235,241)),'lift':((170,176,186),(228,232,239)),'roof':((111,132,166),(205,217,234)),'rain':((46,56,82),(105,118,151)),'room':((216,221,232),(249,246,250)),'cafe':((208,184,158),(249,238,220)),'alley':((74,83,104),(149,160,185)),'stage':((55,40,74),(137,101,178))}

def ft(n,b=0): return ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc' if b else '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def rr(d,b,r,fill=None,outline=None,w=1): d.rounded_rectangle(b,radius=r,fill=fill,outline=outline,width=w)
def sd(s): return random.Random(int(hashlib.sha256(s.encode()).hexdigest()[:16],16))
def hist():
 try:return json.loads(H.read_text(encoding='utf-8'))
 except:return []
def wrap(d,s,f,m):
 out=[]; cur=''
 for ch in s:
  if d.textbbox((0,0),cur+ch,font=f)[2]<=m: cur+=ch
  else:
   if cur: out.append(cur)
   cur=ch
 if cur: out.append(cur)
 return out
def grad(a,b,h=HGT):
 im=Image.new('RGB',(W,h)); px=im.load()
 for y in range(h):
  t=y/max(1,h-1); c=tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
  for x in range(W): px[x,y]=c
 return im

def trends():
 s={k:1 for k in ['romance','thriller','action','fantasy','drama','school']}
 for u in ['https://www.webtoons.com/en/ranking/popular','https://comic.naver.com/webtoon?tab=genre']:
  try:
   q=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 DailyComicBot/4.0'}); t=urllib.request.urlopen(q,timeout=8).read(350000).decode('utf-8','ignore').lower(); t=re.sub(r'<[^>]+>',' ',t)
   for k in s: s[k]+=t.count(k)
  except Exception as e: print('trend fallback',type(e).__name__)
 return s
def choose(day,hs):
 used={x.get('theme') for x in hs[-8:]}; pool=[x for x in ST if x['theme'] not in used] or ST; sc=trends(); weighted=[]
 for x in pool: weighted += [x]*min(60,1+sum(sc.get(k,1) for k in x['keys']))
 return sd(day).choice(weighted)

def bg(scene,i,day):
 im=grad(*COL[scene]).convert('RGBA'); glow=Image.new('RGBA',im.size,(0,0,0,0)); gd=ImageDraw.Draw(glow); gd.ellipse((300,0,780,420),fill=(255,255,255,45)); im=Image.alpha_composite(im,glow.filter(ImageFilter.GaussianBlur(28))); d=ImageDraw.Draw(im,'RGBA'); r=sd(day+str(i))
 if scene in {'night','hall','stairs','office','lift','room'}:
  for x in (80,325,570,815): d.rectangle((x,120,x+170,360),outline=(255,255,255,95),width=3)
 if scene in {'rain','alley'}:
  for _ in range(90):
   x=r.randint(0,W); y=r.randint(0,HGT); d.line((x,y,x-14,y+32),fill=(230,238,255,85),width=2)
 if scene=='stage':
  for x in (180,420,660,900): d.polygon([(x,90),(x-65,360),(x+65,360)],fill=(255,255,255,25))
 if scene=='phone': rr(d,(380,120,700,500),42,(18,20,31,170),(255,255,255,55),3)
 if scene=='hook': d.rectangle((0,0,W,HGT),fill=(45,8,34,30))
 return im.convert('RGB')

def person(d,x,y,hair,coat,mood='calm',s=1.0):
 skin=(247,220,200); out=(43,46,58); accent=(169,188,230)
 d.ellipse((x-90*s,y+300*s,x+90*s,y+330*s),fill=(0,0,0,24)); d.line((x-22*s,y+210*s,x-28*s,y+340*s),fill=(61,64,82),width=int(13*s)); d.line((x+22*s,y+210*s,x+28*s,y+340*s),fill=(61,64,82),width=int(13*s)); rr(d,(x-64*s,y+92*s,x+64*s,y+245*s),int(28*s),coat); rr(d,(x-38*s,y+116*s,x+38*s,y+225*s),int(18*s),accent); d.rectangle((x-12*s,y+70*s,x+12*s,y+104*s),fill=skin); d.ellipse((x-48*s,y-18*s,x+48*s,y+92*s),fill=skin); d.pieslice((x-55*s,y-34*s,x+55*s,y+69*s),180,360,fill=hair); rr(d,(x-52*s,y-8*s,x+52*s,y+32*s),int(17*s),hair)
 ey=y+42*s; ex=19*s
 if mood in {'shock','fear','panic','hook'}:
  for dx in (-ex,ex): d.ellipse((x+dx-7*s,ey-4*s,x+dx+7*s,ey+11*s),fill='white',outline=out,width=2)
 else:
  d.line((x-ex-7*s,ey+4*s,x-ex+7*s,ey+4*s),fill=out,width=3); d.line((x+ex-7*s,ey+4*s,x+ex+7*s,ey+4*s),fill=out,width=3)
 d.line((x-10*s,y+70*s,x+10*s,y+70*s),fill=out,width=3); d.line((x-58*s,y+135*s,x-92*s,y+175*s),fill=coat,width=int(14*s)); d.line((x+58*s,y+135*s,x+92*s,y+175*s),fill=coat,width=int(14*s))

def panel(st,i,out,day):
 scene,dialog,cap=st['p'][i-1]; im=bg(scene,i,day); d=ImageDraw.Draw(im,'RGBA'); mood='shock' if i in (2,4,5) else 'calm'; person(d,290 if i%2 else 760,245,(61,45,65),(228,233,246),mood,1.2); person(d,770 if i%2 else 285,280,(38,48,73),(177,203,221),'calm',1.05); rr(d,(38,30,235,75),18,(20,22,32,230)); d.text((54,40),f'EP {day[5:].replace("-",".")} · {i}',font=ft(23,1),fill='white'); tw=d.textbbox((0,0),cap,font=ft(24,1))[2]; rr(d,(38,88,70+tw,132),18,(255,255,255,235)); d.text((54,97),cap,font=ft(24,1),fill=(37,42,58)); dark=i==5; fill=(29,31,43) if dark else (255,255,255); color='white' if dark else (28,31,40); rr(d,(48,HGT-218,W-48,HGT-40),27,fill,(82,87,107),2); who,said=dialog.split('：',1) if '：' in dialog else ('旁白',dialog); d.text((72,HGT-198),who,font=ft(27,1),fill=color); yy=HGT-158
 for line in wrap(d,said,ft(26),W-150): d.text((72,yy),line,font=ft(26),fill=color); yy+=35
 if dark:d.text((W-175,34),'下回待續',font=ft(28,1),fill=(255,248,252,230))
 im.save(out)

def share(st,paths,out,day):
 y=220; poses=[]
 for _,w,h,a,g in LAY: poses.append((w,h,a,y)); y+=h+g
 total=y+90; cv=Image.new('RGB',(W,total),(247,247,250)); hd=grad((31,34,50),(91,62,110),220); cv.paste(hd,(0,0)); d=ImageDraw.Draw(cv); d.text((50,32),st['title'],font=ft(44,1),fill='white'); d.text((50,90),st['summary'],font=ft(23),fill=(240,240,246)); d.text((50,150),'  '.join('#'+x for x in st['tags']),font=ft(21,1),fill=(235,219,249))
 for p,(w,h,a,y0) in zip(paths,poses):
  im=Image.open(p).resize((w,h),Image.Resampling.LANCZOS); x=0 if a=='left' else W-w if a=='right' else (W-w)//2; cv.paste(im,(x,y0))
 d.rectangle((0,total-90,W,total),fill=(21,24,34)); d.text((50,total-57),'每天一小段，留下一個想追下去的鉤子',font=ft(22),fill=(220,225,239)); d.text((W-200,total-57),day,font=ft(22,1),fill=(255,226,240)); cv.save(out)

def index(cfg,meta):
 day=meta['date']; tags=''.join(f'<span>#{t}</span>' for t in meta['tags']); figs=[]
 for i,(name,_,_,align,gap) in enumerate(LAY,1): figs.append(f'<figure class="p {name} {align}" style="--g:{gap}px"><img src="episodes/{day}/panel-{i}.png"></figure>')
 cards=[]
 for p in sorted(C.glob('*.png'),reverse=True)[:36]:
  try:m=json.loads(p.with_suffix('.json').read_text(encoding='utf-8'))
  except:m={}
  cards.append(f'<a class="card" href="comics/{p.name}"><img src="comics/{p.name}"><div><b>{m.get("title",p.stem)}</b><small>{p.stem}</small><p>{m.get("summary","")}</p></div></a>')
 title=cfg['comic']['title']; sub=cfg['comic'].get('subtitle','')
 html=f'''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:#0b0d14;color:#f1f4ff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",sans-serif}}#bar{{position:fixed;top:0;left:0;height:3px;width:0;background:linear-gradient(90deg,#dec7f5,#ffd0e0);z-index:20}}nav{{position:sticky;top:3px;z-index:10;background:#0b0d14dd;backdrop-filter:blur(12px);border-bottom:1px solid #ffffff12;padding:11px 18px}}nav div{{max-width:1120px;margin:auto;display:flex;gap:16px;align-items:center}}nav b{{flex:1}}nav a{{color:inherit;text-decoration:none;font-size:13px}}.hero{{max-width:1120px;margin:auto;padding:56px 20px 44px;display:grid;grid-template-columns:1.1fr .9fr;gap:26px;align-items:end}}h1{{font-size:clamp(50px,8vw,88px);line-height:.9;margin:8px 0 18px;letter-spacing:-.06em}}.hero p{{color:#a4aec8;line-height:1.8}}.tags{{display:flex;gap:8px;flex-wrap:wrap}}.tags span{{border:1px solid #ffffff18;background:#ffffff08;border-radius:999px;padding:7px 11px;font-size:12px}}.cover{{padding:13px;border:1px solid #ffffff12;border-radius:24px;background:#ffffff08}}.cover img{{width:100%;display:block;border-radius:16px;aspect-ratio:4/5;object-fit:cover;object-position:top}}.reader{{background:#f7f7fa;color:#171922;padding:40px 0 70px}}.head{{width:min(820px,calc(100% - 32px));margin:0 auto 42px}}.head h2{{font-size:clamp(34px,6vw,56px);margin:5px 0 10px;letter-spacing:-.04em}}.head p{{color:#686c7c;line-height:1.7}}.col{{width:min(820px,100%);margin:auto;display:flex;flex-direction:column;align-items:center}}.p{{display:flex;margin:0 0 var(--g);width:100%}}.p.left{{justify-content:flex-start}}.p.right{{justify-content:flex-end}}.p.center{{justify-content:center}}.p img{{display:block;width:100%;box-shadow:0 12px 30px #1112}}.hero.p,.reveal{{width:100%}}.support{{width:76%}}.clue{{width:60%}}.tension{{width:82%}}.end{{width:min(820px,calc(100% - 32px));margin:40px auto 0;background:#171b29;color:white;border-radius:20px;padding:24px;text-align:center}}.archive{{max-width:1120px;margin:auto;padding:56px 20px 80px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:15px}}.card{{color:inherit;text-decoration:none;background:#ffffff08;border:1px solid #ffffff12;border-radius:18px;overflow:hidden}}.card img{{width:100%;aspect-ratio:3/4;object-fit:cover;object-position:top}}.card div{{padding:13px}}.card b,.card small{{display:block}}.card small{{color:#909bb4;margin:5px 0}}.card p{{font-size:13px;line-height:1.55;color:#dfe5f5}}@media(max-width:820px){{.hero{{grid-template-columns:1fr}}.support{{width:84%}}.clue{{width:70%}}.tension{{width:90%}}}}</style><body><div id="bar"></div><nav><div><b>{title}</b><span>{meta['title']}</span><a href="#archive">連載庫</a></div></nav><header class="hero"><div><small>DAILY VERTICAL COMIC</small><h1>{title}</h1><p>{sub}<br>不等寬分鏡、長留白、左右偏移與滿版揭露格，讓閱讀速度也成為劇情的一部分。</p><div class="tags">{tags}</div></div><a class="cover" href="#reader"><img src="latest.png"></a></header><main class="reader" id="reader"><section class="head"><small>LATEST EPISODE · {day}</small><h2>{meta['title']}</h2><p>{meta['summary']}</p></section><section class="col">{''.join(figs)}</section><div class="end"><b>下回待續</b><br><small>明天 08:30 自動更新</small></div></main><section class="archive" id="archive"><h2>連載檔案庫</h2><div class="grid">{''.join(cards)}</div></section><script>const b=document.getElementById('bar');function u(){{let m=document.documentElement.scrollHeight-innerHeight;b.style.width=(m?scrollY/m*100:0)+'%'}}addEventListener('scroll',u,{{passive:true}});u()</script></body></html>'''
 (D/'index.html').write_text(html,encoding='utf-8')

def main():
 cfg=yaml.safe_load(CFG.read_text(encoding='utf-8')); day=datetime.now(TZ).strftime('%Y-%m-%d'); hs=hist(); st=choose(day,hs); C.mkdir(parents=True,exist_ok=True); ep=E/day; shutil.rmtree(ep,ignore_errors=True); ep.mkdir(parents=True,exist_ok=True); paths=[]
 for i in range(1,6):
  p=ep/f'panel-{i}.png'; panel(st,i,p,day); paths.append(p)
 out=C/f'{day}.png'; share(st,paths,out,day); meta={'title':st['title'],'theme':st['theme'],'summary':st['summary'],'tags':st['tags'],'date':day,'generator':'webtoon-layout-v4','layout':[x[0] for x in LAY]}; (C/f'{day}.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8'); (D/'latest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8'); shutil.copyfile(out,D/'latest.png'); hs.append({'date':day,'title':st['title'],'theme':st['theme']}); H.parent.mkdir(parents=True,exist_ok=True); H.write_text(json.dumps(hs[-120:],ensure_ascii=False,indent=2),encoding='utf-8'); index(cfg,meta); print('generated',out)
if __name__=='__main__': main()
