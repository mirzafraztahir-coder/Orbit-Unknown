"""Offline Blender 3D renderer for Orbit Unknown. One independent scene per invocation.
Run: blender -b -t 2 --python automation/render_scene_3d.py -- --query "..." --number 1 --output /tmp/scene.png
"""
import argparse, hashlib, math, random, sys
import bpy
from mathutils import Vector

argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
p=argparse.ArgumentParser()
p.add_argument("--query",required=True)
p.add_argument("--number",type=int,required=True)
p.add_argument("--output",required=True)
a=p.parse_args(argv)
seed=int(hashlib.sha256((a.query+str(a.number)).encode()).hexdigest()[:12],16)
rng=random.Random(seed)
q=a.query.lower()
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=16
scene.render.resolution_x=800
scene.render.resolution_y=1280
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.filepath=a.output
scene.render.film_transparent=False
scene.world.color=(0.003,0.006,0.017)
scene.view_settings.view_transform="Standard"

def material(name,color,metallic=0,roughness=0.6,emission=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Metallic"].default_value=metallic
    bs.inputs["Roughness"].default_value=roughness
    if emission:
        bs.inputs["Emission Color"].default_value=(*color,1)
        bs.inputs["Emission Strength"].default_value=emission
    return m

def sphere(name,loc,radius,mat,segments=64,rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=radius,location=loc)
    o=bpy.context.object
    o.name=name
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o

def ring(name,loc,major,minor,mat,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=120,minor_segments=10,location=loc,rotation=rotation,major_radius=major,minor_radius=minor)
    o=bpy.context.object
    o.name=name
    o.data.materials.append(mat)
    return o

def aim(obj,point):
    obj.rotation_euler=(Vector(point)-obj.location).to_track_quat("-Z","Y").to_euler()

def light(loc,power,color,size):
    bpy.ops.object.light_add(type="AREA",location=loc)
    l=bpy.context.object
    l.data.energy=power
    l.data.color=color
    l.data.shape="DISK"
    l.data.size=size
    aim(l,(0,0,0))

def noise_surface(mat,scale=3.0,detail=4.0):
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    tex=nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value=scale
    tex.inputs["Detail"].default_value=detail
    ramp=nodes.new("ShaderNodeValToRGB")
    base=mat.diffuse_color
    ramp.color_ramp.elements[0].color=(base[0]*0.25,base[1]*0.3,base[2]*0.35,1)
    ramp.color_ramp.elements[1].color=(min(1,base[0]*1.4),min(1,base[1]*1.4),min(1,base[2]*1.4),1)
    links.new(tex.outputs["Fac"],ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"],nodes.get("Principled BSDF").inputs["Base Color"])

palette=(0.55,0.23,0.12) if "mars" in q else (0.68,0.55,0.34) if "saturn" in q else (0.64,0.44,0.25) if "jupiter" in q else (0.12,0.32,0.76) if "neptune" in q else (0.9,0.48,0.08) if any(t in q for t in ["sun","star","supernova"]) else (0.28,0.48,0.72)
planetmat=material("Procedural planetary terrain",palette,roughness=0.87)
noise_surface(planetmat,scale=2.0+0.3*a.number)
space=material("Star light",(0.8,0.9,1),emission=8)
gold=material("Warm metallic ring",(0.72,0.54,0.28),metallic=0.8,roughness=0.3)
dark=material("Event horizon",(0.001,0.002,0.006),roughness=0.1)
icy=material("Moon ice",(0.5,0.65,0.76),roughness=0.9)
is_black_hole=any(t in q for t in ["black hole","event horizon","singularity"])
is_moon=any(t in q for t in ["moon","lunar","asteroid","comet"])
is_ring=any(t in q for t in ["saturn","ring","disk","accretion"])
is_sun=any(t in q for t in ["sun","solar","star","supernova"])
if is_black_hole:
    sphere("Dark central event horizon",(0,0,0),1.6,dark)
    for j in range(9):
        ring("Accretion flow %02d"%j,(0,0,0),2.0+j*0.17,0.045,material("Hot plasma %02d"%j,(1,0.25+j*0.045,0.025),emission=1.8),rotation=(0.28,0.2,0.25))
elif is_moon and a.number%2==0:
    sphere("Large cratered moon",(-0.7,0.2,0),1.6,icy)
    sphere("Distant planetary body",(2.5,0.6,-2),0.8,planetmat)
else:
    sphere("Three dimensional main celestial body",(0,0,0),1.8,planetmat)
    if is_ring:
        for j in range(7):
            ring("Physical orbital ring %02d"%j,(0,0,0),2.25+j*0.12,0.026,gold,rotation=(0.42,0.12,0.3))
    if a.number in (2,4):
        sphere("Foreground moon or satellite",(2.1,-1.3,0.7),0.33,icy)
    if is_sun:
        corona=material("Emissive corona",(1,0.36,0.05),emission=3)
        ring("Solar atmosphere",(0,0,0),1.94,0.05,corona,rotation=(0.2,0.4,0.1))
# Scene-specific foreground geometry: each narration beat gets a different composition.
# All elements are original procedural 3D meshes, rendered offline.
if a.number == 2:
    # Wide atmospheric horizon, with the foreground globe below the camera.
    horizon=material("Atmospheric rim",(0.08,0.32,0.75),emission=0.7)
    sphere("Curved planetary horizon",(0,-5,-7.0),7.2,planetmat)
    ring("Atmospheric scattering edge",(0,-5,-7.0),7.25,0.055,horizon,rotation=(0.15,0,0))
elif a.number == 3:
    # Physical field of orbiting fragments instead of another central planet close-up.
    debris=material("Orbiting rock",(0.38,0.32,0.29),metallic=0.15,roughness=0.88)
    for j in range(34):
        theta=2*math.pi*j/34
        radius=rng.uniform(2.7,4.7)
        sphere("Orbiting fragment %02d"%j,
               (radius*math.cos(theta),radius*math.sin(theta),rng.uniform(-1.4,1.4)),
               rng.uniform(0.04,0.16),debris,segments=10,rings=6)
elif a.number == 4:
    # Spacecraft silhouette in the foreground to give the shot scale and depth.
    hull=material("Spacecraft titanium",(0.46,0.53,0.61),metallic=0.75,roughness=0.24)
    solar=material("Solar panels",(0.025,0.08,0.22),metallic=0.35,roughness=0.22)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(-2.2,-2.6,0.3))
    craft=bpy.context.object
    craft.name="Exploration spacecraft fuselage"
    craft.scale=(0.34,0.65,0.25)
    craft.data.materials.append(hull)
    for side in (-1,1):
        bpy.ops.mesh.primitive_cube_add(size=1,location=(-2.2+side*0.95,-2.6,0.3))
        panel=bpy.context.object
        panel.name="Solar array"
        panel.scale=(1.55,0.7,0.045)
        panel.data.materials.append(solar)
elif a.number == 5:
    # Distant moons in a wide establishing composition.
    for j in range(3):
        sphere("Distant moon %02d"%j,
               (-3.3+j*2.6,2.4-j*0.5,-2.5-j),
               0.23+j*0.12,icy)
# Distant stars are actual 3D emissive objects with parallax.
for i in range(125):
    x=rng.uniform(-24,24);y=rng.uniform(-30,30);z=rng.uniform(-23,-12)
    if x*x+y*y<9: continue
    sphere("Star %03d"%i,(x,y,z),rng.uniform(0.018,0.075),space,segments=8,rings=4)
bpy.ops.object.camera_add(location=(4.4+0.8*math.sin(a.number),-8.4,3.0+0.6*math.cos(a.number)))
camera=bpy.context.object
aim(camera,(0,0,0))
camera.data.type="ORTHO"
camera.data.ortho_scale=(9.5 if a.number == 5 else 8.5 if a.number == 3 else 8.0 if is_ring else 6.6)
scene.camera=camera
light((-4,-5,7),1200,(0.78,0.87,1),6)
light((5,3,0),950,(1,0.47,0.19),5)
scene.render.image_settings.color_mode="RGB"
bpy.ops.render.render(write_still=True)
print("ORBIT_3D_RENDER_OK",a.output)
