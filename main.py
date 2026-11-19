"""Thursday 19 November 2026 - The World In One Day.

A 1024x1024 broadsheet drawn procedurally with Pillow: masthead, region
bar, numbers strip, 3 lead cards, 10 small cards, a world map with pins
1-13, 27 one-line briefs, a DATE CHECK footer and a sources line.
40 stories, all from Thursday 19 November 2026. Deterministic, no
network. Writes the image to MAKEFUN_OUTPUT_DIR/entry.png (default
/output/entry.png). If Pillow is unavailable it copies the committed
entry.png beside this file, which this same program generated.
"""
import os
import shutil
import sys

W = 1024
H = 1024

BG = (248, 242, 220)
PAPER = (252, 249, 238)
INK = (22, 22, 22)
MUTED = (92, 84, 70)
RED = (176, 42, 30)
DARKRED = (140, 30, 22)
NAVY = (24, 42, 74)
GOLD = (196, 148, 32)
CREAM_LINE = (120, 108, 84)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"
COND_R = "/usr/share/fonts/truetype/noto/NotoSans-Condensed.ttf"
COND_B = "/usr/share/fonts/truetype/noto/NotoSans-CondensedBold.ttf"

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        from PIL import ImageFont
        try:
            _font_cache[key] = ImageFont.truetype(path, size)
        except Exception:
            _font_cache[key] = ImageFont.truetype(SANS_R, size)
    return _font_cache[key]


def tw(draw, text, font):
    return draw.textlength(text, font=font)


def fit_size(draw, text, path, start, max_w, minimum=8):
    size = start
    while size > minimum:
        if tw(draw, text, F(path, size)) <= max_w:
            return size
        size -= 1
    return minimum


def wrap(draw, text, font, max_w, max_lines=4):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if tw(draw, trial, font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines:
        # mark truncation with an ellipsis only when words remain
        joined = " ".join(lines)
        if len(joined) < len(text):
            lines[-1] = lines[-1].rstrip(" .,;:") + "…"
    return lines


def draw_lines(draw, x, y, lines, font, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def num_badge(draw, x, y, n, fill, r=9):
    draw.ellipse([x, y, x + 2 * r, y + 2 * r], fill=fill)
    f = F(SANS_B, 11 if n < 10 else 10)
    t = str(n)
    w = tw(draw, t, f)
    draw.text((x + r - w / 2, y + r - 6), t, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- data
REGIONS = [
    ("ASIA-PACIFIC 8", (199, 91, 38)),
    ("EUROPE 10", (43, 94, 167)),
    ("AMERICAS 5", (108, 74, 160)),
    ("MIDDLE EAST 5", (146, 118, 26)),
    ("AFRICA 6", (46, 125, 79)),
    ("OCEANIA 4", (30, 122, 138)),
    ("WORLD 2", (58, 58, 58)),
]

NUMBERS = [
    ("3", "presidents at one table"),
    ("9–6", "World Court genocide vote"),
    ("$120bn", "aid goal cut at COP31"),
    ("$81bn", "Anthropic's record IPO"),
    ("109–0", "Danish vote on Arctic pact"),
    ("4.9%", "Australian jobless rate"),
]

LEADS = [
    {
        "n": 1, "tag": "SHENZHEN · SUMMIT", "src": "Reuters · AP",
        "head": "Trump, Xi and Putin hold first three-way summit",
        "body": "The US, Chinese and Russian leaders met for 90 minutes at APEC in Shenzhen and issued a “Declaration on Peace” on nuclear risk and UN reform.",
        "art": "summit",
    },
    {
        "n": 2, "tag": "THE HAGUE · JUSTICE", "src": "Al Jazeera · UN News",
        "head": "World Court: Myanmar committed genocide",
        "body": "By 9 votes to 6 the ICJ found Myanmar guilty of genocide against the Rohingya and ordered reparations.",
        "art": "court",
    },
    {
        "n": 3, "tag": "NASDAQ · MARKETS", "src": "AP",
        "head": "Anthropic debuts in the biggest IPO on record",
        "body": "Priced at $83, above its range, the Claude maker raised $81.3bn and is valued near $1.5tn as ANT starts trading Thursday.",
        "art": "ipo",
    },
]

CARDS = [
    {"n": 4, "tag": "CRIMEA · WAR", "src": "Euronews", "art": "bridge",
     "head": "Ukraine hits Crimea bridge again",
     "body": "Third strike in a week halts trains to Russia."},
    {"n": 5, "tag": "RIYADH · WAR", "src": "Reuters", "art": "missiles",
     "head": "Saudis shoot down Houthi missiles",
     "body": "Debris fell on the capital; no casualties reported."},
    {"n": 6, "tag": "ODISHA · STORM", "src": "IMD", "art": "cyclone",
     "head": "Cyclone Akvan nears India's coast",
     "body": "Over 100,000 in shelters before Friday's landfall."},
    {"n": 7, "tag": "SEOUL · JUSTICE", "src": "AP", "art": "seoul",
     "head": "Korea's top court clears ex-PM Han",
     "body": "Han Duck-soo's martial-law conviction is overturned."},
    {"n": 8, "tag": "GREENLAND · SECURITY", "src": "AP", "art": "arctic",
     "head": "Denmark backs Arctic pact with US",
     "body": "Parliament approves the Greenland security deal 109–0."},
    {"n": 9, "tag": "ANTALYA · CLIMATE", "src": "Reuters · AFP", "art": "cop",
     "head": "COP31 draft drops fossil fuels + $120bn aid goal",
     "body": "No figure for adaptation aid; talks are due to end on Friday."},
    {"n": 10, "tag": "WORLDWIDE · GAMES", "src": "ABC", "art": "game",
     "head": "GTA VI goes on sale after 13 years",
     "body": "The midnight launch draws rave reviews; New Zealand played first."},
    {"n": 11, "tag": "BOGOTÁ · LABOUR", "src": "Infobae", "art": "strike",
     "head": "Colombia's unions hold national strike",
     "body": "Marches in three cities against an economic law."},
    {"n": 12, "tag": "NAIROBI · SPORT", "src": "ABC", "art": "doping",
     "head": "Marathon champion banned for doping",
     "body": "Kenya's Peres Jepchirchir gets three years."},
    {"n": 13, "tag": "CANBERRA · ECONOMY", "src": "ABC", "art": "jobs",
     "head": "Australia's jobless rate hits 4.9%",
     "body": "Highest since 2024; shares and the dollar slide."},
]

BRIEFS = [
    (14, "Shenzhen: Xi urges ban on all nuclear arms", "Al Jazeera"),
    (15, "APEC: Albanese to Putin: “End your war, end it now”", "ABC"),
    (16, "Seoul: Half a million sit college entrance exam", "Sedaily"),
    (17, "Jakarta: Asset-seizure law passes after 18 years", "Kompas"),
    (18, "Hormuz: Iran says mines set 5 tankers ablaze", "Al Jazeera"),
    (19, "Gaza: Israel ends tank raid past truce line", "BBC"),
    (20, "Krasnodar: Kyiv says it hit two oil refineries", "Euronews"),
    (21, "Brussels: EU delays methane rules two years", "Euronews"),
    (22, "UK: Inquiry — yacht Bayesian was vulnerable to wind", "RNZ"),
    (23, "Zurich: Two rivals to challenge FIFA's Infantino", "ABC"),
    (24, "Rome: Author Corrado Augias dies at 91", "Euronews"),
    (25, "Mogadishu: Somalia expels UAE ambassador", "Al Jazeera"),
    (26, "Sudan: Court sentences absent RSF chief to death", "AP"),
    (27, "Pretoria: Central bank holds rate at 7.25%", "SABC"),
    (28, "Canaries: Record 11,000 migrants in 15 days", "Africanews"),
    (29, "Florida: Floods shut Broward, Miami schools again", "CBS"),
    (30, "Wellington: Court — pay-equity cuts broke rights law", "RNZ"),
    (31, "Tonga: Drought emergency takes effect", "RNZ"),
    (32, "Cook Islands: Cyclone Xavier weakens to category 4", "RNZ"),
    (33, "Space: Red giant seen eating a Sun-sized star", "Nature"),
    (34, "Kyiv: Left off the agenda, Ukraine watches Shenzhen", "reports"),
    (35, "Paris: Mélenchon could win, says France's justice minister", ""),
    (36, "Jazan: Saudi Arabia says danger has passed in three cities", ""),
    (37, "Benghazi: Cocaine and millions of pills seized in eastern Libya", ""),
    (38, "Mexico City: Banxico minutes — board cut rates to 6.25% on a 3–2 vote", ""),
    (39, "Ottawa: Carney — Canada rethinks China ties, seeking the right US deal", ""),
    (40, "New Delhi: Modi meets the Prince and Princess of Wales", ""),
]

DATE_CHECK = (
    "Every story on this page happened, or was first reported, on Thursday 19 November 2026. "
    "LEFT OUT AS OTHER DAYS' NEWS — 18 Nov: EU's €45bn Ukraine loan plan · Iran fires on Kuwait "
    "and Bahrain · Nvidia results · Jeffries named US speaker · Voyager 1 crosses one light-day. "
    "20 Nov (not yet): COP31's scheduled close · Cyclone Akvan's landfall."
)

SOURCES = (
    "Sources: Reuters, AP, AFP, BBC, Al Jazeera, UN News, Euronews, ABC, RNZ, Xinhua, Nature — "
    "Claims are attributed, not stated as fact. Pictures and map: original, drawn in code. 2026-11-19"
)


# ---------------------------------------------------------------- art
def _person(draw, cx, top, suit, skin=(232, 183, 140)):
    draw.ellipse([cx - 11, top, cx + 11, top + 22], fill=skin, outline=INK, width=1)
    draw.rectangle([cx - 16, top + 22, cx + 16, top + 52], fill=suit, outline=INK, width=1)
    draw.polygon([(cx - 4, top + 22), (cx + 4, top + 22), (cx, top + 34)], fill=(255, 255, 255))
    draw.polygon([(cx - 2, top + 24), (cx + 2, top + 24), (cx, top + 38)], fill=RED)


def _flag_us(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK, width=1)
    stripe = h / 7.0
    for i in range(0, 7, 2):
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe], fill=(178, 34, 52))
    draw.rectangle([x, y, x + w * 0.42, y + stripe * 4], fill=(60, 59, 110))
    for r in range(3):
        for c in range(4):
            sx = x + 4 + c * (w * 0.42 - 8) / 3.0
            sy = y + 3 + r * (stripe * 4 - 6) / 2.0
            draw.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=(255, 255, 255))


def _flag_cn(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16), outline=INK, width=1)
    draw.polygon([(x + 9, y + 5), (x + 12, y + 12), (x + 5, y + 9), (x + 14, y + 9), (x + 7, y + 12)],
                 fill=(255, 222, 0))
    for dx, dy in [(20, 4), (23, 9), (23, 15), (20, 19)]:
        draw.ellipse([x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2], fill=(255, 222, 0))


def _flag_ru(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK, width=1)
    draw.rectangle([x, y + h / 3.0, x + w, y + 2 * h / 3.0], fill=(0, 57, 166))
    draw.rectangle([x, y + 2 * h / 3.0, x + w, y + h], fill=(213, 43, 30))


def art_summit(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(27, 45, 84))
    draw.rectangle([x0, y0, x1, y0 + 15], fill=GOLD)
    draw.text((x0 + 8, y0 + 3), "APEC 2026 · SHENZHEN", font=F(SANS_B, 11), fill=(24, 32, 54))
    draw.text((x1 - 8 - tw(draw, "FIRST THREE-WAY SUMMIT", F(SANS_B, 11)),
               y0 + 3), "FIRST THREE-WAY SUMMIT", font=F(SANS_B, 11), fill=(24, 32, 54))
    fw, fh = 62, 34
    _flag_us(draw, x0 + 28, y0 + 24, fw, fh)
    _flag_cn(draw, (x0 + x1) / 2 - fw / 2, y0 + 24, fw, fh)
    _flag_ru(draw, x1 - 28 - fw, y0 + 24, fw, fh)
    cy = y0 + 34
    _person(draw, x0 + 59, cy, (38, 58, 110))
    _person(draw, (x0 + x1) / 2, cy, (120, 28, 28))
    _person(draw, x1 - 59, cy, (52, 52, 58))
    draw.rectangle([x0 + 10, y1 - 20, x1 - 10, y1 - 4], fill=(92, 58, 30), outline=INK, width=1)
    for label, cx in [("TRUMP", x0 + 59), ("XI", (x0 + x1) / 2), ("PUTIN", x1 - 59)]:
        f = F(SANS_B, 11)
        draw.text((cx - tw(draw, label, f) / 2, y1 - 18), label, font=f, fill=(255, 255, 255))


def art_court(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(168, 198, 222))
    cx = (x0 + x1) / 2
    # clock tower behind the roof line
    draw.rectangle([cx - 13, y0 + 16, cx + 13, y0 + 44], fill=(178, 104, 62), outline=INK, width=1)
    draw.polygon([(cx - 18, y0 + 17), (cx + 18, y0 + 17), (cx, y0 + 2)], fill=(70, 50, 38))
    draw.ellipse([cx - 7, y0 + 22, cx + 7, y0 + 36], fill=(255, 255, 255), outline=INK, width=1)
    draw.line([cx, y0 + 29, cx, y0 + 24], fill=INK, width=2)
    draw.line([cx, y0 + 29, cx + 4, y0 + 31], fill=INK, width=2)
    # courthouse body with pediment and bold columns
    draw.rectangle([x0 + 52, y0 + 56, x1 - 52, y1 - 6], fill=(238, 233, 218), outline=INK, width=1)
    draw.polygon([(x0 + 44, y0 + 56), (x1 - 44, y0 + 56), (cx, y0 + 40)], fill=(96, 72, 50))
    for i in range(4):
        px = x0 + 76 + i * ((x1 - x0 - 152) / 3.0)
        draw.rectangle([px - 6, y0 + 62, px + 6, y1 - 14], fill=(255, 255, 255), outline=INK, width=2)
    draw.rectangle([x0 + 52, y1 - 14, x1 - 52, y1 - 6], fill=(96, 72, 50))
    draw.text((x0 + 8, y0 + 33), "THE HAGUE", font=F(SANS_B, 9), fill=(24, 42, 74))
    draw.text((x0 + 8, y0 + 44), "WORLD COURT", font=F(SANS_B, 9), fill=(24, 42, 74))
    # scales of justice in a white disc, front right
    sx, sy = x1 - 34, y0 + 58
    draw.ellipse([sx - 25, sy - 24, sx + 25, sy + 26], fill=(255, 255, 255), outline=INK, width=2)
    draw.line([sx, sy - 18, sx, sy + 14], fill=INK, width=3)
    draw.line([sx - 16, sy - 12, sx + 16, sy - 12], fill=INK, width=3)
    for dx in (-16, 16):
        draw.line([sx + dx, sy - 12, sx + dx - 7, sy + 2], fill=INK, width=2)
        draw.line([sx + dx, sy - 12, sx + dx + 7, sy + 2], fill=INK, width=2)
        draw.arc([sx + dx - 8, sy - 2, sx + dx + 8, sy + 10], start=0, end=180, fill=INK, width=3)
    draw.rectangle([sx - 10, sy + 14, sx + 10, sy + 19], fill=INK)
    draw.rectangle([x0 + 8, y0 + 6, x0 + 62, y0 + 30], fill=RED)
    draw.text((x0 + 14, y0 + 9), "9 – 6", font=F(SERIF_B, 17), fill=(255, 255, 255))


def art_ipo(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(16, 74, 52))
    draw.text((x0 + 8, y0 + 3), "ANT", font=F(SERIF_B, 30), fill=(255, 255, 255))
    draw.text((x0 + 8, y0 + 34), "NASDAQ", font=F(SANS_B, 10), fill=(150, 230, 180))
    draw.text((x0 + 8, y0 + 48), "FIRST DAY", font=F(SANS_B, 10), fill=(150, 230, 180))
    # grid + candles rising
    for gy in range(4):
        yy = y0 + 18 + gy * 20
        draw.line([x0 + 92, yy, x1 - 10, yy], fill=(40, 110, 82), width=1)
    candles = [(110, 62, 48), (140, 54, 36), (170, 60, 44), (200, 42, 24), (230, 34, 14), (260, 22, 6)]
    base = y1 - 12
    for i, (ox, top_off, bot_off) in enumerate(candles):
        cx = x0 + ox
        top = y0 + top_off
        bot = y0 + bot_off + 34
        col = (46, 204, 113) if i != 2 else (231, 76, 60)
        draw.line([cx, top - 6, cx, bot + 6], fill=col, width=2)
        draw.rectangle([cx - 8, top, cx + 8, bot], fill=col, outline=(255, 255, 255), width=1)
    pts = [(x0 + 100, base - 14), (x0 + 150, base - 30), (x0 + 200, base - 40), (x0 + 262, base - 66)]
    draw.line(pts, fill=(255, 213, 90), width=3)
    draw.polygon([(x1 - 22, y0 + 10), (x1 - 8, y0 + 16), (x1 - 22, y0 + 22)], fill=(255, 213, 90))
    draw.rectangle([x1 - 66, y1 - 26, x1 - 8, y1 - 6], fill=GOLD)
    f = F(SANS_B, 12)
    draw.text((x1 - 62, y1 - 23), "IPO $83", font=f, fill=(20, 20, 20))


def art_small(draw, kind, box):
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    if kind == "bridge":
        draw.rectangle(box, fill=(38, 64, 110))
        draw.arc([x0 + 14, y0 + 8, x1 - 14, y0 + 66], start=180, end=360, fill=(240, 200, 90), width=4)
        draw.line([x0 + 8, y0 + 40, x1 - 8, y0 + 40], fill=(240, 200, 90), width=3)
        for i in range(5):
            px = x0 + 26 + i * (w - 52) / 4.0
            draw.line([px, y0 + 40, px, y0 + 18 + (10 if i in (0, 4) else 2)], fill=(200, 200, 200), width=1)
        draw.polygon([(cx - 4, y0 + 16), (cx, y0 + 6), (cx + 4, y0 + 16), (cx + 12, y0 + 20),
                      (cx + 4, y0 + 22), (cx + 6, y0 + 32), (cx, y0 + 26), (cx - 6, y0 + 32),
                      (cx - 4, y0 + 22), (cx - 12, y0 + 20)], fill=(255, 160, 40))
        f = F(SANS_B, 10)
        draw.text((x0 + 6, y0 + 3), "KERCH BRIDGE", font=f, fill=(255, 255, 255))
    elif kind == "missiles":
        draw.rectangle(box, fill=(18, 22, 52))
        for sx, sy in [(x0 + 24, y0 + 8), (x0 + 70, y0 + 5), (x1 - 30, y0 + 10), (x1 - 70, y0 + 6)]:
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        draw.rectangle([x0, y1 - 12, x1, y1], fill=(10, 12, 30))
        for bx, bw, bh in [(x0 + 10, 22, 12), (x0 + 40, 16, 18), (cx - 10, 24, 20), (x1 - 52, 18, 15), (x1 - 28, 22, 11)]:
            draw.rectangle([bx, y1 - 12 - bh, bx + bw, y1 - 12], fill=(52, 62, 100), outline=(90, 100, 140), width=1)
        for mx, my in [(x0 + 58, y0 + 15), (x1 - 52, y0 + 12)]:
            draw.polygon([(mx, my), (mx + 16, my + 8), (mx + 12, my + 14), (mx - 2, my + 6)], fill=(220, 220, 220))
            draw.polygon([(mx + 22, my + 16), (mx + 30, my + 8), (mx + 32, my + 20), (mx + 26, my + 24)], fill=(255, 150, 50))
        f = F(SANS_B, 10)
        draw.text((x0 + 6, y0 + 2), "OVER RIYADH", font=f, fill=(255, 213, 90))
    elif kind == "cyclone":
        draw.rectangle(box, fill=(30, 90, 130))
        scx, scy = x1 - 42, cy - 2
        for r in (17, 12, 7):
            draw.arc([scx - r, scy - r, scx + r, scy + r], start=20, end=320, fill=(255, 255, 255), width=3)
        draw.ellipse([scx - 3, scy - 3, scx + 3, scy + 3], fill=(255, 213, 90))
        f = F(SANS_B, 10)
        draw.text((x0 + 6, y0 + 3), "ODISHA", font=f, fill=(255, 255, 255))
        draw.text((x0 + 6, y1 - 14), "CYCLONE AKVAN", font=f, fill=(255, 255, 255))
    elif kind == "seoul":
        draw.rectangle(box, fill=(210, 224, 238))
        draw.rectangle([x0 + 16, y0 + 16, x1 - 16, y1 - 6], fill=(238, 234, 222), outline=INK, width=1)
        draw.polygon([(x0 + 10, y0 + 16), (x1 - 10, y0 + 16), (cx, y0 + 4)], fill=(70, 80, 100))
        # Korea flag disc
        draw.ellipse([x0 + 24, y0 + 20, x0 + 48, y0 + 44], fill=(255, 255, 255), outline=INK, width=1)
        draw.pieslice([x0 + 28, y0 + 24, x0 + 44, y0 + 40], start=90, end=270, fill=(205, 46, 58))
        draw.pieslice([x0 + 28, y0 + 24, x0 + 44, y0 + 40], start=270, end=90, fill=(0, 71, 160))
        draw.rectangle([cx - 2, y0 + 20, x1 - 14, y0 + 38], fill=RED)
        f = F(SANS_B, 9)
        t = "OVERTURNED"
        draw.text((cx + 2, y0 + 24), t, font=f, fill=(255, 255, 255))
    elif kind == "arctic":
        draw.rectangle(box, fill=(196, 224, 236))
        draw.polygon([(x0, y1), (x0 + 50, y0 + 18), (x0 + 100, y1)], fill=(255, 255, 255))
        draw.polygon([(x0 + 90, y1), (cx + 30, y0 + 10), (x1, y1)], fill=(235, 245, 250))
        _flag_us(draw, x0 + 8, y0 + 6, 34, 20)
        draw.rectangle([cx - 17, y0 + 6, cx + 17, y0 + 26], fill=(255, 255, 255), outline=INK, width=1)
        draw.rectangle([cx - 17, y0 + 6, cx - 5, y0 + 26], fill=(200, 16, 46))
        draw.rectangle([x1 - 52, y0 + 6, x1 - 8, y0 + 28], fill=NAVY)
        draw.text((x1 - 48, y0 + 10), "109–0", font=F(SANS_B, 12), fill=(255, 255, 255))
        draw.text((x0 + 6, y1 - 14), "GREENLAND", font=F(SANS_B, 10), fill=INK)
    elif kind == "cop":
        draw.rectangle(box, fill=(24, 92, 74))
        draw.ellipse([x0 + 10, y0 + 8, x0 + 44, y0 + 42], fill=(70, 160, 220), outline=(255, 255, 255), width=2)
        draw.ellipse([x0 + 18, y0 + 14, x0 + 30, y0 + 24], fill=(90, 190, 110))
        draw.rectangle([x0 + 52, y0 + 6, x1 - 10, y1 - 6], fill=(252, 249, 238), outline=INK, width=1)
        draw.text((x0 + 58, y0 + 8), "DRAFT · 19 NOV", font=F(SANS_B, 9), fill=INK)
        f = F(SANS_B, 11)
        draw.text((x0 + 58, y0 + 20), "FOSSIL FUELS", font=f, fill=INK)
        draw.line([x0 + 56, y0 + 29, x1 - 12, y0 + 29], fill=RED, width=3)
        draw.text((x0 + 58, y1 - 16), "$120BN AID CUT", font=F(SANS_B, 9), fill=MUTED)
    elif kind == "game":
        draw.rectangle(box, fill=(88, 40, 140))
        # controller
        draw.rounded_rectangle([cx - 44, y0 + 4, cx + 10, y0 + 30], radius=12, fill=(30, 30, 36), outline=(255, 255, 255), width=2)
        draw.line([cx - 32, y0 + 13, cx - 32, y0 + 21], fill=(255, 255, 255), width=3)
        draw.line([cx - 36, y0 + 17, cx - 28, y0 + 17], fill=(255, 255, 255), width=3)
        for dx, dy, col in [(-12, 11, (255, 90, 90)), (-4, 17, (90, 220, 120)), (-12, 21, (90, 150, 255))]:
            draw.ellipse([cx + dx, y0 + dy, cx + dx + 6, y0 + dy + 6], fill=col)
        draw.text((x1 - 58, y0 + 6), "VI", font=F(SERIF_B, 30), fill=(255, 110, 190))
        draw.text((x0 + 6, y1 - 14), "GTA VI · 13 YEARS ON", font=F(SANS_B, 10), fill=(255, 255, 255))
    elif kind == "strike":
        draw.rectangle(box, fill=(240, 228, 190))
        draw.rectangle([cx - 52, y0 + 4, cx + 52, y0 + 16], fill=(255, 205, 40), outline=INK, width=1)
        f = F(SANS_B, 9)
        t = "PARO NACIONAL"
        draw.text((cx - tw(draw, t, f) / 2, y0 + 5), t, font=f, fill=INK)
        cols = [(200, 60, 50), (50, 110, 180), (60, 160, 90), (230, 140, 40), (140, 80, 170), (220, 100, 140), (80, 80, 80)]
        for i, col in enumerate(cols):
            px = x0 + 18 + i * (w - 36) / 6.0
            draw.ellipse([px - 5, y0 + 24, px + 5, y0 + 34], fill=(232, 183, 140), outline=INK, width=1)
            draw.rectangle([px - 6, y0 + 34, px + 6, y1 - 4], fill=col)
    elif kind == "doping":
        draw.rectangle(box, fill=(250, 244, 224))
        draw.polygon([(cx - 30, y0 + 4), (cx - 18, y0 + 20), (cx - 26, y0 + 20)], fill=(200, 40, 50))
        draw.polygon([(cx + 30, y0 + 4), (cx + 18, y0 + 20), (cx + 26, y0 + 20)], fill=(40, 90, 180))
        draw.ellipse([cx - 17, y0 + 16, cx + 17, y0 + 46], fill=GOLD, outline=INK, width=2)
        draw.line([cx - 11, y0 + 22, cx + 11, y0 + 40], fill=RED, width=4)
        draw.line([cx + 11, y0 + 22, cx - 11, y0 + 40], fill=RED, width=4)
        draw.rectangle([x1 - 76, y0 + 6, x1 - 8, y0 + 24], fill=RED)
        draw.text((x1 - 70, y0 + 9), "BANNED", font=F(SANS_B, 11), fill=(255, 255, 255))
        draw.text((x0 + 6, y1 - 13), "DOPING · 3 YEARS", font=F(SANS_B, 9), fill=INK)
    elif kind == "jobs":
        draw.rectangle(box, fill=(252, 249, 238))
        for i, bh in enumerate([10, 16, 13, 22, 28]):
            bx = x0 + 12 + i * 18
            draw.rectangle([bx, y1 - 10 - bh, bx + 12, y1 - 10], fill=(70, 110, 180) if i < 4 else RED)
        draw.text((x1 - 66, y0 + 4), "4.9%", font=F(SERIF_B, 22), fill=RED)
        draw.text((x1 - 66, y0 + 30), "JOBLESS", font=F(SANS_B, 9), fill=INK)
    else:
        draw.rectangle(box, fill=(200, 200, 200))


# ---------------------------------------------------------------- map
# rough continent blobs in lon/lat space: (lon, lat) polygons
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 49), (-122, 37), (-110, 30), (-105, 20),
     (-97, 16), (-92, 15), (-83, 9), (-79, 9), (-87, 13), (-95, 19), (-97, 26),
     (-90, 21), (-86, 28), (-81, 25), (-80, 32), (-76, 35), (-70, 42), (-65, 44),
     (-60, 47), (-65, 50), (-80, 55), (-95, 60), (-120, 66), (-150, 66)],
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-70, -18),
     (-70, -24), (-70, -34), (-72, -42), (-74, -50), (-70, -54), (-66, -50),
     (-68, -40), (-62, -35), (-52, -30), (-48, -22), (-40, -12), (-35, -8),
     (-44, -3), (-52, 2), (-60, 6), (-68, 9), (-74, 11), (-79, 9)],
    [(-17, 15), (-10, 5), (-8, 4), (2, 6), (9, 4), (13, -5), (12, -15),
     (14, -24), (17, -32), (20, -35), (27, -34), (32, -28), (33, -22),
     (36, -18), (40, -12), (42, -5), (48, 2), (51, 10), (44, 11), (40, 15),
     (37, 20), (34, 24), (32, 31), (30, 31), (20, 32), (10, 34), (5, 37),
     (-2, 35), (-10, 31), (-17, 25)],
    [(-10, 36), (-9, 43), (-2, 44), (0, 46), (-5, 48), (-1, 50), (2, 51),
     (5, 53), (8, 55), (8, 57), (18, 56), (21, 58), (24, 60), (30, 60),
     (30, 65), (28, 69), (40, 68), (50, 69), (60, 69), (45, 64), (40, 60),
     (35, 55), (30, 50), (28, 46), (23, 40), (19, 42), (12, 44), (8, 44),
     (3, 42), (3, 39), (0, 38), (-2, 37)],
    [(40, 60), (60, 69), (90, 70), (120, 70), (150, 70), (178, 66), (170, 60),
     (158, 52), (142, 50), (140, 40), (135, 35), (127, 33), (122, 31), (120, 25),
     (110, 20), (108, 15), (106, 8), (103, 5), (100, 8), (98, 14), (95, 17),
     (92, 20), (89, 22), (86, 20), (80, 15), (77, 8), (73, 18), (70, 22),
     (66, 25), (61, 25), (57, 27), (52, 28), (50, 29), (48, 30), (52, 25),
     (55, 24), (59, 22), (55, 17), (52, 15), (45, 12), (43, 12), (40, 15),
     (38, 20), (35, 28), (36, 36), (30, 36), (27, 37), (30, 41), (33, 42),
     (40, 45), (45, 50), (40, 60)],
    [(113, -22), (114, -30), (117, -35), (124, -33), (130, -32), (135, -35),
     (138, -35), (141, -38), (147, -38), (150, -37), (153, -30), (153, -25),
     (150, -22), (146, -19), (145, -15), (142, -11), (142, -15), (140, -18),
     (136, -15), (135, -12), (132, -11), (126, -14), (122, -17), (117, -20)],
]

PINS = [
    (1, 114, 22), (2, 5, 52), (3, -74, 41), (4, 34, 45), (5, 47, 25),
    (6, 86, 20), (7, 127, 37), (8, -42, 72), (9, 31, 37), (10, -30, 28),
    (11, -74, 5), (12, 37, 0), (13, 149, -35),
]


def draw_map(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(196, 218, 232), outline=INK, width=1)

    def proj(lon, lat):
        px = x0 + (lon + 180) / 360.0 * (x1 - x0)
        py = y0 + (78 - lat) / 130.0 * (y1 - y0)
        return (px, py)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=(226, 214, 170), outline=(150, 140, 105))
    cols = [(199, 91, 38), (43, 94, 167), (30, 30, 30), (176, 42, 30),
            (146, 118, 26), (30, 122, 138), (43, 94, 167), (58, 58, 58),
            (146, 118, 26), (108, 74, 160), (108, 74, 160), (46, 125, 79),
            (30, 122, 138)]
    for (n, lon, lat), col in zip(PINS, cols):
        px, py = proj(lon, lat)
        r = 8
        draw.ellipse([px - r, py - r, px + r, py + r], fill=col, outline=(255, 255, 255), width=2)
        f = F(SANS_B, 9 if n < 10 else 8)
        t = str(n)
        draw.text((px - tw(draw, t, f) / 2, py - 5), t, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- page
def build_image():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([3, 3, W - 4, H - 4], outline=INK, width=2)
    X0, X1 = 14, W - 14
    CW = X1 - X0

    # masthead
    d.text((X0, 9), "THE WORLD IN ONE DAY", font=F(SANS_B, 13), fill=DARKRED)
    right = "40 STORIES · 7 REGIONS · ONE PAGE"
    f = F(SANS_B, 12)
    d.text((X1 - tw(d, right, f), 10), right, font=f, fill=INK)
    d.line([X0, 28, X1, 28], fill=INK, width=2)
    title = "Thursday 19 November 2026"
    ts = fit_size(d, title, SERIF_B, 58, CW)
    d.text((X0 - 1, 31), title, font=F(SERIF_B, ts), fill=INK)
    stand = "Trump, Xi and Putin share one table · The World Court finds genocide in Myanmar · The biggest IPO ever starts trading"
    ss = fit_size(d, stand, SERIF_I, 15, CW, minimum=10)
    d.text((X0, 86), stand, font=F(SERIF_I, ss), fill=DARKRED)
    d.text((X0, 104), "Everything on this page happened, or was first reported, on Thursday 19 November 2026.",
           font=F(SANS_R, 11), fill=MUTED)

    # region bar
    ry = 120
    total = sum([8, 10, 5, 5, 6, 4, 2])
    counts = [8, 10, 5, 5, 6, 4, 2]
    rx = X0
    for i, ((label, col), cnt) in enumerate(zip(REGIONS, counts)):
        seg_w = CW * cnt / total if i < len(REGIONS) - 1 else X1 - rx
        d.rectangle([rx, ry, rx + seg_w, ry + 20], fill=col)
        lf = F(COND_B, 12)
        d.text((rx + (seg_w - tw(d, label, lf)) / 2, ry + 3), label, font=lf, fill=(255, 255, 255))
        rx += seg_w

    # numbers strip
    ny = 143
    d.line([X0, ny + 40, X1, ny + 40], fill=INK, width=1)
    cell = CW / 6.0
    for i, (big, cap) in enumerate(NUMBERS):
        cx0 = X0 + i * cell
        if i > 0:
            d.line([cx0, ny + 2, cx0, ny + 36], fill=CREAM_LINE, width=1)
        bf = F(SERIF_B, 25)
        d.text((cx0 + 6, ny), big, font=bf, fill=DARKRED if i in (1, 3, 5) else INK)
        cf = F(COND_R, 11)
        lines = wrap(d, cap, cf, cell - 10, 1)
        d.text((cx0 + 6, ny + 27), lines[0] if lines else cap, font=cf, fill=INK)

    # lead cards: art (100 drawn + 16 black banner) over text
    ly = 190
    lh = 218
    gap = 6
    lw = (CW - 2 * gap) / 3.0
    banners = ["APEC 2026 · SHENZHEN", "WORLD COURT · THE HAGUE", "NASDAQ · NEW YORK"]
    for i, lead in enumerate(LEADS):
        bx = X0 + i * (lw + gap)
        d.rectangle([bx, ly, bx + lw, ly + lh], fill=PAPER, outline=INK, width=1)
        art_box = (bx + 1, ly + 1, bx + lw - 1, ly + 101)
        if lead["art"] == "summit":
            art_summit(d, art_box)
        elif lead["art"] == "court":
            art_court(d, art_box)
        else:
            art_ipo(d, art_box)
        d.rectangle([bx + 1, ly + 101, bx + lw - 1, ly + 117], fill=(16, 16, 16))
        ban = banners[i]
        banf = F(SANS_B, 12)
        d.text((bx + (lw - tw(d, ban, banf)) / 2, ly + 103), ban, font=banf, fill=(255, 255, 255))
        tx = bx + 8
        num_badge(d, tx, ly + 122, lead["n"], RED)
        d.text((tx + 24, ly + 123), lead["tag"] + " — " + lead["src"].upper(),
               font=F(COND_B, 11), fill=DARKRED)
        hf = F(SERIF_B, 20)
        hlines = wrap(d, lead["head"], hf, lw - 16, 2)
        yy = draw_lines(d, tx, ly + 140, hlines, hf, INK, 21)
        bf2 = F(SANS_R, 11)
        blines = wrap(d, lead["body"], bf2, lw - 16, 3)
        draw_lines(d, tx, yy + 1, blines, bf2, (40, 40, 40), 12)

    # small cards 4-13: 5 columns x 2 rows, taller art, bigger headlines
    cy0 = ly + lh + 6
    ch = 134
    cw5 = (CW - 4 * gap) / 5.0
    for idx, card in enumerate(CARDS):
        row, col = divmod(idx, 5)
        bx = X0 + col * (cw5 + gap)
        by = cy0 + row * (ch + gap)
        d.rectangle([bx, by, bx + cw5, by + ch], fill=PAPER, outline=INK, width=1)
        art_small(d, card["art"], (bx + 1, by + 1, bx + cw5 - 1, by + 50))
        tx = bx + 6
        num_badge(d, tx, by + 54, card["n"], NAVY, r=8)
        d.text((tx + 20, by + 55), card["tag"], font=F(COND_B, 10), fill=DARKRED)
        hf = F(SERIF_B, 14)
        hlines = wrap(d, card["head"], hf, cw5 - 12, 2)
        yy = draw_lines(d, tx, by + 71, hlines, hf, INK, 15)
        bf2 = F(COND_R, 11)
        blines = wrap(d, card["body"] + " — " + card["src"], bf2, cw5 - 12, 2)
        draw_lines(d, tx, yy, blines, bf2, (40, 40, 40), 12)

    # bottom: map + briefs
    by0 = cy0 + 2 * ch + gap + 8
    d.text((X0, by0), "WHERE IT HAPPENED", font=F(SANS_B, 11), fill=INK)
    d.text((X0 + 138, by0 + 1), "numbers match the stories", font=F(SANS_I, 10), fill=MUTED)
    bh = "ALSO ON THURSDAY 19 NOVEMBER — 27 MORE STORIES"
    bf_h = F(SANS_B, 11)
    d.text((330, by0), bh, font=bf_h, fill=INK)
    d.text((330 + tw(d, bh, bf_h) + 8, by0 + 1), "place · what happened · source", font=F(SANS_I, 10), fill=MUTED)
    map_box = (X0, by0 + 16, 318, by0 + 16 + 176)
    draw_map(d, map_box)
    # briefs in two columns
    col_x = [330, 672]
    col_w = 338
    row_h = 12.6
    top = by0 + 18
    for j, (n, text, src) in enumerate(BRIEFS):
        col = 0 if j < 14 else 1
        row = j if col == 0 else j - 14
        yy = top + row * row_h
        xx = col_x[col]
        num_badge(d, xx, yy, n, RED if n % 2 == 0 else NAVY, r=6)
        full = text + ((" — " + src) if src else "")
        ff = F(COND_R, 11)
        # shrink to fit one line
        size = 11
        while tw(d, full, F(COND_R, size)) > col_w - 18 and size > 8:
            size -= 1
            ff = F(COND_R, size)
        d.text((xx + 17, yy - 1), full, font=ff, fill=INK)

    # date check
    dy = by0 + 16 + 176 + 8
    d.rectangle([X0, dy, X1, dy + 62], fill=(253, 244, 224), outline=RED, width=2)
    d.text((X0 + 8, dy + 5), "DATE CHECK", font=F(SANS_B, 11), fill=DARKRED)
    d.line([X0 + 84, dy + 10, X0 + 89, dy + 15], fill=(46, 125, 79), width=2)
    d.line([X0 + 89, dy + 15, X0 + 99, dy + 5], fill=(46, 125, 79), width=2)
    df = F(SANS_R, 10)
    dlines = wrap(d, DATE_CHECK, df, CW - 110, 4)
    draw_lines(d, X0 + 104, dy + 4, dlines, df, INK, 12)
    sy = dy + 68
    sf = fit_size(d, SOURCES, SANS_R, 10, CW, minimum=8)
    d.text((X0, sy), SOURCES, font=F(SANS_R, sf), fill=MUTED)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    try:
        img = build_image()
        img.save(out_path, format="PNG", optimize=False)
    except ImportError:
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
        if os.path.abspath(src) != os.path.abspath(out_path):
            shutil.copyfile(src, out_path)
    print("wrote " + out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
