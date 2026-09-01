from __future__ import annotations
import hashlib,json,random,shutil
from datetime import datetime,timezone,timedelta
from pathlib import Path
import yaml
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('.'); CFG=ROOT/'config.yaml'; HIST=ROOT/'data/history.json'; DOCS=ROOT/'docs'; COMICS=DOCS/'comics'; TPE=timezone(timedelta(hours=8))
def font(n,b=False):
    for p in (["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc","/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"] if b else ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc","/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]):
        if Path(p).exists(): return ImageFont.truetype(p,n)
    return ImageFont.truetype('DejaVuSans.ttf',n)
def rr(d,b,r,fill=None,outline=None,w=1): d.rounded_rectangle(b,radius=r,fill=fill,outline=outline,width=w)
def grad(sz,a,b):
    w,h=sz; im=Image.new('RGB',sz,a); px=im.load()
    for y in range(h):
        t=y/max(h-1,1); c=tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
        for x in range(w): px[x,y]=c
    return im
def seed(s): return random.Random(int(hashlib.sha256(s.encode()).hexdigest()[:16],16))
def load_hist():
    try:return json.loads(HIST.read_text(encoding='utf-8'))
    except:return []
def wrap(d,t,f,m):
    out=[]; cur=''
    for ch in t:
        if d.textbbox((0,0),cur+ch,font=f)[2]<=m: cur+=ch
        else:
            if cur: out.append(cur)
            cur=ch
    if cur: out.append(cur)
    return out
STORIES={
'AI 與日常生活的荒謬瞬間':('記憶體不足','阿曜建立完整提醒系統，唯一忘記的是查看提醒。',[('desk','proud','阿曜：所有事情都有記錄，就不會忘。','方法論'),('desk','focus','阿曜：待辦、日曆、提醒，全同步。','同步完成'),('room','worried','阿曜：我今天是不是有什麼事？','晚上'),('room','deadpan','米米：有，提醒你「記得看提醒」。','通知 37 則')]),
'工程師與機器人的小型冒險':('捷徑的捷徑','阿曜想找最快路徑，結果米米直接找了最近的椅子。',[('street','focus','阿曜：今天去咖啡店，我要走最佳路徑。','導航中'),('street','proud','阿曜：距離、紅綠燈、陰影都算進去。','模型完成'),('cafe','surprised','阿曜：米米，你怎麼先到了？','三分鐘後'),('cafe','deadpan','米米：我先去最近的地方，坐著等你。','最佳化成功')]),
'咖啡店裡發生的奇怪事件':('最懂儀式感的人','阿曜研究手沖參數半天，米米只在乎杯子有沒有對齊。',[('cafe','focus','阿曜：水溫 91 度，粉水比 1:15。','今日沖煮'),('cafe','proud','阿曜：萃取曲線今天一定漂亮。','理論滿分'),('cafe','worried','阿曜：怎麼喝起來還是普通？','沉默 5 秒'),('cafe','deadpan','米米：你最在意的是角度，不是味道。','儀式感過量')]),
'下班後才開始的第二人生':('晚上才上線','白天的阿曜是上班族，晚上卻把人生排得像副本。',[('room','tired','阿曜：今天終於下班了。','18:31'),('desk','focus','阿曜：先練琴，再寫程式，再畫圖。','第二人生'),('desk','worried','阿曜：怎麼感覺比上班還忙？','行程爆滿'),('room','deadpan','米米：你把休息也排成任務了。','主線：睡覺')]),
'把普通小事想得太複雜':('早餐決策樹','只是買早餐，阿曜卻做出了像論文一樣的選擇流程。',[('room','focus','阿曜：先做一份早餐決策樹。','07:02'),('street','proud','阿曜：口味、距離、價格、健康，全納入。','變數 12 個'),('store','worried','阿曜：算完了，店休。','結果輸出'),('store','deadpan','米米：所以我先買好蛋餅了。','實務派勝利')]),
'科技讓生活更方便，也更荒謬':('一鍵完成','阿曜追求一鍵完成，最後多了八個步驟來找那顆鍵。',[('desk','proud','阿曜：我最喜歡一鍵完成。','效率信仰'),('desk','focus','阿曜：先把快速鍵設定到最完美。','設定頁第 8 層'),('desk','worried','阿曜：等等，我把一鍵放哪了？','迷路中'),('desk','deadpan','米米：在「尋找一鍵」捷徑裡。','方便升級')]),
'朋友之間一本正經的胡說八道':('專業分析','兩個人很認真地討論，最後發現根本只是想喝飲料。',[('street','focus','阿曜：我們要從需求本質切入。','會議開始'),('street','proud','阿曜：先做優先序、風險與成本分析。','非常專業'),('cafe','surprised','米米：所以結論是？','大家沉默'),('cafe','deadpan','阿曜：珍奶半糖少冰。','會議圓滿')])}
PAL={'desk':((225,241,255),(190,216,248)),'room':((255,239,220),(242,214,191)),'cafe':((255,232,211),(230,196,168)),'street':((222,244,235),(185,220,212)),'store':((239,232,255),(210,201,239))}
def bg(scene):
    im=grad((1024,1024),*PAL.get(scene,PAL['desk'])); d=ImageDraw.Draw(im); fy=760; d.rectangle((0,fy,1024,1024),fill=(238,230,221)); d.rectangle((0,fy-5,1024,fy),fill=(110,105,102))
    if scene=='desk':
        rr(d,(70,110,320,280),24,(252,253,255),(92,107,136),5); d.line((110,220,275,160),fill=(106,137,200),width=10); rr(d,(680,130,940,330),22,(255,255,255),(130,150,180),5)
    elif scene=='room':
        d.rectangle((80,120,390,350),fill=(255,250,246),outline=(145,118,99),width=5); d.rectangle((600,110,940,360),fill=(216,236,255),outline=(128,148,174),width=5)
    elif scene=='cafe':
        rr(d,(70,105,320,350),18,(91,63,44),(63,44,32),4); d.rectangle((640,120,950,320),fill=(255,249,239),outline=(130,110,96),width=5)
    elif scene=='street':
        d.rectangle((0,760,1024,1024),fill=(185,190,196)); d.rectangle((120,130,330,430),fill=(255,247,237),outline=(125,140,145),width=4); d.rectangle((650,120,940,440),fill=(236,249,255),outline=(125,140,145),width=4)
    else:
        d.rectangle((65,130,955,370),fill=(255,253,249),outline=(150,145,158),width=4)
    return im
def human(d,x,y,s,m):
    O=(31,31,34); skin=(246,215,188); hood=(56,72,96)
    rr(d,(x-52*s,y+112*s,x-10*s,y+245*s),14*s,(58,67,79),O,max(1,int(4*s))); rr(d,(x+10*s,y+112*s,x+52*s,y+245*s),14*s,(58,67,79),O,max(1,int(4*s)))
    rr(d,(x-76*s,y+12*s,x+76*s,y+158*s),30*s,hood,O,max(1,int(5*s))); rr(d,(x-39*s,y+44*s,x+39*s,y+132*s),18*s,(236,238,243))
    if m in ('proud','surprised'): pts=[(-68,60,-125,10),(68,60,125,5)]
    elif m=='worried': pts=[(-68,60,-118,128),(68,60,108,115)]
    else: pts=[(-68,60,-125,103),(68,60,125,103)]
    for a,b,c,e in pts: d.line((x+a*s,y+b*s,x+c*s,y+e*s),fill=hood,width=max(2,int(16*s))); d.ellipse((x+c*s-12*s,y+e*s-12*s,x+c*s+12*s,y+e*s+12*s),fill=skin,outline=O,width=max(1,int(3*s)))
    d.ellipse((x-60*s,y-88*s,x+60*s,y+30*s),fill=skin,outline=O,width=max(1,int(5*s))); d.pieslice((x-68*s,y-104*s,x+68*s,y+35*s),180,360,fill=O)
    rr(d,(x-48*s,y-20*s,x-4*s,y+12*s),12*s,None,O,max(1,int(4*s))); rr(d,(x+4*s,y-20*s,x+48*s,y+12*s),12*s,None,O,max(1,int(4*s))); d.line((x-4*s,y-4*s,x+4*s,y-4*s),fill=O,width=max(1,int(3*s)))
    if m=='worried': d.arc((x-35*s,y-8*s,x-15*s,y+8*s),190,350,fill=O,width=max(1,int(3*s))); d.arc((x+15*s,y-8*s,x+35*s,y+8*s),190,350,fill=O,width=max(1,int(3*s)))
    elif m=='surprised': d.ellipse((x-31*s,y-12*s,x-14*s,y+5*s),outline=O,width=max(1,int(3*s))); d.ellipse((x+14*s,y-12*s,x+31*s,y+5*s),outline=O,width=max(1,int(3*s)))
    else: d.line((x-31*s,y-4*s,x-16*s,y-6*s),fill=O,width=max(1,int(3*s))); d.line((x+16*s,y-6*s,x+31*s,y-4*s),fill=O,width=max(1,int(3*s)))
    if m=='deadpan': d.line((x-14*s,y+16*s,x+14*s,y+16*s),fill=O,width=max(1,int(3*s)))
    elif m=='worried': d.arc((x-15*s,y+10*s,x+15*s,y+24*s),180,360,fill=O,width=max(1,int(3*s)))
    else: d.arc((x-16*s,y+5*s,x+16*s,y+24*s),0,180,fill=O,width=max(1,int(3*s)))
def robot(d,x,y,s,m):
    O=(45,61,77); A=(91,182,255); rr(d,(x-58*s,y-48*s,x+58*s,y+72*s),28*s,(247,250,254),O,max(1,int(5*s))); d.rectangle((x-8*s,y-78*s,x+8*s,y-48*s),fill=O); d.ellipse((x-16*s,y-96*s,x+16*s,y-68*s),fill=A,outline=O,width=max(1,int(3*s)))
    d.ellipse((x-31*s,y-15*s,x-8*s,y+10*s),fill=A); d.ellipse((x+8*s,y-15*s,x+31*s,y+10*s),fill=A); d.line((x-18*s,y+32*s,x+18*s,y+32*s),fill=O,width=max(1,int(4*s)))
    d.line((x-45*s,y+30*s,x-68*s,y+80*s),fill=O,width=max(1,int(5*s))); d.line((x+45*s,y+30*s,x+68*s,y+80*s),fill=O,width=max(1,int(5*s))); d.line((x-28*s,y+70*s,x-40*s,y+120*s),fill=O,width=max(1,int(5*s))); d.line((x+28*s,y+70*s,x+40*s,y+120*s),fill=O,width=max(1,int(5*s)))
def props(d,scene):
    if scene=='desk': rr(d,(295,650,770,710),18,(172,137,111),(95,73,57),4); rr(d,(340,545,530,660),16,(72,84,102),(42,49,61),4); d.rectangle((355,560,515,640),fill=(183,216,255),outline=(30,60,90),width=3)
    elif scene=='room': rr(d,(620,645,920,765),22,(224,205,185),(128,100,84),4); d.ellipse((100,570,300,700),fill=(124,173,98),outline=(76,119,62),width=4)
    elif scene=='cafe': rr(d,(250,695,790,755),22,(151,111,86),(98,69,52),4); d.ellipse((510,605,590,685),fill='white',outline=(90,90,90),width=3)
    elif scene=='street': d.rectangle((185,770,335,910),fill=(208,83,83),outline=(100,50,50),width=4)
    else: rr(d,(225,700,825,770),26,(176,145,121),(96,76,62),4)
def panel(p,i,out,date):
    im=bg(p['scene']); d=ImageDraw.Draw(im); props(d,p['scene']); human(d,360 if i%2==0 else 405,490,1.18,p['mood']); robot(d,750,555,1.12, 'deadpan')
    r=seed(date+str(i));
    for _ in range(9):
        x,y=r.randint(35,985),r.randint(35,420); q=r.randint(3,7); d.ellipse((x-q,y-q,x+q,y+q),fill=r.choice([(255,255,255),(255,235,154),(181,226,255)]))
    rr(d,(42,40,162,104),18,(24,31,43)); d.text((86,52),str(i),font=font(34,True),fill='white'); im.save(out)
def compose(cfg,story,paths,out,date):
    W,H=1800,2450; im=grad((W,H),(248,250,255),(235,240,249)); d=ImageDraw.Draw(im)
    for x in range(0,W,44):
        for y in range(0,H,44):
            if (x+y)//44%2==0:d.ellipse((x+8,y+8,x+12,y+12),fill=(231,235,244))
    rr(d,(70,60,W-70,360),40,(27,34,49)); rr(d,(92,82,W-92,338),34,(35,47,70)); d.text((130,115),story['title'],font=font(74,True),fill='white'); d.text((132,210),story['summary'],font=font(32),fill=(214,224,239))
    chips=[story['theme'],date,'零額度自動生成']; cx=132; cf=font(28,True)
    for c in chips:
        tw=d.textbbox((0,0),c,font=cf)[2]; rr(d,(cx,272,cx+tw+38,320),22,(241,246,255)); d.text((cx+19,282),c,font=cf,fill=(32,45,69)); cx+=tw+56
    M,T,G=90,410,40; cw=(W-2*M-G)//2; ch=900; cap=font(25,True); df=font(31,True); sm=font(24)
    for i,(p,path) in enumerate(zip(story['panels'],paths)):
        row,col=divmod(i,2); x=M+col*(cw+G); y=T+row*(ch+G); rr(d,(x+10,y+14,x+cw+10,y+ch+14),34,(220,226,236)); rr(d,(x,y,x+cw,y+ch),34,'white',(209,218,232),3)
        rr(d,(x+24,y+24,x+cw-24,y+540),28,(244,246,250)); pi=Image.open(path).convert('RGB'); pi.thumbnail((cw-48,516)); im.paste(pi,(x+24+(cw-48-pi.width)//2,y+24+(516-pi.height)//2))
        tw=d.textbbox((0,0),p['caption'],font=cap)[2]; rr(d,(x+42,y+44,x+tw+86,y+94),20,'white'); d.text((x+64,y+56),p['caption'],font=cap,fill=(52,60,80)); rr(d,(x+cw-110,y+42,x+cw-42,y+110),22,(28,35,48)); d.text((x+cw-82,y+56),str(i+1),font=cap,fill='white')
        lines=wrap(d,p['dialogue'],df,cw-110); bh=30+len(lines)*(df.size+8); fill=(245,248,255) if p['dialogue'].startswith('阿曜') else (238,249,245); rr(d,(x+32,y+570,x+cw-32,y+570+bh),26,fill); yy=y+586
        for line in lines:d.text((x+52,yy),line,font=df,fill=(28,32,40)); yy+=df.size+8
        d.text((x+36,y+ch-52),f"scene · {p['scene']}   mood · {p['mood']}",font=sm,fill=(124,133,146))
    im.save(out,quality=95)
def index(cfg,meta):
    cards=[]
    for p in sorted(COMICS.glob('*.png'),reverse=True)[:48]:
        m={}
        try:m=json.loads(p.with_suffix('.json').read_text(encoding='utf-8'))
        except:pass
        cards.append(f'<a class="card" href="comics/{p.name}"><img src="comics/{p.name}"><div><b>{m.get("title",p.stem)}</b><span>{p.stem}</span><p>{m.get("summary","")}</p></div></a>')
    total=len(list(COMICS.glob('*.png'))); title=cfg['comic']['title']; sub=cfg['comic'].get('subtitle','零額度自動漫畫站')
    html=f'''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>:root{{--bg:#090d18;--p:#121a2d;--l:#2a3550;--t:#f1f5ff;--m:#a9b5cf}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at top,#1b2747,#090d18 48%);color:var(--t);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",sans-serif}}.w{{max-width:1200px;margin:auto;padding:48px 22px 90px}}.hero{{display:grid;grid-template-columns:1.05fr .95fr;gap:22px}}.box{{background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,.025));border:1px solid var(--l);border-radius:28px;box-shadow:0 18px 50px #0004}}.intro{{padding:36px}}h1{{font-size:clamp(42px,7vw,78px);line-height:.95;margin:0 0 18px;letter-spacing:-.06em}}.muted{{color:var(--m);line-height:1.75}}.chips{{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0}}.chip{{background:#edf3ff;color:#26344f;padding:9px 13px;border-radius:999px;font-weight:700;font-size:14px}}.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}.stat{{background:#ffffff0a;border:1px solid #ffffff0d;border-radius:18px;padding:18px}}.stat b{{font-size:32px;display:block}}.latest{{display:block;padding:16px;text-decoration:none;color:inherit}}.latest img{{width:100%;display:block;border-radius:20px;background:#fff}}.latest h2{{font-size:30px;margin:18px 8px 8px}}.latest p{{margin:0 8px 14px;color:var(--m);line-height:1.65}}h3{{font-size:28px;margin:38px 4px 16px}}.archive{{padding:18px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill;minmax(250px,1fr));gap:16px}}.card{{background:#ffffff08;border:1px solid #ffffff0d;border-radius:22px;overflow:hidden;text-decoration:none;color:inherit;transition:.18s}}.card:hover{{transform:translateY(-4px);border-color:#8094cf}}.card img{{width:100%;aspect-ratio:1800/2450;object-fit:cover;display:block;background:#fff}}.card div{{padding:14px 15px 18px}}.card b{{font-size:19px}}.card span{{display:block;color:var(--m);font-size:12px;margin:5px 0 9px}}.card p{{margin:0;color:#d9e0f2;font-size:14px;line-height:1.55}}footer{{text-align:center;color:var(--m);font-size:13px;margin-top:24px}}@media(max-width:900px){{.hero{{grid-template-columns:1fr}}}}@media(max-width:600px){{.stats{{grid-template-columns:1fr}}.w{{padding:28px 15px 70px}}}}</style><body><main class="w"><section class="hero"><div class="box intro"><h1>{title}</h1><p class="muted">{sub}<br>Python 程式化角色、場景與對白，API 花鲷維挋 0。</p><div class="chips"><span class="chip">Procedural Python V3</span><span class="chip">API 成本 0</span><span class="chip">每日 08:30</span></div><div class="stats"><div class="stat"><b>{total}</b><span>累稇篇數</span></div><div class="stat"><b>0</b><span>API 舱費支工</span></div><div class="stat"><b>4</b><span>每篇格整</span></div></div></div><a class="box latest" href="latest.png"><img src="latest.png"><h2>{meta['title']}</h2><p>{meta['summary']}</p></a></section><h3>歷史翫嘍亅</h3><section class="box archive"><div class="grid">{''.join(cards)}</div></section><footer>GitHub Actions · GitHub Pages · Zero-credit Comic Engine</footer></main></body></html>'''; (DOCS/'index.html').write_text(html,encoding='utf-8')
def main():
    cfg=yaml.safe_load(CFG.read_text(encoding='utf-8')); hist=load_hist(); date=datetime.now(TPE).strftime('%Y-%m-%d'); themes=cfg.get('themes',list(STORIES)); recent={x.get('theme') for x in hist[-10:]}; avail=[x for x in themes if x not in recent] or themes; theme=seed(date).choice(avail); title,summary,raw=STORIES.get(theme,STORIES[themes[0]]); story={'title':title,'theme':theme,'summary':summary,'panels':[{'scene':a,"mood':b,'dialogue':c,'caption':d} for a,b,c,d in raw]}
    COMICS.mkdir(parents=True,exist_ok=True); tmp=ROOT/'.tmp_panels'; shutil.rmtree(tmp,ignore_errors=True); tmp.mkdir(); paths=[]
    for i,p en enumerate(story['panels',1): q=tmp/f'{i}.png'; panel(p,i,q,date); paths.append(q)
    out=COMICS/f'{date}.png'; compose(cfg,story,paths,out,date); meta={**story,'date':date,'generator':'procedural-python-v3','api_cost':0,'dry_run':False}; (COMICS/f'{date}.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8'); shutil.copyfile(out,DOCS/'latest.png'); (DOCS/'latest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8'); hist.append({'date':date,'title':title,'theme':theme}); HIST.parent.mkdir(parents=True,exist_ok=True); HIST.write_text(json.dumps(hist[-120:],ensure_ascii=False,indent=2),encoding='utf-8'); index(cfg,meta); shutil.rmtree(tmp;ignore_errors=True); print('done',out)
if __name__=='__main__': main()
