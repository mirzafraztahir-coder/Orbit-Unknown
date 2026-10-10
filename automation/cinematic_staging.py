"""Staging renderer: 42-second narrated vertical Shorts. Not connected to publishing."""
import json, math, random, subprocess, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path("outbox/cinematic_test")
ROOT.mkdir(parents=True,exist_ok=True)
W,H,FPS,DURATION=720,1280,24,42
SCENES=[
 ("WHAT IF THE SUN VANISHED?","Imagine the Sun disappearing right now."),
 ("EIGHT MINUTES","For eight minutes and twenty seconds, Earth would still receive the sunlight already traveling through space."),
 ("THE LAST LIGHT","Then the last rays would arrive, and the daylit sky would turn dark."),
 ("ORBIT ENDS","The change in the Sun's gravitational influence would also reach us after that delay. Earth would leave its former orbit."),
 ("A WORLD GROWS COLD","Temperatures would fall over time. Oceans would begin freezing from the surface, not instantly turn to ice."),
 ("LIFE BELOW?","Geothermal energy might support small underground communities, but growing enough food would be a huge challenge."),
 ("A WANDERING PLANET","Earth would travel through space as a cold wanderer. How long could humanity survive?")
]
def run(*args): subprocess.run(args,check=True)
def font(size):
 p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
 return ImageFont.truetype(p,size)
def wrap(d,s,f,maxwidth):
 lines=[];cur=""
 for word in s.split():
  test=(cur+" "+word).strip()
  if d.textbbox((0,0),test,font=f)[2]>maxwidth and cur:
   lines.append(cur);cur=word
  else:cur=test
 if cur:lines.append(cur)
 return lines
def artwork(index):
 rng=random.Random(791+index)
 im=Image.new("RGB",(W,H),(3+index*2,8,24+index*3))
 d=ImageDraw.Draw(im,"RGBA")
 for j in range(350):
  x=rng.randrange(W);y=rng.randrange(H);r=rng.choice([1,1,2])
  d.ellipse((x,y,x+r,y+r),fill=(215,225,255,rng.randint(60,210)))
 if index in (0,1,2):
  x,y=(W//2,490)
  for r in range(265,85,-14):
   d.ellipse((x-r,y-r,x+r,y+r),fill=(255,125+int(70*r/265),25,max(10,75-int(r/5))))
  d.ellipse((x-105,y-105,x+105,y+105),fill=(255,211,85,255))
 if index in (3,4,5,6):
  x,y=(W//2,515)
  d.ellipse((x-225,y-225,x+225,y+225),fill=(15,55,130,255),outline=(110,195,255,230),width=5)
  for k in range(7):
   xx=x+rng.randint(-150,150);yy=y+rng.randint(-120,120)
   d.ellipse((xx-35,yy-15,xx+40,yy+18),fill=(22,110,100,210))
  d.ellipse((x-225,y-225,x+225,y+225),outline=(130,205,255,150),width=3)
 return im
def main():
 durations=[6]*7
 narration=" ".join(t for _,t in SCENES)
 (ROOT/"script.txt").write_text(narration)
 (ROOT/"metadata.json").write_text(json.dumps({"title":"What If the Sun Vanished? | Orbit Unknown #Shorts","caption":"What happens eight minutes after the Sun disappears? #space #science #shorts","privacyStatus":"private","testOnly":True},indent=2))
 # Speech is an explicit test dependency; reject a silent render.
 run("espeak-ng","-v","en-us+m3","-s","205","-w",str(ROOT/"narration.wav"),narration)
 with wave.open(str(ROOT/"narration.wav")) as a: speech=a.getnframes()/a.getframerate()
 if speech>DURATION-1: raise RuntimeError(f"Narration too long: {speech:.1f}s")
 for i,(headline,body) in enumerate(SCENES):
  im=artwork(i);d=ImageDraw.Draw(im,"RGBA")
  d.rounded_rectangle((32,65,W-32,139),radius=16,fill=(0,0,0,175))
  d.text((55,82),"ORBIT UNKNOWN",font=font(32),fill=(255,210,115,255))
  lines=wrap(d,headline,font(48),W-90)
  for j,line in enumerate(lines):d.text((45,180+j*63),line,font=font(48),fill=(255,255,255,255))
  lines=wrap(d,body,font(31),W-100)
  yy=930
  d.rounded_rectangle((25,yy-30,W-25,min(H-60,yy+len(lines)*49+40)),radius=25,fill=(0,0,0,205))
  for j,line in enumerate(lines):d.text((50,yy+j*49),line,font=font(31),fill=(240,245,255,255))
  im.save(ROOT/f"scene_{i:02d}.png")
 # Gentle zoom on each unique scene, concatenate with ffmpeg.
 clips=[]
 for i in range(7):
  p=ROOT/f"clip_{i:02d}.mp4"
  run("ffmpeg","-y","-loglevel","error","-loop","1","-i",str(ROOT/f"scene_{i:02d}.png"),"-vf",f"zoompan=z='min(zoom+0.00025,1.07)':d={FPS*6}:s={W}x{H}:fps={FPS},format=yuv420p","-frames:v",str(FPS*6),"-an","-c:v","libx264","-preset","veryfast",str(p))
  clips.append(p)
 concat=ROOT/"concat.txt"
 concat.write_text("".join("file '"+p.name+"'\n" for p in clips))
 run("ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-i",str(ROOT/"narration.wav"),"-f","lavfi","-i","sine=frequency=85:sample_rate=44100","-filter_complex","[1:a]volume=1.0[voice];[2:a]volume=0.035,lowpass=f=200[bed];[voice][bed]amix=inputs=2:duration=longest[a]","-map","0:v","-map","[a]","-t",str(DURATION),"-c:v","copy","-c:a","aac","-pix_fmt","yuv420p","-movflags","+faststart",str(ROOT/"preview.mp4"))
 run("ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1",str(ROOT/"preview.mp4"))
 print("Staging only; not published. Audio is a basic synthetic proof, not approved final narration.")
if __name__=="__main__":main()
