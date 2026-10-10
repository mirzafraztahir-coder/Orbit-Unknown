"""Image-driven Orbit Unknown renderer. Fails closed without five independent source photographs."""
import json
import math
import os
import subprocess
import wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path("assets/cinematic")
OUT=Path("outbox")
W,H,FPS,DURATION=720,1280,20,40
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def run(cmd):
    subprocess.run(cmd,check=True)

def validate_images(topic):
    folder=ROOT/topic
    paths=[folder/f"scene_{i:02d}.jpg" for i in range(1,6)]
    if not all(p.is_file() for p in paths):
        raise SystemExit("QUALITY GATE: Five separate cinematic scene JPEGs are required at "+str(folder)+"; refusing template video and YouTube upload.")
    for p in paths:
        with Image.open(p) as im:
            if im.width<720 or im.height<1100:
                raise SystemExit(f"QUALITY GATE: {p} is too small: {im.size}")
    return paths

def caption(im,txt):
    d=ImageDraw.Draw(im,"RGBA")
    font=ImageFont.truetype(FONT,35)
    words=txt.split()
    lines=[];line=""
    for word in words:
        candidate=(line+" "+word).strip()
        if d.textbbox((0,0),candidate,font=font)[2] > 610:
            if line:lines.append(line)
            line=word
        else:line=candidate
    if line:lines.append(line)
    if len(lines)>3:raise SystemExit("QUALITY GATE: Caption too long")
    y=970
    d.rounded_rectangle((40,y-20,680,y+len(lines)*53+23),radius=22,fill=(0,0,0,195))
    for j,line in enumerate(lines):
        width=d.textbbox((0,0),line,font=font)[2]
        d.text(((W-width)//2,y+j*53),line,font=font,fill="white")
    d.text((W//2,1210),"ORBIT UNKNOWN",anchor="mm",font=ImageFont.truetype(FONT,22),fill=(255,225,185,255))

def render(topic,scenes,voice_file):
    paths=validate_images(topic)
    OUT.mkdir(exist_ok=True)
    frames=OUT/"cinematic_frames";frames.mkdir(exist_ok=True)
    for old in frames.glob("*.jpg"):old.unlink()
    for scene in range(5):
        with Image.open(paths[scene]) as original:
            src=original.convert("RGB")
            scale=max(790/src.width,1410/src.height)
            src=src.resize((round(src.width*scale),round(src.height*scale)),Image.Resampling.LANCZOS)
        for f in range(8*FPS):
            progress=f/(8*FPS-1)
            # Restrained pan and push, always cropping from an individual scene image.
            zoom=1+0.045*progress
            crop_w=int(720/zoom);crop_h=int(1280/zoom)
            x=int((src.width-crop_w)*(0.42+0.16*progress))
            y=int((src.height-crop_h)*(0.48+0.04*math.sin(progress*math.pi)))
            x=max(0,min(x,src.width-crop_w));y=max(0,min(y,src.height-crop_h))
            frame=src.crop((x,y,x+crop_w,y+crop_h)).resize((W,H),Image.Resampling.LANCZOS)
            caption(frame,scenes[scene])
            frame.save(frames/f"frame_{scene*8*FPS+f:05d}.jpg",quality=90)
    # Original low-level cinematic drone; never use copyrighted soundtrack.
    rate=24000
    audio=np.arange(rate*DURATION)/rate
    music=np.zeros(len(audio))
    for hz,vol in [(55,.085),(82.4,.045),(110,.03)]:
        music+=vol*np.sin(2*np.pi*hz*audio)
    music*=np.minimum(1,audio/3)*np.minimum(1,(DURATION-audio)/3)
    with wave.open(str(OUT/"score.wav"),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
        w.writeframes((np.clip(music,-1,1)*32767).astype("<i2").tobytes())
    run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",str(frames/"frame_%05d.jpg"),"-i",str(voice_file),"-i",str(OUT/"score.wav"),"-filter_complex","[1:a]apad,atrim=0:40,volume=1.8[v];[2:a]volume=0.6[m];[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]","-map","0:v","-map","[a]","-c:v","libx264","-preset","medium","-crf","23","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-t","40","-movflags","+faststart",str(OUT/"latest.mp4")])
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(OUT/"latest.mp4")]))
    streams=probe["streams"]
    v=next((s for s in streams if s["codec_type"]=="video"),None)
    if not v or (v["width"],v["height"])!=(720,1280) or not any(s["codec_type"]=="audio" for s in streams):
        raise SystemExit("QUALITY GATE: Invalid MP4 format or missing audio")
    if abs(float(probe["format"]["duration"])-40)>0.5:
        raise SystemExit("QUALITY GATE: MP4 is not approximately 40 seconds")
    print("Technical quality gate passed",topic)

if __name__=="__main__":
    topic=os.environ.get("ORBIT_TOPIC","earth-rings")
    folder=ROOT/topic
    scenes=json.loads((folder/"captions.json").read_text())
    if len(scenes)!=5:raise SystemExit("QUALITY GATE: exactly five captions required")
    voice=folder/"narration.wav"
    if not voice.is_file():raise SystemExit("QUALITY GATE: documentary narration WAV missing")
    render(topic,scenes,voice)
