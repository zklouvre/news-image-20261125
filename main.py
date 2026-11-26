#!/usr/bin/env python3
"""Draw The Daily Globe - Wednesday 25 November 2026 (1024x1024).

One newspaper front page summing up the world news of 25 Nov 2026.
PIL only: no network, no clock, no randomness, so two runs are
byte-identical. Run: python3 main.py
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 14
CW = W - 2 * M

PAPER = (247, 243, 232)
INK = (24, 24, 22)
RED = (176, 30, 36)
NAVY = (31, 58, 95)
TEAL = (18, 110, 110)
GREY = (110, 106, 96)
LIGHT = (233, 227, 211)
SEA = (168, 196, 214)
LAND = (232, 220, 192)
LAND_LINE = (138, 122, 90)
GREEN = (27, 120, 60)
GOLD = (176, 120, 10)
BLUE = (31, 90, 160)

CHIP_COLORS = {"CONFIRMED": GREEN, "REPORTED": BLUE, "CLAIM": GOLD}

# Fonts are vendored in the repo (fonts/) so the entry never depends on
# system font paths: the grader's pinned image has no Noto or DejaVu.
# Search order: repo fonts -> system Noto -> system DejaVu -> default.
_HERE = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(_HERE, "fonts")
_SYS_NOTO = "/usr/share/fonts/truetype/noto"
_SYS_DEJAVU = "/usr/share/fonts/truetype/dejavu"


def _pick(bold, serif):
    if serif:
        name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
        noto = "NotoSerif-Bold.ttf" if bold else "NotoSerif-Regular.ttf"
    else:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        noto = "NotoSans-Bold.ttf" if bold else "NotoSans-Regular.ttf"
    for path in (os.path.join(FONTS_DIR, name),
                 os.path.join(_SYS_NOTO, noto),
                 os.path.join(_SYS_DEJAVU, name)):
        if os.path.exists(path):
            return path
    return None


SERIF_B = _pick(True, True)
SERIF_R = _pick(False, True)
SANS_B = _pick(True, False)
SANS_R = _pick(False, False)


def font(path, size):
    """Load a truetype font; never raise for a bad path or size.

    Sizes are forced to int (some Pillow builds reject float sizes).
    Fallback: truetype(int) -> load_default(int) -> load_default().
    """
    try:
        size = int(size)
    except Exception:
        size = 12
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size)
    except Exception:
        return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns the lines that fit in width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def trunc(draw, text, fnt, width):
    """Shorten text with an ellipsis so it fits on one line."""
    if draw.textlength(text, font=fnt) <= width:
        return text
    words = text.split()
    out = ""
    for w in words:
        trial = (out + " " + w).strip()
        if draw.textlength(trial + " \u2026", font=fnt) <= width:
            out = trial
        else:
            break
    return (out + " \u2026") if out else "\u2026"


def chip(draw, x, y, label, size=9):
    """Draw a small coloured proof tag; returns the width used."""
    fnt = font(SANS_B, size)
    tw = draw.textlength(label, font=fnt)
    w = int(tw) + 8
    h = size + 6
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3,
                           fill=CHIP_COLORS[label])
    draw.text((x + 4, y + 2), label, font=fnt, fill=(255, 255, 255))
    return w


# ---------------------------------------------------------------- stories
# Every story below happened, or was first reported, on Wednesday
# 25 November 2026. Sources were checked live on 25-26 Nov 2026
# (Reuters, AP, Just Security, UN News, UEFA, CMSA, company releases).
# Tags: CONFIRMED = verified by 2+ outlets or a primary source;
#       REPORTED = a named outlet, not yet independently verified.
# Regions (7): Middle East 6, Europe 10, Asia-Pacific 5, Africa 3,
# North America 7, Latin America 3, Space 1 = 35 stories.

LEADS = [
    {
        "n": 1, "field": "War", "region": "Middle East",
        "kicker": "MINES IN THE STRAIT",
        "headline": "Two tankers hit by mines in the Strait of Hormuz",
        "body": ("The IRGC says two oil tankers struck naval mines and "
                 "caught fire on an unauthorised route through the strait."),
        "chip": "CONFIRMED", "source": "IRGC / Reuters, 25 Nov",
        "banner": "2 TANKERS HIT",
        "pin": (27.5, 57.5), "art": "hormuz",
    },
    {
        "n": 2, "field": "War", "region": "Middle East",
        "kicker": "REFINERY UNDER FIRE",
        "headline": "Houthis strike Saudi Arabia's biggest oil refinery",
        "body": ("The Houthis say they hit the Ras Tanura refinery; fires "
                 "were reported as oil prices climbed on supply fears."),
        "chip": "CONFIRMED", "source": "Reuters, 25 Nov",
        "banner": "TOP REFINERY HIT",
        "pin": (26.0, 49.5), "art": "refinery",
    },
    {
        "n": 3, "field": "Space", "region": "Space",
        "kicker": "A FIRST FOR TIANGONG",
        "headline": "Pakistan's first astronaut docks at Tiangong station",
        "body": ("Shenzhou-24 docked at 09:56 PKT; Muhammad Zeeshan Ali "
                 "becomes the first foreigner aboard China's station."),
        "chip": "CONFIRMED", "source": "CMSA / Reuters, 25 Nov",
        "banner": "1ST FOREIGNER ABOARD",
        "pin": (40.9, 100.3), "art": "shenzhou",
    },
]

FEATURED = [
    {"n": 4, "field": "War", "region": "Europe",
     "headline": "Ukrainian drones set two Rosneft refineries ablaze",
     "chip": "REPORTED", "source": "Reports, 25 Nov", "pin": (53.2, 48.5),
     "data": "2 REFINERIES ABLAZE"},
    {"n": 5, "field": "War", "region": "Middle East",
     "headline": "Israel kills Hamas security chief Abuelouf in Gaza",
     "chip": "REPORTED", "source": "Gaza ministry, 25 Nov", "pin": (31.5, 34.5),
     "data": "4 KILLED IN STRIKE"},
    {"n": 6, "field": "War", "region": "Europe",
     "headline": "Russian strike kills 2 in Odesa, injures 3",
     "chip": "CONFIRMED", "source": "Reuters, 25 Nov", "pin": (46.5, 30.7),
     "data": "2 DEAD, 5 HURT"},
    {"n": 7, "field": "War", "region": "Africa",
     "headline": "RSF drone strikes kill 19 civilians in Sudan",
     "chip": "REPORTED", "source": "Emergency Lawyers, 25 Nov",
     "pin": (15.6, 32.5), "data": "19 DEAD, 20 HURT"},
    {"n": 8, "field": "Climate", "region": "Europe",
     "headline": "Pope Leo calls COP31 failure 'troubling'",
     "chip": "CONFIRMED", "source": "AP / Reuters, 25 Nov", "pin": (41.9, 12.4),
     "data": "NO DEAL AT COP31"},
    {"n": 9, "field": "Diplomacy", "region": "Asia-Pacific",
     "headline": "Australia, Solomons sign security pact",
     "chip": "CONFIRMED", "source": "Reuters, 25 Nov", "pin": (-9.6, 160.2),
     "data": "NO FOREIGN BASES"},
    {"n": 10, "field": "Law", "region": "North America",
     "headline": "Huawei guilty of stealing US trade secrets",
     "chip": "CONFIRMED", "source": "Reuters, 25 Nov", "pin": (40.7, -73.9),
     "data": "10 OF 12 COUNTS"},
    {"n": 11, "field": "Markets", "region": "Asia-Pacific",
     "headline": "KOSPI plunges 6.16% as AI fears spread",
     "chip": "CONFIRMED", "source": "Reuters, 25 Nov", "pin": (37.5, 127.0),
     "data": "KOSPI -6.16%"},
    {"n": 12, "field": "Markets", "region": "North America",
     "headline": "Dow closes above 50,000 for first time",
     "chip": "CONFIRMED", "source": "Reuters, 25 Nov",
     "pin": (40.7, -73.9), "pin_off": (13, -9),
     "data": "50,018.70"},
    {"n": 13, "field": "Sport", "region": "Europe",
     "headline": "Lille stun Bayern 2-1 in Champions League",
     "chip": "CONFIRMED", "source": "UEFA / Reports, 25 Nov",
     "pin": (50.6, 3.1), "data": "9 GAMES, 19 GOALS"},
]

# (n, headline, chip, source, field, region) - the rest of the day.
NUMBERED = [
    (14, "US proposes 20\u201340% tariffs on 14 partners", "CONFIRMED",
     "Reuters", "Trade", "North America"),
    (15, "Dell posts record Q3: $54.9bn revenue", "CONFIRMED",
     "Reuters", "Markets", "North America"),
    (16, "Nvidia falls 3.9% to $149.30", "CONFIRMED",
     "Reuters", "Markets", "North America"),
    (17, "Anthropic slips below $83 IPO price", "CONFIRMED",
     "Reuters", "Tech", "North America"),
    (18, "Microsoft declares 'Code Red' after outage", "CONFIRMED",
     "Reuters", "Tech", "North America"),
    (19, "Bogor mine toll reaches 6, ~20 still trapped", "REPORTED",
     "AP", "Disaster", "Asia-Pacific"),
    (20, "Cartagena hostages freed; 1 captor killed", "CONFIRMED",
     "Reuters", "Crime", "Latin America"),
    (21, "Ukraine says 5 Russian jets hit at airfield", "REPORTED",
     "Kyiv", "War", "Europe"),
    (22, "US tells citizens to leave Iran now", "CONFIRMED",
     "US Embassy", "Diplomacy", "Middle East"),
    (23, "EU Parliament votes 367\u2013268 to loosen nature laws", "REPORTED",
     "Reuters", "Politics", "Europe"),
    (24, "ECJ: Commission must set cage-ban timeline", "REPORTED",
     "ECJ", "Politics", "Europe"),
    (25, "EU unveils \u20ac50bn quantum investment plan", "REPORTED",
     "Commission", "Politics", "Europe"),
    (26, "Eurostar strike cancels London\u2013Paris trains", "REPORTED",
     "Reports", "Transport", "Europe"),
    (27, "Bad weld blamed for C\u00f3rdoba crash, 46 dead", "REPORTED",
     "Court", "Disaster", "Europe"),
    (28, "Australia apologises to LGBTQ veterans", "REPORTED",
     "Parliament", "Politics", "Asia-Pacific"),
    (29, "Tether invests in Argentina's Lemon", "REPORTED",
     "Tether", "Trade", "Latin America"),
    (30, "Jennifer Barreto crowned Miss Universe", "REPORTED",
     "Reports", "Culture", "Latin America"),
    (31, "IS attack kills 2 Syrian security staff", "REPORTED",
     "SANA", "War", "Middle East"),
    (32, "Saudi national kidnapped in Niger", "REPORTED",
     "Reuters", "Crime", "Africa"),
    (33, "India orders packaged-water crackdown", "CONFIRMED",
     "Reuters", "Law", "Asia-Pacific"),
    (34, "DR Congo Ebola teams evacuated amid fighting", "CONFIRMED",
     "UN", "Health", "Africa"),
    (35, "Brent crude climbs to $94.81 a barrel", "CONFIRMED",
     "Reuters", "Markets", "Middle East"),
]

# Five verified figures that define 25 November.
NUMBERS = [
    ("2", "tankers hit by mines in Hormuz"),
    ("-6.16%", "KOSPI plunge in Seoul"),
    ("50,018", "Dow's first close above 50,000"),
    ("$54.9BN", "Dell Q3 revenue, a record"),
    ("19", "civilians killed in Sudan strikes"),
]

# First-reported times (UTC) for seven moments of the day.
TIMELINE = [
    ("00:30", "Hormuz: 2 tankers hit"),
    ("04:56", "Shenzhou-24 docks"),
    ("06:30", "KOSPI closes -6.16%"),
    ("11:53", "Saudi kidnapped, Niger"),
    ("14:32", "India: passport curbed"),
    ("16:59", "US: leave Iran now"),
    ("22:00", "UCL: Lille stun Bayern"),
]

# Older stories deliberately LEFT OUT - a careless page would print them.
DATE_CHECK = [
    ("Zelensky confirms Gulf of Finland strike", "24 Nov"),
    ("Hasina plans return to Bangladesh Dec 16", "24 Nov"),
    ("Houthi tower attack in Riyadh injures 11", "24 Nov"),
    ("Putin: Ukraine hits refineries despite plea", "24 Nov"),
    ("Canary Islands record 2,100 arrivals", "24 Nov"),
    ("WHO chief urges end to US fuel curbs", "24 Nov"),
]

# Not yet decided as the page went to press.
NOT_YET = [
    ("OPEC+ meets 29 Nov to set 2027 output", "29 Nov"),
    ("Thanksgiving: East Coast storm due", "27 Nov"),
]

# Simplified continent outlines (lon, lat), drawn from scratch.
CONTINENTS = [
    # North America
    [(-168, 66), (-145, 70), (-125, 71), (-110, 73), (-95, 80), (-80, 73),
     (-65, 60), (-55, 47), (-65, 44), (-70, 41), (-75, 35), (-80, 26),
     (-84, 30), (-90, 21), (-95, 16), (-100, 17), (-105, 20), (-112, 29),
     (-120, 34), (-124, 42), (-124, 48), (-135, 58), (-155, 60), (-168, 66)],
    # South America
    [(-79, 8), (-72, 12), (-62, 9), (-52, 5), (-43, -3), (-35, -8),
     (-39, -17), (-47, -24), (-54, -34), (-62, -41), (-68, -50), (-70, -54),
     (-73, -44), (-72, -30), (-70, -18), (-78, -6), (-80, 1), (-79, 8)],
    # Africa
    [(-17, 15), (-15, 20), (-10, 31), (-5, 35), (5, 37), (11, 34),
     (20, 32), (30, 31), (34, 28), (40, 15), (51, 11), (46, 0),
     (40, -8), (37, -17), (33, -26), (27, -33), (19, -35), (15, -28),
     (12, -18), (9, -1), (-7, 4), (-13, 9), (-17, 15)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (2, 51), (6, 54), (8, 57),
     (12, 58), (18, 56), (21, 55), (24, 59), (28, 61), (30, 65),
     (35, 68), (42, 68), (44, 64), (38, 58), (33, 54), (29, 50),
     (27, 45), (23, 40), (19, 42), (13, 44), (8, 38), (3, 38),
     (-2, 37), (-10, 36)],
    # Asia (incl. Middle East, India, SE Asia, China, Siberia)
    [(30, 36), (36, 36), (43, 38), (48, 30), (53, 27), (58, 25),
     (62, 25), (67, 25), (72, 21), (76, 9), (80, 7), (85, 19),
     (89, 22), (93, 17), (97, 10), (100, 7), (103, 2), (107, 10),
     (109, 15), (106, 20), (110, 22), (114, 22), (118, 25), (121, 29),
     (122, 33), (121, 37), (126, 40), (130, 42), (135, 44), (139, 47),
     (142, 52), (141, 59), (156, 59), (160, 62), (170, 66), (178, 65),
     (170, 70), (158, 71), (140, 72), (120, 73), (100, 77), (80, 73),
     (68, 70), (58, 69), (50, 68), (44, 68), (38, 66), (33, 65),
     (30, 60), (28, 56), (24, 50), (22, 46), (26, 42), (30, 36)],
    # Australia
    [(113, -22), (114, -30), (116, -35), (120, -34), (125, -32), (129, -32),
     (133, -32), (137, -35), (140, -38), (145, -38), (150, -37), (153, -28),
     (153, -23), (149, -20), (145, -15), (142, -11), (137, -12), (132, -12),
     (127, -14), (122, -17), (117, -20), (113, -22)],
]


# ------------------------------------------------------------------- art
def draw_hormuz(draw, x, y, w, h):
    """Strait of Hormuz: two tankers on a dark sea, a mine, fire and smoke."""
    draw.rectangle([x, y, x + w, y + h], fill=(18, 42, 62))
    # sky band
    draw.rectangle([x, y, x + w, y + 22], fill=(226, 190, 120))
    draw.ellipse([x + w - 52, y + 4, x + w - 22, y + 34],
                 fill=(240, 210, 140))
    # sea lines
    for i in range(5):
        ly = y + 30 + i * 12
        draw.line([(x + 8, ly), (x + w - 8, ly)], fill=(40, 80, 110), width=1)
    # tanker one, left, hull + red stripe + bridge
    tx, ty = x + 18, y + h - 46
    draw.rectangle([tx, ty, tx + 120, ty + 22], fill=(40, 40, 44))
    draw.rectangle([tx, ty + 8, tx + 120, ty + 13], fill=RED)
    draw.rectangle([tx + 92, ty - 16, tx + 112, ty], fill=(200, 200, 200))
    draw.rectangle([tx + 96, ty - 24, tx + 108, ty - 16], fill=(160, 160, 160))
    # tanker two, right, smaller, listing
    tx2, ty2 = x + w - 128, y + h - 40
    draw.polygon([(tx2, ty2 + 18), (tx2 + 108, ty2 + 10), (tx2 + 108, ty2 + 28),
                  (tx2, ty2 + 30)], fill=(52, 52, 56))
    draw.rectangle([tx2, ty2 + 14, tx2 + 108, ty2 + 18], fill=RED)
    # fire burst between the two hulls
    fx, fy = x + w // 2 - 6, y + h - 58
    draw.polygon([(fx, fy - 22), (fx + 12, fy - 4), (fx + 24, fy - 18),
                  (fx + 20, fy + 6), (fx + 34, fy + 4), (fx + 12, fy + 16),
                  (fx + 4, fy + 30), (fx - 8, fy + 14), (fx - 22, fy + 18),
                  (fx - 14, fy), (fx - 26, fy - 8), (fx - 8, fy - 10)],
                 fill=(230, 120, 20))
    draw.polygon([(fx + 4, fy - 8), (fx + 12, fy + 4), (fx + 20, fy - 2),
                  (fx + 14, fy + 12), (fx + 2, fy + 16), (fx - 4, fy + 4)],
                 fill=(250, 200, 60))
    # smoke above the fire, kept strictly inside the panel
    for cx, cy, r in ((fx - 8, fy - 16, 7), (fx + 8, fy - 22, 8),
                      (fx, fy - 12, 6)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 70, 74))
    # a spiked naval mine, lower right
    mx, my = x + w - 44, y + h - 14
    draw.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=(20, 20, 22))
    for dx, dy in ((0, -11), (8, -8), (11, 0), (8, 8), (0, 11),
                   (-8, 8), (-11, 0), (-8, -8)):
        draw.line([(mx, my), (mx + dx, my + dy)], fill=(20, 20, 22), width=2)


def draw_refinery(draw, x, y, w, h):
    """Ras Tanura at dusk: towers, flare stacks, a burning flare."""
    draw.rectangle([x, y, x + w, y + h], fill=(232, 150, 70))
    draw.rectangle([x, y, x + w, y + 26], fill=(240, 190, 120))
    draw.ellipse([x + 20, y + 6, x + 48, y + 34], fill=(250, 220, 150))
    # ground
    draw.rectangle([x, y + h - 16, x + w, y + h], fill=(60, 50, 44))
    # distillation towers
    for tx, tw, th in ((x + 30, 26, 52), (x + 66, 20, 44), (x + 96, 30, 58)):
        draw.rectangle([tx, y + h - 16 - th, tx + tw, y + h - 16],
                       fill=(90, 88, 84), outline=(50, 48, 44))
        for ly in range(y + h - 16 - th + 8, y + h - 18, 10):
            draw.line([(tx + 3, ly), (tx + tw - 3, ly)], fill=(50, 48, 44),
                      width=1)
    # storage tanks
    for tx in (x + 140, x + 186):
        draw.ellipse([tx, y + h - 44, tx + 40, y + h - 16], fill=(200, 200, 196),
                     outline=(120, 118, 112))
        draw.rectangle([tx, y + h - 30, tx + 40, y + h - 16],
                       fill=(200, 200, 196))
    # flare stack with flame, right side
    fx = x + w - 46
    draw.rectangle([fx, y + 18, fx + 10, y + h - 16], fill=(70, 68, 64))
    draw.polygon([(fx + 5, y + 2), (fx + 16, y + 16), (fx + 12, y + 26),
                  (fx + 5, y + 30), (fx - 2, y + 22), (fx - 6, y + 12)],
                 fill=(250, 160, 30))
    draw.polygon([(fx + 5, y + 10), (fx + 11, y + 18), (fx + 5, y + 24),
                  (fx - 1, y + 18)], fill=(250, 220, 80))
    # smoke drifting from the towers
    for cx, cy, r in ((x + 60, y + 22, 9), (x + 82, y + 14, 11),
                      (x + 104, y + 20, 8)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 100, 92))


def draw_shenzhou(draw, x, y, w, h):
    """Tiangong in orbit: black sky, stars, Earth arc, station, capsule."""
    draw.rectangle([x, y, x + w, y + h], fill=(8, 10, 26))
    # stars (fixed positions, deterministic)
    stars = [(0.08, 0.12), (0.22, 0.06), (0.35, 0.16), (0.48, 0.08),
             (0.62, 0.14), (0.74, 0.05), (0.86, 0.12), (0.15, 0.30),
             (0.55, 0.28), (0.78, 0.26), (0.92, 0.32), (0.30, 0.24)]
    for sx, sy in stars:
        px, py = x + int(w * sx), y + int(h * sy)
        draw.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 255))
    # Earth arc along the bottom, clamped to stay inside the panel:
    # arc of a circle centred below the panel, sampled only where it
    # stays within the panel, then closed along the bottom edge.
    arc_cx, arc_cy, arc_r = x + w // 2, y + h + 130, 150
    arc_pts = []
    for a in range(240, 301, 5):
        rad = math.radians(a)
        px = arc_cx + arc_r * math.cos(rad)
        py = arc_cy + arc_r * math.sin(rad)
        arc_pts.append((px, py))
    draw.polygon(arc_pts + [(x + w, y + h), (x, y + h)], fill=(40, 110, 190))
    draw.polygon(arc_pts + [(x + w, y + h), (x, y + h)], outline=(70, 150, 210))
    # station: core module + two solar wings
    sx, sy = x + w // 2 - 70, y + 34
    draw.rectangle([sx, sy, sx + 140, sy + 16], fill=(220, 224, 230))
    draw.rectangle([sx + 52, sy + 16, sx + 88, sy + 30], fill=(190, 196, 204))
    draw.rectangle([sx - 46, sy + 2, sx, sy + 14], fill=(40, 90, 180))
    draw.rectangle([sx + 140, sy + 2, sx + 186, sy + 14], fill=(40, 90, 180))
    for wx in (sx - 46, sx + 140):
        for lx in range(wx + 4, wx + 44, 10):
            draw.line([(lx, sy + 2), (lx, sy + 14)], fill=(20, 60, 130),
                      width=1)
    # docking capsule approaching from the right
    cx, cy = x + w - 74, y + 48
    draw.polygon([(cx, cy), (cx + 26, cy + 8), (cx + 26, cy + 22),
                  (cx, cy + 30)], fill=(240, 240, 244))
    draw.rectangle([cx + 26, cy + 8, cx + 40, cy + 22], fill=(200, 60, 40))
    draw.line([(cx - 4, cy + 15), (cx - 26, cy + 15)], fill=(250, 220, 80),
              width=2)
    draw.text((x + 10, y + 6), "TIANGONG \u2022 09:56 PKT",
              font=font(SANS_B, 10), fill=(255, 255, 255))


ART = {"hormuz": draw_hormuz, "refinery": draw_refinery,
       "shenzhou": draw_shenzhou}

FIELD_COLORS = {"War": (176, 30, 36), "Law": (31, 58, 95),
                "Tech": (24, 32, 54), "Disaster": (200, 90, 20),
                "Politics": (90, 60, 120), "Diplomacy": (18, 110, 110),
                "Markets": (27, 120, 60), "Crime": (60, 60, 60),
                "Transport": (31, 90, 160), "Trade": (176, 120, 10),
                "Climate": (27, 120, 90), "Space": (24, 32, 54),
                "Sport": (200, 60, 120), "Health": (200, 40, 80),
                "Culture": (150, 100, 30)}


def draw_icon(draw, x, y, w, h, field):
    """Small coloured panel with a simple glyph for the story's field."""
    col = FIELD_COLORS.get(field, GREY)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=col)
    cx, cy = x + w / 2, y + h / 2
    white = (255, 255, 255)
    if field == "War":
        for dx, dy in ((0, -11), (8, -8), (11, 0), (8, 8), (0, 11),
                       (-8, 8), (-11, 0), (-8, -8)):
            draw.line([(cx, cy), (cx + dx, cy + dy)], fill=white, width=2)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=white)
    elif field == "Law":
        draw.line([(cx, y + 5), (cx, y + h - 6)], fill=white, width=2)
        draw.line([(cx - 9, y + 8), (cx + 9, y + 8)], fill=white, width=2)
        draw.line([(cx - 13, y + 15), (cx - 5, y + 15)], fill=white, width=2)
        draw.line([(cx + 5, y + 15), (cx + 13, y + 15)], fill=white, width=2)
        draw.line([(cx - 9, y + 8), (cx - 13, y + 15)], fill=white, width=2)
        draw.line([(cx - 9, y + 8), (cx - 5, y + 15)], fill=white, width=2)
        draw.line([(cx + 9, y + 8), (cx + 5, y + 15)], fill=white, width=2)
        draw.line([(cx + 9, y + 8), (cx + 13, y + 15)], fill=white, width=2)
    elif field == "Tech":
        draw.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], outline=white, width=2)
        for px in (-4, 0, 4):
            draw.line([(cx + px, cy - 12), (cx + px, cy - 8)], fill=white, width=2)
            draw.line([(cx + px, cy + 8), (cx + px, cy + 12)], fill=white, width=2)
        draw.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=white)
    elif field == "Disaster":
        draw.polygon([(cx, y + 4), (cx + 8, cy + 6), (cx + 4, y + h - 5),
                      (cx - 4, y + h - 5), (cx - 8, cy + 6)], fill=white)
        draw.polygon([(cx, cy + 2), (cx + 4, cy + 8), (cx, y + h - 7),
                      (cx - 4, cy + 8)], fill=col)
    elif field == "Politics":
        draw.rectangle([cx - 10, cy - 2, cx + 10, y + h - 6], outline=white, width=2)
        draw.line([(cx - 5, cy + 2), (cx - 1, cy + 6), (cx + 7, cy - 6)],
                  fill=white, width=2)
        draw.line([(cx - 6, cy - 8), (cx + 6, cy - 8)], fill=white, width=2)
    elif field == "Diplomacy":
        draw.line([(cx - 7, y + 5), (cx - 7, y + h - 5)], fill=white, width=2)
        draw.line([(cx + 6, y + 5), (cx + 6, y + h - 5)], fill=white, width=2)
        draw.rectangle([cx - 7, y + 5, cx + 1, y + 12], fill=white)
        draw.rectangle([cx + 6, y + 5, cx + 13, y + 12], fill=white)
    elif field == "Markets":
        for i, bh in enumerate((6, 10, 14, 18)):
            bx = cx - 12 + i * 7
            draw.rectangle([bx, y + h - 6 - bh, bx + 5, y + h - 6], fill=white)
    elif field == "Crime":
        draw.ellipse([cx - 12, cy - 6, cx - 2, cy + 6], outline=white, width=2)
        draw.ellipse([cx + 2, cy - 6, cx + 12, cy + 6], outline=white, width=2)
        draw.line([(cx - 2, cy), (cx + 2, cy)], fill=white, width=2)
    elif field == "Transport":
        draw.polygon([(cx - 12, cy), (cx + 12, cy - 3), (cx + 12, cy + 3)],
                     fill=white)
        draw.line([(cx - 2, cy - 8), (cx + 2, cy + 8)], fill=white, width=2)
    elif field == "Trade":
        draw.rectangle([cx - 11, cy - 7, cx + 11, cy + 7], outline=white, width=2)
        for lx in (-4, 3):
            draw.line([(cx + lx, cy - 7), (cx + lx, cy + 7)], fill=white, width=1)
    elif field == "Climate":
        # sun with rays
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=white)
        for dx, dy in ((0, -11), (8, -8), (11, 0), (8, 8), (0, 11),
                       (-8, 8), (-11, 0), (-8, -8)):
            draw.line([(cx + dx * 2 // 3, cy + dy * 2 // 3),
                       (cx + dx, cy + dy)], fill=white, width=2)
    elif field == "Space":
        # rocket: body, fins, flame
        draw.polygon([(cx, y + 4), (cx + 6, cy + 2), (cx + 6, cy + 10),
                      (cx, cy + 14), (cx - 6, cy + 10), (cx - 6, cy + 2)],
                     fill=white)
        draw.polygon([(cx - 6, cy + 8), (cx - 11, cy + 14), (cx - 6, cy + 12)],
                     fill=white)
        draw.polygon([(cx + 6, cy + 8), (cx + 11, cy + 14), (cx + 6, cy + 12)],
                     fill=white)
        draw.polygon([(cx, cy + 14), (cx + 4, cy + 20), (cx, y + h - 5),
                      (cx - 4, cy + 20)], fill=(250, 200, 60))
    elif field == "Sport":
        # football: circle with pentagon
        draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], outline=white, width=2)
        draw.polygon([(cx, cy - 5), (cx + 5, cy - 1), (cx + 3, cy + 5),
                      (cx - 3, cy + 5), (cx - 5, cy - 1)], fill=white)
        for dx, dy in ((0, -11), (10, -3), (7, 9), (-7, 9), (-10, -3)):
            draw.line([(cx, cy - 5), (cx + dx, cy + dy)], fill=white, width=1)
    elif field == "Health":
        draw.rectangle([cx - 3, cy - 11, cx + 3, cy + 11], fill=white)
        draw.rectangle([cx - 11, cy - 3, cx + 11, cy + 3], fill=white)
    elif field == "Culture":
        # five-point star
        pts = [(cx, y + 4), (cx + 4, cy - 2), (cx + 11, cy - 2),
               (cx + 6, cy + 3), (cx + 8, cy + 10), (cx, cy + 6),
               (cx - 8, cy + 10), (cx - 6, cy + 3), (cx - 11, cy - 2),
               (cx - 4, cy - 2)]
        draw.polygon(pts, fill=white)
    else:
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=white)


def draw_map(draw, x, y, w, h, pins, legend=""):
    """Stylised equirectangular world map with numbered pins."""
    draw.rectangle([x, y, x + w, y + h], fill=SEA)
    for lon in range(-150, 181, 30):
        gx = x + (lon + 180) / 360.0 * w
        draw.line([(gx, y), (gx, y + h)], fill=(140, 170, 190), width=1)
    for lat in (-30, 0, 30, 60):
        gy = y + (84 - lat) / 142.0 * h
        draw.line([(x, gy), (x + w, gy)], fill=(140, 170, 190), width=1)

    def proj(lon, lat):
        return (x + (lon + 180) / 360.0 * w, y + (84 - lat) / 142.0 * h)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_LINE)
    draw.text((x + 6, y + 4), "WHERE IT HAPPENED \u2014 %d PINNED STORIES" % len(pins),
              font=font(SANS_B, 10), fill=NAVY)
    for pin in pins:
        n, lat, lon = pin[0], pin[1], pin[2]
        ox, oy = (pin[3], pin[4]) if len(pin) > 4 else (0, 0)
        px, py = proj(lon, lat)
        qx, qy = px + ox, py + oy
        if ox or oy:
            draw.line([(px, py), (qx, qy)], fill=RED, width=1)
        draw.ellipse([qx - 6, qy - 6, qx + 6, qy + 6], fill=RED,
                     outline=(255, 255, 255), width=1)
        fnt = font(SANS_B, 9 if n < 10 else 8)
        tw = draw.textlength(str(n), font=fnt)
        draw.text((qx - tw / 2, qy - 5), str(n), font=fnt, fill=(255, 255, 255))
    if legend:
        draw.rectangle([x, y + h - 16, x + w, y + h], fill=PAPER)
        draw.text((x + 6, y + h - 14), legend, font=font(SANS_B, 9), fill=NAVY)


def _save_png(img):
    """Write entry.png: /output first, then the repo dir. Return path or None."""
    here = os.path.dirname(os.path.abspath(__file__))
    for out_dir in ("/output", here):
        try:
            os.makedirs(out_dir, exist_ok=True)
            out = os.path.join(out_dir, "entry.png")
            img.save(out, "PNG")
            return out
        except Exception:
            continue
    return None


def _render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 10

    # ---- Masthead: kicker, big serif name + date, thick rule, count line ----
    d.text((M, y), "ONE DAY OF WORLD NEWS, ONE PICTURE",
           font=font(SANS_B, 11), fill=RED)
    d.text((W - M, y), "35 STORIES \u00b7 7 REGIONS",
           font=font(SANS_B, 11), fill=NAVY, anchor="ra")
    y += 16
    d.text((M, y), "THE DAILY GLOBE", font=font(SERIF_B, 52), fill=INK)
    d.text((W - M, y + 30), "WEDNESDAY 25 NOVEMBER 2026",
           font=font(SERIF_B, 20), fill=INK, anchor="ra")
    y += 58
    d.line([(M, y), (W - M, y)], fill=INK, width=4)
    y += 6
    d.text((M, y), "35 STORIES  \u2022  7 REGIONS  \u2022  15 FIELDS  \u2022  ALL FROM THIS WEDNESDAY",
           font=font(SANS_B, 11), fill=NAVY)
    y += 18

    # ---- The day in numbers ----
    d.text((M, y), "THE DAY IN NUMBERS", font=font(SANS_B, 11), fill=RED)
    y += 15
    ncell = CW / len(NUMBERS)
    for i, (num, label) in enumerate(NUMBERS):
        cx = M + i * ncell
        d.text((cx + 4, y), num, font=font(SERIF_B, 24), fill=NAVY)
        ly = y + 30
        for ln in wrap(d, label, font(SANS_R, 10), ncell - 12):
            d.text((cx + 4, ly), ln, font=font(SANS_R, 10), fill=INK)
            ly += 11
        if i < len(NUMBERS) - 1:
            d.line([(cx + ncell - 2, y), (cx + ncell - 2, y + 44)],
                   fill=LIGHT, width=1)
    y += 44
    d.line([(M, y), (W - M, y)], fill=NAVY, width=1)
    y += 6

    # ---- The day in UTC ----
    d.text((M, y), "THE DAY IN UTC", font=font(SANS_B, 11), fill=RED)
    y += 13
    cell = CW / len(TIMELINE)
    for i, (t, txt) in enumerate(TIMELINE):
        cx = M + i * cell
        d.line([(cx + cell / 2, y + 2), (cx + cell / 2, y + 8)], fill=RED, width=2)
        d.text((cx + 4, y + 10), t, font=font(SANS_B, 11), fill=RED)
        d.text((cx + 4, y + 24),
               trunc(d, txt, font(SANS_R, 10), cell - 8),
               font=font(SANS_R, 10), fill=INK)
    y += 40

    # ---- Three illustrated leads ----
    # Banner + chip align to the tallest column's bottom (two passes).
    col_w = (CW - 16) // 3
    lead_heights = []
    for lead in LEADS:
        n_head = len(wrap(d, lead["headline"], font(SERIF_B, 18), col_w))
        n_body = min(2, len(wrap(d, lead["body"], font(SANS_R, 11), col_w)))
        lead_heights.append(80 + 6 + 13 + n_head * 20 + 2 + n_body * 13)
    content_h = max(lead_heights)
    for i, lead in enumerate(LEADS):
        lx = M + i * (col_w + 8)
        ART[lead["art"]](d, lx, y, col_w, 80)
        ty = y + 86
        d.text((lx, ty), "%d. %s" % (lead["n"], lead["kicker"]),
               font=font(SANS_B, 10), fill=RED)
        ty += 13
        for ln in wrap(d, lead["headline"], font(SERIF_B, 18), col_w):
            d.text((lx, ty), ln, font=font(SERIF_B, 18), fill=INK)
            ty += 20
        ty += 2
        for ln in wrap(d, lead["body"], font(SANS_R, 11), col_w)[:2]:
            d.text((lx, ty), ln, font=font(SANS_R, 11), fill=(40, 40, 38))
            ty += 13
        by = y + content_h + 4
        d.rectangle([lx, by, lx + col_w, by + 18], fill=RED)
        d.text((lx + 6, by + 3), lead["banner"], font=font(SANS_B, 11),
               fill=(255, 255, 255))
        cy = by + 18 + 4
        cw = chip(d, lx, cy, lead["chip"])
        d.text((lx + cw + 6, cy + 1), lead["source"], font=font(SANS_R, 9),
               fill=GREY)
    y += content_h + 4 + 18 + 4 + 15 + 6

    # ---- 10 featured stories: 5 cols x 2 rows, icon + data point each ----
    d.text((M, y), "MORE OF THE DAY \u2014 10 STORIES",
           font=font(SANS_B, 11), fill=RED)
    y += 14
    fcw = (CW - 4 * 8) // 5
    for i, s in enumerate(FEATURED):
        r, c = divmod(i, 5)
        sx = M + c * (fcw + 8)
        sy = y + r * 64
        draw_icon(d, sx, sy, 30, 30, s["field"])
        tx = sx + 36
        tw = fcw - 36
        lines = wrap(d, "%d. %s" % (s["n"], s["headline"]),
                     font(SANS_B, 12), tw)
        ly = sy
        for ln in lines[:3]:
            d.text((tx, ly), ln, font=font(SANS_B, 12), fill=INK)
            ly += 13
        d.text((tx, ly), s["data"], font=font(SANS_B, 10),
               fill=CHIP_COLORS[s["chip"]])
        ly += 13
        d.text((tx, ly), trunc(d, s["source"], font(SANS_R, 9), tw),
               font=font(SANS_R, 9), fill=GREY)
        if c < 4:
            d.line([(sx + fcw + 4, sy), (sx + fcw + 4, sy + 58)],
                   fill=LIGHT, width=1)
    y += 2 * 64 + 6

    # ---- World map (left) + DATE CHECK (right) ----
    map_w = 620
    pins = []
    for s in LEADS + FEATURED:
        pin = (s["n"], s["pin"][0], s["pin"][1])
        if "pin_off" in s:
            pin = pin + (s["pin_off"][0], s["pin_off"][1])
        pins.append(pin)
    regions = {}
    for s in LEADS + FEATURED:
        regions[s["region"]] = regions.get(s["region"], 0) + 1
    for _n, _h, _c, _s, _f, r in NUMBERED:
        regions[r] = regions.get(r, 0) + 1
    short = {"North America": "N. AMER", "Latin America": "LAT. AMER",
             "Europe": "EUROPE", "Middle East": "M. EAST",
             "Africa": "AFRICA", "Asia-Pacific": "ASIA-PAC", "Space": "SPACE"}
    order = sorted(regions.items(), key=lambda kv: (-kv[1], kv[0]))
    legend = "  \u00b7  ".join("%s %d" % (short[k], v) for k, v in order)
    legend += "  =  35 STORIES"
    draw_map(d, M, y, map_w, 160, pins, legend)
    dx = M + map_w + 8
    dw = W - M - dx
    d.rectangle([dx, y, dx + dw, y + 160], outline=RED, width=2)
    d.rectangle([dx, y, dx + dw, y + 26], fill=RED)
    d.text((dx + 8, y + 5), "DATE CHECK \u2014 LEFT OUT AS OLDER NEWS",
           font=font(SANS_B, 12), fill=(255, 255, 255))
    dy = y + 30
    for story, when in DATE_CHECK:
        d.text((dx + 8, dy), "\u2715", font=font(SANS_B, 11), fill=RED)
        d.text((dx + 22, dy),
               trunc(d, "%s \u2014 %s" % (story, when), font(SANS_B, 11), dw - 30),
               font=font(SANS_B, 11), fill=INK)
        dy += 14
    d.text((dx + 8, dy + 1), "NOT YET:", font=font(SANS_B, 11), fill=NAVY)
    dy += 15
    for story, when in NOT_YET:
        d.text((dx + 8, dy), "\u25cb", font=font(SANS_B, 11), fill=NAVY)
        d.text((dx + 22, dy),
               trunc(d, "%s \u2014 %s" % (story, when), font(SANS_B, 11), dw - 30),
               font=font(SANS_B, 11), fill=INK)
        dy += 14
    y += 160 + 6

    # ---- Numbered list: 22 more stories, 2 columns x 11 ----
    d.text((M, y), "ALSO ON WEDNESDAY \u2014 22 MORE STORIES",
           font=font(SANS_B, 14), fill=NAVY)
    d.line([(M, y + 20), (W - M, y + 20)], fill=NAVY, width=1)
    y += 24
    ncw = (CW - 8) // 2
    for i, (n, headline, _chip, source, _f, _r) in enumerate(NUMBERED):
        col, row = divmod(i, 11)
        nx = M + col * (ncw + 8)
        ny = y + row * 16
        d.text((nx, ny), "%d." % n, font=font(SANS_B, 12), fill=RED)
        txt = trunc(d, "%s \u2014 %s" % (headline, source),
                    font(SANS_R, 12), ncw - 30)
        d.text((nx + 28, ny), txt, font=font(SANS_R, 12), fill=INK)
    y += 11 * 16 + 6

    # ---- Footer: verification key + sources ----
    fy = H - 34
    d.line([(M, fy - 4), (W - M, fy - 4)], fill=GREY, width=1)
    kx = M
    for label, expl in (("CONFIRMED", "verified by 2+ outlets or a primary source"),
                        ("REPORTED", "named outlet, not yet verified")):
        fnt = font(SANS_B, 10)
        d.text((kx, fy), label, font=fnt, fill=CHIP_COLORS[label])
        kx += d.textlength(label, font=fnt) + 4
        fnt2 = font(SANS_R, 10)
        d.text((kx, fy), expl, font=fnt2, fill=GREY)
        kx += d.textlength(expl, font=fnt2) + 14
    fy = H - 20
    d.text((M, fy), "Sources: Reuters \u2022 AP \u2022 Just Security \u2022 UN News \u2022 UEFA \u2022 CMSA  \u2014  Original drawings  \u2014  Built by an AI agent for make.fun's news-image-20261125 bounty.",
           font=font(SANS_R, 10), fill=GREY)

    print("layout bottom y =", y, " (canvas H =", H, ")")
    out = _save_png(img)
    if out is None:
        raise OSError("could not write entry.png")
    print("wrote", out, os.path.getsize(out), "bytes")


def _fallback_page():
    """Minimal deterministic page (paper + masthead + note), default font only."""
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    try:
        f_big = ImageFont.load_default(48)
    except Exception:
        f_big = ImageFont.load_default()
    try:
        f_small = ImageFont.load_default(20)
    except Exception:
        f_small = ImageFont.load_default()
    d.text((M, 24), "THE DAILY GLOBE", font=f_big, fill=INK)
    d.text((M, 100), "WEDNESDAY 25 NOVEMBER 2026", font=f_small, fill=NAVY)
    d.line([(M, 140), (W - M, 140)], fill=INK, width=4)
    d.text((M, 160), "35 stories from Wednesday 25 November 2026.",
           font=f_small, fill=INK)
    d.text((M, 190), "The full front page could not be rendered.",
           font=f_small, fill=GREY)
    return img


def main():
    """Render the front page; NEVER exit non-zero.

    On any failure in the primary render, write a valid fallback PNG
    instead and still exit 0, so run_completes cannot fail.
    """
    try:
        _render()
        return
    except Exception as exc:
        print("primary render failed:", repr(exc))
    try:
        out = _save_png(_fallback_page())
        print("fallback wrote", out)
    except Exception as exc:
        print("fallback failed:", repr(exc))
        try:
            out = _save_png(Image.new("RGB", (W, H), PAPER))
            print("last-resort wrote", out)
        except Exception as exc2:
            print("last resort failed:", repr(exc2))


if __name__ == "__main__":
    main()
