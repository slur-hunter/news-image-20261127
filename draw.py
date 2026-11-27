#!/usr/bin/env python3
"""Render the 27 November 2026 front page as a 1024x1024 PNG.

Written fresh for the news-image-20261127 entry. No network access,
no randomness: the same input always produces the same bytes.

Run: python3 draw.py [output.png]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (176, 30, 36)
NAVY = (31, 58, 95)
MUTED = (110, 105, 95)
FAINT = (70, 65, 55)
FONTDIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONTDIR + name, size)


SERIFB = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANSB = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


class Sheet:
    """A thin wrapper around an ImageDraw so sections read like layout."""

    def __init__(self):
        self.img = Image.new("RGB", (PAGE, PAGE), PAPER)
        self.d = ImageDraw.Draw(self.img)

    def line(self, x0, y0, x1, y1, fill=INK, width=1):
        self.d.line([(x0, y0), (x1, y1)], fill=fill, width=width)

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=width)

    def text(self, x, y, s, f, fill=INK, anchor="la"):
        self.d.text((x, y), s, font=f, fill=fill, anchor=anchor)

    def centre(self, x, y, s, f, fill=INK):
        self.d.text((x, y), s, font=f, fill=fill, anchor="ma")

    def wrap(self, s, f, width):
        out, cur = [], ""
        for w in s.split():
            trial = (cur + " " + w).strip()
            if self.d.textlength(trial, font=f) <= width:
                cur = trial
            else:
                if cur:
                    out.append(cur)
                cur = w
        if cur:
            out.append(cur)
        return out

    def save(self, path):
        self.img.save(path, format="PNG")


# ------------------------------------------------------------------ data
# Six numbers from the day, each with a two-line label.
NUMBERS = [
    {"value": "500,000+", "label": ["HOMES WITHOUT POWER", "IN THE STORM"]},
    {"value": "$12.9bn", "label": ["BLACK FRIDAY ONLINE", "SALES FORECAST"]},
    {"value": "67 of 131", "label": ["NZ COALITION SEATS", "FINAL COUNT"]},
    {"value": "1", "label": ["KILLED IN JAZAN", "REFINERY ATTACK"]},
    {"value": "204", "label": ["SOORYAVANSHI RUNS", "OFF 53 BALLS"]},
    {"value": "$1tn", "label": ["US HOLIDAY SALES", "FIRST TIME OVER $1TN"]},
]
# Region bars: name, story count, dot colour. Counts sum to 50.
REGIONS = [
    {"name": "N. AMERICA", "n": 12, "colour": (176, 30, 36)},
    {"name": "S. AMERICA", "n": 2, "colour": (31, 120, 90)},
    {"name": "EUROPE", "n": 12, "colour": (31, 58, 95)},
    {"name": "MIDDLE EAST", "n": 2, "colour": (190, 120, 30)},
    {"name": "AFRICA", "n": 2, "colour": (120, 80, 30)},
    {"name": "S. ASIA", "n": 8, "colour": (200, 90, 40)},
    {"name": "E. ASIA & PACIFIC", "n": 12, "colour": (90, 90, 160)},
]
# The four lead stories: number, kicker, headline, body, source, picture.
LEADS = [
    {"num": 1, "kicker": "STORM  ·  NEW YORK",
     "head": "Storm cuts power to 500,000; parade moves",
     "body": "High winds cut power to over half a million homes; the 100th Macy's parade moves to Saturday.",
     "source": "NEWSTALK ZB / REUTERS", "art": "parade"},
    {"num": 2, "kicker": "JAZAN  ·  SAUDI ARABIA",
     "head": "Houthi projectile hits Jazan refinery; one killed",
     "body": "A hostile aerial projectile strikes the Jazan refinery and starts a fire; one is killed and several are hurt.",
     "source": "SAUDI GAZETTE", "art": "refinery"},
    {"num": 3, "kicker": "ELECTION  ·  WELLINGTON",
     "head": "Final count gives NZ coalition a slim 67-seat majority",
     "body": "Final results, with about 400,000 special votes counted, give the coalition 67 of 131 seats.",
     "source": "NEWSTALK ZB", "art": "ballot"},
    {"num": 4, "kicker": "MIGRATION  ·  LONDON",
     "head": "UK net migration falls to near three-decade low",
     "body": "Net migration falls to almost its lowest in nearly three decades, excluding the pandemic slump, official figures show.",
     "source": "ARAB NEWS", "art": "chart"},
]

# Ten short cards, stories 5 to 14: number, kicker, headline, source, band.
CARDS = [
    {"num": 5, "kicker": "BLACK FRIDAY  ·  USA",
     "head": "Black Friday online sales seen at $12.9bn",
     "source": "ADOBE / XTB", "band": (176, 30, 36)},
    {"num": 6, "kicker": "DEPORTATION  ·  WASHINGTON",
     "head": "Abrego Garcia leaves US for Spain",
     "source": "CBS / BBC", "band": (31, 58, 95)},
    {"num": 7, "kicker": "PLOT  ·  BERLIN",
     "head": "Germany arrests two Iraqis over synagogue attack plot",
     "source": "ARAB NEWS", "band": (60, 60, 60)},
    {"num": 8, "kicker": "SPILL  ·  IBIZA",
     "head": "Spain races to stop oil spill off Ibiza",
     "source": "ARAB NEWS", "band": (31, 90, 120)},
    {"num": 9, "kicker": "ANNIVERSARY  ·  HONG KONG",
     "head": "Hong Kong marks deadly fire anniversary",
     "source": "ARAB NEWS", "band": (150, 60, 40)},
    {"num": 10, "kicker": "CRICKET  ·  INDIA",
     "head": "Sooryavanshi smashes 204 off 53 balls",
     "source": "TIMES OF INDIA", "band": (200, 110, 30)},
    {"num": 11, "kicker": "BORDER  ·  BEIJING",
     "head": "China: India-China border areas 'generally stable'",
     "source": "REUTERS", "band": (120, 40, 40)},
    {"num": 12, "kicker": "STRIKE  ·  BRASILIA",
     "head": "Brazil postal strike hits Black Friday deliveries",
     "source": "WHY IT LANDS", "band": (30, 120, 80)},
    {"num": 13, "kicker": "MINE  ·  JAKARTA",
     "head": "Indonesia searches for trapped gold miners",
     "source": "TIMES OF INDIA", "band": (90, 90, 60)},
    {"num": 14, "kicker": "DEFENCE  ·  HELSINKI",
     "head": "Five European nations buy combat vehicles from BAE",
     "source": "ARAB NEWS", "band": (31, 58, 95)},
]
# The numbered also-on list, stories 15 to 50: number, one line, source.
REST = [
    (15, "NYSE and Nasdaq run a half-day Black Friday session", "AP"),
    (16, "S&P futures point to Black Friday gains", "MORNINGSTAR"),
    (17, "Bitcoin trades at $60,695, up 2.9%", "TRADINGVIEW"),
    (18, "Mastercard sees holiday retail up 5.5%", "XTB"),
    (19, "Salesforce sees $357bn in Cyber Week online sales", "XTB"),
    (20, "US retail stocks up 3.5% this year, behind the S&P 500", "XTB"),
    (21, "Cyber Monday seen at $15.1bn online", "ADOBE / XTB"),
    (22, "Canada left out of new US tariff proposal", "COLLECTOR"),
    (23, "Pacific Northwest hit by a second storm", "NEWSTALK ZB"),
    (24, "Consumer NZ warns half of Black Friday deals are no cheaper", "CONSUMER NZ"),
    (25, "NZ English curriculum on hold until a new government forms", "NEWSTALK ZB"),
    (26, "NZ driver licence waits reach 80 days in places", "NEWSTALK ZB"),
    (27, "Barrett to captain the All Blacks for the first time", "NEWSTALK ZB"),
    (28, "Kibori tied second after day one of the Australian PGA", "NEWSTALK ZB"),
    (29, "India and New Zealand start the second Test in Christchurch", "NEWSTALK ZB"),
    (30, "Sinner out of the 2027 Australian Open with a knee injury", "THE DAILY JAGRAN"),
    (31, "Philippines defence exercise runs through 27 November", "MITHRIL"),
    (32, "Tata Trusts to move High Court over Chandrasekaran", "THE DAILY JAGRAN"),
    (33, "Kharge: U.P. taught BJP a lesson in the 2024 polls", "THE DAILY JAGRAN"),
    (34, "India's top court wants stronger food warning labels", "EDUCATION TIMES"),
    (35, "Advani wins the historic Crucible Cup", "EDUCATION TIMES"),
    (36, "Vaziralli reaches the QSF 5 squash final", "EDUCATION TIMES"),
    (37, "Flipkart chief to step down next month", "EDUCATION TIMES"),
    (38, "EPFO plans a major digital upgrade in February 2027", "EDUCATION TIMES"),
    (39, "German court rejects AfD youth-wing gun permit revocations", "ARAB NEWS"),
    (40, "Macron slams Le Pen 'arrogance'", "ARAB NEWS"),
    (41, "Romania seeks a bigger German role amid Russian provocations", "ARAB NEWS"),
    (42, "Meloni talks tough on the EU budget", "ARAB NEWS"),
    (43, "Pro-monarchist Iran activists disrupt a Paris event", "ARAB NEWS"),
    (44, "Man guilty of attempted murders of 14, ten on a London train", "ARAB NEWS"),
    (45, "Ukrainian long-range strikes spreading across the globe", "ARAB NEWS"),
    (46, "Allegro shares up 112% this year", "XTB"),
    (47, "Hostage recounts the 17-hour Cartagena supermarket siege", "ARAB NEWS"),
    (48, "Houthi drone intercepted near Jeddah Islamic Port", "SAUDI GAZETTE"),
    (49, "Nigerian governor declares 27 November a workers' holiday", "LEGIT.NG"),
    (50, "Kenya's PMI 55.0 tops Africa's private-sector growth", "BUSINESSDAY"),
]
# Real stories from other days, named so the reader knows they were left out.
NOT_TODAY = [
    ("Two Italians killed in Kuwait drone attack", "26 Nov"),
    ("Bangkok refinery fire injures nine", "26 Nov"),
    ("Ramaphosa wins court bid on impeachment report", "25 Nov"),
    ("Israeli judges urge dropping Netanyahu Case 4000", "25 Nov"),
]
# Map pins for stories 1 to 14: number, longitude, latitude.
PINS = [
    (1, -74, 41), (2, 42, 17), (3, 175, -41), (4, 0, 51),
    (5, -95, 39), (6, -77, 39), (7, 13, 52), (8, 1, 39),
    (9, 114, 22), (10, 78, 21), (11, 116, 40), (12, -48, -16),
    (13, 107, -6), (14, 25, 60),
]
# Rough continent outlines as (lon, lat) chains, for the schematic map.
LAND = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 62),
     (-55, 47), (-70, 42), (-75, 35), (-80, 25), (-85, 20), (-90, 15),
     (-95, 18), (-105, 22), (-115, 30), (-125, 40), (-125, 50), (-150, 60)],
    [(-80, 10), (-60, 5), (-50, 0), (-35, -5), (-40, -20), (-50, -30),
     (-60, -40), (-70, -50), (-75, -35), (-80, -20)],
    [(-10, 36), (-5, 44), (0, 50), (5, 58), (10, 60), (20, 70), (30, 70),
     (40, 68), (30, 60), (25, 55), (20, 45), (15, 40), (10, 38), (0, 36)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 10), (48, 0), (40, -10), (35, -25), (30, -35), (20, -35),
     (15, -20), (12, -5), (9, 4), (-8, 5)],
    [(40, 68), (60, 70), (90, 75), (120, 75), (150, 70), (170, 66), (160, 60),
     (140, 55), (130, 45), (127, 40), (120, 30), (110, 20), (105, 10),
     (100, 8), (95, 15), (90, 22), (80, 10), (75, 8), (70, 20), (60, 25),
     (50, 28), (43, 12), (40, 30), (40, 40)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (135, -12), (130, -13), (122, -17)],
]


# ------------------------------------------------------------- pictures
def draw_parade(s, x0, y0, x1, y1):
    """Night sky over a parade route: rain, lit towers, a balloon, 100."""
    d = s.d
    s.rect(x0, y0, x1, y1, fill=(28, 42, 74))
    for i in range(6):  # rain slashes
        d.line([(x0 + 12 + i * 22, y0 + 6), (x0 + 6 + i * 22, y0 + 26)],
               fill=(140, 170, 220), width=2)
    for bx in (x0 + 8, x0 + 52, x0 + 96):  # towers with lit windows
        s.rect(bx, y1 - 40, bx + 34, y1 - 6, fill=(12, 20, 40))
        for wy in range(y1 - 36, y1 - 8, 10):
            s.rect(bx + 5, wy, bx + 11, wy + 5, fill=(240, 200, 80))
    cx = (x0 + x1) // 2
    d.ellipse([cx - 26, y0 + 12, cx + 26, y0 + 50], fill=(200, 40, 50),
              outline=(255, 255, 255), width=2)
    d.polygon([(cx - 8, y0 + 50), (cx + 8, y0 + 50), (cx, y0 + 62)],
              fill=(200, 40, 50))
    s.rect(x0 + 6, y1 - 20, x0 + 78, y1 - 6, fill=RED)
    s.text(x0 + 10, y1 - 19, "100", SANSB(11), fill=(255, 255, 255))


def draw_refinery(s, x0, y0, x1, y1):
    """Refinery at dusk: tanks, a flame, smoke, a low sun."""
    d = s.d
    s.rect(x0, y0, x1, y1, fill=(245, 180, 90))
    s.rect(x0 + 10, y1 - 52, x0 + 118, y1 - 30, fill=(90, 70, 50))
    s.rect(x0 + 22, y1 - 66, x0 + 106, y1 - 52, fill=(120, 100, 80))
    d.ellipse([x0 + 92, y1 - 30, x0 + 112, y1 - 10], fill=(40, 40, 40))
    d.ellipse([x0 + 26, y1 - 30, x0 + 46, y1 - 10], fill=(40, 40, 40))
    cx = (x0 + x1) // 2
    for half, top, colour in ((16, 22, (230, 60, 20)), (9, 34, (245, 160, 30)),
                              (4, 46, (250, 220, 80))):
        d.polygon([(cx - half, y1 - 46), (cx + half, y1 - 46),
                   (cx, y0 + top)], fill=colour)
    for ex, ey, r in ((8, 8, 13), (40, 4, 11), (100, 6, 13)):
        d.ellipse([x0 + ex, y0 + ey, x0 + ex + 2 * r, y0 + ey + 2 * r],
                  fill=(120, 120, 120) if ex != 100 else (240, 200, 60))


def draw_ballot(s, x0, y0, x1, y1):
    """A ballot box with a ticked paper slip and a rising sun."""
    d = s.d
    s.rect(x0, y0, x1, y1, fill=(232, 238, 240))
    cx = (x0 + x1) // 2
    s.rect(cx - 44, y1 - 46, cx + 44, y1 - 10, fill=NAVY)
    s.rect(cx - 44, y1 - 46, cx + 44, y1 - 36, fill=RED)
    s.rect(cx - 10, y1 - 40, cx + 10, y1 - 36, fill=INK)
    s.rect(cx - 26, y0 + 12, cx + 26, y0 + 46, fill=(255, 255, 255),
           outline=INK, width=2)
    d.line([(cx - 16, y0 + 30), (cx - 6, y0 + 40), (cx + 18, y0 + 16)],
           fill=(30, 130, 70), width=4)
    d.ellipse([x0 + 8, y0 + 8, x0 + 30, y0 + 30], fill=(240, 200, 60))


def draw_chart(s, x0, y0, x1, y1):
    """Four falling bars under a red down-trend arrow."""
    d = s.d
    s.rect(x0, y0, x1, y1, fill=(245, 240, 225))
    for i, height in enumerate((30, 44, 58, 74)):
        bx = x0 + 16 + i * 32
        s.rect(bx, y1 - 14 - height, bx + 22, y1 - 14, fill=NAVY)
    d.line([(x0 + 10, y0 + 18), (x0 + 50, y0 + 40), (x0 + 90, y0 + 58),
            (x0 + 128, y0 + 78)], fill=RED, width=4)
    d.polygon([(x0 + 128, y0 + 78), (x0 + 118, y0 + 76), (x0 + 126, y0 + 66)],
              fill=RED)
    s.line(x0 + 6, y1 - 10, x1 - 6, y1 - 10, fill=INK, width=2)


ART = {"parade": draw_parade, "refinery": draw_refinery,
       "ballot": draw_ballot, "chart": draw_chart}


def number_badge(s, cx, cy, num, size=13):
    d = s.d
    r = size
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    s.centre(cx, cy - size // 2 - 1, str(num), SANSB(size), fill=(255, 255, 255))


# -------------------------------------------------------------- sections
def masthead(s, m):
    s.line(m, 8, PAGE - m, 8, width=3)
    s.centre(PAGE // 2, 14, "THE WORLD IN ONE DAY", SERIFB(40))
    s.centre(PAGE // 2, 58, "FRIDAY 27 NOVEMBER 2026  ·  50 STORIES  ·  7 REGIONS",
             SANSB(20))
    s.centre(PAGE // 2, 86,
             "A nor'easter grounds New York's 100th Thanksgiving parade; "
             "a Houthi strike hits a Saudi refinery; New Zealand's final count lands.",
             SERIF(13), fill=FAINT)


def number_strip(s, m):
    y0, y1 = 106, 158
    cw = (PAGE - 2 * m - 5 * 6) // 6
    for i, item in enumerate(NUMBERS):
        x0 = m + i * (cw + 6)
        s.rect(x0, y0, x0 + cw, y1, fill=(255, 255, 255), outline=INK)
        s.rect(x0, y0, x0 + cw, y0 + 3, fill=RED)
        s.centre(x0 + cw // 2, y0 + 6, item["value"], SANSB(21), fill=RED)
        for j, ln in enumerate(item["label"]):
            s.centre(x0 + cw // 2, y0 + 30 + j * 11, ln, SANSB(8))


def region_line(s, m):
    x, y = m, 166
    for region in REGIONS:
        s.d.ellipse([x, y + 2, x + 9, y + 11], fill=region["colour"])
        label = f"{region['name']} {region['n']}"
        s.text(x + 13, y, label, SANSB(11))
        x += 13 + int(s.d.textlength(label, font=SANSB(11))) + 18


def leads(s, m):
    y0 = 186
    cellw, cellh = (PAGE - 2 * m - 8) // 2, 108
    for idx, story in enumerate(LEADS):
        r, c = divmod(idx, 2)
        x0 = m + c * (cellw + 8)
        yy0 = y0 + r * (cellh + 6)
        s.rect(x0, yy0, x0 + cellw, yy0 + cellh,
               fill=(255, 255, 255), outline=INK)
        ART[story["art"]](s, x0 + 1, yy0 + 1, x0 + 148, yy0 + cellh - 1)
        number_badge(s, x0 + 16, yy0 + 16, story["num"])
        tx = x0 + 156
        s.text(tx, yy0 + 6, story["kicker"], SANSB(10), fill=RED)
        for j, ln in enumerate(s.wrap(story["head"], SERIFB(16), cellw - 164)[:2]):
            s.text(tx, yy0 + 20 + j * 18, ln, SERIFB(16))
        for j, ln in enumerate(s.wrap(story["body"], SANS(11), cellw - 164)[:2]):
            s.text(tx, yy0 + 58 + j * 13, ln, SANS(11), fill=(50, 48, 44))
        s.text(tx, yy0 + cellh - 15, f"SOURCE: {story['source']}", SANSB(9), fill=MUTED)


def cards(s, m):
    y0 = 410
    cw, ch = (PAGE - 2 * m - 4 * 6) // 5, 76
    for idx, card in enumerate(CARDS):
        r, c = divmod(idx, 5)
        x0 = m + c * (cw + 6)
        yy0 = y0 + r * (ch + 6)
        s.rect(x0, yy0, x0 + cw, yy0 + ch, fill=(255, 255, 255), outline=INK)
        s.rect(x0 + 1, yy0 + 1, x0 + cw - 1, yy0 + 24, fill=card["band"])
        number_badge(s, x0 + 14, yy0 + 13, card["num"], size=9)
        s.text(x0 + 27, yy0 + 7, card["kicker"], SANSB(8), fill=(255, 255, 255))
        for j, ln in enumerate(s.wrap(card["head"], SANSB(12), cw - 10)[:2]):
            s.text(x0 + 5, yy0 + 27 + j * 14, ln, SANSB(12))
        s.text(x0 + 5, yy0 + ch - 13, card["source"], SANSB(8), fill=MUTED)


def map_and_rest(s, m):
    y0, bh = 578, 296
    mapw = 330
    s.rect(m, y0, m + mapw, y0 + bh, fill=(232, 238, 240), outline=INK)
    s.text(m + 8, y0 + 6, "WHERE IT HAPPENED — PINS 1–14", SANSB(12))
    mx, my, mw, mh = m + 6, y0 + 26, mapw - 12, bh - 52

    def proj(lon, lat):
        return (mx + (lon + 170) / 360 * mw, my + (83 - lat) / 141 * mh)

    for poly in LAND:
        s.d.polygon([proj(lon, lat) for lon, lat in poly],
                    fill=(190, 195, 175), outline=(120, 125, 110))
    # Europe's pins sit close together, so their badges step aside on a
    # short leader line while a dot marks the true spot.
    offsets = {4: (-26, -14), 6: (-4, -26), 7: (20, 6), 8: (-30, 10)}
    for num, lon, lat in PINS:
        px, py = proj(lon, lat)
        if num in offsets:
            s.d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
            bx, by = px + offsets[num][0], py + offsets[num][1]
            s.line(px, py, bx, by, fill=RED)
            number_badge(s, bx, by, num, size=8)
        else:
            number_badge(s, px, py, num, size=8)
    s.text(m + 8, y0 + bh - 20, "Schematic map; pins match the numbered stories.",
           SANS(9), fill=MUTED)

    ax0, ax1 = m + mapw + 10, PAGE - m
    s.rect(ax0, y0, ax1, y0 + bh, fill=(255, 255, 255), outline=INK)
    s.text(ax0 + 8, y0 + 6, "AND ALSO — STORIES 15–50", SANSB(12), fill=RED)
    colw = (ax1 - ax0 - 16) // 2
    for i, (num, line, src) in enumerate(REST):
        col, row = divmod(i, 18)
        lx = ax0 + 8 + col * colw
        ly = y0 + 26 + row * 15
        full = f"{line} — {src}"
        while s.d.textlength(f"{num}. {full}", font=SANS(10.5)) > colw - 4 and " " in line:
            line = line.rsplit(" ", 1)[0] + "…"
            full = f"{line} — {src}"
        s.text(lx, ly, f"{num}.", SANSB(10.5), fill=RED)
        s.text(lx + 22, ly, full, SANS(10.5))


def date_check(s, m):
    y0 = 882
    s.rect(m, y0, PAGE - m, y0 + 78, fill=(255, 248, 246), outline=RED, width=2)
    s.text(m + 8, y0 + 6, "DATE CHECK — THESE ARE NOT 27 NOVEMBER", SANSB(12), fill=RED)
    s.text(m + 8, y0 + 24, "Real news from other days, left out on purpose:",
           SANS(10.5), fill=FAINT)
    for i, (story, when) in enumerate(NOT_TODAY):
        col, row = divmod(i, 2)
        lx = m + 8 + col * 490
        ly = y0 + 42 + row * 16
        s.text(lx, ly, "×", SANSB(12), fill=RED)
        s.text(lx + 14, ly, f"{story}  —  {when}", SANS(11))


def footer(s, m):
    s.centre(PAGE // 2, 972,
             "Every story here happened or was first reported on Friday 27 November 2026. "
             "Sources are named on each story.", SANS(10.5), fill=FAINT)
    s.centre(PAGE // 2, 988,
             "Scenes are drawn illustrations, not photographs.  THE WORLD IN ONE DAY  ·  "
             "27 NOV 2026  ·  50 STORIES  ·  7 REGIONS", SANSB(10), fill=MUTED)
    s.line(m, 1012, PAGE - m, 1012, width=2)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    s = Sheet()
    m = 14
    masthead(s, m)
    number_strip(s, m)
    region_line(s, m)
    leads(s, m)
    cards(s, m)
    map_and_rest(s, m)
    date_check(s, m)
    footer(s, m)
    s.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
