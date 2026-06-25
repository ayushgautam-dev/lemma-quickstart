#!/usr/bin/env python3
"""
Build index.html from lemma-quickstart.template.html + screenshots/.

The template uses {{IMG_*}} placeholders. This script processes the source
screenshots (redact a private email, crop the browser chrome, draw annotation
boxes/labels), encodes them to WebP data-URIs, embeds the OpenCode GIF, and
writes a single self-contained index.html.

Usage:
    pip install pillow
    python3 build.py
"""
import base64
import io
import json
import os
import re

from PIL import Image, ImageDraw, ImageFont, ImageFilter

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots")
TEMPLATE = os.path.join(HERE, "lemma-quickstart.template.html")
GIF = os.path.join(HERE, "opencode-desktop-walkthrough.gif")
OUT = os.path.join(HERE, "index.html")

CHROME_CROP = 176          # px of browser chrome to trim from the top of Step-1 shots
EMAIL_BOX = (1480, 762, 1915, 888)   # private email row on 2.png (blurred before crop)
PURPLE = (91, 75, 208)
WHITE = (255, 255, 255)


def load_font(size=44):
    for p in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


FONT = load_font(44)


def _box(d, b, w=9):
    d.rounded_rectangle(b, radius=18, outline=PURPLE, width=w)


def _label(d, xy, text, anchor="lt"):
    pad = 16
    tb = d.textbbox((0, 0), text, font=FONT)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    x, y = xy
    if anchor == "rt":
        x = x - (tw + 2 * pad)
    d.rounded_rectangle((x, y, x + tw + 2 * pad, y + th + 2 * pad + 6), radius=14, fill=PURPLE)
    d.text((x + pad, y + pad - 2), text, font=FONT, fill=WHITE)


def annotate(img, draws):
    im = img.convert("RGB")
    d = ImageDraw.Draw(im)
    for b, lab, lp, la in draws:
        _box(d, b)
        _label(d, lp, lab, la)
    return im


def shot(name):
    return Image.open(os.path.join(SHOTS, name)).convert("RGB")


def webp_datauri(im, width=1320, quality=82):
    w, h = im.size
    im2 = im.resize((width, int(h * width / w)), Image.LANCZOS)
    buf = io.BytesIO()
    im2.save(buf, "WEBP", quality=quality, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def blur(im, box, radius=16):
    im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(radius)), box)
    return im


def build_images():
    # ---- shared images (referenced by {{IMG_*}} placeholders) ----
    data = {}
    # Step 1 — homepage: crop the browser chrome off the top
    data["home"] = webp_datauri(shot("1.png").crop((0, CHROME_CROP, 2880, 1800)))
    # Step 1 — sign-in: blur the private email row, THEN crop the chrome
    sign = blur(shot("2.png"), EMAIL_BOX, 22)
    data["signin"] = webp_datauri(sign.crop((0, CHROME_CROP, 2880, 1800)))
    # Step 4 — the `lemma auth login` browser page (chrome + bookmarks cropped off)
    data["cli_login"] = webp_datauri(shot("cli-login.png").crop((0, 255, 2880, 1800)), quality=80)
    # Step 6 — the agent building the pod (shared illustration)
    data["agent_building"] = webp_datauri(shot("agent-building.png"), quality=80)
    # OpenCode free-credits walkthrough (animated GIF, embedded as-is)
    with open(GIF, "rb") as f:
        data["opencode_gif"] = "data:image/gif;base64," + base64.b64encode(f.read()).decode()

    # ---- per-agent swappable shots: step2 (open), step3 (prompt+working), step5 (done) ----
    # OpenCode step 2: box the + (Open project) button
    op = shot("step2-openproject.png")
    _box(ImageDraw.Draw(op), (32, 212, 100, 278))
    # Claude step 5: blur the account email
    claude5 = blur(shot("claude-install.png"), (790, 345, 1045, 392))
    # Codex step 5: blur the pod / company name
    codex5 = blur(shot("codex-install.png"), (925, 84, 1110, 120))

    shots = {
        "opencode": {
            "step2": webp_datauri(op, quality=80),
            "step3": webp_datauri(shot("oc-step3.png"), quality=80),
            "step5": webp_datauri(shot("agent-starters.png"), quality=80),
        },
        "codex": {
            "step2": webp_datauri(shot("codex-open.png"), quality=80),
            "step3": webp_datauri(shot("codex-step3.png"), quality=80),
            "step5": webp_datauri(codex5, quality=80),
        },
        "claude": {
            "step2": webp_datauri(shot("claude-open.png"), quality=80),
            "step3": webp_datauri(shot("claude-step3.png"), quality=80),
            "step5": webp_datauri(claude5, quality=80),
        },
    }
    return data, shots


PLACEHOLDERS = {
    "{{IMG_HOME}}": "home",
    "{{IMG_SIGNIN}}": "signin",
    "{{IMG_CLI_LOGIN}}": "cli_login",
    "{{IMG_AGENT_BUILDING}}": "agent_building",
    "{{IMG_GIF}}": "opencode_gif",
}


def main():
    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    data, shots = build_images()
    for ph, key in PLACEHOLDERS.items():
        html = html.replace(ph, data[key])
    # The template uses local image paths so it previews cleanly before build.
    # For the final single-file page, promote data-embed values into src.
    html = re.sub(r'src="[^"]*"\s+data-embed="(data:image/[^"]+)"', r'src="\1"', html)
    html = html.replace("{{SHOTS_JS}}", json.dumps(shots))
    leftover = re.findall(r"\{\{[^}]+\}\}", html)
    if leftover:
        raise SystemExit(f"Unfilled placeholders: {leftover}")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {OUT}  ({len(html.encode()) // 1024} KB)")


if __name__ == "__main__":
    main()
