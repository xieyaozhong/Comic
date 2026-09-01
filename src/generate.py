import hashlib,json,random,shutil
from datetime import datetime,timezone,timedelta
from pathlib import Path
import yaml
from PIL import Image,ImageDraw,ImageFont
R=Path('.'); C=R/'config.yaml'; H=R/'data/history.json'; D=R/'docs'; O=D/'comics'; TZ=timezone(timedelta(hours=8))
def F(n,b=0):
 p='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc' if b else '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'; return ImageFont.truetype(p,n)
def rr(d,b,r,f=None,o=None,w=1): d.rounded_rectangle(b,radius=r,fill=f,outline=o,width=w)
def G(sz,a,b):
 im=Image.new('RGB',sz); p=im.load(); W,H=sz
 for y in range(H):
  t=y/max(H-1,1); c=tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
  for x in range(W): p[x,y]=c
 return im
def rng(s): return random.Random(int(hashlib.sha256(s.encode()).hexdigest()[:16],16))
def hist():
 try:return json.loads(H.read_text(encoding='utf-8'))
 except:return []
def W(d,t,f,m):
 a=[]; s=''
 for ch in t:
  if d.textbbox((0,0),s+ch,font=f)[2]<=m:s+=ch
  else:a.append(s);s=ch
 if s:a.append(s)
 return a
S={
'AI 與日常生活的荒謬瞬間':('記憶體不足','阿曜建立完整提醒系統，唯一忘記的是查看提醒。',[('desk','proud','阿曜：所有事情都有記錄，就不會忘。','方法論'),('desk','focus','阿曜：待辦、日曆、提醒，全同步。','同步完成'),('room','worried','阿曜：我今天是不是有什麼事？','晚上'),('room','deadpan','米米：有，提醒你「記得看提醒」。','通知 37 則')]),
'工程師與機器人的小型冒險':('捷徑的捷徑','阿曜想找最快路徑，結果米米直接找了最近的椅子。',[('street','focus','阿曜：今天去咖啡店，我要走最佳路徑。','導航中'),('street','proud','阿曜：距離、紅綠燈、陰影都算進去。','模型完成'),('cafe','surprised','阿曜：米米，你怎麼先到了？','三分鐘後'),('cafe','deadpan','米米：我先去最近的地方，坐著等你。','最佳化成功')]),
'咖啡店裡發生的奇怪事件':('最懂儀式感的人','阿曜研究手沖參數半天，米米只在乎杯子有沒有對齊。',[('cafe','focus','阿曜：水溫 91 度，粉水比 1:15。','今日沖煮'),('cafe','proud','阿曜：萃取曲線今天一定漂亮。','理論滿分'),('cafe','worried','阿曜：怎麼喝起來還是普通？','沉默 5 秒'),('cafe','deadpan','米米：你最在意的是角度，不是味道。','儀式感過量')]),
'下班後才開始的第二人生':('晚上才上線','白天的阿曜是上班族，晚上卻把人生排得像副本。',[('room','tired','阿曜：今天終於下班了。','18:31'),('desk','focus','阿曜：先練琴，再寫程式，再畫圖。','第二人生'),('desk','worried','阿曜：怎麼感覺比上班還忙？','行程爆滿'),('room','deadpan','米米：你把休息也排成任務了。','主線：睡覺')]),
'把普通小事想得太複雜':('早餐決策樹','只是買早餐，阿曜卻做出了像論文一樣的選擇流程。',[('room','focus','阿曜：先做一份早餐決策樹。','07:02'),('street','proud','阿曜：口味、距離、價格、健康，全納入。','變數 12 個'),('store','worried','阿曜：算完了，店休。','結果輸出'),('store','deadpan','米米：所以我先買好蛋餅了。','實務派勝利')]),
'科技讓生活更方便，也更荒謬':('一鍵完成','阿曜追求一鍵完成，最後多了八個步驟來找那顆鍵。',[('desk','proud','阿曜：我最喜歡一鍵完成。','效率信仰'),('desk','focus','阿曜：先把快速鍵設定到最完美。','設定頁第 8 層'),('desk','worried','阿曜：等等，我把一鍵放哪了？','迷路中'),('desk','deadpan','米米：在「尋找一鍵」捷徑裡。','方便升級')]),
'朋友之間一本正經的胡說八道':('專業分析','兩個人很認真地討論，最後發現根本只是想喝飲料。',[('street','focus','阿曜：我們要從需求本質切入。','會議開始'),('street','proud','阿曜：先做優先序、風險與成本分析。','非常專業'),('cafe','surprised','米米：所以結論是？','大家沉默'),('cafe','deadpan','阿曜：珍奶半糖少冰。','會議圓滿')])}
P={'desk':((225,241,255),(190,216,248)),'room':((255,239,220),(242,214,191)),'cafe':((255,232,211),(230,196,168)),'street':((222,244,235),(185,220,212)),'store':((239,232,255),(210,201,239))}
def B(sc):
 im=G((1024,1024),*P[sc]);d=ImageDraw.Draw(im);d.rectangle((0,760,1024,1024),fill=(238,230,221));d.rectangle((0,755,1024,760),fill=(110,105,102))
 if sc=='desk':rr(d,(70,110,320,280),24,(252,253,255),(92,107,136),5);rr(d,(680,130,940,330),22,'white',(130,150,180),5)
 elif sc=='room':d.rectangle((80,120,390,350),fill=(255,250,246),outline=(145,118,99),width=5);d.rectangle((600,110,940,360),fill=(216,236,255),outline=(128,148,174),width=5)
 elif sc=='cafe':rr(d,(70,105,320,350),18,(91,63,44),(63,44,32),4);d.rectangle((640,120,950,320),fill=(255,249,239),outline=(130,110,96),width=5)
 elif sc=='street':d.rectangle((0,760,1024,1024),fill=(185,190,196));d.rectangle((120,130,330,430),fill=(255,247,237),outline=(125,140,145),width=4);d.rectangle((650,120,940,440),fill=(236,249,255),outline=(125,140,145),width=4)
 else:d.rectangle((65,130,955,370),fill=(255,253,249),outline=(150,145,158),width=4)
 return im
def Hm(d,x,y,s,m):
 o=(31,31,34);skin=(246,215,188);hood=(56,72,96);rr(d,(x-72*s,y+15*s,x+72*s,y+160*s),28*s,hood,o,int(5*s));rr(d,(x-38*s,y+45*s,x+38*s,y+130*s),18*s,(236,238,243));rr(d,(x-48*s,y+125*s,x-8*s,y+250*s),13*s,(58,67,79),o,int(4*s));rr(d,(x+8*s,y+125*s,x+48*s,y+250*s),13*s,(58,67,79),o,int(4*s));d.ellipse((x-58*s,y-85*s,x+58*s,y+30*s),fill=skin,outline=o,width=int(5*s));d.pieslice((x-66*s,y-100*s,x+66*s,y+35*s),180,360,fill=o);rr(d,(x-46*s,y-20*s,x-4*s,y+10*s),11*s,None,o,int(4*s));rr(d,(x+4*s,y-20*s,x+46*s,y+10*s),11*s,None,o,int(4*s));d.line((x-4*s,y-5*s,x+4*s,y-5*s),fill=o,width=int(3*s));d.line((x-30*s,y-5*s,x-16*s,y-5*s),fill=o,width=int(3*s));d.line((x+16*s,y-5*s,x+30*s,y-5*s),fill=o,width=int(3*s));
 if m=='deadpan':d.line((x-14*s,y+16*s,x+14*s,y+16*s),fill=o,width=int(3*s))
 else:d.arc((x-15*s,y+7*s,x+15*s,y+24*s),0 if m!='worried' else 180,180 if m!='worried' else 360,fill=o,width=int(3*s))
 ay=y+65*s;up=m in ('proud','surprised');d.line((x-65*s,ay,x-120*s,y+(10 if up else 110)*s),fill=hood,width=int(16*s));d.line((x+65*s,ay,x+120*s,y+(5 if up else 110)*s),fill=hood,width=int(16*s))
def Rb(d,x,y,s):
 o=(45,61,77);a=(91,182,255);rr(d,(x-56*s,y-48*s,x+56*s,y+70*s),27*s,(247,250,254),o,int(5*s));d.rectangle((x-8*s,y-78*s,x+8*s,y-48*s),fill=o);d.ellipse((x-16*s,y-96*s,x+16*s,y-68*s),fill=a,outline=o,width=int(3*s));d.ellipse((x-30*s,y-14*s,x-8*s,y+10*s),fill=a);d.ellipse((x+8*s,y-14*s,x+30*s,y+10*s),fill=a);d.line((x-18*s,y+31*s,x+18*s,y+31*s),fill=o,width=int(4*s));d.line((x-42*s,y+30*s,x-65*s,y+80*s),fill=o,width=int(5*s));d.line((x+42*s,y+30*s,x+65*s,y+80*s),fill=o,width=int(5*s))
def panel(p,i,out,date):
 im=B(p['scene']);d=ImageDraw.Draw(im);Hm(d,390,490,1.18,p['mood']);Rb(d,750,555,1.12);q=rng(date+str(i))
 for _ in range(10):x,y=q.randint(35,985),q.randint(35,420);r=q.randint(3,7);d.ellipse((x-r,y-r,x+r,y+r),fill=q.choice(['white',(255,235,154),(181,226,255)]))
 rr(d,(42,40,162,104),18,(24,31,43));d.text((84,52),str(i),font=F(34,1),fill='white');im.save(out)
def compose(story,paths,out,date):
 im=G((1800,2450),(248,250,255),(235,240,249));d=ImageDraw.Draw(im);rr(d,(70,60,1730,360),40,(27,34,49));rr(d,(92,82,1708,338),34,(35,47,70));d.text((130,115),story['title'],font=F(74,1),fill='white');d.text((132,210),story['summary'],font=F(32),fill=(214,224,239));cf=F(28,1);cx=132
 for c in [story['theme'],date,'零額度自動生成']:
  tw=d.textbbox((0,0),c,font=cf)[2];rr(d,(cx,272,cx+tw+38,320),22,(241,246,255));d.text((cx+19,282),c,font=cf,fill=(32,45,69));cx+=tw+56
 cw=790;ch=900;cap=F(25,1);df=F(31,1);sm=F(24)
 for i,(p,path) in enumerate(zip(story['panels'],paths)):
  row,col=divmod(i,2);x=90+col*830;y=410+row*940;rr(d,(x+10,y+14,x+cw+10,y+ch+14),34,(220,226,236));rr(d,(x,y,x+cw,y+ch),34,'white',(209,218,232),3);rr(d,(x+24,y+24,x+cw-24,y+540),28,(244,246,250));pi=Image.open(path);pi.thumbnail((742,516));im.paste(pi,(x+24+(742-pi.width)//2,y+24+(516-pi.height)//2));tw=d.textbbox((0,0),p['caption'],font=cap)[2];rr(d,(x+42,y+44,x+tw+86,y+94),20,'white');d.text((x+64,y+56),p['caption'],font=cap,fill=(52,60,80));rr(d,(x+680,y+42,x+748,y+110),22,(28,35,48));d.text((x+708,y+56),str(i+1),font=cap,fill='white');ls=W(d,p['dialogue'],df,680);bh=30+len(ls)*39;rr(d,(x+32,y+570,x+758,y+570+bh),26,(245,248,255) if p['dialogue'].startswith('阿曜') else (238,249,245));yy=y+586
  for l in ls:d.text((x+52,yy),l,font=df,fill=(28,32,40));yy+=39
  d.text((x+36,y+848),f"scene · {p['scene']}   mood · {p['mood']}",font=sm,fill=(124,133,146))
 im.save(out,quality=95)
def page(cfg,meta):
 cards=[]
 for p in sorted(O.glob('*.png'),reverse=True)[:48]:
  try:m=json.loads(p.with_suffix('.json').read_text(encoding='utf-8'))
  except:m={}
  cards.append(f'<a class="c" href="comics/{p.name}"><img src="comics/{p.name}"><div><b>{m.get("title",p.stem)}</b><span>{p.stem}</span><p>{m.get("summary","")}</p></div></a>')
 t=cfg['comic']['title'];sub=cfg['comic'].get('subtitle','零額度自動漫畫站');n=len(list(O.glob('*.png')));css='body{margin:0;background:radial-gradient(circle at top,#1b2747,#090d18 48%);color:#f1f5ff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",sans-serif}.w{max-width:1200px;margin:auto;padding:48px 22px 90px}.h{display:grid;grid-template-columns:1.05fr .95fr;gap:22px}.b{background:#ffffff09;border:1px solid #2a3550;border-radius:28px;box-shadow:0 18px 50px #0004}.i{padding:36px}h1{font-size:clamp(42px,7vw,78px);line-height:.95;margin:0 0 18px}.m{color:#a9b5cf;line-height:1.75}.s{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.s div{background:#ffffff0a;border-radius:18px;padding:18px}.s b{font-size:32px;display:block}.l{display:block;padding:16px;color:inherit;text-decoration:none}.l img{width:100%;border-radius:20px}.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px;padding:18px}.c{background:#ffffff08;border:1px solid #ffffff0d;border-radius:22px;overflow:hidden;text-decoration:none;color:inherit}.c img{width:100%;aspect-ratio:1800/2450;object-fit:cover}.c div{padding:14px}.c span{display:block;color:#a9b5cf;font-size:12px;margin:5px 0}.c p{margin:0;color:#d9e0f2;font-size:14px}@media(max-width:900px){.h{grid-template-columns:1fr}}'
 html=f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>{css}</style><main class="w"><section class="h"><div class="b i"><h1>{t}</h1><p class="m">{sub}<br>Python 程式化角色、場景與對白，API 花費維持 0。</p><div class="s"><div><b>{n}</b>累積篇數</div><div><b>0</b>API 花費</div><div><b>4</b>每篇格數</div></div></div><a class="b l" href="latest.png"><img src="latest.png"><h2>{meta["title"]}</h2><p class="m">{meta["summary"]}</p></a></section><h2>歷史漫畫</h2><section class="b g'>{"".join(cards)}</section></main>';(D/'index.html').write_text(html,encoding='utf-8')
def main():
 cfg=yaml.safe_load(C.read_text(encoding='utf-8'));h=hist();date=datetime.now(TZ).strftime('%Y-%m-%d');ts=cfg.get('themes',list(S));recent={x.get('theme') for x in h[-10:]};av=[x for x in ts if x not in recent] or ts;theme=rng(date).choice(av);title,summary,raw=S[theme];story={'title':title,'theme':theme,'summary':summary,'panels':[{'scene':a,'mood':b,'dialogue':c,'caption':d} for a,b,c,d in raw]};O.mkdir(parents=True,exist_ok=True);tmp=R/'.tmp';shutil.rmtree(tmp,ignore_errors=True);tmp.mkdir();ps=[]
 for i,p in enumerate(story['panels'],1):q=tmp/f'{i}.png';panel(p,i,q,date);ps.append(q)
 out=O/f'{date}.png';compose(story,ps,out,date);m={**story,'date':date,'generator':'procedural-python-v3','api_cost':0,'dry_run':False};(O/f'{date}.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');shutil.copyfile(out,D/'latest.png');(D/'latest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');h.append({'date':date,'title':title,'theme':theme});H.parent.mkdir(parents=True,exist_ok=True);H.write_text(json.dumps(h[-120:],ensure_ascii=False,indent=2),encoding='utf-8');page(cfg,m);shutil.rmtree(tmp,ignore_errors=True);print('done')
if __name__=='__main__':main()
