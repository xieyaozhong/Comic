from __future__ import annotations

import base64
import json
import os
import random
import re
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.yaml"
HISTORY_PATH = ROOT / "data" / "history.json"
DOCS = ROOT / "docs"
COMICS_DIR = DOCS / "comics"
LATEST_PATH = DOCS / "latest.png"
LATEST_JSON = DOCS / "latest.json"
TAIPEI = timezone(timedelta(hours=8))


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_history(history: list[dict]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(history[-60:], ensure_ascii=False, indent=2), encoding="utf-8")


def find_cjk_font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Bold.otf" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def extract_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return json.loads(text[text.find("{"):text.rfind("}") + 1])


def character_bible(config: dict) -> str:
    return "\n".join(f"- {c['name']}: {c['description']}" for c in config.get("characters", []))


def select_theme(config: dict, history: list[dict]) -> str:
    recent = {x.get("theme") for x in history[-10:]}
    choices = [x for x in config.get("themes", []) if x not in recent]
    return random.choice(choices or config.get("themes") or ["日常小反轉"])


def dry_story(theme: str) -> dict:
    return {
        "title": "今天不要過度自動化",
        "theme": theme,
        "summary": "阿曜想把泡咖啡完全自動化，最後發現米米早已把最重要的部分自動化了。",
        "panels": [
            {"scene": "早晨工作桌旁，阿曜盯著咖啡機與筆電，米米在旁邊。", "dialogue": ["阿曜：今天我要把咖啡完全自動化。"], "caption": "08:01"},
            {"scene": "阿曜快速打程式，米米安靜看著。", "dialogue": ["阿曜：研磨、注水、計時，全交給程式。"], "caption": "08:17"},
            {"scene": "咖啡機開始運作，阿曜得意地舉手，米米端著一杯咖啡。", "dialogue": ["阿曜：成功！人類終於自由了。"], "caption": "08:31"},
            {"scene": "米米把咖啡遞給阿曜。", "dialogue": ["米米：其實你昨晚已經叫我今天直接泡。", "阿曜：……那我剛剛在忙什麼？"], "caption": "系統：自動化完成"},
        ],
    }


def generate_story(config: dict, theme: str, history: list[dict], dry_run: bool) -> dict:
    if dry_run:
        return dry_story(theme)
    from openai import OpenAI
    client = OpenAI()
    model = os.getenv("OPENAI_TEXT_MODEL", "gpt-5.6-luna")
    rules = "\n".join(f"- {x}" for x in config.get("story_rules", []))
    prompt = f'''你是每日四格漫畫編劇。產生一篇原創、可獨立閱讀的繁體中文四格漫畫。
今天主題：{theme}
固定角色：\n{character_bible(config)}
規則：\n{rules}
最近標題不要重複：{[x.get('title','') for x in history[-12:]]}
每格 scene 描述可直接拿去做圖的動作、場景、表情與構圖。圖片不畫字，對白由後製加入。
只輸出合法 JSON：
{{"title":"短標題","theme":"{theme}","summary":"一句摘要","panels":[{{"scene":"...","dialogue":["角色：台詞"],"caption":""}},{{"scene":"...","dialogue":["角色：台詞"],"caption":""}},{{"scene":"...","dialogue":["角色：台詞"],"caption":""}},{{"scene":"...","dialogue":["角色：台詞"],"caption":""}}]}}'''
    response = client.responses.create(model=model, reasoning={"effort":"low"}, input=prompt)
    story = extract_json(response.output_text)
    if len(story.get("panels", [])) != 4:
        raise ValueError("Story must contain exactly 4 panels")
    return story


def placeholder(panel: dict, idx: int, out: Path) -> None:
    img = Image.new("RGB", (1024, 1024), (242, 239, 231))
    d = ImageDraw.Draw(img)
    title = find_cjk_font(56, True)
    body = find_cjk_font(34)
    d.rectangle((45,45,979,979), outline=(28,28,28), width=8)
    d.text((80,80), f"DRY RUN · PANEL {idx}", font=title, fill=(25,25,25))
    y = 200
    for chunk in [panel.get("scene", "")[i:i+20] for i in range(0, len(panel.get("scene", "")), 20)]:
        d.text((80,y), chunk, font=body, fill=(45,45,45)); y += 58
    img.save(out)


def panel_image(config: dict, panel: dict, idx: int, out: Path, dry_run: bool) -> None:
    if dry_run:
        placeholder(panel, idx, out); return
    from openai import OpenAI
    client = OpenAI()
    prompt = f'''Create panel {idx} of an original 4-panel comic.
Visual style: {config['comic']['style']}.
Characters must remain visually consistent:\n{character_bible(config)}
Scene: {panel['scene']}
Single comic panel, expressive faces, clean hierarchy. No letters, captions, speech bubbles, logos or watermarks.'''
    result = client.images.generate(model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2"), prompt=prompt, size=config["comic"].get("image_size","1024x1024"), quality=config["comic"].get("image_quality","low"))
    out.write_bytes(base64.b64decode(result.data[0].b64_json))


def lines_by_width(draw, text, font, max_width):
    lines, cur = [], ""
    for ch in text:
        if draw.textbbox((0,0), cur + ch, font=font)[2] <= max_width:
            cur += ch
        else:
            if cur: lines.append(cur)
            cur = ch
    if cur: lines.append(cur)
    return lines


def compose(config: dict, story: dict, paths: list[Path], out: Path, date_str: str) -> None:
    W, margin, gap, title_h, footer_h = 1600, 70, 34, 180, 90
    cell_w = (W - margin * 2 - gap) // 2
    image_h, text_h = cell_w, 250
    cell_h = image_h + text_h
    H = margin + title_h + cell_h * 2 + gap + footer_h + margin
    canvas = Image.new("RGB", (W,H), "white")
    d = ImageDraw.Draw(canvas)
    title_font, meta_font = find_cjk_font(62,True), find_cjk_font(27)
    dialog_font, caption_font = find_cjk_font(31,True), find_cjk_font(24)
    d.text((margin,margin), story.get("title","每日漫畫"), font=title_font, fill=(18,18,18))
    d.text((margin,margin+92), f"{date_str} · {story.get('theme','')}", font=meta_font, fill=(90,90,90))
    for i,(panel,path) in enumerate(zip(story["panels"], paths)):
        row,col = divmod(i,2); x = margin + col*(cell_w+gap); y = margin+title_h+row*(cell_h+gap)
        pi = Image.open(path).convert("RGB"); pi.thumbnail((cell_w,image_h))
        bg = Image.new("RGB", (cell_w,image_h), (246,246,246)); bg.paste(pi, ((cell_w-pi.width)//2,(image_h-pi.height)//2)); canvas.paste(bg,(x,y))
        d.rectangle((x,y,x+cell_w,y+image_h), outline=(25,25,25), width=6)
        ty = y+image_h; d.rectangle((x,ty,x+cell_w,ty+text_h), fill=(250,250,248), outline=(25,25,25), width=6)
        cy = ty+24
        if panel.get("caption"):
            d.text((x+28,cy), panel["caption"], font=caption_font, fill=(105,105,105)); cy += 42
        for dialogue in panel.get("dialogue",[])[:2]:
            for line in lines_by_width(d, dialogue, dialog_font, cell_w-56):
                d.text((x+28,cy), line, font=dialog_font, fill=(26,26,26)); cy += 47
            cy += 8
        d.ellipse((x+13,y+13,x+75,y+75), fill=(20,20,20)); d.text((x+33,y+25), str(i+1), font=find_cjk_font(28,True), fill="white")
    d.text((margin,H-margin-footer_h+25), config["comic"].get("footer","AI DAILY COMIC"), font=caption_font, fill=(120,120,120))
    canvas.save(out, quality=95)


def rebuild_index(config: dict) -> None:
    cards=[]
    for p in sorted(COMICS_DIR.glob("*.png"), reverse=True)[:40]:
        meta_file = p.with_suffix(".json"); title=p.stem
        if meta_file.exists():
            try: title=json.loads(meta_file.read_text(encoding="utf-8")).get("title",title)
            except Exception: pass
        cards.append(f'<a class="card" href="comics/{p.name}"><img src="comics/{p.name}" alt="{title}"><div><b>{title}</b><span>{p.stem}</span></div></a>')
    html=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{config['comic']['title']}</title><style>:root{{--bg:#0f1115;--card:#181b21;--text:#f3f4f6;--muted:#969ca8;--line:#2a2f38}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC",sans-serif}}.wrap{{max-width:1120px;margin:auto;padding:56px 22px 90px}}header{{display:flex;justify-content:space-between;gap:20px;align-items:end;margin-bottom:32px}}h1{{font-size:clamp(36px,7vw,74px);line-height:.95;margin:0;letter-spacing:-.05em}}p{{color:var(--muted)}}.latest{{display:block;background:var(--card);border:1px solid var(--line);padding:14px;border-radius:24px}}.latest img{{display:block;width:100%;border-radius:14px}}h2{{margin:56px 0 18px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:18px;overflow:hidden;color:inherit;text-decoration:none}}.card img{{width:100%;aspect-ratio:1/1.42;object-fit:cover;object-position:top;display:block}}.card div{{padding:13px 14px;display:flex;flex-direction:column}}.card span{{font-size:12px;color:var(--muted)}}</style></head><body><main class="wrap"><header><div><h1>{config['comic']['title']}</h1><p>每天自動生成 · 四格原創漫畫 · GitHub Actions</p></div></header><a class="latest" href="latest.png"><img src="latest.png" alt="最新漫畫"></a><h2>歷史漫畫</h2><section class="grid">{''.join(cards)}</section></main></body></html>'''
    (DOCS/"index.html").write_text(html, encoding="utf-8")


def main():
    config=load_config(); dry_run=env_bool("DRY_RUN",False); now=datetime.now(TAIPEI); date_str=now.strftime("%Y-%m-%d"); run_id=os.getenv("COMIC_DATE",date_str)
    COMICS_DIR.mkdir(parents=True,exist_ok=True); history=load_history(); theme=select_theme(config,history); story=generate_story(config,theme,history,dry_run)
    temp=ROOT/".tmp_panels"; shutil.rmtree(temp,ignore_errors=True); temp.mkdir()
    paths=[]
    for idx,panel in enumerate(story["panels"],1):
        p=temp/f"panel_{idx}.png"; print(f"Generating panel {idx}/4..."); panel_image(config,panel,idx,p,dry_run); paths.append(p)
    comic=COMICS_DIR/f"{run_id}.png"; meta_path=COMICS_DIR/f"{run_id}.json"; compose(config,story,paths,comic,date_str)
    meta={**story,"date":date_str,"dry_run":dry_run}; meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8"); shutil.copyfile(comic,LATEST_PATH); LATEST_JSON.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    history.append({"date":date_str,"title":story.get("title"),"theme":story.get("theme")}); save_history(history); rebuild_index(config); shutil.rmtree(temp,ignore_errors=True); print(f"Done: {comic}")


if __name__ == "__main__":
    main()
