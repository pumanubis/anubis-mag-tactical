# Blender 4.3: blender -b -P tools/build_metal_crate.py -- <directorio-de-salida>
import bpy, math, random, os, sys
from mathutils import Vector
from math import sin, cos, pi

OUT=os.path.abspath(sys.argv[sys.argv.index('--')+1])
os.makedirs(OUT,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
rng=random.Random(782)

def mat(name,c,r=.58,metal=0,pattern=None):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Roughness'].default_value=r;p.inputs['Metallic'].default_value=metal
    if pattern:
        im=bpy.data.images.new(name+'_albedo',width=128,height=128,alpha=False)
        pix=[]
        for y in range(128):
            for x in range(128):
                grain=rng.uniform(-.045,.045)
                if pattern=='fabric':
                    k=1+grain+.047*cos(x*pi/2)+.04*cos(y*pi/2)+.075*sin(x*.11)*cos(y*.15)
                else:
                    k=1+grain+.10*sin(x*.13)*sin(y*.10)+.07*cos(x*.28+y*.10)
                    if (x+4*y)%109==0 and (x+2*y)%42<12:k+=.33
                pix.extend([min(1,max(0,a*k)) for a in c]+[1])
        im.pixels.foreach_set(pix);im.pack()
        n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im
        m.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
    return m

rubber=mat('Goma negra',(.038,.045,.039),.87)
edge=mat('Polímero carbón',(.075,.085,.077),.59)
steel=mat('Acero oscurecido',(.33,.35,.32),.34,.75)
olive=mat('Pintura oliva envejecida',(.29,.34,.19),.59,.22,'paint')
olive_dark=mat('Carcasa verde oliva',(.19,.24,.145),.69,.03,'paint')
lip=mat('Soldadura y bordes',(.225,.27,.14),.54,.36)
light=mat('Rotulación marfil',(.8,.81,.64),.66)
lcd=mat('Pantalla verde polarizada',(.28,.37,.22),.32,.08)
ink=mat('Tinta de pantalla',(.075,.12,.063),.63)
green=mat('Piloto verde',(.36,.65,.22),.34)
orange=mat('Botón ámbar',(.74,.32,.14),.5)
cloth=mat('Lona oliva tramada',(.295,.329,.181),.95,0,'fabric')
cloth2=mat('Lona de bolsillos',(.365,.383,.234),.96,0,'fabric')
webbing=mat('Cincha verde oscuro',(.162,.193,.11),.95,0,'fabric')
stitch=mat('Hilo caqui',(.56,.54,.34),.85)
patch=mat('Parche arena',(.58,.51,.32),.9,0,'fabric')

def assign(o,n,m):
    o.name=n
    o.data.materials.append(m)
    return o

def box(n,xyz,sz,m,r=.009,rot=None,segs=3):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
    o=assign(bpy.context.object,n,m);o.dimensions=sz
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rot:o.rotation_euler=rot
    if r:
        b=o.modifiers.new('Cantos redondeados','BEVEL');b.width=r;b.segments=segs
        w=o.modifiers.new('Normales ponderadas','WEIGHTED_NORMAL');w.keep_sharp=True
    return o

def cyl(n,xyz,r,d,m,rot=None,v=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=xyz)
    o=assign(bpy.context.object,n,m)
    if rot:o.rotation_euler=rot
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return o

def ball(n,xyz,dims,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,location=xyz)
    o=assign(bpy.context.object,n,m);o.dimensions=dims
    for p in o.data.polygons:p.use_smooth=True
    return o

def bar(n,a,b,w,d,m,r=.005):
    a,b=Vector(a),Vector(b); delta=b-a
    o=box(n,(a+b)/2,(w,d,delta.length),m,r)
    o.rotation_mode='QUATERNION';o.rotation_quaternion=delta.to_track_quat('Z','Y')
    return o

def path(n,pts,r,m,smooth=False):
    c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.resolution_u=8;c.bevel_depth=r;c.bevel_resolution=2
    if smooth:
        s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
        for p,xyz in zip(s.bezier_points,pts):
            p.co=xyz;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    else:
        s=c.splines.new('POLY');s.points.add(len(pts)-1)
        for p,xyz in zip(s.points,pts):p.co=(*xyz,1)
    o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o)
    return assign(o,n,m)

def txt(n,value,xyz,size,m):
    f=bpy.data.curves.new(n,'FONT');f.body=value;f.size=size;f.align_x='CENTER';f.align_y='CENTER'
    o=bpy.data.objects.new(n,f);bpy.context.collection.objects.link(o);o.location=xyz;o.rotation_euler=(pi/2,0,0)
    return assign(o,n,m)

def select_only(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)

def combine(objs):
    select_only(objs)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.object.convert(target='MESH')
    by_mat={}
    for o in bpy.context.selected_objects:
        by_mat.setdefault(o.data.materials[0].name,[]).append(o)
    out=[]
    for name,group in by_mat.items():
        select_only(group)
        bpy.context.view_layer.objects.active=group[0]
        if len(group)>1:bpy.ops.object.join()
        o=bpy.context.view_layer.objects.active;o.name=name;out.append(o)
    return out

def export(fn,objs):
    select_only(objs)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,fn),export_format='GLB',use_selection=True,export_apply=True,export_normals=True,export_cameras=False,export_lights=False)


# Paint, sheet steel, seal, and hardware are different PBR materials.
enamel=mat('Acero pintado verde oliva',(.225,.244,.191),.53,.28,'paint')
edgepaint=mat('Acero oliva en cantos',(.174,.192,.149),.54,.32,'paint')
latchpaint=mat('Cierre de acero pintado',(.190,.210,.169),.48,.40,'paint')
worn=mat('Acero expuesto',(.39,.405,.37),.33,.80)
blacksteel=mat('Acero ennegrecido',(.045,.056,.049),.38,.69)
underside=mat('Sello de goma',(.036,.042,.036),.85)
white=mat('Estrella blanca estarcida',(.84,.84,.78),.66,.05)

# Tall folded metal shell, rolled overlapping lid and a narrow black seal.
box('Cuerpo de chapa plegada',(0,0,.117),(.362,.192,.226),enamel,.010,None,5)
box('Costura inferior', (0,0,.013),(.362,.192,.014),edgepaint,.006)
box('Junta negra bajo tapa',(0,0,.220),(.366,.196,.011),underside,.005)
box('Borde enrollado de tapa',(0,0,.233),(.387,.207,.024),edgepaint,.006,None,5)
box('Tapa de lámina',(0,0,.247),(.383,.203,.012),enamel,.007,None,5)
box('Estampado de tapa',(0,0,.252),(.332,.157,.006),enamel,.004,None,4)
for x in [-.107,.107]:
    box('Base rebajada del asa',(x,0,.256),(.038,.044,.008),edgepaint,.004)
    cyl('Pasador del asa',(x,0,.260),.006,.025,blacksteel,(pi/2,0,0),16)
# Flat raised wire bail: a static depiction of the folding handle.
path('Asa abatible de acero',[(-.109,0,.261),(-.087,0,.299),(-.080,0,.304),(.080,0,.304),(.087,0,.299),(.109,0,.261)],.0037,blacksteel)
box('Zona de agarre',(0,0,.304),(.096,.009,.009),blacksteel,.003)
for x in [-.108,.108]:
    for y in [-.013,.013]:cyl('Remache de asa',(x,y,.261),.003,.0016,worn,None,12)

# Side clasp and bracket, facing right in the reference.
box('Placa del cierre',(.183,0,.164),(.010,.124,.115),latchpaint,.009,None,4)
box('Leva abatible',(.192,0,.151),(.009,.105,.080),latchpaint,.005,None,4)
box('Retén bajo tapa',(.188,0,.221),(.013,.113,.014),blacksteel,.004)
cyl('Eje superior del cierre',(.195,0,.202),.007,.127,blacksteel,(pi/2,0,0),16)
for y in [-.056,.056]:
    cyl('Remache del cierre',(.192,y,.186),.004,.004,worn,(0,pi/2,0),12)
path('Uña de la palanca',[(.198,-.043,.140),(.202,-.048,.111),(.200,-.038,.094),(.200,.038,.094),(.202,.048,.111),(.198,.043,.140)],.0035,blacksteel)
cyl('Agujero ciego de la leva',(.1975,.015,.151),.0054,.0012,underside,(0,pi/2,0),16)
# Rear rolled hinges.
for x in [-.115,.115]:
    box('Bisagra trasera',(x,.098,.213),(.045,.009,.038),latchpaint,.005)
    cyl('Eje de bisagra',(x,.103,.226),.0065,.049,blacksteel,(0,pi/2,0),16)
    for xx in [x-.013,x+.013]:cyl('Remache trasero',(xx,.103,.204),.003,.0025,worn,(pi/2,0,0),12)

# Front stencil baked into an opaque PBR texture on the visible shell surface.
c=(.225,.244,.191)
def uv_layer(o):
    u=o.data.uv_layers.new(name='UV pintura')
    for p in o.data.polygons:
        for i in p.loop_indices:
            xyz=o.data.vertices[o.data.loops[i].vertex_index].co
            u.data[i].uv=((xyz.x+.164)/.328,(xyz.z-.021)/.184)
pts=[(-.164,-.09615,.021),(.164,-.09615,.021),(.164,-.09615,.205),(-.164,-.09615,.205)]
me=bpy.data.meshes.new('Superficie de chapa');me.from_pydata(pts,[],[(0,1,2,3)]);me.update()
o=bpy.data.objects.new('Estrella pintada en la chapa',me);bpy.context.collection.objects.link(o);uv_layer(o)
stencil=mat('Oliva con estrella blanca desgastada',c,.54,.25)
resx,resy=512,288
im=bpy.data.images.new('Estrella pintada · albedo',width=resx,height=resy,alpha=False)
from array import array
data=array('f')
verts=[(cos(pi/2+j*pi/5)*(.068 if j%2==0 else .029),sin(pi/2+j*pi/5)*(.068 if j%2==0 else .029)) for j in range(10)]
rng=random.Random(810)
chips=[(rng.uniform(-.070,.070),rng.uniform(-.070,.070),rng.uniform(.0005,.0027),rng.uniform(.0003,.0016)) for _ in range(530)]
buckets={}
for xx,zz,w,d in chips:
    for gx in range(math.floor((xx-w)/.004),math.floor((xx+w)/.004)+1):
        for gz in range(math.floor((zz-d)/.004),math.floor((zz+d)/.004)+1):
            buckets.setdefault((gx,gz),[]).append((xx,zz,w,d))
def in_star(x,z):
    inside=False
    for j,(a,b) in enumerate(verts):
        c1,d=verts[j-1]
        if (b>z)!=(d>z) and x<(c1-a)*(z-b)/(d-b)+a:inside=not inside
    return inside
for yi in range(resy):
    for xi in range(resx):
        x=(xi/(resx-1)-.5)*.328;z=(yi/(resy-1)-.48)*.184
        r=math.hypot(x,z)
        angle=(math.atan2(z,x)-pi/2)%(2*pi/5)
        border=.0 if not (.053<r<.064 and .085<angle<(2*pi/5)-.085) else 1.0
        painted=border or (r<.069 and in_star(x,z))
        noise=1+rng.uniform(-.028,.028)+.043*sin(x*109)*cos(z*118)+.025*cos(x*265+z*262)
        if painted and not any(((x-xx)/w)**2+((z-zz)/d)**2<1 for xx,zz,w,d in buckets.get((math.floor(x/.004),math.floor(z/.004)),[])):
            color=(.84,.84,.78)
        else:color=c
        data.extend([min(1,a*noise) for a in color]+[1])
im.pixels.foreach_set(data);im.pack()
tex=stencil.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im
stencil.node_tree.links.new(tex.outputs['Color'],stencil.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
assign(o,'Estrella blanca pintada',stencil)
for i in range(23):
    x=rng.uniform(-.166,.165);z=rng.choice([rng.uniform(.009,.019),rng.uniform(.207,.216)])
    box('Pequeño desgaste de canto',(x,-.0962,z),(rng.uniform(.002,.009),.0007,rng.uniform(.0005,.0013)),worn,0,(0,rng.uniform(-.35,.35),0))
objects=combine(list(bpy.context.scene.objects))
export('caja-municiones-metalica.glb',objects)

# Studio render for visual QA only.
ground=mat('Superficie neutra',(.27,.294,.264),.88)
box('Suelo',(0,0,-.017),(50,50,.028),ground,0)
def point(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for n,loc,energy,size in [
    ('Luz principal',(-.8,-1.0,1.2),100,1.1),('Contraluz',(.55,.62,.91),75,.61),('Relleno',(.83,-.49,.57),30,.7)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object;o.name=n;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;point(o,(0,0,.13))
bpy.ops.object.camera_add(location=(.58,-1.16,.67))
cam=bpy.context.object;point(cam,(0,0,.15));cam.data.type='ORTHO';cam.data.ortho_scale=.55
s=bpy.context.scene;s.camera=cam;s.render.engine='CYCLES';s.cycles.samples=45;s.cycles.use_denoising=False
s.world=bpy.data.worlds.new('Ambiente');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[1].default_value=.20
s.render.resolution_x=800;s.render.resolution_y=700;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.filepath=os.path.join(OUT,'preview-caja.png')
bpy.ops.render.render(write_still=True)
