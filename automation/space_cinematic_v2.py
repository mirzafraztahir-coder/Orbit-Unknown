"""Orbit Unknown: independently sourced NASA imagery, 40-second cinematic video.
No manual uploads, no legacy cartoon templates, and no publication in this script.
NASA imagery illustrates hypothetical scenarios; it does not depict the scenario itself.
"""
import asyncio
import hashlib
import json
import math
import os
import random
import re
import subprocess
import wave
from datetime import datetime, timedelta, timezone, date
from extra_episodes import EXTRA_TOPICS
from io import BytesIO
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps, ImageStat

try:
    import edge_tts
except ImportError as exc:
    raise SystemExit("QUALITY GATE: edge-tts missing; refusing robotic narration") from exc

ROOT = Path("outbox")
FRAMES = ROOT / "frames_cinematic"
W, H, FPS, SECONDS = 720, 1280, 20, 40
PKT = timezone(timedelta(hours=5))
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "OrbitUnknownScienceShorts/1.0 (NASA media attribution)"})
TIMEOUT = (12, 30)

# Each entry has five distinct documentary shots, lines of narration and visible captions.
# The topic rotates deterministically and cannot repeat on consecutive days.
TOPICS = [
    {"slug":"earth-rings","title":"What If Earth Had Rings Like Saturn?","beats":[
        ("What if Earth suddenly had magnificent rings, just like Saturn? Our night sky would never look the same.","WHAT IF EARTH HAD RINGS?","planet earth blue marble space"),
        ("Imagine vast shimmering bands overhead, visible from the ground, but looking different at different latitudes.","A SKY TRANSFORMED","earth horizon atmosphere space"),
        ("Those rings could contain countless fragments of ice and rock, each racing around our planet.","BILLIONS OF ORBITING PIECES","saturn rings Cassini"),
        ("Their shadows could sometimes reduce sunlight reaching parts of Earth, affecting the world beneath them.","SHADOWS ACROSS EARTH","earth from space clouds shadows"),
        ("Satellites would face new hazards. Beautiful from below, but far more complicated for space travel.","BEAUTIFUL, BUT DANGEROUS","earth satellites space station")
    ]},
    {"slug":"sun-vanished","title":"What If the Sun Vanished?","beats":[
        ("What if the Sun vanished instantly? On Earth, everything would still look normal for eight minutes.","THE SUN DISAPPEARS","sun solar observatory"),
        ("Then the last sunlight would pass us, and Earth's sunlit side would fall into darkness.","EIGHT MINUTES LATER","earth city lights night space"),
        ("That is also when changes in the Sun's gravity would reach Earth, ending our familiar solar orbit.","GRAVITY'S DELAY","earth solar system planet orbit"),
        ("Without sunlight, temperatures would fall over time, and oceans would eventually freeze from the surface.","A WORLD GROWING COLDER","earth polar ice from space"),
        ("Geothermal energy might sustain small groups underground. But survival would be extraordinarily difficult.","COULD ANYONE SURVIVE?","earth aurora stars space")
    ]},
    {"slug":"moon-vanished","title":"What If the Moon Vanished Tonight?","beats":[
        ("Suppose the Moon disappeared tonight. The sky would darken, but Earth would not instantly collapse.","THE MOON IS GONE","full moon lunar surface"),
        ("The Moon creates much of our ocean tide, so tidal patterns would change significantly.","OUR TIDES WOULD CHANGE","earth ocean coastline space"),
        ("The Sun would still produce tides. So the sea would never simply stop moving.","THE SUN STILL MAKES TIDES","ocean earth from orbit"),
        ("Over much longer timescales, Earth's tilt could become less stable without the Moon's influence.","EARTH'S TILT MATTERS","earth tilt axis space"),
        ("The result would be a different world, but not an instant doomsday. Would you miss it?","NOT AN INSTANT APOCALYPSE","Earthrise Apollo 8 moon")
    ]},
    {"slug":"jupiter-dive","title":"What If You Fell Into Jupiter?","beats":[
        ("What would happen if you tried to fall through Jupiter's giant swirling clouds?","FALLING INTO JUPITER","jupiter planet Juno"),
        ("There is no familiar solid ground waiting beneath that spectacular cloud cover.","NO SOLID SURFACE","jupiter clouds great red spot"),
        ("As you descend, pressure and temperature rise to crushing, unimaginable levels.","PRESSURE KEEPS RISING","jupiter atmosphere Juno clouds"),
        ("Deep inside, hydrogen behaves in strange ways, potentially becoming a conducting metallic fluid.","STRANGE DEEP INTERIOR","jupiter planet Juno"),
        ("Jupiter is breathtaking from space. But it is definitely not a planet you could land on.","A WORLD WITHOUT LANDING","jupiter planet Hubble")
    ]},
    {"slug":"saturn-rings","title":"What If Saturn Lost Its Rings?","beats":[
        ("Imagine looking at Saturn one morning, only to discover that its legendary rings are gone.","SATURN WITHOUT RINGS","saturn Cassini rings"),
        ("The rings contain enormous numbers of icy particles, orbiting in a thin, wide disk.","ICE IN ORBIT","saturn ring details Cassini"),
        ("Without them, Saturn would still remain an enormous gas giant with magnificent cloud bands.","THE PLANET SURVIVES","saturn globe Cassini"),
        ("Its moons would continue their journeys, though their interactions with ring material would change.","SATURN'S MANY MOONS","saturn moon Titan Cassini"),
        ("The solar system would lose one of its greatest sights. Which view would you prefer?","A COSMIC LOSS","saturn planet NASA")
    ]},
    {"slug":"mars-ocean","title":"What If Mars Had an Ocean Today?","beats":[
        ("Imagine oceans rolling beneath the pink skies of Mars, where dry plains stretch today.","OCEANS ON MARS?","Mars planet surface panorama"),
        ("Ancient Martian landscapes preserve powerful evidence that water once flowed across the planet.","WATER ON ANCIENT MARS","mars ancient river delta Perseverance"),
        ("But liquid oceans today would need a dramatically thicker atmosphere and much warmer conditions.","A THICKER ATMOSPHERE","mars horizon clouds rover"),
        ("Even with blue seas, intense radiation and other challenges could still threaten life.","WATER IS NOT ENOUGH","Mars planet NASA orbiter"),
        ("Could humans someday build a new world there? The physics makes it very difficult.","THE RED PLANET REIMAGINED","Mars planet full disk")
    ]},
    {"slug":"nearby-supernova","title":"What If a Star Exploded Near Earth?","beats":[
        ("What if a nearby star exploded in a brilliant supernova? Distance would determine everything.","A STAR EXPLODES","supernova nebula Hubble"),
        ("From far enough away, the blast would be an extraordinary light in the night sky.","A COSMIC FLASH","supernova remnant telescope"),
        ("But very close explosions can release radiation capable of damaging Earth's atmosphere.","DANGEROUS RADIATION","stellar explosion remnant nebula"),
        ("Our protective atmosphere matters enormously, but it cannot stop every possible cosmic threat.","EARTH'S PROTECTIVE SHIELD","earth atmosphere sunrise space"),
        ("Fortunately, truly dangerous nearby supernovae appear very uncommon. Space is both beautiful and immense.","DISTANCE IS OUR SHIELD","milky way stars galaxy")
    ]},
    {"slug":"two-moons","title":"What If Earth Had Two Moons?","beats":[
        ("Imagine two brilliant moons hanging over our cities every night.","TWO MOONS ABOVE US","full moon lunar NASA"),
        ("Both moons would pull on Earth's oceans, making tides more complicated.","TWICE THE GRAVITY?","earth ocean space"),
        ("The exact effects would depend on each moon's size, distance, and orbital path.","ORBITS DECIDE EVERYTHING","moon earth spacecraft"),
        ("Some configurations might remain stable, while others could evolve into dangerous gravitational encounters.","A DELICATE DANCE","moon surface earth sky"),
        ("A second moon sounds magical. But orbital mechanics always has the final say.","A BEAUTIFUL COMPLICATION","earthrise Apollo moon")
    ]},
    {"slug":"neptune-winds","title":"What If You Entered Neptune's Storms?","beats":[
        ("Neptune looks calm and blue from a distance. Up close, its atmosphere is anything but peaceful.","A WORLD OF STORMS","Neptune Voyager 2"),
        ("Winds on this distant planet can reach astonishing speeds, far beyond Earth's strongest hurricanes.","SUPERSONIC-FAST WINDS","Neptune planet NASA"),
        ("The planet receives very little sunlight, yet giant storms still develop in its atmosphere.","STORMS IN THE DARK","Neptune dark spot storm"),
        ("Far below the clouds, the pressure increases dramatically in a world very different from Earth.","BENEATH THE CLOUDS","Neptune blue planet"),
        ("Neptune remains one of our most mysterious neighbors. What other secrets are hidden there?","DISTANT AND MYSTERIOUS","Neptune Voyager NASA")
    ]},
    {"slug":"black-hole","title":"What If a Black Hole Passed Near Earth?","beats":[
        ("What if a black hole moved through our cosmic neighborhood? You might never see it directly.","AN INVISIBLE VISITOR","black hole nasa illustration"),
        ("Black holes affect their surroundings through gravity, not by magically swallowing everything.","GRAVITY IS THE THREAT","black hole accretion disk NASA"),
        ("Its mass, speed and distance would decide whether Earth's orbit changed.","DISTANCE CHANGES EVERYTHING","earth solar system orbit space"),
        ("A close encounter could disturb planets and send objects into different paths.","ORBITS UNDER THREAT","solar system planets NASA"),
        ("The universe holds extreme objects, but space is vast, making such encounters extraordinarily unlikely.","SPACE IS ENORMOUS","milky way deep field stars")
    ]}
]

TOPICS.extend(EXTRA_TOPICS)

def log(message):
    print(message, flush=True)

def command(args, capture=False):
    if capture:
        return subprocess.check_output(args, stderr=subprocess.STDOUT).decode("utf-8")
    subprocess.run(args, check=True)

def choose_today():
    dt = datetime.now(PKT).date()
    slot = os.environ.get("ORBIT_SLOT", "").strip().lower()
    if slot not in ("morning", "evening"):
        raise RuntimeError("ORBIT_SLOT must be morning or evening; refusing ambiguous production")
    # Each slot consumes one distinct episode. Reserve the original Sun Vanished
    # episode as the reference movie, not as a recycled upload.
    available = [ep for ep in TOPICS if ep["slug"] != "sun-vanished"]
    days = (dt - date(2026, 10, 11)).days
    ordinal = 2 * days + (0 if slot == "morning" else 1)
    if ordinal < 0 or ordinal >= len(available):
        raise RuntimeError("Unique topics exhausted: add original episodes; never silently repeat videos.")
    topic = available[ordinal]
    return dt.isoformat(), topic, slot

def get_json(url, **kwargs):
    r = SESSION.get(url, timeout=TIMEOUT, **kwargs)
    r.raise_for_status()
    return r.json()

def fetch_photo(query, used_ids, used_hashes, folder, number):
    search = get_json("https://images-api.nasa.gov/search",
                      params={"q": query, "media_type":"image", "page_size":30})
    items = search.get("collection", {}).get("items", [])
    blocked = ("logo", "patch", "infographic", "chart", "diagram", "poster", "screenshot", "press conference")
    errors = []
    for entry in items[:24]:
        data = (entry.get("data") or [{}])[0]
        nasa_id = data.get("nasa_id")
        title = str(data.get("title", ""))
        # Reject a photograph or rendering of the wrong celestial body.
        # NASA free-text search may otherwise pair an Earth/Moon script with
        # an unrelated exoplanet, even when the video file passes ffprobe.
        query_low = query.lower()
        title_low = title.lower()
        incompatible_worlds = (
            "trappist", "kepler-", "exoplanet", "proxima", "venus",
            "mars", "mercury", "jupiter", "saturn", "uranus",
            "neptune", "pluto", "titan", "enceladus", "europa", "phobos"
        )
        if any(world in title_low and world not in query_low for world in incompatible_worlds):
            continue
        if any(word in title_low for word in ("artist's concept", "artists concept", "artist impression")) and "illustration" not in query_low:
            continue
        if not nasa_id or nasa_id in used_ids or any(x in title.lower() for x in blocked):
            continue
        if data.get("copyright"):
            continue
        try:
            manifest = get_json(entry["href"])
            assets = (manifest if isinstance(manifest, list)
                      else manifest.get("collection", {}).get("items", []))
            urls = [a if isinstance(a, str) else a.get("href", "") for a in assets]
            urls = [u for u in urls if re.search(r"\.(jpe?g|png)(\?.*)?$", u, re.I)]
            preferred = sorted(urls, key=lambda u: (
                0 if "~large" in u.lower() else
                1 if "~orig" in u.lower() else
                2 if "~medium" in u.lower() else 3))
            for url in preferred[:3]:
                r = SESSION.get(url, timeout=(12,38), stream=True)
                r.raise_for_status()
                total = 0
                chunks = []
                for chunk in r.iter_content(65536):
                    if chunk:
                        chunks.append(chunk)
                        total += len(chunk)
                        if total > 14_000_000:
                            break
                if total > 14_000_000:
                    continue
                with Image.open(BytesIO(b"".join(chunks))) as raw:
                    im = ImageOps.exif_transpose(raw).convert("RGB")
                if im.width < 900 or im.height < 600:
                    continue
                if max(im.width, im.height) < 1150:
                    continue
                small = im.resize((16,16)).convert("L")
                digest = hashlib.sha256(small.tobytes()).hexdigest()
                if digest in used_hashes:
                    continue
                used_ids.add(nasa_id)
                used_hashes.add(digest)
                dest = folder / f"source_{number:02d}.jpg"
                im.thumbnail((2500,2500), Image.Resampling.LANCZOS)
                im.save(dest, quality=93, optimize=True)
                return dest, {"nasa_id":nasa_id,"title":title,"url":url,"query":query,
                              "center":data.get("center","NASA")}
        except Exception as exc:
            errors.append(str(exc)[:100])
            continue
    raise RuntimeError("Could not download a distinct high-resolution NASA image for: " + query +
                       "; samples: " + " | ".join(errors[:2]))

def photograph_canvas(photo, dest):
    # One photo per scene: crop to a tall cinematic frame, then restrained contrast/color grading.
    with Image.open(photo) as raw:
        pic = ImageOps.exif_transpose(raw).convert("RGB")
    pic = ImageOps.fit(pic, (800, 1422), method=Image.Resampling.LANCZOS, centering=(0.5,0.48))
    pic = ImageEnhance.Contrast(pic).enhance(1.08)
    pic = ImageEnhance.Color(pic).enhance(1.13)
    pic = ImageEnhance.Brightness(pic).enhance(0.92)
    pic.save(dest, quality=94, optimize=True)

def overlay(caption, dest):
    canvas = Image.new("RGBA",(W,H),(0,0,0,0))
    d = ImageDraw.Draw(canvas,"RGBA")
    bfont = ImageFont.truetype(FONT,36)
    sfont = ImageFont.truetype(FONT,23)
    d.rounded_rectangle((34,48,328,102),radius=16,fill=(0,0,0,168))
    d.text((52,61),"ORBIT UNKNOWN",font=sfont,fill=(255,227,180,255))
    words=caption.upper().split()
    lines=[];running=""
    for word in words:
        trial=(running+" "+word).strip()
        if d.textbbox((0,0),trial,font=bfont)[2] > 590:
            if running: lines.append(running)
            running=word
        else: running=trial
    if running: lines.append(running)
    if len(lines)>3: raise RuntimeError("Caption too long to fit safe area: "+caption)
    y=940
    top=y-23
    bot=y+len(lines)*53+22
    if bot > 1150:raise RuntimeError("Caption overlaps Shorts UI safe area")
    d.rounded_rectangle((42,top,678,bot),radius=24,fill=(0,0,0,196))
    for i,line in enumerate(lines):
        width=d.textbbox((0,0),line,font=bfont)[2]
        d.text(((W-width)/2, y+i*53),line,font=bfont,fill=(255,255,255,255))
    canvas.save(dest)

async def synthesize_voice(beats,folder):
    """Use Edge neural speech when available, with offline Piper neural fallback."""
    try:
        for index,(sentence,_,_) in enumerate(beats,1):
            file = folder / f"narration_{index:02d}.mp3"
            await edge_tts.Communicate(sentence, voice="en-US-ChristopherNeural", rate="+7%").save(str(file))
            if not file.is_file() or file.stat().st_size < 2000:
                raise RuntimeError("Edge narration missing or too small")
        return
    except Exception as exc:
        log(f"Edge neural voice unavailable ({exc}); switching to Piper neural voice.")
    model = folder / "en_US-lessac-medium.onnx"
    config = folder / "en_US-lessac-medium.onnx.json"
    base = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/"
    for name,dest in [(model.name,model),(config.name,config)]:
        if not dest.exists():
            response = SESSION.get(base + name, timeout=(20,180))
            response.raise_for_status()
            dest.write_bytes(response.content)
    if model.stat().st_size < 1000000:
        raise RuntimeError("Piper neural model download invalid")
    for index,(sentence,_,_) in enumerate(beats,1):
        wav = folder / f"piper_{index:02d}.wav"
        subprocess.run(["python","-m","piper","--model",str(model),"--config",str(config),
                        "--output_file",str(wav)],input=sentence,text=True,check=True)
        command(["ffmpeg","-y","-loglevel","error","-i",str(wav),
                 "-codec:a","libmp3lame","-qscale:a","3",
                 str(folder / f"narration_{index:02d}.mp3")])
        if (folder / f"narration_{index:02d}.mp3").stat().st_size < 2000:
            raise RuntimeError("Piper neural narration invalid for scene " + str(index))

def score_and_voice(beats,folder,outfile):
    rate=24000
    t=np.arange(SECONDS*rate,dtype=np.float64)/rate
    music=np.zeros(len(t),dtype=np.float64)
    for freq,amp in [(55.0,.023),(82.41,.014),(110.0,.009),(164.8,.008)]:
        music+=amp*np.sin(2*np.pi*freq*t)
    music+=.009*np.sin(2*np.pi*220*t)*(np.sin(2*np.pi*.25*t)**2)
    music*=np.minimum(1,t/2.0)*np.minimum(1,(SECONDS-t)/3.0)
    rng=np.random.default_rng(176)
    for beat in range(5):
        delta=np.maximum(0,t-beat*8)
        music+=np.where(t>=beat*8,.028*np.exp(-2*delta)*np.sin(2*np.pi*(48*delta+14*delta*delta)),0)
    combined=music.copy()
    for i in range(5):
        pcm=folder/f"voice_{i+1:02d}.pcm"
        command(["ffmpeg","-y","-loglevel","error","-i",str(folder/f"narration_{i+1:02d}.mp3"),
                 "-ac","1","-ar",str(rate),"-f","s16le",str(pcm)])
        samples=np.fromfile(pcm,dtype="<i2").astype(np.float64)/32768
        maximum=rate*7.5
        if len(samples)>maximum:
            ratio=len(samples)/maximum
            if ratio>1.17:
                raise RuntimeError(f"Neural narration in scene {i+1} exceeds 8-second shot ({len(samples)/rate:.1f}s)")
            samples=np.interp(np.linspace(0,len(samples)-1,int(maximum)),
                              np.arange(len(samples)),samples)
        voice_rms=np.sqrt(np.mean(samples*samples))
        if voice_rms<.003:
            raise RuntimeError("Narration has low audio level")
        samples*=min(3.3,.15/voice_rms)
        start=(i*8)*rate+int(rate*.25)
        end=min(len(combined),start+len(samples))
        combined[start:end]+=samples[:end-start]
    peak=np.max(np.abs(combined))
    if peak>0.93:combined*=0.93/peak
    with wave.open(str(outfile),"wb") as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate)
        wav.writeframes((combined*32767).astype("<i2").tobytes())

def render_video(images,captions,folder):
    frame_folder=folder/"frames"
    frame_folder.mkdir(exist_ok=True)
    for p in frame_folder.glob("frame_*.jpg"): p.unlink()
    for k,image_path in enumerate(images):
        with Image.open(image_path) as raw:
            src=raw.convert("RGB")
        with Image.open(folder/f"overlay_{k+1:02d}.png") as raw_overlay:
            layer=raw_overlay.convert("RGBA")
        for f in range(8*FPS):
            p=f/(8*FPS-1)
            zoom=1+0.055*p
            crop_w=int(720/zoom);crop_h=int(1280/zoom)
            x=int((src.width-crop_w)*(0.4+0.2*p))
            y=int((src.height-crop_h)*(0.48+0.04*math.sin(p*math.pi)))
            x=max(0,min(x,src.width-crop_w))
            y=max(0,min(y,src.height-crop_h))
            img=src.crop((x,y,x+crop_w,y+crop_h)).resize((W,H),Image.Resampling.BICUBIC).convert("RGBA")
            img.alpha_composite(layer)
            img.convert("RGB").save(frame_folder/f"frame_{k*8*FPS+f:05d}.jpg",quality=86)
    out=ROOT/"latest.mp4"
    command(["ffmpeg","-y","-loglevel","error",
             "-framerate",str(FPS),"-i",str(frame_folder/"frame_%05d.jpg"),
             "-i",str(folder/"final_audio.wav"),
             "-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p",
             "-c:a","aac","-b:a","160k","-t","40","-movflags","+faststart",str(out)])
    return out

def technical_gate(video,shots,meta):
    if len(shots)!=5 or len({x["nasa_id"] for x in shots})!=5:
        raise RuntimeError("QUALITY GATE: missing distinct visual scenes")
    inspect=json.loads(command(["ffprobe","-v","error","-show_streams","-show_format",
                                "-of","json",str(video)],capture=True))
    v=next((s for s in inspect["streams"] if s.get("codec_type")=="video"),None)
    a=next((s for s in inspect["streams"] if s.get("codec_type")=="audio"),None)
    duration=float(inspect["format"]["duration"])
    if not v or not a or (v["width"],v["height"])!=(W,H) or abs(duration-40)>.4:
        raise RuntimeError("QUALITY GATE: invalid orientation, duration, or audio stream")
    if video.stat().st_size < 350000:
        raise RuntimeError("QUALITY GATE: output video unexpectedly small")
    probe_path=ROOT/"last_frame.jpg"
    command(["ffmpeg","-y","-loglevel","error","-ss","39.5","-i",str(video),
             "-frames:v","1",str(probe_path)])
    with Image.open(probe_path) as im:
        if sum(ImageStat.Stat(im).stddev)/3 < 8:
            raise RuntimeError("QUALITY GATE: video frames too uniform")
    return {"video":str(video),"duration_seconds":duration,"width":W,"height":H,
            "video_bytes":video.stat().st_size,"sha256":hashlib.sha256(video.read_bytes()).hexdigest(),
            "scene_count":len(shots),"audio_codec":a["codec_name"],"source":"NASA Image and Video Library",
            "visual_relevance_gate_version":1,
            "status":"technical_checks_passed"}

def main():
    edition,topic,slot=choose_today()
    ROOT.mkdir(exist_ok=True)
    work=ROOT/"working";work.mkdir(exist_ok=True)
    beats=topic["beats"]
    ids=set();hashes=set();photos=[];credits=[]
    log(f"Orbit Unknown edition={edition} slot={slot} topic={topic['title']}")
    for i,(_,caption,query) in enumerate(beats,1):
        log(f"Retrieving independent NASA scene {i}: {query}")
        img,credit=fetch_photo(query,ids,hashes,work,i)
        frame=work/f"scene_{i:02d}.jpg"
        photograph_canvas(img,frame)
        overlay(caption,work/f"overlay_{i:02d}.png")
        photos.append(frame)
        credits.append(credit)
    asyncio.run(synthesize_voice(beats,work))
    score_and_voice(beats,work,work/"final_audio.wav")
    video=render_video(photos,[b[1] for b in beats],work)
    credit_lines="\n".join(f"Scene {i}: NASA Image Library ID {x['nasa_id']} ({x['title'][:80]})" for i,x in enumerate(credits,1))
    package={"edition_date_pkt":edition,"edition_id":edition+"-"+slot,"slot":slot,"topic":topic["title"],"slug":topic["slug"],
             "script":" ".join(b[0] for b in beats),
             "metadata":{"title":topic["title"][:100],
                         "caption":topic["title"]+"\n\nImpossible Questions. Real Science.\n"+
                         "Illustrative NASA imagery; hypothetical scenarios are not real footage.\n\n"+
                         credit_lines+"\n\n#space #science #whatif #shorts #orbitunknown",
                         "privacyStatus":"public"},
             "scenes":[{"start":i*8,"end":(i+1)*8,"voice":v,"caption":c,
                        "image_id":credits[i]["nasa_id"]} for i,(v,c,q) in enumerate(beats)],
             "source_credits":credits}
    (ROOT/"latest.json").write_text(json.dumps(package,indent=2),encoding="utf-8")
    verification=technical_gate(video,credits,package)
    verification["edition_date_pkt"]=edition
    verification["edition_id"]=edition+"-"+slot
    verification["slot"]=slot
    (ROOT/"quality_report.json").write_text(json.dumps(verification,indent=2))
    (ROOT/"nasa_credits.json").write_text(json.dumps(credits,indent=2))
    log("QUALITY GATE PASSED: "+json.dumps(verification))
if __name__=="__main__":
    main()
