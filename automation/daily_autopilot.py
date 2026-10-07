import json
import math
import os
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path("outbox")
OUT.mkdir(exist_ok=True)

TOPICS = [
    {
        "topic": "What if Earth stopped spinning for 5 seconds?",
        "hook": "Earth hits pause. Physics does not.",
        "fact": "At the equator, Earth rotates at about 1,670 km/h.",
        "danger": "The ground stops, but air, oceans and loose objects keep moving.",
        "payoff": "It would feel less like a pause and more like a planet-sized slap.",
    },
    {
        "topic": "What if a black hole passed through Earth?",
        "hook": "A black hole crosses Earth like a silent bullet.",
        "fact": "Gravity acts even when the object is tiny.",
        "danger": "It could trigger violent seismic effects along its path.",
        "payoff": "The scary part is not darkness. It is gravity cutting cleanly.",
    },
    {
        "topic": "What if the Moon disappeared tonight?",
        "hook": "The Moon vanishes. The ocean notices first.",
        "fact": "The Moon strongly affects tides and stabilizes Earth's tilt.",
        "danger": "Tides weaken, nights darken and long-term climate stability changes.",
        "payoff": "The sky looks empty, but the real damage starts in the oceans.",
    },
    {
        "topic": "What if you dropped neutron-star matter on Earth?",
        "hook": "Imagine a sugar cube heavier than a mountain.",
        "fact": "Neutron-star matter is incredibly dense nuclear-scale material.",
        "danger": "Its gravity and pressure would violently disturb everything nearby.",
        "payoff": "A tiny cube would behave less like an object and more like a disaster.",
    },
]

CAPTION_SUFFIX = "\n\nImpossible questions. Real science.\n#space #science #whatif #physics #shorts #orbitunknown"


def pick_topic():
    return random.choice(TOPICS)


def build_package(seed):
    script = (
        f"{seed['hook']}\n\n"
        f"{seed['fact']}\n\n"
        f"Now the dangerous part: {seed['danger']}\n\n"
        f"{seed['payoff']}\n\n"
        "Orbit Unknown. Impossible questions. Real science."
    )
    metadata = {
        "title": seed["topic"].replace("What if", "What If"),
        "caption": f"{seed['topic']} 🌍🚀" + CAPTION_SUFFIX,
        "privacyStatus": "public",
        "madeAt": datetime.now(timezone.utc).isoformat(),
    }
    scenes = [
        {"time": "0-4s", "text": seed["hook"]},
        {"time": "4-8s", "text": seed["fact"]},
        {"time": "8-13s", "text": seed["danger"]},
        {"time": "13-16s", "text": seed["payoff"]},
    ]
    return {"topic": seed["topic"], "script": script, "metadata": metadata, "scenes": scenes}


def font(size, bold=False):
    base = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(base, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_caption(draw, text, w, h):
    fnt = font(46, True)
    lines = wrap(draw, text, fnt, w - 120)
    box_h = len(lines) * 62 + 44
    y = h - 360
    draw.rounded_rectangle((48, y, w - 48, y + box_h), radius=34, fill=(0, 0, 0, 180))
    yy = y + 24
    for line in lines:
        tw = draw.textbbox((0, 0), line, font=fnt)[2]
        draw.text(((w - tw) / 2, yy), line, font=fnt, fill=(255, 255, 255))
        yy += 62


def draw_earth(draw, cx, cy, r, shocked=False):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(20, 110, 215), outline=(115, 220, 255), width=6)
    for i in range(7):
        a = i * 0.95
        x = cx + math.cos(a) * r * 0.43
        y = cy + math.sin(a * 1.25) * r * 0.35
        draw.ellipse((x - r * 0.16, y - r * 0.09, x + r * 0.18, y + r * 0.11), fill=(45, 190, 95))
    if shocked:
        draw.ellipse((cx - r * 0.35, cy - r * 0.16, cx - r * 0.22, cy - r * 0.02), fill=(255, 255, 255))
        draw.ellipse((cx + r * 0.22, cy - r * 0.16, cx + r * 0.35, cy - r * 0.02), fill=(255, 255, 255))
        draw.ellipse((cx - r * 0.1, cy + r * 0.17, cx + r * 0.1, cy + r * 0.34), fill=(0, 0, 0))
    else:
        draw.arc((cx - r * 0.25, cy + r * 0.1, cx + r * 0.25, cy + r * 0.35), 0, 180, fill=(0, 0, 0), width=6)


def make_video(package):
    w, h, fps, duration = 1080, 1920, 24, 16
    frames = OUT / "frames"
    frames.mkdir(exist_ok=True)
    for old in frames.glob("*.jpg"):
        old.unlink()
    captions = [s["text"] for s in package["scenes"]]
    for i in range(fps * duration):
        t = i / fps
        img = Image.new("RGB", (w, h), (5, 7, 24))
        draw = ImageDraw.Draw(img, "RGBA")
        random.seed(10)
        for s in range(180):
            x = (random.randint(0, w) + int(t * (8 + s % 5))) % w
            y = random.randint(0, h)
            draw.ellipse((x, y, x + 2, y + 2), fill=(255, 255, 255, random.randint(50, 170)))
        draw.rounded_rectangle((55, 64, 430, 122), 22, fill=(0, 0, 0, 125))
        draw.text((80, 78), "ORBIT UNKNOWN", font=font(38, True), fill=(255, 220, 140))
        if t < 4:
            draw.text((70, 220), "WHAT IF", font=font(90, True), fill=(255, 255, 255))
            draw.text((70, 325), "EARTH STOPPED", font=font(78, True), fill=(255, 192, 96))
            draw.text((70, 420), "SPINNING?", font=font(90, True), fill=(105, 220, 255))
            draw_earth(draw, 540, 900, 245, False)
        elif t < 8:
            draw_earth(draw, 540, 770, 260, True)
            draw.rounded_rectangle((160, 1180, 920, 1285), 28, fill=(255, 65, 65, 220))
            draw.text((235, 1210), "PHYSICS SAYS NO", font=font(58, True), fill=(255, 255, 255))
        elif t < 13:
            for y in range(500, 1360, 120):
                draw.line((80, y, 1000, y + 45), fill=(95, 220, 255, 110), width=10)
            draw_earth(draw, 540 + 18 * math.sin(t * 35), 790, 245, True)
        else:
            draw_earth(draw, 540, 720, 260, False)
            draw.text((90, 1185), "ORBIT UNKNOWN", font=font(82, True), fill=(255, 255, 255))
            draw.text((120, 1290), "Impossible Questions.", font=font(52, True), fill=(255, 200, 95))
            draw.text((250, 1360), "Real Science.", font=font(52, True), fill=(105, 220, 255))
        cap = captions[min(int(t / 4), len(captions) - 1)]
        draw_caption(draw, cap, w, h)
        img.save(frames / f"frame_{i:05d}.jpg", quality=90)

    out = OUT / "latest.mp4"
    cmd = [
        "ffmpeg", "-y", "-framerate", str(fps), "-i", str(frames / "frame_%05d.jpg"),
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100", "-shortest",
        "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)
    ]
    subprocess.run(cmd, check=True)
    return str(out)


def main():
    seed = pick_topic()
    package = build_package(seed)
    (OUT / "latest.json").write_text(json.dumps(package, indent=2), encoding="utf-8")
    (OUT / "latest_caption.txt").write_text(package["metadata"]["caption"], encoding="utf-8")
    (OUT / "latest_script.txt").write_text(package["script"], encoding="utf-8")
    make_video(package)
    print(json.dumps(package["metadata"], indent=2))


if __name__ == "__main__":
    main()
