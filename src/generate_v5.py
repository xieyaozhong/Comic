# -*- coding: utf-8 -*-
import json, re, urllib.request
from PIL import ImageDraw
import generate_v4 as core

CURRENT_GENRE = 'romance'

STORIES = [
    {
        'genre':'romance','theme':'成熟戀愛','keys':['romance','adult'],
        'title':'別在離婚後才說愛我',
        'summary':'簽完離婚協議那晚，她第一次聽見丈夫說「不要走」；可門外已經有人替她拿好了行李。',
        'tags':['大人系','婚姻','情感','鉤子'],
        'p':[
            ('office','徐允：簽完了，我明天搬走。','桌上的兩杯咖啡都已經冷掉'),
            ('paper','海準：妳真的一次都不問原因？','他第一次避開她的視線'),
            ('lift','徐允：現在才說，太晚了。','電梯門就在這時打開'),
            ('roof','陌生男人：徐小姐，我來接妳。','海準的表情瞬間僵住'),
            ('hook','海準：他怎麼會知道妳住這裡？','男人手上拿著他們結婚當天的照片')]
    },
    {
        'genre':'romance','theme':'職場曖昧','keys':['romance','adult'],
        'title':'只限今晚的男朋友',
        'summary':'為了躲過前任的婚宴，她臨時找上公司最難接近的人假扮男友；但他早就準備好了戒指盒。',
        'tags':['愛情','職場','曖昧','反轉'],
        'p':[
            ('office','閔夏：拜託，只要陪我去一晚。','她把婚宴邀請函推到他面前'),
            ('paper','海準：假男友要做到什麼程度？','他沒有笑，只慢慢扣好袖扣'),
            ('lift','閔夏：牽手就夠了吧？','電梯門開了，他卻沒有放手'),
            ('roof','前任：你們什麼時候開始的？','所有人都在等她回答'),
            ('hook','海準：不是開始，是我等她很久了。','他掌心藏著一只戒指盒')]
    },
    {
        'genre':'school','theme':'校園秘密','keys':['school','drama'],
        'title':'全班只有我看得到她',
        'summary':'轉學生坐在最後一排整整一週，所有人卻堅持那張座位一直是空的。',
        'tags':['校園','青春','秘密','懸疑'],
        'p':[
            ('hall','徐允：老師，新同學不用點名嗎？','全班突然安靜'),
            ('phone','老師：哪來的新同學？','最後一排的女孩抬頭看向她'),
            ('night','訊息：不要再跟我說話。','發件人名稱顯示「不存在」'),
            ('stairs','閔夏：妳是不是坐過最後一排？','她手腕上有一模一樣的紅線'),
            ('hook','徐允：畢業照裡的人……是妳？','照片年份是十二年前')]
    },
    {
        'genre':'school','theme':'社群戀愛','keys':['school','romance'],
        'title':'匿名告白帳號只追蹤我',
        'summary':'學校爆紅的匿名告白帳號每天只發一句話，直到她發現所有內容都在預告自己的明天。',
        'tags':['校園','戀愛','社群','懸念'],
        'p':[
            ('hall','徐允：這帳號今天又爆了。','貼文只有一句：她會穿藍色外套'),
            ('phone','新貼文：午休，她會拒絕一個人。','配圖竟是她的桌角'),
            ('cafe','同學：徐允，我喜歡妳。','她腦中只剩那句預告'),
            ('stairs','徐允：到底是誰在拍我？','走廊盡頭只有一支遺落手機'),
            ('hook','螢幕：下一篇——她今晚不會回家。','帳號正在輸入中')]
    },
    {
        'genre':'martial','theme':'回歸武俠','keys':['martial','fantasy','action'],
        'title':'被逐出師門那天，我重生了',
        'summary':'前世被廢武功逐出山門的弟子醒回入門第一天，這一次他決定先找到真正背叛宗門的人。',
        'tags':['武俠','回歸','成長','爽感'],
        'p':[
            ('rain','海準：這裡是……入門考核？','掌心還記得斷劍刺穿的痛'),
            ('room','長老：最後一名，逐出山門。','前世的仇人正站在第一排'),
            ('alley','海準：那就從第一招重新來。','木劍出鞘，所有人都笑了'),
            ('stage','弟子：怎麼可能只用一招？','劍風切斷場邊三盞燈'),
            ('hook','海準：前世偷走祕卷的人，是你。','長老袖口露出他熟悉的血印')]
    },
    {
        'genre':'martial','theme':'奇幻成長','keys':['fantasy','action'],
        'title':'最弱獵人今天不想升級',
        'summary':'被所有人認定最弱的獵人突然看見只有自己能讀的「拒絕升級」任務，而獎勵是改寫一次死亡。',
        'tags':['奇幻冒險','成長','系統','反轉'],
        'p':[
            ('night','系統：完成副本即可升至 2 級。','所有人都在等他按確認'),
            ('phone','海準：我拒絕。','系統畫面第一次變成紅色'),
            ('alley','隊友：你瘋了？怪物來了！','出口在身後直接封死'),
            ('stage','系統：隱藏條件已達成。','獎勵不是經驗，而是一個名字'),
            ('hook','海準：這是……昨天死掉的人？','名單最下面，還有他自己的名字')]
    },
    {
        'genre':'thriller','theme':'社群驚悚','keys':['thriller','horror'],
        'title':'右滑之後，她消失了',
        'summary':'朋友逼她玩一款沒有上架紀錄的交友 App；每次右滑，現實裡就會少一個人。',
        'tags':['驚悚','社群','都市','懸疑'],
        'p':[
            ('night','閔夏：這 App 為什麼搜尋不到？','圖示是一張沒有五官的臉'),
            ('phone','配對成功：距離 3 公尺。','房間裡明明只有她一個人'),
            ('hall','閔夏：徐允？妳還在線嗎？','好友聊天室突然只剩空白'),
            ('alley','系統：再右滑一次，即可找回她。','螢幕出現徐允的照片'),
            ('hook','閔夏：這不是徐允……','照片背景裡，真正的徐允正在敲玻璃')]
    },
    {
        'genre':'thriller','theme':'身份懸疑','keys':['thriller','drama'],
        'title':'醒來後，所有人都叫我兇手',
        'summary':'他在醫院醒來失去三天記憶，所有人都說他殺了一個人；只有手機裡的自己說別相信任何人。',
        'tags':['驚悚','身份','記憶','反轉'],
        'p':[
            ('night','海準：我只是睡了一覺吧？','手腕卻被銬住'),
            ('paper','刑警：你殺了人。','時間是三天前的凌晨'),
            ('phone','影片中的海準：醒來後不要相信徐允。','影片拍攝時間是今晚 23:40'),
            ('hall','徐允：你終於醒了。','現在才下午四點'),
            ('hook','海準：那這段影片是誰拍的？','監視器裡，另一個他正走近病房')]
    }
]

LAYOUTS = {
    'romance':[('hero',1080,740,'center',120),('support',760,640,'right',180),('clue',620,520,'left',120),('tension',900,660,'center',190),('reveal',1080,850,'center',0)],
    'school':[('hero',1080,690,'center',90),('support',650,560,'right',140),('clue',760,610,'left',110),('tension',880,650,'center',160),('reveal',1080,810,'center',0)],
    'martial':[('hero',1080,730,'center',70),('support',920,610,'left',80),('clue',690,540,'right',65),('tension',990,690,'center',95),('reveal',1080,850,'center',0)],
    'thriller':[('hero',1080,660,'center',180),('support',700,580,'left',190),('clue',610,510,'right',220),('tension',860,650,'center',220),('reveal',1080,890,'center',0)]
}

PALETTES = {
    'romance': {'office':((238,226,222),(202,210,226)),'paper':((242,232,233),(217,218,229)),'lift':((210,211,220),(237,235,239)),'roof':((148,158,178),(224,218,224)),'hook':((108,76,92),(183,133,153))},
    'school': {'hall':((225,238,249),(180,208,233)),'phone':((32,38,55),(105,126,157)),'night':((43,50,86),(105,126,178)),'stairs':((126,147,175),(209,220,234)),'cafe':((239,221,199),(248,239,222)),'hook':((73,75,101),(150,126,165))},
    'martial': {'rain':((72,79,88),(153,163,166)),'room':((225,217,202),(185,190,181)),'alley':((88,95,97),(166,173,166)),'stage':((92,79,76),(185,157,132)),'night':((58,65,70),(122,135,137)),'phone':((31,37,42),(86,99,101)),'hook':((70,62,60),(145,95,84))},
    'thriller': {'night':((33,38,54),(84,91,111)),'phone':((20,23,34),(69,77,99)),'hall':((87,100,120),(145,156,173)),'alley':((50,58,72),(103,114,132)),'paper':((89,88,96),(148,141,146)),'hook':((67,29,38),(139,54,64))}
}


def trend_scores():
    scores = {'romance':1,'school':1,'martial':1,'thriller':1}
    terms = {
        'romance':['愛情','大人系','戀愛','婚姻','romance'],
        'school':['校園','青春','學校','school'],
        'martial':['武俠','奇幻冒險','回歸','獵人','action','fantasy'],
        'thriller':['驚悚','恐怖','懸疑','thriller','horror']
    }
    for url in ['https://www.webtoons.com/zh-hant/','https://www.webtoons.com/zh-hant/ranking/popular']:
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 DailyComicBot/5.0'})
            text = urllib.request.urlopen(req, timeout=8).read(500000).decode('utf-8','ignore').lower()
            text = re.sub(r'<[^>]+>', ' ', text)
            for key, words in terms.items():
                scores[key] += sum(text.count(word.lower()) for word in words)
        except Exception as exc:
            print('trend fallback', type(exc).__name__)
    return scores


def choose(day, history):
    global CURRENT_GENRE
    recent = {x.get('theme') for x in history[-10:]}
    pool = [x for x in STORIES if x['theme'] not in recent] or STORIES
    scores = trend_scores()
    weighted = []
    for story in pool:
        weighted += [story] * max(1, min(80, scores.get(story['genre'], 1)))
    pick = core.sd(day).choice(weighted)
    CURRENT_GENRE = pick['genre']
    core.LAY = LAYOUTS[CURRENT_GENRE]
    core.COL.update(PALETTES[CURRENT_GENRE])
    print('zh-hant trend', scores, '=>', CURRENT_GENRE, pick['theme'])
    return pick


def person(draw, x, y, hair, coat, mood='calm', s=1.0):
    # Original simplified characters, but with taller body proportions and cleaner webtoon-like silhouettes.
    skin=(247,220,200); outline=(40,43,52)
    if CURRENT_GENRE=='martial': coat=(68,73,77)
    elif CURRENT_GENRE=='thriller': coat=(78,82,96)
    elif CURRENT_GENRE=='romance': coat=(232,230,235) if x < 520 else (48,52,63)
    elif CURRENT_GENRE=='school': coat=(230,236,248) if x < 520 else (176,198,225)
    # longer legs / narrower torso
    draw.ellipse((x-82*s,y+315*s,x+82*s,y+345*s),fill=(0,0,0,22))
    draw.line((x-18*s,y+220*s,x-23*s,y+380*s),fill=(57,61,77),width=max(8,int(11*s)))
    draw.line((x+18*s,y+220*s,x+23*s,y+380*s),fill=(57,61,77),width=max(8,int(11*s)))
    core.rr(draw,(x-54*s,y+92*s,x+54*s,y+252*s),int(24*s),coat)
    draw.rectangle((x-11*s,y+70*s,x+11*s,y+103*s),fill=skin)
    draw.ellipse((x-46*s,y-18*s,x+46*s,y+92*s),fill=skin)
    draw.pieslice((x-54*s,y-33*s,x+54*s,y+69*s),180,360,fill=hair)
    core.rr(draw,(x-50*s,y-7*s,x+50*s,y+31*s),int(16*s),hair)
    ey=y+41*s; ex=18*s
    if mood in {'shock','fear','panic','hook'}:
        for dx in (-ex,ex): draw.ellipse((x+dx-7*s,ey-4*s,x+dx+7*s,ey+11*s),fill='white',outline=outline,width=2)
    else:
        draw.line((x-ex-8*s,ey+4*s,x-ex+8*s,ey+4*s),fill=outline,width=max(2,int(3*s)))
        draw.line((x+ex-8*s,ey+4*s,x+ex+8*s,ey+4*s),fill=outline,width=max(2,int(3*s)))
    draw.line((x-10*s,y+70*s,x+10*s,y+69*s),fill=outline,width=max(2,int(3*s)))
    if CURRENT_GENRE=='martial':
        draw.line((x-48*s,y+135*s,x-118*s,y+105*s),fill=coat,width=max(9,int(13*s)))
        draw.line((x+48*s,y+135*s,x+126*s,y+90*s),fill=coat,width=max(9,int(13*s)))
        draw.line((x+105*s,y+92*s,x+210*s,y+18*s),fill=(48,49,53),width=max(3,int(5*s)))
    else:
        draw.line((x-48*s,y+135*s,x-82*s,y+178*s),fill=coat,width=max(9,int(13*s)))
        draw.line((x+48*s,y+135*s,x+82*s,y+178*s),fill=coat,width=max(9,int(13*s)))


def face(draw, x, y, hair, mood='calm', scale=1.0):
    skin=(247,220,200); outline=(39,42,50); r=105*scale
    draw.ellipse((x-r*.62,y-r*.58,x+r*.62,y+r*.82),fill=skin)
    draw.pieslice((x-r*.70,y-r*.72,x+r*.70,y+r*.48),180,360,fill=hair)
    core.rr(draw,(x-r*.67,y-r*.42,x+r*.67,y-r*.04),int(17*scale),hair)
    ey=y+6*scale; ex=36*scale
    if mood=='shock':
        for dx in (-ex,ex): draw.ellipse((x+dx-9*scale,ey-5*scale,x+dx+9*scale,ey+13*scale),fill='white',outline=outline,width=2)
    else:
        draw.line((x-ex-10*scale,ey+3*scale,x-ex+10*scale,ey+3*scale),fill=outline,width=max(2,int(3*scale)))
        draw.line((x+ex-10*scale,ey+3*scale,x+ex+10*scale,ey+3*scale),fill=outline,width=max(2,int(3*scale)))
    draw.line((x-15*scale,y+51*scale,x+14*scale,y+49*scale),fill=outline,width=max(2,int(3*scale)))


def panel(st, i, out, day):
    scene, dialog, cap = st['p'][i-1]
    im = core.bg(scene, i, day)
    draw = ImageDraw.Draw(im, 'RGBA')
    genre = st['genre']
    if genre=='romance' and i in {2,3}:
        face(draw,330,285,(61,45,65),'calm',1.22)
        face(draw,760,300,(38,48,73),'calm',1.08)
        if i==3:
            draw.ellipse((482,390,548,456),fill=(247,220,200,255)); draw.ellipse((535,395,601,461),fill=(247,220,200,255)); draw.line((520,440,578,440),fill=(118,85,98),width=4)
    else:
        mood='shock' if i in (2,4,5) else 'calm'
        person(draw,290 if i%2 else 760,220,(61,45,65),(228,233,246),mood,1.18)
        person(draw,770 if i%2 else 285,250,(38,48,73),(177,203,221),'calm',1.03)
    if genre=='martial' and i in {2,3,4}:
        for n in range(12): draw.line((50+n*85,190,280+n*70,45),fill=(255,255,255,75),width=2)
    if genre=='school' and i==2:
        core.rr(draw,(720,110,1000,330),28,(247,249,253,235),(110,120,145),2)
        draw.text((752,145),'匿名訊息',font=core.ft(24,1),fill=(40,44,56))
        draw.text((752,195),'新通知  1',font=core.ft(22),fill=(78,86,102))
    if genre=='thriller' and i==5:
        draw.rectangle((0,0,14,core.HGT),fill=(166,43,55,230))
    core.rr(draw,(38,30,235,75),18,(20,22,32,230))
    draw.text((54,40),f'EP {day[5:].replace("-",".")} · {i}',font=core.ft(23,1),fill='white')
    tw=draw.textbbox((0,0),cap,font=core.ft(24,1))[2]
    core.rr(draw,(38,88,70+tw,132),18,(255,255,255,235))
    draw.text((54,97),cap,font=core.ft(24,1),fill=(37,42,58))
    dark=i==5; fill=(29,31,43) if dark else (255,255,255); color='white' if dark else (28,31,40)
    core.rr(draw,(48,core.HGT-218,core.W-48,core.HGT-40),27,fill,(82,87,107),2)
    who,said=dialog.split('：',1) if '：' in dialog else ('旁白',dialog)
    draw.text((72,core.HGT-198),who,font=core.ft(27,1),fill=color); yy=core.HGT-158
    for line in core.wrap(draw,said,core.ft(26),core.W-150):
        draw.text((72,yy),line,font=core.ft(26),fill=color); yy+=35
    if dark: draw.text((core.W-175,34),'下回待續',font=core.ft(28,1),fill=(255,248,252,230))
    im.save(out)

core.ST = STORIES
core.trends = trend_scores
core.choose = choose
core.person = person
core.panel = panel

if __name__ == '__main__':
    core.main()
    # Mark the new generator in metadata; this field is not displayed on the site.
    latest_path = core.D/'latest.json'
    if latest_path.exists():
        meta = json.loads(latest_path.read_text(encoding='utf-8'))
        meta['generator'] = 'webtoon-zh-trend-v5'
        meta['genre'] = CURRENT_GENRE
        latest_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
        archive_meta = core.C/f"{meta['date']}.json"
        if archive_meta.exists():
            archive_meta.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
