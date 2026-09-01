from __future__ import annotations

import json
import math
import os
import random
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config.yaml"
HISTORY = ROOT / "data" / "history.json"
DOCS = ROOT / "docs"
COMICS = DOCS / "comics"
LATEST = DOCS / "latest.png"
LATEST_JSON = DOCS / "latest.json"
TAIPEI = timezone(timedelta(hours=8))


def load_yaml():
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def load_history():
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_history(items):
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(items[-90:], ensure_ascii=False, indent=2), encoding="utf-8")


def fnt(size, bold=False):
    paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(draw, text, font, width):
    out, cur = [], ""
    for ch in text:
        if draw.textbbox((0, 0), cur + ch, font=font)[2] <= width:
            cur += ch
        else:
            if cur:
                out.append(cur)
            cur = ch
    if cur:
        out.append(cur)
    return out


def story(theme, rng):
    banks = [
        ("自動化到最後", "阿曜把泡咖啡做成自動化專案，米米最後指出最短路徑。", [
            ("desk", "focus", "阿曜：今天做一套全自動咖啡系統。", "08:05"),
            ("desk", "happy", "阿曜：研磨、注水、計時，全交給程式。", "08:22"),
            ("cafe", "proud", "阿曜：成功！人類自由了。", "08:41"),
            ("cafe", "deadpan", "米米：直接按咖啡機不就好了？|阿曜：……先不要破壞氣氛。", "系統：完成"),
        ]),
        ("五分鐘的捷徑", "為了每天省五分鐘，阿曜先花一小時做工具。", [
            ("room", "annoyed", "阿曜：每天整理桌面要五分鐘，好浪費。", "問題發現"),
            ("desk", "focus", "阿曜：我寫個程式解決。", "+ 62 分鐘"),
            ("desk", "proud", "阿曜：以後每天省五分鐘！", "部署成功"),
            ("room", "deadpan", "米米：回本只要十三天。|阿曜：這叫長期投資。", "ROI"),
        ]),
        ("咖啡因版本控制", "阿曜把一杯咖啡當成軟體版本管理。", [
            ("cafe", "focus", "阿曜：今天測試新的沖煮參數。", "v1.0"),
            ("cafe", "serious", "阿曜：水溫 92，時間 2:37。", "v1.1"),
            ("cafe", "worried", "阿曜：等等，這杯跟上一版差在哪？", "debug"),
            ("cafe", "deadpan", "米米：差在這杯還沒被我喝掉。", "release"),
        ]),
        ("下班後的第二回合", "阿曜說今晚只休息，兩分鐘後又想到新功能。", [
            ("street", "tired", "阿曜：今天絕對不碰電腦了。", "18:32"),
            ("room", "relaxed", "阿曜：今晚只休息。", "18:47"),
            ("room", "shocked", "阿曜：等等，我想到一個超簡單的功能。", "18:49"),
            ("desk", "deadpan", "米米：你對『休息』有自己的定義？", "23:58"),
        ]),
        ("天氣預報的漏洞", "阿曜相信所有數據，卻忘了窗戶也是資料來源。", [
            ("room", "focus", "阿曜：降雨機率只有 20%。", "出門前"),
            ("rain", "shocked", "阿曜：這 20% 怎麼剛好在我頭上？", "三分鐘後"),
            ("desk", "serious", "阿曜：我要研究預報模型。", "回家"),
            ("room", "deadpan", "米米：你剛才其實可以先看窗外。", "資料來源：窗戶"),
        ]),
        ("會議的最短路徑", "阿曜努力最佳化會議，米米給出終極方案。", [
            ("office", "serious", "阿曜：今天把會議效率提升 50%。", "09:00"),
            ("office", "focus", "阿曜：議程、計時、順序都最佳化。", "09:25"),
            ("office", "proud", "阿曜：還有什麼能再省？", "09:59"),
            ("office", "deadpan", "米米：不開會。|阿曜：……這版本太強了。", "v2.0"),
        ]),
        ("記憶體不足", "阿曜建立完整提醒系統，唯一忘記的是查看提醒。", [
            ("desk", "proud", "阿曜：所有事情都有記錄，就不會忘。", "方法論"),
            ("desk", "focus", "阿曜：待辦、日曆、提醒，全同步。", "同步完成"),
            ("room", "worried", "阿曜：我今天是不是有什麼事？", "晚上"),
            ("room", "deadpan", "米米：有，提醒你『記得看提醒』。", "通知 37 則"),
        ]),
    ]
    title, summary, raw = rng.choice(banks)
    panels = []
    for scene, mood, text, caption in raw:
        panels.append({"scene": scene, "mood": mood, "dialogue": text.split("|"), "caption": caption})
    return {"title": title, "theme": theme, "summary": summary, "panels": panels}


def background(d, scene, rng, W=1024, H=1024):
    palettes = [
        ((247,235,219),(224,194,159),(83,72,63)),
        ((225,239,241),(171,207,215),(62,82,89)),
        ((238,233,248),(199,188,228),(75,66,101)),
        ((240,244,225),(195,212,155),(74,88,59)),
    ]
    sky, mid, dark = rng.choice(palettes)
    d.rectangle((0,0,W,H), fill=sky)
    if scene in {"desk","office"}:
        d.rectangle((0,700,W,H), fill=mid)
        d.rectangle((70,480,650,535), fill=dark)
        d.rectangle((110,300,410,475), fill=(39,43,49), outline=dark, width=5)
        d.rectangle((130,320,390,450), fill=(126,197,207))
        if scene == "office":
            d.rectangle((700,180,940,400), fill=(250,249,244), outline=dark, width=6)
            d.line((735,355,790,300,840,325,900,245), fill=(81,145,180), width=9)
    elif scene == "cafe":
        d.rectangle((0,715,W,H), fill=(177,135,96))
        d.rectangle((70,155,370,370), fill=(111,74,51), outline=dark, width=6)
        d.rectangle((92,177,348,348), fill=(226,198,157))
        d.ellipse((155,220,290,300), outline=(117,82,55), width=9)
        d.rectangle((540,520,930,565), fill=dark)
        d.rectangle((690,405,800,520), fill=(218,218,210), outline=dark, width=5)
    elif scene in {"street","rain"}:
        d.rectangle((0,650,W,H), fill=(151,159,161))
        for x in (55,340,660):
            h=rng.randint(220,390)
            d.rectangle((x,650-h,x+220,650), fill=mid, outline=dark, width=5)
        if scene == "rain":
            for _ in range(60):
                x=rng.randrange(W); y=rng.randrange(H)
                d.line((x,y,x-12,y+28), fill=(83,129,162), width=3)
    else:
        d.rectangle((0,735,W,H), fill=mid)
        d.rectangle((70,150,375,390), fill=(255,252,243), outline=dark, width=5)
        d.line((222,150,222,390), fill=dark, width=5)
        d.line((70,270,375,270), fill=dark, width=5)
        d.rounded_rectangle((585,520,950,700), radius=30, fill=(133,118,157), outline=dark, width=6)


def ayao(d, x, y, mood):
    ink=(31,34,39); skin=(232,188,156); hoodie=(57,63,73); hair=(29,30,34)
    d.rectangle((x-44,y+118,x-10,y+250), fill=(49,54,61), outline=ink, width=4)
    d.rectangle((x+10,y+118,x+44,y+250), fill=(49,54,61), outline=ink, width=4)
    d.rounded_rectangle((x-88,y-20,x+88,y+150), radius=28, fill=hoodie, outline=ink, width=5)
    d.line((x-70,y+55,x-112,y+135), fill=skin, width=18); d.line((x+70,y+55,x+112,y+135), fill=skin, width=18)
    d.ellipse((x-76,y-155,x+76,y+2), fill=skin, outline=ink, width=5)
    d.pieslice((x-80,y-174,x+80,y-32),180,360,fill=hair)
    for cx in (x-38,x+38): d.ellipse((cx-31,y-108,cx+31,y-72), outline=ink, width=5)
    d.line((x-6,y-90,x+6,y-90), fill=ink, width=4)
    if mood in {"happy","proud","relaxed"}:
        d.arc((x-55,y-100,x-23,y-76),0,180,fill=ink,width=4); d.arc((x+23,y-100,x+55,y-76),0,180,fill=ink,width=4)
        d.arc((x-25,y-55,x+25,y-20),0,180,fill=ink,width=4)
    elif mood in {"worried","annoyed","tired"}:
        d.line((x-53,y-86,x-29,y-81),fill=ink,width=4); d.line((x+29,y-81,x+53,y-86),fill=ink,width=4)
        d.arc((x-24,y-40,x+24,y-15),180,360,fill=ink,width=4)
    elif mood == "shocked":
        d.ellipse((x-51,y-95,x-33,y-77),fill=ink); d.ellipse((x+33,y-95,x+51,y-77),fill=ink)
        d.ellipse((x-15,y-51,x+15,y-21),outline=ink,width=4)
    else:
        d.ellipse((x-50,y-92,x-36,y-78),fill=ink); d.ellipse((x+36,y-92,x+50,y-78),fill=ink)
        d.line((x-18,y-35,x+18,y-35),fill=ink,width=4)


def mimi(d, x, y, deadpan=False):
    ink=(41,47,55); shell=(239,243,244); blue=(70,151,209); shadow=(198,210,214)
    d.line((x,y-150,x,y-205),fill=ink,width=5); d.ellipse((x-10,y-215,x+10,y-195),fill=blue,outline=ink)
    d.ellipse((x-82,y-165,x+82,y-15),fill=shell,outline=ink,width=5)
    d.rounded_rectangle((x-92,y-20,x+92,y+135),radius=40,fill=shell,outline=ink,width=5)
    d.rectangle((x-64,y+110,x+64,y+155),fill=shadow,outline=ink,width=4)
    for ex in (x-35,x+35): d.ellipse((ex-14,y-101,ex+14,y-73),fill=blue,outline=ink,width=3)
    if deadpan: d.line((x-25,y-49,x+25,y-49),fill=ink,width=4)
    else: d.arc((x-28,y-66,x+28,y-30),0,180,fill=ink,width=4)
    d.line((x-80,y+25,x-125,y+60),fill=ink,width=12); d.line((x+80,y+25,x+125,y+60),fill=ink,width=12)


def props(d, scene, rng):
    ink=(39,43,49)
    if scene == "desk":
        d.polygon([(390,610),(650,610),(610,465),(430,465)], fill=(48,54,62), outline=ink)
        d.rectangle((450,490,590,560), fill=(89,183,169))
        for i in range(4): d.line((465,505+i*14,555-rng.randint(0,30),505+i*14),fill=(229,246,237),width=3)
    if scene == "cafe":
        d.rectangle((430,590,490,650),fill=(157,98,54),outline=ink,width=5); d.arc((475,600,520,640),270,90,fill=ink,width=5)


def render(panel, idx, out, rng):
    img=Image.new("RGB",(1024,1024),(245,240,232)); d=ImageDraw.Draw(img)
    background(d,panel["scene"],rng); props(d,panel["scene"],rng)
    ayao(d,360+rng.randint(-18,18),600,panel["mood"]); mimi(d,765+rng.randint(-12,12),625,idx==4)
    for _ in range(20):
        x=rng.randrange(0,1024,16); y=rng.randrange(0,1024,16); s=rng.choice((4,8,12)); d.rectangle((x,y,x+s,y+s),fill=(255,255,255))
    img.save(out)


def compose(config, story_data, panels, out, date):
    W=1600; margin=70; gap=34; title_h=185; footer_h=90
    cell_w=(W-margin*2-gap)//2; image_h=cell_w; text_h=255; cell_h=image_h+text_h
    H=margin+title_h+cell_h*2+gap+footer_h+margin
    canvas=Image.new("RGB",(W,H),(250,248,244)); d=ImageDraw.Draw(canvas)
    d.text((margin,margin),story_data["title"],font=fnt(64,True),fill=(24,25,28))
    d.text((margin,margin+98),f"{date} · {story_data['theme']} · ZERO-CREDIT",font=fnt(27),fill=(102,103,108))
    for i,(p,path) in enumerate(zip(story_data["panels"],panels)):
        row,col=divmod(i,2); x=margin+col*(cell_w+gap); y=margin+title_h+row*(cell_h+gap)
        canvas.paste(Image.open(path).convert("RGB").resize((cell_w,image_h)),(x,y))
        d.rectangle((x,y,x+cell_w,y+image_h),outline=(30,31,34),width=6)
        ty=y+image_h; d.rectangle((x,ty,x+cell_w,ty+text_h),fill=(255,254,250),outline=(30,31,34),width=6)
        cy=ty+22; d.text((x+28,cy),p["caption"],font=fnt(24),fill=(112,110,105)); cy+=42
        for text in p["dialogue"][:2]:
            for line in wrap(d,text,fnt(31,True),cell_w-56): d.text((x+28,cy),line,font=fnt(31,True),fill=(25,25,27)); cy+=47
            cy+=6
        d.ellipse((x+14,y+14,x+76,y+76),fill=(25,26,29)); d.text((x+34,y+27),str(i+1),font=fnt(27,True),fill="white")
    d.text((margin,H-margin-footer_h+25),config["comic"].get("footer","DAILY COMIC · ZERO API"),font=fnt(24),fill=(118,116,112))
    canvas.save(out,quality=95)


def rebuild(config):
    cards=[]
    for p in sorted(COMICS.glob("*.png"),reverse=True)[:60]:
        title=p.stem; meta=p.with_suffix(".json")
        if meta.exists():
            try: title=json.loads(meta.read_text(encoding="utf-8")).get("title",title)
            except Exception: pass
        cards.append(f'<a class="card" href="comics/{p.name}"><img src="comics/{p.name}" alt="{title}"><div><b>{title}</b><span>{p.stem}</span></div></a>')
    html=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{config['comic']['title']}</title><style>:root{{--bg:#101114;--card:#191b20;--text:#f5f1e8;--muted:#a49f95;--line:#30333a;--accent:#f0c96d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",sans-serif}}.wrap{{max-width:1120px;margin:auto;padding:50px 22px 90px}}.badge{{display:inline-block;border:1px solid #5b523d;color:var(--accent);border-radius:999px;padding:7px 12px;font-size:12px;margin-bottom:15px}}h1{{font-size:clamp(38px,7vw,76px);line-height:.95;margin:0;letter-spacing:-.05em}}p{{color:var(--muted);max-width:720px}}.latest{{display:block;background:var(--card);border:1px solid var(--line);padding:14px;border-radius:24px;margin-top:30px}}.latest img{{display:block;width:100%;border-radius:14px}}h2{{margin:54px 0 18px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:18px;overflow:hidden;color:inherit;text-decoration:none}}.card img{{width:100%;aspect-ratio:1/1.42;object-fit:cover;object-position:top;display:block}}.card div{{padding:13px 14px;display:flex;flex-direction:column}}.card span{{font-size:12px;color:var(--muted)}}</style></head><body><main class="wrap"><span class="badge">ZERO API · ZERO CREDITS</span><h1>{config['comic']['title']}</h1><p>每天 08:30 由 GitHub Actions 自動產生四格漫畫。劇情、角色、場景與排版全部由 Python 程式生成，不呼叫任何付費 AI API。</p><a class="latest" href="latest.png"><img src="latest.png" alt="最新漫畫"></a><h2>歷史漫畫</h2><section class="grid">{''.join(cards)}</section></main></body></html>'''
    (DOCS/"index.html").write_text(html,encoding="utf-8")


def main():
    config=load_yaml(); now=datetime.now(TAIPEI); date=now.strftime("%Y-%m-%d"); issue=os.getenv("COMIC_DATE",date)
    seed=sum((i+1)*ord(ch) for i,ch in enumerate(issue+"|ZERO-CREDIT-V2")); rng=random.Random(seed)
    COMICS.mkdir(parents=True,exist_ok=True); history=load_history()
    recent={x.get("theme") for x in history[-7:]}; themes=[x for x in config.get("themes",[]) if x not in recent] or config.get("themes",[]) or ["生活裡的小荒謬"]
    data=story(rng.choice(themes),rng); temp=ROOT/".tmp_panels"; shutil.rmtree(temp,ignore_errors=True); temp.mkdir(); paths=[]
    for i,panel in enumerate(data["panels"],1):
        p=temp/f"panel_{i}.png"; render(panel,i,p,random.Random(seed+i*997)); paths.append(p)
    comic=COMICS/f"{issue}.png"; compose(config,data,paths,comic,date)
    meta={**data,"date":date,"generator":"procedural-python-v2","api_cost":0,"dry_run":False}
    (COMICS/f"{issue}.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    shutil.copyfile(comic,LATEST); LATEST_JSON.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    history=[h for h in history if h.get("date")!=date]; history.append({"date":date,"title":data["title"],"theme":data["theme"],"generator":"procedural-python-v2"}); save_history(history)
    rebuild(config); shutil.rmtree(temp,ignore_errors=True); print(f"Generated zero-credit comic: {comic}")


if __name__ == "__main__":
    main()
