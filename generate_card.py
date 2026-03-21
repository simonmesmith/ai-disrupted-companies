#!/usr/bin/env python3
"""
AI-Disrupted Companies — Card Generator v7
Generates visually compelling "trading card" PNGs for AI-disrupted companies.

Design: Giant glitched ticker as hero visual, 1080×1350 portrait (4:5).
Callable by AI — pass short one-sentence descriptions for what_they_do and ai_impact.
"""

import csv
import io
import math
import random
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# ─── Configuration ───────────────────────────────────────────────────────────

CARD_W, CARD_H = 1080, 1350   # 4:5 portrait — standard for X/Instagram
MARGIN = 60
INNER_W = CARD_W - 2 * MARGIN

FONT_DIR = "/usr/share/fonts/truetype"
FONTS = {
    "bold":       f"{FONT_DIR}/google-fonts/Poppins-Bold.ttf",
    "semibold":   f"{FONT_DIR}/google-fonts/Poppins-SemiBold.ttf",
    "medium":     f"{FONT_DIR}/google-fonts/Poppins-Medium.ttf",
    "regular":    f"{FONT_DIR}/google-fonts/Poppins-Regular.ttf",
    "lato":       f"{FONT_DIR}/lato/Lato-Regular.ttf",
    "lato_bold":  f"{FONT_DIR}/lato/Lato-Bold.ttf",
    "lato_heavy": f"{FONT_DIR}/lato/Lato-Heavy.ttf",
    "lato_black": f"{FONT_DIR}/lato/Lato-Black.ttf",
    "lato_light": f"{FONT_DIR}/lato/Lato-Light.ttf",
    "lato_thin":  f"{FONT_DIR}/lato/Lato-Thin.ttf",
    "mono":       f"{FONT_DIR}/noto/NotoSansMono-Bold.ttf",
    "mono_reg":   f"{FONT_DIR}/noto/NotoSansMono-Regular.ttf",
}

CATEGORY_COLORS = {
    "Education Technology":              "#4A9EFF",
    "Customer Experience / BPO":         "#A855F7",
    "Stock Media / Visual Content":      "#14B8A6",
    "Online Recruitment Platform":       "#3B82F6",
    "Staffing & Workforce Solutions":    "#FF8C42",
    "Translation & Language Services":   "#06B6D4",
    "IT Staffing & Consulting":          "#22C55E",
    "IT Services & Consulting":          "#22C55E",
    "IT Services & Software Engineering":"#22C55E",
    "Nearshore IT Services & Software Engineering": "#22C55E",
    "Freelance Marketplace":             "#EC4899",
    "Advertising & Marketing Services":  "#F43F5E",
    "Professional Information Services": "#6366F1",
    "SEO & Digital Marketing SaaS":      "#818CF8",
    "Tax Preparation Services":          "#F97316",
    "Creative Software":                 "#8B5CF6",
    "Legal Technology":                  "#EAB308",
    "Business Process Outsourcing":      "#C084FC",
    "HR Outsourcing / PEO":              "#D946EF",
    "Executive Search & Consulting":     "#FB923C",
    "Staffing & Recruitment Platforms":  "#FF8C42",
    "News Publishing / Media":           "#E11D48",
    "Digital Media / Affiliate Commerce":"#E11D48",
    "Multi-Utility / Network Marketing": "#64748B",
    "Expense Management SaaS":           "#0EA5E9",
    "Digital Advertising Technology":    "#06B6D4",
    "Conversational AI Platform":        "#10B981",
    "Market Research & Advisory":        "#F59E0B",
    "Contact Center Cloud Software / CCaaS": "#7C3AED",
    "Travel / Online Reviews":           "#0EA5E9",
    "Customer Support / ITSM SaaS":      "#38BDF8",
    "Social Media Management SaaS":      "#F472B6",
    "Research Analytics / IP Services":   "#A78BFA",
    "Healthcare Data Analytics / Commercial Intelligence": "#34D399",
    "Online Dating / Social Platform":  "#E11D8C",
    "Content Moderation & AI Data Services": "#F59E0B",
    "IT Services & Digital Transformation": "#22C55E",
    "Project Management SaaS":          "#7C3AED",
    "Fintech / AP Automation SaaS":     "#0EA5E9",
}
DEFAULT_ACCENT = "#6366F1"

CATEGORY_SHORT = {
    "Customer Experience / BPO": "CX / BPO",
    "IT Services & Software Engineering": "IT SERVICES",
    "Nearshore IT Services & Software Engineering": "IT OUTSOURCING",
    "Professional Information Services": "INFO SERVICES",
    "Contact Center Cloud Software / CCaaS": "CONTACT CENTER",
    "Digital Media / Affiliate Commerce": "DIGITAL MEDIA",
    "Advertising & Marketing Services": "ADVERTISING",
    "Digital Advertising Technology": "AD TECH",
    "Multi-Utility / Network Marketing": "UTILITIES",
    "Staffing & Recruitment Platforms": "RECRUITMENT",
    "Customer Support / ITSM SaaS": "SUPPORT SAAS",
    "Healthcare Data Analytics / Commercial Intelligence": "HEALTHCARE DATA",
}

DOMAIN_MAP = {
    "CHGG": "chegg.com", "TTEC": "ttec.com", "GETY": "gettyimages.com",
    "ZIP": "ziprecruiter.com", "TBI": "trueblue.com", "CNXC": "concentrix.com",
    "MAN": "manpowergroup.com", "RHI": "roberthalf.com", "SSTK": "shutterstock.com",
    "FVRR": "fiverr.com", "ASGN": "asgn.com", "COUR": "coursera.org",
    "KELYA": "kellyservices.com", "HRB": "hrblock.com", "ADBE": "adobe.com",
    "LZ": "legalzoom.com", "G": "genpact.com", "CTSH": "cognizant.com",
    "OMC": "omnicomgroup.com", "BBSI": "barrettbusiness.com", "KFY": "kornferry.com",
    "IBEX": "ibex.co", "UPWK": "upwork.com", "SEMR": "semrush.com",
    "NWSA": "newscorp.com", "FORR": "forrester.com", "ZD": "ziffdavis.com",
    "FIVN": "five9.com", "TRIP": "tripadvisor.com", "EPAM": "epam.com",
    "EXFY": "expensify.com", "PERI": "perion.com", "LPSN": "liveperson.com",
    "IPG": "interpublic.com", "FRSH": "freshworks.com",
    "LON:RWS": "rws.com", "LON:WPP": "wpp.com",
    "AMS:WKL": "wolterskluwer.com", "TEP": "utilitywarehouse.co.uk",
    "PUBGY": "publicisgroupe.com", "RCRUY": "recruit-holdings.com", "RELX": "relx.com",
    "BMBL": "bumble.com", "SPT": "sproutsocial.com", "CLVT": "clarivate.com",
    "DH": "definitivehc.com", "TASK": "taskus.com", "GLOB": "globant.com",
    "ASAN": "asana.com", "BILL": "bill.com",
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def font(name, size):
    return ImageFont.truetype(FONTS[name], size)


def wrap_text(draw, text, fnt, max_width, max_lines=4):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=fnt)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while True:
            test = last + "..."
            bbox = draw.textbbox((0, 0), test, font=fnt)
            if bbox[2] - bbox[0] <= max_width or len(last) <= 10:
                lines[-1] = test
                break
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-4]
    return lines


def draw_text_lines(draw, lines, x, y, fnt, fill, line_height):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def fetch_logo(ticker, size=128):
    domain = DOMAIN_MAP.get(ticker)
    if not domain:
        return None
    urls = [
        f"https://{domain}/apple-touch-icon.png",
        f"https://www.{domain}/apple-touch-icon.png",
        f"https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://{domain}&size=128",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=8, allow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and len(r.content) > 800:
                img = Image.open(io.BytesIO(r.content)).convert("RGBA")
                if img.size[0] >= 32:
                    return img
        except Exception:
            continue
    return None


def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = xy
    r = min(radius, (x1-x0)//2, (y1-y0)//2)
    if fill:
        draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
        draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
        draw.pieslice([x0, y0, x0+2*r, y0+2*r], 180, 270, fill=fill)
        draw.pieslice([x1-2*r, y0, x1, y0+2*r], 270, 360, fill=fill)
        draw.pieslice([x0, y1-2*r, x0+2*r, y1], 90, 180, fill=fill)
        draw.pieslice([x1-2*r, y1-2*r, x1, y1], 0, 90, fill=fill)
    if outline:
        draw.arc([x0, y0, x0+2*r, y0+2*r], 180, 270, fill=outline, width=width)
        draw.arc([x1-2*r, y0, x1, y0+2*r], 270, 360, fill=outline, width=width)
        draw.arc([x0, y1-2*r, x0+2*r, y1], 90, 180, fill=outline, width=width)
        draw.arc([x1-2*r, y1-2*r, x1, y1], 0, 90, fill=outline, width=width)
        draw.line([x0+r, y0, x1-r, y0], fill=outline, width=width)
        draw.line([x0+r, y1, x1-r, y1], fill=outline, width=width)
        draw.line([x0, y0+r, x0, y1-r], fill=outline, width=width)
        draw.line([x1, y0+r, x1, y1-r], fill=outline, width=width)


def make_circle_mask(size):
    """Create an anti-aliased circle mask by rendering at 4x and downscaling."""
    big = size * 4
    mask_big = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask_big).ellipse([0, 0, big - 1, big - 1], fill=255)
    return mask_big.resize((size, size), Image.LANCZOS)


# ─── Glitch Effect for Text ─────────────────────────────────────────────────

def render_glitched_text(text, fnt, intensity=0.5, accent_rgb=(100, 100, 255)):
    dummy = Image.new("RGBA", (1, 1))
    dd = ImageDraw.Draw(dummy)
    bbox = dd.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    padding = int(tw * 0.15)

    w, h = tw + padding * 2, th + padding * 2

    base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    d.text((padding - bbox[0], padding - bbox[1]), text, font=fnt, fill=(255, 255, 255, 255))

    r, g, b, a = base.split()

    max_offset = max(2, int(tw * 0.06 * intensity + 1))
    r_off = max(1, int(max_offset * 0.9))
    b_off = max(1, int(max_offset * 1.1))

    r_img = Image.new("L", (w, h), 0)
    r_img.paste(r, (-r_off, 0))

    b_img = Image.new("L", (w, h), 0)
    b_img.paste(b, (b_off, 0))

    result = Image.merge("RGBA", [r_img, g, b_img, a])

    if intensity > 0.35:
        arr = np.array(result)
        rng = random.Random(hash(text) % 10000)
        num_blocks = int(3 + intensity * 10)
        for _ in range(num_blocks):
            bh = rng.randint(2, max(3, int(h * 0.12 * intensity)))
            by = rng.randint(0, h - bh)
            shift = rng.randint(-int(w * 0.10 * intensity), int(w * 0.10 * intensity))
            if shift != 0:
                block = arr[by:by+bh, :, :].copy()
                arr[by:by+bh, :, :] = np.roll(block, shift, axis=1)
        result = Image.fromarray(arr)

    if intensity > 0.15:
        scan = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(scan)
        spacing = max(3, int(5 - intensity * 2))
        alpha = int(20 + intensity * 40)
        for y in range(0, h, spacing):
            sd.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
        result = Image.alpha_composite(result, scan)

    return result


# ─── Background ──────────────────────────────────────────────────────────────

def create_background(w, h, accent_rgb, intensity=0.5):
    bg = np.full((h, w, 3), [13, 17, 23], dtype=np.float32)

    for x in range(0, w, 40):
        bg[:, max(0,x):min(w,x+1), :] += 5
    for y in range(0, h, 40):
        bg[max(0,y):min(h,y+1), :, :] += 5

    glow_range = min(600, h)
    for y in range(glow_range):
        t = 1.0 - (y / glow_range)
        glow = t ** 2.5 * 0.1 * (0.5 + intensity * 0.5)
        bg[y, :, 0] += accent_rgb[0] * glow
        bg[y, :, 1] += accent_rgb[1] * glow
        bg[y, :, 2] += accent_rgb[2] * glow

    cx, cy = w / 2, h / 2
    ys = np.arange(h).reshape(-1, 1)
    xs = np.arange(w).reshape(1, -1)
    dist = np.sqrt((xs - cx)**2 + (ys - cy)**2) / math.sqrt(cx**2 + cy**2)
    bg *= (1.0 - 0.35 * dist ** 1.5)[:, :, np.newaxis]

    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8), "RGB")


def draw_down_arrow(draw, cx, cy, size, fill):
    half = size // 2
    points = [(cx - half, cy - half//2), (cx + half, cy - half//2), (cx, cy + half//2)]
    draw.polygon(points, fill=fill)


# ─── Main Card Generator ────────────────────────────────────────────────────

def generate_card(
    ticker, name, category,
    what_they_do,     # Short, one sentence
    ai_impact,        # Short, one sentence
    pre_price, current_price,
    logo_img=None, output_path=None, card_date="2026-03-10",
):
    decline_pct = ((pre_price - current_price) / pre_price) * 100
    glitch_intensity = min(1.0, max(0.15, decline_pct / 100.0))

    accent_hex = CATEGORY_COLORS.get(category, DEFAULT_ACCENT)
    accent_rgb = hex_to_rgb(accent_hex)

    cat_display = CATEGORY_SHORT.get(category, category).upper()

    card = create_background(CARD_W, CARD_H, accent_rgb, glitch_intensity).convert("RGBA")
    draw = ImageDraw.Draw(card)

    # ─── Top accent bar ──────────────────────
    for x in range(CARD_W):
        t = x / CARD_W
        r = int(accent_rgb[0] * (1 - t * 0.3))
        g = int(accent_rgb[1] * (1 - t * 0.3))
        b = int(accent_rgb[2] * (1 - t * 0.3))
        draw.line([(x, 0), (x, 5)], fill=(r, g, b, 255))

    # ─── Category badge (left) ───────────────
    cat_font = font("lato_bold", 18)
    cat_bbox = draw.textbbox((0, 0), cat_display, font=cat_font)
    cat_text_w = cat_bbox[2] - cat_bbox[0]
    cat_text_h = cat_bbox[3] - cat_bbox[1]

    pill_h = 34
    pill_pad_x = 16

    pill_x0 = MARGIN
    pill_y0 = 28
    pill_x1 = pill_x0 + cat_text_w + pill_pad_x * 2
    pill_y1 = pill_y0 + pill_h

    draw_rounded_rect(draw,
        (pill_x0, pill_y0, pill_x1, pill_y1),
        radius=pill_h // 2, fill=accent_rgb + (30,), outline=accent_rgb + (80,), width=1)

    # Vertically center text inside pill using textbbox
    text_y = pill_y0 + (pill_h - cat_text_h) // 2 - cat_bbox[1]
    draw.text((pill_x0 + pill_pad_x, text_y), cat_display,
              font=cat_font, fill=accent_rgb + (230,))

    # ─── Logo badge (right) — clean anti-aliased circle ──
    if logo_img:
        badge_size = 40
        logo_resized = logo_img.resize((badge_size, badge_size), Image.LANCZOS)
        circle_mask = make_circle_mask(badge_size)
        badge_x = CARD_W - MARGIN - badge_size
        badge_y = pill_y0 + (pill_h - badge_size) // 2
        # Background ring
        ring_pad = 3
        ring_mask = make_circle_mask(badge_size + ring_pad * 2)
        ring_bg = Image.new("RGBA", (badge_size + ring_pad*2, badge_size + ring_pad*2), (0,0,0,0))
        ring_draw = ImageDraw.Draw(ring_bg)
        ring_draw.rectangle([0, 0, ring_bg.width, ring_bg.height], fill=(30, 35, 45, 220))
        card.paste(ring_bg, (badge_x - ring_pad, badge_y - ring_pad), ring_mask)
        # Logo
        card.paste(logo_resized, (badge_x, badge_y), circle_mask)

    # ─── Hero: Giant Glitched Ticker ─────────
    # Plenty of clearance below the category pill
    ticker_display = ticker.split(":")[-1]

    if len(ticker_display) <= 3:
        ticker_size = 160
    elif len(ticker_display) <= 4:
        ticker_size = 136
    elif len(ticker_display) <= 5:
        ticker_size = 112
    else:
        ticker_size = 92

    ticker_font = font("bold", ticker_size)
    glitched = render_glitched_text(ticker_display, ticker_font, glitch_intensity, accent_rgb)

    gx = (CARD_W - glitched.width) // 2
    gy = 100  # Fixed Y with clear gap after pill area

    # Paste glitched ticker directly — no background box
    card.paste(glitched, (gx, gy), glitched)

    y = gy + glitched.height + 30

    # ─── Company Name ─────────────────────────
    for sz in [40, 36, 30, 26]:
        name_font = font("medium", sz)
        bbox = draw.textbbox((0, 0), name, font=name_font)
        nw = bbox[2] - bbox[0]
        if nw <= INNER_W:
            break
    draw.text(((CARD_W - nw) // 2, y), name, font=name_font, fill=(255, 255, 255, 230))
    y += (bbox[3] - bbox[1]) + 48

    # ─── Price Comparison Box ────────────────
    box_m = 70
    box_x0, box_x1 = box_m, CARD_W - box_m
    box_y0 = y
    box_h = 100
    box_y1 = box_y0 + box_h
    box_cx = (box_x0 + box_x1) // 2

    draw_rounded_rect(draw, (box_x0, box_y0, box_x1, box_y1),
                      radius=16, fill=(18, 22, 30, 230))
    draw_rounded_rect(draw, (box_x0, box_y0, box_x1, box_y1),
                      radius=16, outline=accent_rgb + (40,), width=1)

    lbl_font = font("lato", 15)
    price_font = font("lato_heavy", 36)

    left_cx = box_x0 + (box_cx - box_x0) // 2
    pre_label = "PRE-CHATGPT"
    pre_str = f"${pre_price:,.2f}"

    lbl_bbox = draw.textbbox((0, 0), pre_label, font=lbl_font)
    draw.text((left_cx - (lbl_bbox[2]-lbl_bbox[0])//2, box_y0 + 16),
              pre_label, font=lbl_font, fill=(130, 140, 160, 180))

    p_bbox = draw.textbbox((0, 0), pre_str, font=price_font)
    draw.text((left_cx - (p_bbox[2]-p_bbox[0])//2, box_y0 + 42),
              pre_str, font=price_font, fill=(255, 255, 255, 240))

    # Chevron arrow
    arr_cx, arr_cy = box_cx, box_y0 + 58
    arr_sz = 10
    draw.line([(arr_cx - arr_sz, arr_cy - arr_sz), (arr_cx + arr_sz, arr_cy)],
              fill=accent_rgb + (140,), width=3)
    draw.line([(arr_cx - arr_sz, arr_cy + arr_sz), (arr_cx + arr_sz, arr_cy)],
              fill=accent_rgb + (140,), width=3)

    right_cx = box_cx + (box_x1 - box_cx) // 2
    cur_label = "CURRENT"
    cur_str = f"${current_price:,.2f}"

    lbl_bbox = draw.textbbox((0, 0), cur_label, font=lbl_font)
    draw.text((right_cx - (lbl_bbox[2]-lbl_bbox[0])//2, box_y0 + 16),
              cur_label, font=lbl_font, fill=(130, 140, 160, 180))

    p_bbox = draw.textbbox((0, 0), cur_str, font=price_font)
    draw.text((right_cx - (p_bbox[2]-p_bbox[0])//2, box_y0 + 42),
              cur_str, font=price_font, fill=(255, 70, 70, 255))

    y = box_y1 + 36

    # ─── Big Decline Percentage ──────────────
    pct_str = f"{decline_pct:.0f}%"
    pct_font = font("bold", 64)
    pct_bbox = draw.textbbox((0, 0), pct_str, font=pct_font)
    pct_w = pct_bbox[2] - pct_bbox[0]

    if decline_pct > 80:
        pct_color = (255, 30, 30, 255)
    elif decline_pct > 50:
        pct_color = (255, 60, 50, 255)
    else:
        pct_color = (255, 90, 60, 255)

    arrow_w = 30
    total_w = arrow_w + 12 + pct_w
    start_x = (CARD_W - total_w) // 2

    draw_down_arrow(draw, start_x + arrow_w // 2, y + 38, 30, pct_color)
    draw.text((start_x + arrow_w + 12, y), pct_str, font=pct_font, fill=pct_color)

    y += 90

    # ─── Disruption Severity Bar ─────────────
    bar_m = MARGIN + 60
    bar_x0b, bar_x1b = bar_m, CARD_W - bar_m
    bar_w = bar_x1b - bar_x0b
    bar_h = 10

    draw_rounded_rect(draw, (bar_x0b, y, bar_x1b, y + bar_h),
                      radius=5, fill=(30, 35, 45, 200))

    fill_w = int(bar_w * min(1.0, decline_pct / 100.0))
    if fill_w > 10:
        for i in range(fill_w):
            t = i / fill_w
            r = int(accent_rgb[0] * (1 - t) + 255 * t)
            g = int(accent_rgb[1] * (1 - t) + 40 * t)
            b = int(accent_rgb[2] * (1 - t) + 40 * t)
            draw.line([(bar_x0b + i, y + 1), (bar_x0b + i, y + bar_h - 1)],
                      fill=(r, g, b, 220))

    sev_font = font("lato", 13)
    sev_text = "DISRUPTION SEVERITY"
    sb = draw.textbbox((0, 0), sev_text, font=sev_font)
    draw.text(((CARD_W - (sb[2]-sb[0])) // 2, y + bar_h + 6),
              sev_text, font=sev_font, fill=(90, 100, 120, 160))

    y += bar_h + 56

    # ─── Divider ─────────────────────────────
    draw.line([(MARGIN + 30, y), (CARD_W - MARGIN - 30, y)],
              fill=(40, 45, 55, 100), width=1)
    y += 44

    # ─── "What They Do" ─────────────────────
    body_font = font("lato", 28)
    body_lh = 42
    section_label_font = font("lato_bold", 15)

    draw.text((MARGIN, y), "WHAT THEY DO", font=section_label_font, fill=accent_rgb + (180,))
    y += 36

    desc_lines = wrap_text(draw, what_they_do, body_font, INNER_W, max_lines=3)
    y = draw_text_lines(draw, desc_lines, MARGIN, y, body_font, (215, 222, 232, 245), body_lh)
    y += 44

    # ─── "AI Impact" callout box ─────────────
    box_pad_x = 24
    box_pad_y = 24
    accent_bar_w = 4

    impact_font = font("lato", 28)
    impact_label_font = font("lato_bold", 15)

    impact_lines = wrap_text(draw, ai_impact, impact_font,
                             INNER_W - box_pad_x * 2 - accent_bar_w - 14,
                             max_lines=4)
    label_h = 26
    box_content_h = label_h + 8 + len(impact_lines) * body_lh
    box_total_h = box_content_h + box_pad_y * 2

    bx0 = MARGIN
    bx1 = CARD_W - MARGIN
    by0 = y
    by1 = by0 + box_total_h

    draw_rounded_rect(draw, (bx0, by0, bx1, by1), radius=12,
                      fill=(20, 24, 32, 200))

    # Left accent bar (red)
    draw.rectangle([bx0, by0 + 12, bx0 + accent_bar_w, by1 - 12],
                   fill=(255, 60, 60, 200))

    inner_x = bx0 + accent_bar_w + box_pad_x
    inner_y = by0 + box_pad_y
    draw.text((inner_x, inner_y), "AI IMPACT",
              font=impact_label_font, fill=(255, 70, 70, 210))
    inner_y += label_h + 8

    draw_text_lines(draw, impact_lines, inner_x, inner_y,
                    impact_font, (215, 222, 232, 245), body_lh)

    # ─── Footer — pinned to bottom ───────────
    footer_line_y = CARD_H - 56
    footer_text_y = CARD_H - 40

    draw.line([(MARGIN, footer_line_y), (CARD_W - MARGIN, footer_line_y)],
              fill=(40, 45, 55, 120), width=1)

    brand_font = font("lato_heavy", 18)
    draw.text((MARGIN, footer_text_y), "AI-DISRUPTED COMPANIES",
              font=brand_font, fill=(255, 255, 255, 120))

    date_font = font("lato", 16)
    db = draw.textbbox((0, 0), card_date, font=date_font)
    draw.text((CARD_W - MARGIN - (db[2]-db[0]), footer_text_y + 1),
              card_date, font=date_font, fill=(90, 100, 120, 140))

    # ─── Card border glow ────────────────────
    border = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(border)
    bd.rectangle([0, 0, CARD_W-1, CARD_H-1], outline=accent_rgb + (30,), width=2)
    card = Image.alpha_composite(card, border)

    # ─── Final output ────────────────────────
    final = Image.new("RGB", (CARD_W, CARD_H), (13, 17, 23))
    final.paste(card, mask=card.split()[3])

    if output_path:
        final.save(output_path, "PNG", quality=95)
        print(f"  -> Saved: {output_path}")

    return final


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    output_dir = Path("/sessions/hopeful-intelligent-mendel/mnt/AI Loser Stocks/cards")
    output_dir.mkdir(exist_ok=True)

    samples = [
        {
            "ticker": "CHGG",
            "name": "Chegg Inc",
            "category": "Education Technology",
            "what_they_do": "Online homework help and textbook rental platform used by millions of college students.",
            "ai_impact": "ChatGPT replaced Chegg's core homework help product almost overnight, causing 30%+ subscriber losses and a 91% stock collapse.",
            "pre_price": 14.74,
            "current_price": 1.35,
        },
        {
            "ticker": "LPSN",
            "name": "LivePerson Inc",
            "category": "Conversational AI Platform",
            "what_they_do": "Enterprise chatbot and conversational AI platform for automating customer interactions.",
            "ai_impact": "Generative AI commoditized chatbots — enterprises now build superior bots with foundation models, eliminating the need for LivePerson's platform.",
            "pre_price": 10.68,
            "current_price": 3.04,
        },
        {
            "ticker": "FIVN",
            "name": "Five9 Inc",
            "category": "Contact Center Cloud Software / CCaaS",
            "what_they_do": "Cloud contact center software that charges per-seat for human agents handling customer calls.",
            "ai_impact": "AI agents are replacing human call center staff, directly shrinking Five9's per-seat revenue model as enterprises need fewer human operators.",
            "pre_price": 60.23,
            "current_price": 17.71,
        },
        {
            "ticker": "TRIP",
            "name": "TripAdvisor Inc",
            "category": "Travel / Online Reviews",
            "what_they_do": "The world's largest travel reviews platform with over 1 billion user opinions on hotels and restaurants.",
            "ai_impact": "Google AI Overviews now answer travel queries directly in search results, destroying TripAdvisor's core click-through traffic engine.",
            "pre_price": 19.58,
            "current_price": 10.07,
        },
    ]

    for s in samples:
        print(f"\n{'='*50}")
        print(f"{s['ticker']} | {s['name']} | {((s['pre_price']-s['current_price'])/s['pre_price']*100):.0f}% decline")

        logo = fetch_logo(s["ticker"])
        if logo:
            print(f"  Logo: {logo.size[0]}x{logo.size[1]}")
        else:
            print(f"  No logo (OK - ticker is the hero)")

        generate_card(
            ticker=s["ticker"], name=s["name"], category=s["category"],
            what_they_do=s["what_they_do"], ai_impact=s["ai_impact"],
            pre_price=s["pre_price"], current_price=s["current_price"],
            logo_img=logo,
            output_path=str(output_dir / f"{s['ticker'].replace(':','_')}_card.png"),
        )

    print(f"\n{'='*50}")
    print(f"Done! Cards in: {output_dir}")
