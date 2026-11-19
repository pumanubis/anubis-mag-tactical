# Fictional, decorative exterior game prop. No internals or moving parts.
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

shell=mat('Pintura oliva gastada',(.195,.235,.122),.54,.27,'paint')
band=mat('Aros de acero satinado',(.39,.43,.44),.40,.70,'paint')
dark=mat('Soporte grafito',(.075,.094,.087),.57,.42)
rim=mat('Ribete verde oscuro',(.106,.139,.081),.65,.28)
bolt=mat('Metal pulido',(.34,.365,.37),.34,.77)
yellow=mat('Amarillo de identificación',(.90,.55,.052),.57)
ink=mat('Tinta negra',(.033,.041,.028),.80)
offwhite=mat('Marfil impreso',(.71,.75,.63),.76)
z0=.155
profile=[(-.31,.057),(-.302,.085),(-.285,.106),(-.256,.115),(-.21,.118),(-.13,.119),(-.02,.119),(.09,.117),(.145,.110),(.19,.098),(.23,.080),(.26,.060),(.28,.043),(.297,.023),(.300,.010)]
sides=64
verts=[(x,r*cos(2*pi*i/sides),z0+r*sin(2*pi*i/sides)) for x,r in profile for i in range(sides)]
faces=[tuple(reversed(range(sides)))]
for j in range(len(profile)-1):
    for i in range(sides):
        a=j*sides+i;b=j*sides+(i+1)%sides
        faces.append((a,b,b+sides,a+sides))
faces.append(tuple(range((len(profile)-1)*sides,len(profile)*sides)))
mesh=bpy.data.meshes.new('Superficie exterior');mesh.from_pydata(verts,[],faces);mesh.update()
body=bpy.data.objects.new('Cápsula decorativa',mesh);bpy.context.collection.objects.link(body);assign(body,'Cápsula decorativa',shell)
uv=mesh.uv_layers.new(name='Pintura')
for poly in mesh.polygons:
    if len(poly.vertices)==4:poly.use_smooth=True
    ii=[mesh.loops[i].vertex_index%sides for i in poly.loop_indices]
    seam=0 in ii and sides-1 in ii and len(poly.vertices)==4
    for l,i in zip(poly.loop_indices,ii):
        v=mesh.loops[l].vertex_index
        uv.data[l].uv=((profile[v//sides][0]+.31)/.61,1 if seam and i==0 else i/sides)
# Metal bands and display cradle are game art only.
for x,rad in [(-.186,.125),(.076,.124)]:
    for xo,r,d,m in [(0,rad,.040,band),(-.017,rad+.003,.005,bolt),(.017,rad+.003,.005,bolt)]:
        bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=8,location=(x+xo,0,z0),rotation=(0,pi/2,0),major_radius=r-.004,minor_radius=.004)
        o=assign(bpy.context.object,'Borde de aro',m)
        if xo==0:
            bpy.data.objects.remove(o,do_unlink=True)
            cyl('Aro de acero',(x,0,z0),rad-.003,d,m,(0,pi/2,0),64)
    for yy in [-.115,.115]:
        box('Hebilla de aro',(x,yy,.12),(.047,.025,.032),band,.004)
        for xx in [x-.012,x+.012]:
            cyl('Remache exterior',(xx,yy*1.12,.13),.0035,.003,bolt,(pi/2,0,0),10)
    box('Apoyo lateral',(x,0,.026),(.077,.217,.039),dark,.008)
    for yy in [-.074,.074]:
        bar('Soporte exterior',(x,yy,.03),(x,yy*.72,.062),.052,.030,band,.005)
for yy in [-.086,.086]:
    box('Patín de exhibición',(-.052,yy,.015),(.365,.036,.030),dark,.008)
for x in [-.261,-.026,.139]:
    for angle in [15,78,143,210,260,306]:
        a=angle*pi/180
        rr=.117 if x<.1 else .110
        o=ball('Remache de carcasa',(x,rr*cos(a),z0+rr*sin(a)),(.006,.006,.006),rim)
# Fictional visual identifier. It deliberately uses a diamond, not real hazard markings.
box('Distintivo amarillo',(.164,-.107,.157),(.046,.005,.046),yellow,.005,(0,pi/4,0))
txt('Icono','!',(.164,-.111,.158),.035,ink)
box('Placa de juego',(-.061,-.12,.167),(.106,.004,.031),rim,.004)
txt('Rotulado','ANUBIS',(-.061,-.123,.172),.016,offwhite)
txt('Subtítulo','OBJETO VIRTUAL',(-.061,-.123,.158),.0075,offwhite)
objs=combine(list(bpy.context.scene.objects))
export('artefacto-virtual.glb',objs)
def point(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
ground=mat('Estudio',(.19,.22,.18),.9)
box('Suelo',(0,0,-.019),(50,50,.031),ground,0)
for n,loc,power,size in [('Principal',(-.8,-1.1,1.2),115,1.05),('Contorno',(.7,.5,1),95,.75),('Relleno',(.6,-.75,.6),32,.72)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object;o.name=n;o.data.energy=power;o.data.shape='DISK';o.data.size=size;point(o,(0,0,.14))
bpy.ops.object.camera_add(location=(.6,-1.3,.64))
cam=bpy.context.object;point(cam,(0,0,.13));cam.data.type='ORTHO';cam.data.ortho_scale=.77
s=bpy.context.scene;s.camera=cam;s.render.engine='CYCLES';s.cycles.samples=35;s.cycles.use_denoising=False
s.world=bpy.data.worlds.new('Ambiente');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[1].default_value=.22
s.render.resolution_x=860;s.render.resolution_y=560;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.render.filepath=os.path.join(OUT,'preview.png');bpy.ops.render.render(write_still=True)
