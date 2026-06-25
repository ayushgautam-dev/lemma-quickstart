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


def build_images():
    data = {}

    # Step 1 — homepage: crop the browser chrome off the top
    home = shot("1.png").crop((0, CHROME_CROP, 2880, 1800))
    data["home"] = webp_datauri(home)

    # Step 1 — sign-in: blur the private email row, THEN crop the chrome
    sign = shot("2.png")
    sign.paste(sign.crop(EMAIL_BOX).filter(ImageFilter.GaussianBlur(22)), EMAIL_BOX)
    sign = sign.crop((0, CHROME_CROP, 2880, 1800))
    data["signin"] = webp_datauri(sign)

    # Step 2 — onboarding "Connect your AI": box the Recheck button
    data["onboard_connect"] = webp_datauri(annotate(shot("3-onboarding.png"), [
        ((1905, 762, 2125, 842), "Click Recheck after the prompt", (1885, 772), "rt"),
    ]), quality=80)

    # Step 4 — detected harness selected
    data["onboard_select"] = webp_datauri(annotate(shot("5-onboarding.png"), [
        ((788, 798, 2092, 928), "Click your agent to select it", (788, 690), "lt"),
    ]), quality=80)

    # Step 5 — describe your pod
    data["describe"] = webp_datauri(shot("6.png"), quality=80)

    # Step 6 — pod working: box the model selector in the message bar
    data["working"] = webp_datauri(annotate(shot("7.png"), [
        ((942, 1670, 1145, 1744), "Click the model to change it", (942, 1556), "lt"),
    ]), quality=80)

    # Step 7 — choose-model modal + default selected
    data["model_modal"] = webp_datauri(shot("8.png"), quality=80)
    data["model_default"] = webp_datauri(shot("9.png"), quality=80)

    # OpenCode desktop walkthrough (animated GIF, embedded as-is)
    with open(GIF, "rb") as f:
        data["opencode_gif"] = "data:image/gif;base64," + base64.b64encode(f.read()).decode()
    return data


PLACEHOLDERS = {
    "{{IMG_HOME}}": "home",
    "{{IMG_SIGNIN}}": "signin",
    "{{IMG_ONBOARD_CONNECT}}": "onboard_connect",
    "{{IMG_ONBOARD_SELECT}}": "onboard_select",
    "{{IMG_DESCRIBE}}": "describe",
    "{{IMG_WORKING}}": "working",
    "{{IMG_MODEL_MODAL}}": "model_modal",
    "{{IMG_MODEL_DEFAULT}}": "model_default",
    "{{IMG_GIF}}": "opencode_gif",
}


def main():
    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    images = build_images()
    for ph, key in PLACEHOLDERS.items():
        html = html.replace(ph, images[key])
    leftover = re.findall(r"\{\{[^}]+\}\}", html)
    if leftover:
        raise SystemExit(f"Unfilled placeholders: {leftover}")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {OUT}  ({len(html.encode()) // 1024} KB)")


if __name__ == "__main__":
    main()
