import json
import random
import shutil
import hashlib
import re
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path('.')
CFG = ROOT / 'config.yaml'
DOCS = ROOT / 'docs'
COMICS = DOCS / 'comics'
EPISODES = DOCS / 'episodes'
HISTORY = ROOT / 'data' / 'history.json'
TPE = timezone(timedelta(hours=8))

W = 1080
PANEL_H = 760
PANELS = 5

# Open-source-layout-inspired reading grammar:
# wide establish -> offset reaction -> narrow clue -> medium tension -> full reveal
LAYOUTS = [
    {'name': 'hero', 'width': 1080, 'height': 760, 'align': 'center', 'gap_after': 90},
    {'name': 'support-left', 'width': 820, 'height': 650, 'align': 'left', 'gap_after': 150},
    {'name': 'clue-right', 'width': 650, 'height': 610, 'align': 'right', 'gap_after': 95},
    {'name': 'tension', 'width': 880, 'height': 680, 'align': 'center', 'gap_after': 180},
    {'name': 'reveal', 'width': 1080, 'height': 820, 'align': 'center', 'gap_after': 0},
]

CHARACTERS = {
    'seo': {'name': 'å¾å…', 'hair': (62, 45, 66), 'coat': (227, 232, 246), 'accent': (167, 181, 232)},
    'min': {'name': 'é–”å¤', 'hair': (92, 66, 54), 'coat': (230, 239, 251), 'accent': (157, 186, 235)},
    'hae': {'name': 'æµ·æº–', 'hair': (35, 44, 70), 'coat': (221, 235, 234), 'accent': (146, 187, 188)},
}

STORIES = [
    {
        'theme': 'æ ¡åœ’ç¥•å¯†ç›´æ’­',
        'keys': ['thriller', 'school', 'drama'],
        'title': 'å‡Œæ™¨ 2:13 çš„ç›´æ’­é–“',
        'summary': 'è½‰å­¸ç”Ÿèª¤å…¥ä¸€å ´åªæœ‰è¢«é»åè€…æ‰èƒ½çœ‹è¦‹çš„ç›´æ’­ï¼Œè€Œä¸‹ä¸€å€‹åå­—ç«Ÿç„¶æ˜¯å¥¹ã€‚',
        'tags': ['æ ¡åœ’', 'æ‡¸ç–‘', 'ç›´æ’­', 'åè½‰'],
        'panels': [
            ('night', 'tense', 'å¾å…ï¼šé€™ä¸æ˜¯æˆ‘å€‘å­¸æ ¡çš„ç¤¾ç¾¤å—â€¦ï¼Ÿ', 'åˆå¤œï¼Œæ‰‹æ©Ÿçªç„¶è·³å‡ºæœªè¨‚é–±ç›´æ’­'),
            ('phone', 'shock', 'ç•«é¢ï¼šä»Šæ™šæœƒæ¶ˆå¤±çš„äºº', 'è§€çœ¾åå–®ä¸€å€‹ä¸€å€‹äº®èµ·'),
            ('hall', 'fear', 'é–”å¤ï¼šå¦³ä¹Ÿæ”¶åˆ°äº†ï¼Ÿåƒè¬åˆ¥ç•™è¨€ã€‚', 'åªæœ‰å°‘æ•¸å­¸ç”Ÿçœ‹å¾—è¦‹'),
            ('stairs', 'urgent', 'å¾å…ï¼šç­‰ç­‰ï¼Œæœ€å¾Œé‚£å€‹åå­—æ˜¯æˆ‘ï¼Ÿ', 'ç•«é¢åˆ‡åˆ°ç©ºç„¡ä¸€äººçš„æ¨“æ¢¯é–“'),
            ('hook', 'cliffhanger', 'åŒ¿åè¨Šæ¯ï¼š2:30 å‰ï¼Œæ‰¾åˆ°ã€Œç¬¬äºŒæ”¯æ‰‹æ©Ÿã€ã€‚', 'ä¸‹ä¸€ç§’ï¼Œç›´æ’­é¡é ­å°æº–äº†å¾å…èº«å¾Œ'),
        ],
    },
    {
        'theme': 'è·å ´å½æˆ€æ„›',
        'keys': ['romance', 'drama'],
        'title': 'ç°½ä¸‹å»å°±è¦å‡è£äº¤å¾€',
        'summary': 'æ™®é€šä¼åŠƒç‚ºäº†ä¿ä½å·¥ä½œç­”æ‡‰ä¸‰å€‹æœˆå‡æˆ€æ„›ï¼Œå»åœ¨åˆç´„æœ€å¾Œä¸€é çœ‹åˆ°çˆ¶è¦ªçš„åå­—ã€‚',
        'tags': ['è·å ´', 'æˆ€æ„›', 'å¥‘ç´„', 'ç¥•å¯†'],
        'panels': [
            ('office', 'awkward', 'æµ·æº–ï¼šä¸‰å€‹æœˆï¼Œå¦³æœƒå¾—åˆ°å‡è·ã€‚', 'ä»–éä¾†ä¸€ä»½å¥‡æ€ªçš„åˆç´„'),
            ('paper', 'skeptical', 'é–”å¤ï¼šå‡è£äº¤å¾€ä¹Ÿå¯«é€² KPIï¼Ÿ', 'æ¢æ¬¾ 7ï¼šä¸å¾—å°å¤–å¦èªé—œä¿‚'),
            ('lift', 'flutter', 'åŒäº‹ï¼šä½ å€‘çœŸçš„åœ¨ä¸€èµ·äº†ï¼Ÿ', 'æ¶ˆæ¯æ¯”å…¬å‘Šæ›´å¿«å‚³éå…¬å¸'),
            ('roof', 'uneasy', 'æµ·æº–ï¼šå¦‚æœç¾åœ¨åæ‚”ï¼Œå·²ç¶“ä¾†ä¸åŠã€‚', 'æ¨“ä¸‹åœè‘—ä¸‰å°è¨˜è€…è»Š'),
            ('hook', 'cliffhanger', 'é–”å¤ï¼šç‚ºä»€éº¼æˆ‘çˆ¸ä¹Ÿç°½éé€™ä»½åˆç´„ï¼Ÿ', 'æœ€å¾Œä¸€é å¤¾è‘—åäº”å¹´å‰çš„ç…§ç‰‡'),
        ],
    },
    {
        'theme': 'è¿´æ­¸å€’æ•¸',
        'keys': ['action', 'fantasy', 'thriller'],
        'title': 'æˆ‘åˆå›åˆ°å‡ºäº‹å‰ä¸‰å¤©',
        'summary': 'äº‹æ•…å¾Œé†’ä¾†ï¼Œæ™‚é–“å›åˆ°ä¸‰å¤©å‰ï¼›å”¯ä¸€è¨˜å¾—çœŸç›¸çš„äººï¼Œæ˜¯æ›¾ç¶“æœ€è¨å­ä»–çš„å¥³å­©ã€‚',
        'tags': ['å›æ­¸', 'æ‡¸ç–‘', 'å‘½é‹', 'æ•‘è´–'],
        'panels': [
            ('rain', 'pain', 'æµ·æº–ï¼šæˆ‘ä¸æ˜¯å·²ç¶“æ­»äº†å—ï¼Ÿ', 'ç…è»Šè²ä»åœ¨è€³é‚Š'),
            ('room', 'shock', 'æ‰‹æ©Ÿæ—¥æœŸï¼š10 æœˆ 14 æ—¥', 'äº‹æ•…å‰ä¸‰å¤©'),
            ('cafe', 'cold', 'å¾å…ï¼šé€™æ¬¡ä½ ç¸½ç®—è¨˜å¾—æˆ‘äº†ï¼Ÿ', 'å¥¹æ¨å‡ºä¸€å¼µè»Šç¦ç…§ç‰‡'),
            ('alley', 'urgent', 'å¾å…ï¼šç¬¬ä¸‰å¤©ï¼Œä½ æœƒå®³æ­»ä¸€å€‹äººã€‚', 'è€Œé‚£å€‹äººä¸æ˜¯ä½ '),
            ('hook', 'cliffhanger', 'å¾å…ï¼šä»Šæ™š 11 é»ï¼Œä¸è¦å›å®¶ã€‚', 'é–€å¤–å»ç«™è‘—å¦ä¸€å€‹æµ·æº–'),
        ],
    },
    {
        'theme': 'å¶åƒç”Ÿå­˜æˆ°',
        'keys': ['drama', 'thriller', 'romance'],
        'title': 'ç¬¬ 7 åä¸å‡†å‡ºé“',
        'summary': 'ç·´ç¿’ç”Ÿåœ¨æœ€çµ‚æ’åå‰æ”¶åˆ°åŒ¿åè¦å‰‡ï¼šæˆç‚ºç¬¬ 7 åçš„äººï¼Œæœƒè¢«ç¯€ç›®æŠ¹å»å­˜åœ¨ã€‚',
        'tags': ['å¶åƒ', 'ç”Ÿå­˜è³½', 'ç«¶çˆ­', 'æ‡¸å¿µ'],
        'panels': [
            ('stage', 'nervous', 'å°æ¼”ï¼šæœ€çµ‚æ’åäº”åˆ†é˜å¾Œå…¬é–‹ã€‚', 'å€™å ´å€å®‰éœå¾—ç•°å¸¸'),
            ('phone', 'fear', 'åŒ¿åè¨Šæ¯ï¼šåˆ¥æ‹¿ç¬¬ 7 åã€‚', 'ä¸Šä¸€å€‹ç¬¬ 7 åå·²ä¸å­˜åœ¨'),
            ('hall', 'whisper', 'é–”å¤ï¼šå¦³ä¹Ÿçœ‹åˆ°é‚£æ¢è¦å‰‡ï¼Ÿ', 'å¥¹çš„åç‰Œæœ‰è¢«æ’•æ‰çš„ç—•è·¡'),
            ('stage', 'panic', 'å¾å…ï¼šå¦‚æœæ•…æ„å¤±èª¤å‘¢ï¼Ÿ', 'è€³æ©Ÿå‚³ä¾†è‡ªå·±çš„è²éŸ³ï¼šå¤ªæ™šäº†'),
            ('hook', 'cliffhanger', 'ä¸»æŒäººï¼šç¬¬ 7 åâ€”â€”', 'å…¨å ´ç‡ˆå…‰çªç„¶ç†„æ»…'),
        ],
    },
]

COLORS = {
    'night': ((30, 34, 68), (93, 108, 165)),
    'phone': ((19, 22, 34), (68, 77, 102)),
    'hall': ((117, 137, 164), (199, 212, 227)),
    'stairs': ((51, 56, 79), (119, 128, 156)),
    'hook': ((80, 53, 92), (170, 117, 176)),
    'office': ((230, 235, 245), (198, 213, 234)),
    'paper': ((226, 230, 239), (247, 235, 241)),
    'lift': ((170, 176, 186), (228, 232, 239)),
    'roof': ((111, 132, 166), (205, 217, 234)),
    'rain': ((46, 56, 82), (105, 118, 151)),
    'room': ((216, 221, 232), (249, 246, 250)),
    'cafe': ((208, 184, 158), (249, 238, 220)),
    'alley': ((74, 83, 104), (149, 160, 185)),
    'stage': ((55, 40, 74), (137, 101, 178)),
}


def font(size, bold=False):
    path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc' if bold else '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    return ImageFont.truetype(path, size)


def rr(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def gradient(size, top, bottom):
    w, h = size
    img = Image.new('RGB', size)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(w):
            px[x, y] = color
    return img


def seeded(key):
    return random.Random(int(hashlib.sha256(key.encode()).hexdigest()[:16], 16))


def load_history():
    try:
        return json.loads(HISTORY.read_text(encoding='utf-8'))
    except Exception:
        return []


def save_history(items):
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(items[-160:], ensure_ascii=False, indent=2), encoding='utf-8')


def wrap_text(draw, text, fnt, max_width):
    lines, cur = [], ''
    for ch in text:
        if draw.textbbox((0, 0), cur + ch, font=fnt)[2] <= max_width:
            cur += ch
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def trend_scores():
    scores = {k: 1 for k in ['romance', 'thriller', 'action', 'fantasy', 'drama', 'school']}
    terms = {
        'romance': ['romance', 'ë¡œë§¨ìŠ¤', 'í•™ì›ë¡œë§¨ìŠ¤'],
        'thriller': ['thriller', 'ìŠ¤ë¦´ëŸ¬'],
        'action': ['action', 'ì•¡ì…˜', 'ë¨¼ì¹˜í‚¨'],
        'fantasy': ['fantasy', 'íŒíƒ€ì§€', 'ë¡œíŒ', 'ê²Œì„íŒíƒ€ì¤‘'],
        'drama': ['drama', 'í“œë¼í§ˆ', 'í•™ì›ë¬¼'],
        'school': ['school', 'í•™ì›', 'í• ì›ë¡œë†ˆìŠ¤'],
    }
    for url in ['https://www.webtoons.com/en/ranking/popular', 'https://comic.naver.com/webtoon?tab=genre']:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 DailyComicBot/2.0'})
            text = urllib.request.urlopen(req, timeout=8).read(420000).decode('utf-8', 'ignore').lower()
            text = re.sub(r'<[^>]+>', ' ', text)
            for key, words in terms.items():
                scores[key] += sum(text.count(word.lower()) for word in words)
        except Exception as exc:
            print('trend fallback', type(exc).__name__)
    return scores


def choose_story(day, history):
    recent = {x.get('theme') for x in history[-8:]}
    pool = [story for story in STORIES if story['theme'] not in recent] or STORIES
    scores = trend_scores()
    weighted = []
    for story in pool:
        weight = min(80, 1 + sum(scores.get(k, 1) for k in story['keys']))
        weighted.extend([story] * weight)
    picked = seeded(day).choice(weighted)
    print('trend', scores, '=>', picked['theme'])
    return picked


def add_glow(base, center, radius, color=(255, 255, 255, 50), blur=24):
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = center
    d.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composit(base.convert('RGBA'), layer)


def background(scene, mood, rng):
    img = gradient((W, PANEL_H), *COLORS[scene]).convert('RGBA')
    img = add_glow(img, (W // 2, 180), 190)
    d = ImageDraw.Draw(img, 'RGBA')

    if scene in {'night', 'hall', 'stairs', 'office', 'lift', 'room'}:
        for x in (82, 324, 566, 808):
            d.rectangle((x, 125, x + 176, 365), outline=(255, 255, 255, 90), width=3)
    if scene in {'rain', 'alley'}:
        for _ in range(100):
            x = rng.randint(0, W)
            y = rng.randint(0, PANEL_H)
            d.line((x, y, x - 15, y + 34), fill=(228, 238, 255, 88), width=2)
    if scene == 'stage':
        for x in (170, 410, 650, 890):
            d.ellipse((x - 15, 80, x + 15, 110), fill=(255, 255, 255, 120))
            d.polygon([(x, 112), (x - 72, 390), (x + 72, 390)], fill=(255, 255, 255, 25))
    if scene == 'phone':
        rr(d, (380, 120, 700, 510), 44, fill=(16, 18, 28, 170), outline=(255, 255, 255, 50), width=3)
        d.rectangle((410, 170, 670, 450), fill=(74, 84, 110, 100))
    if scene == 'cafe':
        d.rectangle((0, 610, W, PANEL_H), fill=(105, 77, 55, 90))
    if scene == 'hook':
        d.rectangle((0, 0, W, PANEL_H), fill=(45, 8, 34, 28))

    if mood in {'tense', 'fear', 'urgent', 'panic', 'cliffhanger', 'shock'}:
        for _ in range(32):
            x = rng.randint(-50, W)
            y = rng.randint(0, PANEL_H)
            length = rng.randint(45, 150)
            d.line((x, y, x + length, y - rng.randint(5, 24)), fill=(255, 255, 255, 32), width=1)
    return img.convert('RGB')


def person(draw, key, x, y, scale=1.0, mood='calm'):
    c = CHARACTERS[key]
    skin = (247, 220, 200)
    hair = c['hair']
    coat = c['coat']
    accent = c['accent']
    outline = (42, 44, 55)

    # Subtle shadow
    draw.ellipse((x - 90 * scale, y + 300 * scale, x + 90 * scale, y + 330 * scale), fill=(0, 0, 0, 24))

    # Long legs / webtoon proportion
    draw.line((x - 22 * scale, y + 210 * scale, x - 28 * scale, y + 340 * scale), fill=(61, 64, 82), width=max(9, int(13 * scale)))
    draw.line((x + 22 * scale, y + 210 * scale, x + 28 * scale, y + 340 * scale), fill=(61, 64, 82), width=max(9, int(13 * scale)))
    draw.line((x - 40 * scale, y + 342 * scale, x - 7 * scale, y + 342 * scale), fill=outline, width=max(8, int(10 * scale)))
    draw.line((x + 7 * scale, y + 342 * scale, x + 40 * scale, y + 342 * scale), fill=outline, width=max(8, int(10 * scale)))

    # Torso
    rr(draw, (x - 64 * scale, y + 92 * scale, x + 64 * scale, y + 245 * scale), int(28 * scale), fill=coat)
    rr(draw, (x - 38 * scale, y + 116 * scale, x + 38 * scale, y + 225 * scale), int(18 * scale), fill=accent)
    rr(draw, (x - 28 * scale, y + 119 * scale, x + 28 * scale, y + 218 * scale), int(16 * scale), fill=(246, 248, 252))

    # Neck/head
    draw.rectangle((x - 12 * scale, y + 70 * scale, x + 12 * scale, y + 104 * scale), fill=skin)
    draw.ellipse((x - 48 * scale, y - 18 * scale, x + 48 * scale, y + 92 * scale), fill=skin)
    draw.pieslice((x - 55 * scale, y - 34 * scale, x + 55 * scale, y + 69 * scale), 180, 360, fill=hair)
    rr(draw, (x - 52 * scale, y - 8 * scale, x + 52 * scale, y + 32 * scale), int(17 * scale), fill=hair)

    # Arms
    arm_y = y + 135 * scale
    if mood in {'urgent', 'panic', 'shock', 'cliffhanger'}:
        draw.line((x - 58 * scale, arm_y, x - 102 * scale, y + 95 * scale), fill=coat, width=max(10, int(14 * scale)))
        draw.line((x + 58 * scale, arm_y, x + 104 * scale, y + 94 * scale), fill=coat, width=max(10, int(14 * scale)))
    else:
        draw.line((x - 58 * scale, arm_y, x - 92 * scale, y + 175 * scale), fill=coat, width=max(10, int(14 * scale)))
        draw.line((x + 58 * scale, arm_y, x + 92 * scale, y + 175 * scale), fill=coat, width=max(10, int(14 * scale)))

    # Face
    ey = y + 42 * scale
    ex = 19 * scale
    if mood in {'shock', 'fear', 'panic', 'cliffhanger'}:
        for dx in (-ex, ex):
            draw.ellipse((x + dx - 7 * scale, ey - 4 * scale, x + dx + 7 * scale, ey + 11 * scale), fill='white', outline=outline, width=max(1, int(2 * scale)))
            draw.ellipse((x + dx - 2 * scale, ey + 1 * scale, x + dx + 2 * scale, ey + 7 * scale), fill=outline)
    else:
        draw.line((x - ex - 7 * scale, ey + 4 * scale, x - ex + 7 * scale, ey + 4 * scale), fill=outline, width=max(2, int(3 * scale)))
        draw.line((x + ex - 7 * scale, ey + 4 * scale, x + ex + 7 * scale, ey + 4 * scale), fill=outline, width=max(2, int(3 * scale)))

    mouth_y = y + 70 * scale
    if mood in {'awkward', 'skeptical', 'uneasy', 'cold'}:
        draw.line((x - 10 * scale, mouth_y, x + 10 * scale, mouth_y - 1 * scale), fill=outline, width=max(2, int(3 * scale)))
    elif mood in {'shock', 'fear', 'panic'}:
        draw.ellipse((x - 5 * scale, mouth_y - 3 * scale, x + 5 * scale, mouth_y + 10 * scale), outline=outline, width=max(2, int(3 * scale)))
    else:
        draw.arc((x - 12 * scale, mouth_y - 2 * scale, x + 12 * scale, mouth_y + 10 * scale), 5, 175, fill=outline, width=max(2, int(3 * scale)))


def capsule(draw, text, x, y, dark=False):
    fnt = font(24, True)
    tw = draw.textbbox((0, 0), text, font=fnt)[2]
    rr(draw, (x, y, x + tw + 32, y + 43), 19, fill=(21, 23, 34, 230) if dark else (255, 255, 255, 235))
    draw.text((x + 16, y + 8), text, font=fnt, fill='white' if dark else (37, 42, 58))


def speech(draw, dialogue, y1, dark=False):
    who, said = dialogue.split('ï¼š', 1) if 'ï¼š' in dialogue else ('æ—ç™½', dialogue)
    box = (48, y1, W - 48, PANEL_H - 42)
    fill = (29, 31, 43) if dark else (255, 255, 255)
    outline = (80, 85, 105) if dark else (228, 231, 238)
    rr(draw, box, 27, fill=fill, outline=outline, width=2)
    # bubble tail
    draw.polygon([(78, PANEL_H - 58), (98, PANEL_H - 58), (90, PANEL_H - 28)], fill=fill)
    color = (248, 249, 252) if dark else (28, 31, 40)
    draw.text((72, y1 + 17), who, font=font(28, True), fill=color)
    yy = y1 + 59
    for line in wrap_text(draw, said, font(27), W - 150):
        draw.text((72, yy), line, font=font(27), fill=color)
        yy += 36


def make_panel(story, index, output, day):
    scene, mood, dialogue, caption = story['panels'][index - 1]
    rng = seeded(f'{day}-{index}')
    img = background(scene, mood, rng)
    d = ImageDraw.Draw(img, 'RGBA')

    # Deliberately asymmetrical character placement to avoid same-looking frames
    placements = [
        ('seo', 290, 255, 1.25, mood, 'min', 790, 280, 1.08, 'calm'),
        ('min', 770, 255, 1.23, mood, 'seo', 290, 300, 1.00, 'calm'),
        ('seo', 250, 270, 1.08, mood, 'min', 720, 245, 1.30, 'cold'),
        ('hae', 780, 255, 1.22, mod, 'seo', 300, 285, 1.08, 'calm'),
        ('seo', 330, 240, 1.32, mood, 'hae', 800, 295, 1.02, 'cold'),
    ]
    a, ax, ay, asc, am, b, bx, by, bsc, bm = placements[index - 1]
    person(d, a, ax, ay, asc, am)
    person(d, b, bx, by, bsc, bm)

    capsule(d, f'EP {day[5:].replace("-", ".")} Â· CUT {index}', 38, 30, dark=True)
    capsule(d, caption, 38, 88, dark=False)
    speech(d, dialogue, PANEL_H - 220, dark=index == PANELS)
    if index == PANELS:
        d.text((W - 180, 36), 'ä¸‹å›å¾„çºŒ', font=font(28, True), fill=(255, 247, 252, 225))
    img.save(output)


def compose_share(story, panel_paths, output, day):
    # Share image keeps the same open-source-inspired varying geometry.
    canvas_w = 1080
    header_h = 230
    footer_h = 92
    placements = []
    y = header_h
    for spec in LAYOUTS:
        placements.append((spec, y))
        y += spec['height'] + spec['gap_after']
    total_h = y + footer_h
    canvas = Image.new('RGB', (canvas_w, total_h), (247, 247, 250))
    d = ImageDraw.Draw(canvas, 'RGBA')
    header = gradient((canvas_w, header_h), (31, 34, 50), (90, 62, 109))
    canvas.paste(header, (0, 0))
    d.text((52, 34), story['title'], font=font(45, True), fill='white')
    d.text((52, 94), story['summary'], font=font(24), fill=(240, 240, 246))
    d.text((52, 156), '  '.join('#' + t for t in story['tags']), font=font(22, True), fill=(235, 219, 249))

    for path, (spec, y0) in zip(panel_paths, placements):
        panel = Image.open(path).convert('RGB')
        panel = panel.resize((spec['width'], spec['height']), Image.Resampling.LANCZOS)
        if spec['align'] == 'left':
            x0 = 0
        elif spec['align'] == 'right':
            x0 = canvas_w - spec['width']
        else:
            x0 = (canvas_w - spec['width']) // 2
        canvas.paste(panel, (x0, y0))

    d.rectangle((0, total_h - footer_h, canvas_w, total_h), fill=(21, 24, 34))
    d.text((52, total_h - 59), 'æ¯å¤©ä¸€å°æ®µï¼Œç•™ä¸‹ä¸€å€‹æƒ³è¿½ä¸‹å»çš„é‰¤å­', font=font(23), fill=(220, 225, 239))
    d.text((canvas_w - 205, total_h - 59), day, font=font(23, True), fill=(255, 226, 240))
    canvas.save(output)


def build_index(config, latest_meta):
    title = config['comic']['title']
    subtitle = config['comic'].get('subtitle', '')
    latest_day = latest_meta['date']
    latest_folder = f'episodes/{latest_day}'
    latest_tags = ''.join(f'<span class="tag">#{t}</span>' for t in latest_meta['tags'])

    figures = []
    for i, spec in enumerate(LAYOUTS, start=1):
        figures.append(
            f'<figure class="panel-frame {spec["name"]} {spec["align"]}" style="--gap:{spec["gap_after"]}px">'
            f'<img loading="eager" src="{latest_folder}/panel-{i}.png" alt="{latest_meta["title"]} åˆ†é¡ã€í¥ôˆøœ(€€€€€€€€€€€˜œğ½™¥ÕÉ”øœ(€€€€€€€€¤((€€€…É¡¥Ù•}…É‘Ì€ômt(€€€µ•Ñ…Ì€ôíô(€€€™½Èµ˜¥¸=5%L¹±½ˆ œ¨¹©Í½¸œ¤è(€€€€€€€ÑÉäè(€€€€€€€€€€€µ•Ñ…Ímµ˜¹ÍÑ•µt€ô©Í½¸¹±½…‘Ì¡µ˜¹É•…‘}Ñ•áĞ¡•¹½‘¥¹œôÕÑ˜´àœ¤¤(€€€€€€€•á•ÁĞá•ÁÑ¥½¸è(€€€€€€€€€€€Á…ÍÌ(€€€™½ÈÀ¥¸Í½ÉÑ•¡=5%L¹±½ˆ œ¨¹Á¹œœ¤°É•Ù•ÉÍ”õQÉÕ”¥lèĞátè(€€€€€€€´€ôµ•Ñ…Ì¹•Ğ¡À¹ÍÑ•´°íô¤(€€€€€€€Ñ…Ì€ô€œœ¹©½¥¸¡˜œñÍÁ…¸±…ÍÌô‰µ¥¹¤µÑ…œˆøíÑôğ½ÍÁ…¸øœ™½ÈĞ¥¸´¹•Ğ Ñ…Ìœ°mt¥lèÍt¤(€€€€€€€…É¡¥Ù•}…É‘Ì¹…ÁÁ•¹ (€€€€€€€€€€€˜œñ„±…ÍÌô‰…É¡¥Ù”µ…Éˆ¡É•˜ô‰½µ¥Ì½íÀ¹¹…µ•ôˆøñ¥µœÍÉŒô‰½µ¥Ì½íÀ¹¹…µ•ôˆ…±Ğô‰í´¹•Ğ ‰Ñ¥Ñ±”ˆ°À¹ÍÑ•´¥ôˆøœ(€€€€€€€€€€€˜œñ‘¥Ø±…ÍÌô‰…É¡¥Ù”µ½Áäˆøñˆùí´¹•Ğ ‰Ñ¥Ñ±”ˆ°À¹ÍÑ•´¥ôğ½ˆøñÍµ…±°ùíÀ¹ÍÑ•µôğ½Íµ…±°øñÀùí´¹•Ğ ‰ÍÕµµ…Éäˆ°€ˆˆ¥ôğ½Àøñ‘¥ØùíÑ…Íôğ½‘¥Øøğ½‘¥Øøğ½„øœ(€€€€€€€€¤((€€€¡Ñµ°€ô˜œœœğ…‘½ÑåÁ”¡Ñµ°ø(ñ¡Ñµ°±…¹œô‰é µ!…¹Ğˆø(ñ¡•…ø(ñµ•Ñ„¡…ÉÍ•Ğô‰ÕÑ˜´àˆø(ñµ•Ñ„¹…µ”ô‰Ù¥•İÁ½ÉĞˆ½¹Ñ•¹Ğô‰İ¥‘Ñ õ‘•Ù¥”µİ¥‘Ñ °¥¹¥Ñ¥…°µÍ…±”ôÄˆø(ñÑ¥Ñ±”ùíÑ¥Ñ±•ôğ½Ñ¥Ñ±”ø(ñÍÑå±”ø(éÉ½½Ñíì´µ‰œèŒÁˆÁÄĞì´µÍÕÉ™…”èŒÄÈÄØÈĞì´µ±¥¹”èŒÈàÌÄĞäì´µÑ•áĞè˜Å˜Ñ™˜ì´µµÕÑ•èŒå•„áŒÈì´µÁ…Á•Èè˜İ˜İ™„ì´µ…•¹Ğè”Õ™˜äì´µ…•¹ĞÈè™™Ù”Ùõô(©íí‰½àµÍ¥é¥¹œé‰½É‘•Èµ‰½áõô¡Ñµ±ííÍÉ½±°µ‰•¡…Ù¥½ÈéÍµ½½Ñ¡õô‰½‘åííµ…É¥¸èÀí‰…­É½Õ¹éÉ…‘¥…°µÉ…‘¥•¹Ğ¡¥É±”…ĞÑ½À°ŒÈÀÈØĞÀ€À°ŒÄÀÄÌÅ˜€ÌØ”°ŒÀäÁˆÄÈ€ÄÀÀ”¤í½±½ÈéÙ…È ´µÑ•áĞ¤í™½¹Ğµ™…µ¥±äèµ…ÁÁ±”µÍåÍÑ•´±	±¥¹­5…MåÍÑ•µ½¹Ğ°‰M•½”U$ˆ°‰9½Ñ¼M…¹ÌQˆ±Í…¹ÌµÍ•É¥™õô)…íí½±½Èé¥¹¡•É¥Ñõô€ÁÉ½É•ÍÍííÁ½Í¥Ñ¥½¸é™¥á•íÑ½ÀèÀí±•™ĞèÀíİ¥‘Ñ èÄÀÀ”í¡•¥¡ĞèÍÁàí‰…­É½Õ¹è™™™™™˜ÄÈíèµ¥¹‘•àèÄÀÁõôÁÉ½É•ÍÌµ™¥±±íí¡•¥¡ĞèÄÀÀ”íİ¥‘Ñ èÀí‰…­É½Õ¹é±¥¹•…ÈµÉ…‘¥•¹Ğ äÁ‘•œ°”İŒİ™˜°™™Œá‘¤íÑÉ…¹Í¥Ñ¥½¸éİ¥‘Ñ €¸ÀáÌ±¥¹•…Éõô(¹Ñ½Á‰…ÉííÁ½Í¥Ñ¥½¸éÍÑ¥­äíÑ½ÀèÍÁàíèµ¥¹‘•àèÔÀí‰…­‘É½Àµ™¥±Ñ•Èé‰±ÕÈ ÄÙÁà¤í‰…­É½Õ¹èŒÁˆÁÄÑäí‰½É‘•Èµ‰½ÑÑ½´èÅÁàÍ½±¥€™™™™™˜ÄÁõô¹Ñ½Á‰…Èµ¥¹¹•Éííµ…àµİ¥‘Ñ èÄÄÈÁÁàíµ…É¥¸é…ÕÑ¼íÁ…‘‘¥¹œèÄÅÁà€ÄáÁàí‘¥ÍÁ±…äé™±•àí…±¥¸µ¥Ñ•µÌé•¹Ñ•Èí…ÀèÄÑÁáõô¹‰É…¹‘íí™½¹Ğµİ•¥¡ĞèàÀÀíÑ•áĞµ‘•½É…Ñ¥½¸é¹½¹•õô¹•Á¥Í½‘”µ¹…µ•ííµ¥¸µİ¥‘Ñ èÀí½Ù•É™±½Üé¡¥‘‘•¸íÑ•áĞµ½Ù•É™±½Üé•±±¥ÁÍ¥Ìíİ¡¥Ñ”µÍÁ…”é¹½İÉ…Àí½±½ÈéÙ…È ´µµÕÑ•¤í™½¹ĞµÍ¥é”èÄÍÁàí™±•àèÅõô¹©ÕµÁííÑ•áĞµ‘•½É…Ñ¥½¸é¹½¹”íÁ…‘‘¥¹œèİÁà€ÄÅÁàí‰½É‘•ÈèÅÁàÍ½±¥€™™™™™˜Äàí‰½É‘•ÈµÉ…‘¥ÕÌèääåÁàí™½¹ĞµÍ¥é”èÄÉÁàí‰…­É½Õ¹è™™™™™˜Àáõô(¹¡•É½ííµ…àµİ¥‘Ñ èÄÄÈÁÁàíµ…É¥¸èÀ…ÕÑ¼íÁ…‘‘¥¹œèØÉÁà€ÈÁÁà€ĞÑÁàí‘¥ÍÁ±…äéÉ¥íÉ¥µÑ•µÁ±…Ñ”µ½±Õµ¹ÌèÄ¸ÀÕ™Ä€¸äÕ™Èí…ÀèÈáÁàí…±¥¸µ¥Ñ•µÌé•¹‘õô¹•å•‰É½İíí™½¹ĞµÍ¥é”èÄÉÁàí±•ÑÑ•ÈµÍÁ…¥¹œè¸ÄÙ•´í½±½Èè‰ˆİ”Ìí™½¹Ğµİ•¥¡ĞèàÀÁõõ Åíí™½¹ĞµÍ¥é”é±…µÀ ĞáÁà°áÙÜ°àáÁà¤í±¥¹”µ¡•¥¡Ğè¸äí±•ÑÑ•ÈµÍÁ…¥¹œè´¸ÀÙ•´íµ…É¥¸èÄÁÁà€À€ÈÁÁáõô¹¡•É¼Áíí½±½ÈéÙ…È ´µµÕÑ•¤í±¥¹”µ¡•¥¡ĞèÄ¸àÔíµ…àµİ¥‘Ñ èØàÁÁáõô¹Ñ…Ííí‘¥ÍÁ±…äé™±•àí…ÀèåÁàí™±•àµİÉ…ÀéİÉ…Àíµ…É¥¸µÑ½ÀèÈÁÁáõô¹Ñ…œ°¹µ¥¹¤µÑ…íí‘¥ÍÁ±…äé¥¹±¥¹”µ™±•àí‰½É‘•ÈèÅÁàÍ½±¥€™™™™™˜ÄĞí‰…­É½Õ¹è™™™™™˜Ààí‰½É‘•ÈµÉ…‘¥ÕÌèääåÁàíÁ…‘‘¥¹œèİÁà€ÄÅÁàí™½¹ĞµÍ¥é”èÄÉÁàí™½¹Ğµİ•¥¡ĞèÜÀÁõô¹½Ù•Éíí‰½É‘•ÈèÅÁàÍ½±¥€™™™™™˜ÄÈí‰½É‘•ÈµÉ…‘¥ÕÌèÈÙÁàíÁ…‘‘¥¹œèÄÑÁàí‰…­É½Õ¹é±¥¹•…ÈµÉ…‘¥•¹Ğ ÄàÁ‘•œ°™™™™™˜Á„°™™™™™˜ÀĞ¤í‰½àµÍ¡…‘½ÜèÀ€ÈÉÁà€ØÁÁà€ŒÀÀÀİõô¹½Ù•È¥µíí‘¥ÍÁ±…äé‰±½¬íİ¥‘Ñ èÄÀÀ”í‰½É‘•ÈµÉ…‘¥ÕÌèÄáÁàí…ÍÁ•ĞµÉ…Ñ¥¼èÄÀàÀ¼ÄÌÔÀí½‰©•Ğµ™¥Ğé½Ù•Èí½‰©•ĞµÁ½Í¥Ñ¥½¸éÑ½Áõô(¹É•…‘•ÈµÍ¡•±±íí‰…­É½Õ¹éÙ…È ´µÁ…Á•È¤í½±½ÈèŒÄÜÄäÈÈíÁ…‘‘¥¹œèĞÉÁà€À€ÜÑÁàí‰½É‘•ÈµÑ½ÀèÅÁàÍ½±¥€™™™™™˜ÄÀí‰½É‘•Èµ‰½ÑÑ½´èÅÁàÍ½±¥€™™™™™˜ÄÁõô¹•Á¥Í½‘”µ¡•…‘ííİ¥‘Ñ éµ¥¸ àÈÁÁà±…±Œ ÄÀÀ”€´€ÌÉÁà¤¤íµ…É¥¸èÀ…ÕÑ¼€ĞáÁáõô¹•Á¥Í½‘”µ­¥­•Éíí™½¹ĞµÍ¥é”èÄÉÁàí™½¹Ğµİ•¥¡ĞèàÀÀí±•ÑÑ•ÈµÍÁ…¥¹œè¸ÄÉ•´í½±½ÈèŒÜàØàá‘õô¹•Á¥Í½‘”µ¡•… Éíí™½¹ĞµÍ¥é”é±…µÀ ÌÑÁà°ÙÙÜ°ÔáÁà¤í±¥¹”µ¡•¥¡ĞèÄ¸ÀÔíµ…É¥¸èáÁà€À€ÄÉÁàí±•ÑÑ•ÈµÍÁ…¥¹œè´¸ÀÑ•µõô¹•Á¥Í½‘”µ¡•…Áíí½±½ÈèŒØÔØäÜäí±¥¹”µ¡•¥¡ĞèÄ¸ÜÔíµ…É¥¸èÁõô¹İ•‰Ñ½½¸µ½±ííİ¥‘Ñ éµ¥¸ àÈÁÁà°ÄÀÀ”¤íµ…É¥¸èÀ…ÕÑ¼í‘¥ÍÁ±…äé™±•àí™±•àµ‘¥É•Ñ¥½¸é½±Õµ¸í…±¥¸µ¥Ñ•µÌé•¹Ñ•Éõô¹Á…¹•°µ™É…µ•ííµ…É¥¸èÀ€ÀÙ…È ´µ…À¤íİ¥‘Ñ èÄÀÀ”í‘¥ÍÁ±…äé™±•áõô¹Á…¹•°µ™É…µ”¹±•™Ñíí©ÕÍÑ¥™äµ½¹Ñ•¹Ğé™±•àµÍÑ…ÉÑõô¹Á…¹•°µ™É…µ”¹É¥¡Ñíí©ÕÍÑ¥™äµ½¹Ñ•¹Ğé™±•àµ•¹‘õô¹Á…¹•°µ™É…µ”¹•¹Ñ•Éíí©ÕÍÑ¥™äµ½¹Ñ•¹Ğé•¹Ñ•Éõô¹Á…¹•°µ™É…µ”¥µíí‘¥ÍÁ±…äé‰±½¬íİ¥‘Ñ èÄÀÀ”í¡•¥¡Ğé…ÕÑ¼í‰½àµÍ¡…‘½ÜèÀ€ÄÉÁà€ÌÑÁà€ŒÅÈÈÌÈÅõô¹Á…¹•°µ™É…µ”¹¡•É½ííİ¥‘Ñ èÄÀÀ•õô¹Á…¹•°µ™É…µ”¹ÍÕÁÁ½ÉĞµ±•™Ñííİ¥‘Ñ èÜØ•õô¹Á…¹•°µ™É…µ”¹±Õ”µÉ¥¡Ñííİ¥‘Ñ èØÀ•õô¹Á…¹•°µ™É…µ”¹Ñ•¹Í¥½¹ííİ¥‘Ñ èàÈ•õô¹Á…¹•°µ™É…µ”¹É•Ù•…±ííİ¥‘Ñ èÄÀÀ”íµ…É¥¸µ‰½ÑÑ½´èÁõô¹Á…¹•°µ™É…µ”¹É•Ù•…°¥µíí‰½àµÍ¡…‘½ÜèÀ€ÈÁÁà€ĞáÁà€ŒÍŒÈÄÌÔÌÍõô¹½¹Ñ¥¹Õ•ííİ¥‘Ñ éµ¥¸ àÈÁÁà±…±Œ ÄÀÀ”€´€ÌÉÁà¤¤íµ…É¥¸èĞÉÁà…ÕÑ¼€ÀíÁ…‘‘¥¹œèÈáÁàí‰½É‘•ÈµÉ…‘¥ÕÌèÈÉÁàí‰…­É½Õ¹èŒÄØÅ„ÈÜí½±½Èéİ¡¥Ñ”íÑ•áĞµ…±¥¸é•¹Ñ•Éõô¹½¹Ñ¥¹Õ”ÍÑÉ½¹íí‘¥ÍÁ±…äé‰±½¬í™½¹ĞµÍ¥é”èÈÍÁàíµ…É¥¸µ‰½ÑÑ½´èÙÁáõô¹½¹Ñ¥¹Õ”ÍÁ…¹íí½±½Èè…•ˆÙ˜í™½¹ĞµÍ¥é”èÄÍÁáõô(¹…É¡¥Ù”µÍ•Ñ¥½¹ííµ…àµİ¥‘Ñ èÄÄÈÁÁàíµ…É¥¸é…ÕÑ¼íÁ…‘‘¥¹œèÔáÁà€ÈÁÁà€àÙÁáõô¹…É¡¥Ù”µÑ¥Ñ±•íí‘¥ÍÁ±…äé™±•àí…±¥¸µ¥Ñ•µÌé•¹í©ÕÍÑ¥™äµ½¹Ñ•¹ĞéÍÁ…”µ‰•Ñİ••¸í…ÀèÄÑÁàíµ…É¥¸µ‰½ÑÑ½´èÄáÁáõô¹…É¡¥Ù”µÑ¥Ñ±” Ííí™½¹ĞµÍ¥é”èÌÁÁàíµ…É¥¸èÁõô¹…É¡¥Ù”µÑ¥Ñ±”Áííµ…É¥¸èÀí½±½ÈéÙ…È ´µµÕÑ•¤í™½¹ĞµÍ¥é”èÄÍÁáõô¹…É¡¥Ù”µÉ¥‘íí‘¥ÍÁ±…äéÉ¥íÉ¥µÑ•µÁ±…Ñ”µ½±Õµ¹ÌéÉ•Á•…Ğ¡…ÕÑ¼µ™¥±°±µ¥¹µ…à ÈĞÁÁà°Å™È¤¤í…ÀèÄÙÁáõô¹…É¡¥Ù”µ…É‘ííÑ•áĞµ‘•½É…Ñ¥½¸é¹½¹”í‰…­É½Õ¹è™™™™™˜Ààí‰½É‘•ÈèÅÁàÍ½±¥€™™™™™˜ÄÈí‰½É‘•ÈµÉ…‘¥ÕÌèÈÁÁàí½Ù•É™±½Üé¡¥‘‘•¸íÑÉ…¹Í¥Ñ¥½¸è¸ÄáÍõô¹…É¡¥Ù”µ…Éé¡½Ù•ÉííÑÉ…¹Í™½É´éÑÉ…¹Í±…Ñ•d ´ÑÁà¤í‰½É‘•Èµ½±½ÈèŒİŒàİ…õô¹…É¡¥Ù”µ…É¥µíí‘¥ÍÁ±…äé‰±½¬íİ¥‘Ñ èÄÀÀ”í…ÍÁ•ĞµÉ…Ñ¥¼èÌ¼Ğí½‰©•Ğµ™¥Ğé½Ù•Èí½‰©•ĞµÁ½Í¥Ñ¥½¸éÑ½Àí‰…­É½Õ¹è™™™õô¹…É¡¥Ù”µ½ÁåííÁ…‘‘¥¹œèÄÑÁà€ÄÑÁà€ÄİÁáõô¹…É¡¥Ù”µ½Áä‰íí‘¥ÍÁ±…äé‰±½¬í™½¹ĞµÍ¥é”èÄİÁàíµ…É¥¸µ‰½ÑÑ½´èÕÁáõô¹…É¡¥Ù”µ½ÁäÍµ…±±íí‘¥ÍÁ±…äé‰±½¬í½±½ÈéÙ…È ´µµÕÑ•¤íµ…É¥¸µ‰½ÑÑ½´èåÁáõô¹…É¡¥Ù”µ½ÁäÁíí™½¹ĞµÍ¥é”èÄÍÁàí±¥¹”µ¡•¥¡ĞèÄ¸Øí½±½Èè‘™”Õ˜Ôíµ…É¥¸èÀ€À€ÄÅÁáõõ™½½Ñ•ÉííÑ•áĞµ…±¥¸é•¹Ñ•Èí½±½ÈéÙ…È ´µµÕÑ•¤í™½¹ĞµÍ¥é”èÄÉÁàíÁ…‘‘¥¹œèÀ€ÈÁÁà€ÌÙÁáõô)µ•‘¥„¡µ…àµİ¥‘Ñ èàÈÁÁà¥íì¹¡•É½ííÉ¥µÑ•µÁ±…Ñ”µ½±Õµ¹ÌèÅ™ÈíÁ…‘‘¥¹œµÑ½ÀèĞÑÁáõô¹½Ù•Éííµ…àµİ¥‘Ñ èÔÈÁÁáõô¹İ•‰Ñ½½¸µ½±ííİ¥‘Ñ èÄÀÀ•õô¹Á…¹•°µ™É…µ”¹ÍÕÁÁ½ÉĞµ±•™Ñííİ¥‘Ñ èàÈ•õô¹Á…¹•°µ™É…µ”¹±Õ”µÉ¥¡Ñííİ¥‘Ñ èØà•õô¹Á…¹•°µ™É…µ”¹Ñ•¹Í¥½¹ííİ¥‘Ñ èàà•õõõõµ•‘¥„¡µ…àµİ¥‘Ñ èÔØÁÁà¥íì¹Ñ½Á‰…Èµ¥¹¹•ÉííÁ…‘‘¥¹œèåÁà€ÄÉÁáõô¹¡•É½ííÁ…‘‘¥¹œµ±•™ĞèÄÙÁàíÁ…‘‘¥¹œµÉ¥¡ĞèÄÙÁáõô¹É•…‘•ÈµÍ¡•±±ííÁ…‘‘¥¹œµÑ½ÀèÌÁÁáõô¹Á…¹•°µ™É…µ”¹ÍÕÁÁ½ÉĞµ±•™Ñííİ¥‘Ñ èàà•õô¹Á…¹•°µ™É…µ”¹±Õ”µÉ¥¡Ñííİ¥‘Ñ èÜØ•õô¹Á…¹•°µ™É…µ”¹Ñ•¹Í¥½¹ííİ¥‘Ñ èäĞ•õõõµ•‘¥„¡ÁÉ•™•ÉÌµÉ•‘Õ•µµ½Ñ¥½¸éÉ•‘Õ”¥íí¡Ñµ±ííÍÉ½±°µ‰•¡…Ù¥½Èé…ÕÑ½õô©ííÑÉ…¹Í¥Ñ¥½¸é¹½¹”…¥µÁ½ÉÑ…¹Ñõõõô(ğ½ÍÑå±”ø(ğ½¡•…ø(ñ‰½‘äø(ñ‘¥Ø¥ô‰ÁÉ½É•ÍÌˆøñ‘¥Ø¥ô‰ÁÉ½É•ÍÌµ™¥±°ˆøğ½‘¥Øøğ½‘¥Øø(ñ¹…Ø±…ÍÌô‰Ñ½Á‰…Èˆøñ‘¥Ø±…ÍÌô‰Ñ½Á‰…Èµ¥¹¹•Èˆøñ„±…ÍÌô‰‰É…¹ˆ¡É•˜ôˆÑ½ÀˆùíÑ¥Ñ±•ôğ½„øñÍÁ…¸±…ÍÌô‰•Á¥Í½‘”µ¹…µ”ˆùí±…Ñ•ÍÑ}µ•Ñ…lÑ¥Ñ±”uôƒ
Üí±…Ñ•ÍÑ}‘…åôğ½ÍÁ…¸øñ„±…ÍÌô‰©ÕµÀˆ¡É•˜ôˆ…É¡¥Ù”ˆû¦¢ò'–ê¬ğ½„øğ½‘¥Øøğ½¹…Øø(ñ¡•…‘•È±…ÍÌô‰¡•É¼ˆ¥ô‰Ñ½Àˆøñ‘¥Øøñ‘¥Ø±…ÍÌô‰•å•‰É½Üˆù%1dYIQ%0=5%ğ½‘¥Øøñ ÄùíÑ¥Ñ±•ôğ½ ÄøñÀùíÍÕ‰Ñ¥Ñ±•ôñ‰ÈûšZÃ&#š:‡R£’â7¶'–¾³–"¦>‡šW–¾»–'–Ş›–>Ï–?ï¢"šîÿ&#š>·¦rËš‚ó¾ò3¢ºO¦ZÇ¢º¦–ê›šr³¢ê¯’æš"C
ë–*šj’â¦£–"ğ½Àøñ‘¥Ø±…ÍÌô‰Ñ…Ìˆùí±…Ñ•ÍÑ}Ñ…Íôğ½‘¥Øøğ½‘¥Øøñ„±…ÍÌô‰½Ù•Èˆ¡É•˜ôˆÉ•…‘•Èˆøñ¥µœÍÉŒô‰±…Ñ•ÍĞ¹Á¹œˆ…±Ğô‰í±…Ñ•ÍÑ}µ•Ñ…lÑ¥Ñ±”uôˆøğ½„øğ½¡•…‘•Èø(ñµ…¥¸±…ÍÌô‰É•…‘•ÈµÍ¡•±°ˆ¥ô‰É•…‘•ÈˆøñÍ•Ñ¥½¸±…ÍÌô‰•Á¥Í½‘”µ¡•…ˆøñ‘¥Ø±…ÍÌô‰•Á¥Í½‘”µ­¥­•Èˆù1QMPA%M=ƒ
Üí±…Ñ•ÍÑ}‘…åôğ½‘¥Øøñ Èùí±…Ñ•ÍÑ}µ•Ñ…lÑ¥Ñ±”uôğ½ ÈøñÀùí±…Ñ•ÍÑ}µ•Ñ…lÍÕµµ…Éäuôğ½Àøğ½Í•Ñ¥½¸øñÍ•Ñ¥½¸±…ÍÌô‰İ•‰Ñ½½¸µ½°ˆùìœœ¹©½¥¸¡™¥ÕÉ•Ì¥ôğ½Í•Ñ¥½¸øñ‘¥Ø±…ÍÌô‰½¹Ñ¥¹Õ”ˆøñÍÑÉ½¹œû’â/–n{–úê0ğ½ÍÑÉ½¹œøñÍÁ…¸ûšb;–’¤€ÀàèÌÀƒ¢«–.WšnÓšZÃ’â/’â–/¦&“–¶@ğ½ÍÁ…¸øğ½‘¥Øøğ½µ…¥¸ø(ñÍ•Ñ¥½¸±…ÍÌô‰…É¡¥Ù”µÍ•Ñ¥½¸ˆ¥ô‰…É¡¥Ù”ˆøñ‘¥Ø±…ÍÌô‰…É¡¥Ù”µÑ¥Ñ±”ˆøñ‘¥Øøñ Ìû¦¢ò'šªSš†#–ê¬ğ½ ÌøñÀûš2'š^—šr’şwVgš¾?–’§R‹Rj¾®€ğ½Àøğ½‘¥Øøğ½‘¥Øøñ‘¥Ø±…ÍÌô‰…É¡¥Ù”µÉ¥ˆùìœœ¹©½¥¸¡…É¡¥Ù•}…É‘Ì¥ôğ½‘¥Øøğ½Í•Ñ¥½¸ø(ñ™½½Ñ•Èù…¥±ä½µ¥Œƒ
Ü¥Ñ!ÕˆA…•Ìğ½™½½Ñ•Èø(ñÍÉ¥ÁĞø)½¹ÍĞ™¥±°õ‘½Õµ•¹Ğ¹•Ñ±•µ•¹Ñ	å% ÁÉ½É•ÍÌµ™¥±°œ¤ì)™Õ¹Ñ¥½¸ÕÁ‘…Ñ•AÉ½É•ÍÌ ¥íí½¹ÍĞµ…àõ‘½Õµ•¹Ğ¹‘½Õµ•¹Ñ±•µ•¹Ğ¹ÍÉ½±±!•¥¡Ğµ¥¹¹•É!•¥¡Ğí½¹ÍĞÀõµ…àøÀıÍÉ½±±d½µ…àèÀí™¥±°¹ÍÑå±”¹İ¥‘Ñ ô¡À¨ÄÀÀ¤¹Ñ½¥á• È¤¬œ”œíõô)…‘‘Ù•¹Ñ1¥ÍÑ•¹•È ÍÉ½±°œ±ÕÁ‘…Ñ•AÉ½É•ÍÌ±ííÁ…ÍÍ¥Ù”éÑÉÕ•õô¤í…‘‘Ù•¹Ñ1¥ÍÑ•¹•È É•Í¥é”œ±ÕÁ‘…Ñ•AÉ½É•ÍÌ¤íÕÁ‘…Ñ•AÉ½É•ÍÌ ¤ì(ğ½ÍÉ¥ÁĞø(ğ½‰½‘äøğ½¡Ñµ°øœœœ(€€€€¡=L€¼€¥¹‘•à¹¡Ñµ°œ¤¹İÉ¥Ñ•}Ñ•áĞ¡¡Ñµ°°•¹½‘¥¹œôÕÑ˜´àœ¤(()‘•˜µ…¥¸ ¤è(€€€½¹™¥œ€ôå…µ°¹Í…™•}±½…¡¹É•…‘}Ñ•áĞ¡•¹½‘¥¹œôÕÑ˜´àœ¤¤(€€€‘…ä€ô‘…Ñ•Ñ¥µ”¹¹½Ü¡QA¤¹ÍÑÉ™Ñ¥µ” œ•d´•´´•œ¤(€€€¡¥ÍĞ€ô±½…‘}¡¥ÍÑ½Éä ¤(€€€ÍÑ½Éä€ô¡½½Í•}ÍÑ½Éä¡‘…ä°¡¥ÍĞ¤((€€€=5%L¹µ­‘¥È¡Á…É•¹ÑÌõQÉÕ”°•á¥ÍÑ}½¬õQÉÕ”¤(€€€•Á¥Í½‘•}‘¥È€ôA%M=L€¼‘…ä(€€€Í¡ÕÑ¥°¹ÉµÑÉ•”¡•Á¥Í½‘•}‘¥È°¥¹½É•}•ÉÉ½ÉÌõQÉÕ”¤(€€€•Á¥Í½‘•}‘¥È¹µ­‘¥È¡Á…É•¹ÑÌõQÉÕ”°•á¥ÍÑ}½¬õQÉÕ”¤((€€€Á…¹•±}Á…Ñ¡Ì€ômt(€€€™½È¤¥¸É…¹” Ä°A91L€¬€Ä¤è(€€€€€€€½ÕĞ€ô•Á¥Í½‘•}‘¥È€¼˜Á…¹•°µí¥ô¹Á¹œœ(€€€€€€€µ…­•}Á…¹•°¡ÍÑ½Éä°¤°½ÕĞ°‘…ä¤(€€€€€€€Á…¹•±}Á…Ñ¡Ì¹…ÁÁ•¹¡½ÕĞ¤((€€€Í¡…É•}Á¹œ€ô=5%L€¼˜í‘…åô¹Á¹œœ(€€€½µÁ½Í•}Í¡…É”¡ÍÑ½Éä°Á…¹•±}Á…Ñ¡Ì°Í¡…É•}Á¹œ°‘…ä¤((€€€µ•Ñ„€ôì(€€€€€€€€Ñ¥Ñ±”œèÍÑ½ÉålÑ¥Ñ±”t°(€€€€€€€€Ñ¡•µ”œèÍÑ½ÉålÑ¡•µ”t°(€€€€€€€€ÍÕµµ…ÉäœèÍÑ½ÉålÍÕµµ…Éät°(€€€€€€€€Ñ…ÌœèÍÑ½ÉålÑ…Ìt°(€€€€€€€€‘…Ñ”œè‘…ä°(€€€€€€€€•¹•É…Ñ½Èœè€İ•‰Ñ½½¸µ±…å½ÕĞµØĞœ°(€€€€€€€€±…å½ÕĞœèmÍÁ•l¹…µ”t™½ÈÍÁ•Œ¥¸1e=UQMt°(€€€€€€€€Á…¹•±Ìœèl(€€€€€€€€€€€ìÍ•¹”œèÍ•¹”°€µ½½œèµ½½°€‘¥…±½Õ”œè‘¥…±½Õ”°€…ÁÑ¥½¸œè…ÁÑ¥½¹ô(€€€€€€€€€€€™½ÈÍ•¹”°µ½½°‘¥…±½Õ”°…ÁÑ¥½¸¥¸ÍÑ½ÉålÁ…¹•±Ìt(€€€€€€€t°(€€€ô(€€€€¡=5%L€¼˜í‘…åô¹©Í½¸œ¤¹İÉ¥Ñ•}Ñ•áĞ¡©Í½¸¹‘ÕµÁÌ¡µ•Ñ„°•¹ÍÕÉ•}…Í¥¤õ…±Í”°¥¹‘•¹ĞôÈ¤°•¹½‘¥¹œôÕÑ˜´àœ¤(€€€€¡=L€¼€±…Ñ•ÍĞ¹©Í½¸œ¤¹İÉ¥Ñ•}Ñ•áĞ¡©Í½¸¹‘ÕµÁÌ¡µ•Ñ„°•¹ÍÕÉ•}…Í¥¤õ…±Í”°¥¹‘•¹ĞôÈ¤°•¹½‘¥¹œôÕÑ˜´àœ¤(€€€Í¡ÕÑ¥°¹½Áå™¥±”¡Í¡…É•}Á¹œ°=L€¼€±…Ñ•ÍĞ¹Á¹œœ¤((€€€¡¥ÍĞ¹…ÁÁ•¹¡ì‘…Ñ”œè‘…ä°€Ñ¥Ñ±”œèÍÑ½ÉålÑ¥Ñ±”t°€Ñ¡•µ”œèÍÑ½ÉålÑ¡•µ”uô¤(€€€Í…Ù•}¡¥ÍÑ½Éä¡¡¥ÍĞ¤(€€€‰Õ¥±‘}¥¹‘•à¡½¹™¥œ°µ•Ñ„¤(€€€ÁÉ¥¹Ğ •¹•É…Ñ•œ°Í¡…É•}Á¹œ¤(()¥˜}}¹…µ•}|€ôô€}}µ…¥¹}|œè(€€€µ…¥¸ ¤(