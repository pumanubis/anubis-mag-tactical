# Blender 4.3: blender -b -P tools/build_tactical_props.py -- <directorio-de-salida>
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

def mark_screws(coords,y,r=.006):
    for x,z in coords:
        cyl('Tornillo',(x,y,z),r,.003,steel,(pi/2,0,0),12)
        box('Ranura',(x,y-.002,z),(r*1.25,.0016,.0016),edge,.0003)

def radio():
    box('Carcasa', (0,0,.185),(.205,.124,.348),olive_dark,.025, None,5)
    box('Parte trasera',(0,.050,.181),(.176,.045,.247),edge,.015)
    box('Zócalo de goma',(0,0,.026),(.196,.124,.052),rubber,.016)
    box('Panel frontal',(0,-.062,.186),(.175,.022,.271),edge,.017)
    for x in [-.092,.092]:
        box('Protector lateral',(x,-.013,.181),(.028,.11,.25),rubber,.009)
        for z in [.125,.151,.177,.203,.229]:box('Textura lateral',(x,-.053,z),(.029,.013,.008),edge,.003)
    box('Marco de pantalla',(0,-.076,.267),(.134,.012,.058),rubber,.009)
    box('Pantalla',(0,-.083,.267),(.115,.004,.041),lcd,.004)
    txt('Canal','CH  07',(0,-.086,.267),.019,ink)
    txt('Etiqueta','ANUBIS   /   COMMS',(0,-.075,.317),.009,light)
    for i in range(5):box('Abertura de altavoz',(0,-.076,.211-i*.009),(.111-i*.007,.005,.0048),rubber,.002)
    for row in range(3):
        for col in range(3):
            x=(col-1)*.037;z=.149-row*.027
            box('Tecla',(x,-.077,z),(.028,.012,.018),rubber,.005)
            txt('Número',str(row*3+col+1),(x,-.084,z),.009,light)
    for x,m in [(-.032,orange),(.032,green)]:
        box('Selector',(x,-.076,.065),(.035,.011,.012),m,.004)
    mark_screws([(-.073,.288),(.073,.288),(-.073,.078),(.073,.078)],-.075,.005)
    cyl('Anclaje de antena',(-.066,.018,.359),.021,.025,steel)
    cyl('Base de antena',(-.066,.018,.382),.017,.045,rubber)
    path('Antena flexible',[(-.066,.018,.385),(-.066,.019,.444),(-.073,.019,.546),(-.080,.020,.601)],.0068,rubber,True)
    ball('Punta',(-.08,.020,.601),(.016,.016,.017),rubber)
    for x,r in [(.035,.018),(.075,.012)]:
        cyl('Mando de ajuste',(x,.015,.367),r,.038,rubber)
        for i in range(10):
            a=i*2*pi/10;cyl('Estría',(x+cos(a)*r,.015+sin(a)*r,.37),.0021,.026,edge,v=8)
    box('Pulsador lateral',(-.107,.015,.255),(.015,.041,.035),edge,.006)

def backpack():
    box('Cuerpo de lona',(0,.012,.254),(.329,.223,.501),cloth,.085,None,8)
    box('Base reforzada',(0,.011,.041),(.316,.212,.086),webbing,.036,None,5)
    box('Bolsillo exterior principal',(0,-.112,.219),(.25,.115,.244),cloth2,.045,None,6)
    box('Bolsillo superior',(0,-.103,.382),(.245,.097,.116),cloth,.034,None,6)
    path('Cremallera perimetral',[(-.132,-.078,.072),(-.151,-.083,.18),(-.15,-.077,.36),(-.098,-.071,.465),(0,-.079,.483),(.098,-.071,.465),(.15,-.077,.36),(.15,-.083,.15),(.132,-.078,.083)],.0043,webbing,True)
    path('Cremallera frontal',[(-.109,-.166,.28),(-.06,-.175,.295),(.057,-.175,.296),(.112,-.166,.278)],.0045,webbing,True)
    for i in range(37):
        x=-.099+i*.0055
        box('Diente de cremallera',(x,-.177,.294-abs(x)*.09),(.0022,.0024,.004),stitch,.00045,segs=1)
    box('Corredera',(.081,-.178,.292),(.023,.008,.010),steel,.003)
    path('Tirador',[(.09,-.18,.293),(.107,-.185,.287),(.113,-.187,.263)],.003,webbing)
    for z in [.153,.181,.211]:
        box('Cincha horizontal',(0,-.172,z),(.215,.011,.017),webbing,.004)
        for x in [-.091,-.06,-.03,0,.03,.06,.091]:
            box('Remate de costura',(x,-.179,z),(.002,.002,.015),stitch,.00055,segs=1)
    for x in [-.10,.10]:
        box('Cincha vertical',(x,-.117,.416),(.024,.012,.108),webbing,.004, (0,0,0))
        box('Hebilla',(x,-.132,.377),(.033,.016,.028),rubber,.005)
        box('Pestaña',(x,-.142,.376),(.016,.008,.011),edge,.003)
    box('Parche de identificación',(0,-.154,.391),(.09,.009,.039),patch,.005)
    txt('Identificación','ANUBIS',(0,-.16,.393),.013,ink)
    for sign in [-1,1]:
        for z in [.113,.205]:
            box('Cincha lateral',(sign*.157,.006,z),(.017,.15,.022),webbing,.005)
            box('Pasador lateral',(sign*.168,-.028,z),(.020,.032,.033),rubber,.005)
        for a,b,w in [
            ((sign*.076,.095,.446),(sign*.089,.157,.394),.062),
            ((sign*.089,.157,.394),(sign*.111,.187,.29),.060),
            ((sign*.111,.187,.29),(sign*.109,.169,.18),.058),
            ((sign*.109,.169,.18),(sign*.117,.111,.065),.034)]:
            bar('Tirante acolchado',a,b,w,.025,webbing,.010)
    path('Asa superior',[(-.058,.038,.472),(-.047,.046,.517),(0,.049,.535),(.047,.046,.517),(.058,.038,.472)],.011,webbing,True)

def can():
    box('Cuerpo de acero estampado',(0,0,.203),(.313,.147,.407),olive,.039,None,6)
    box('Faja soldada',(0,0,.203),(.317,.044,.412),lip,.036,None,5)
    for sign in [-1,1]:
        y=.071*sign
        box('Relieve de panel',(0,y,.200),(.264,.022,.313),olive,.034,None,5)
        p=[(-.106,y*1.16,.317),(-.045,y*1.20,.243),(.045,y*1.20,.153),(.104,y*1.16,.081)]
        q=[(-.104,y*1.16,.081),(-.045,y*1.20,.153),(.045,y*1.20,.243),(.106,y*1.16,.317)]
        path('Nervadura estampada',p,.0096,lip,True)
        path('Nervadura estampada',q,.0096,lip,True)
        box('Placa repujada',(0,y*1.21,.201),(.075,.021,.062),olive,.014,None,4)
    for y in [-.045,0,.045]:
        path('Asa triple',[(-.119,y,.366),(-.121,y,.420),(-.089,y,.453),(.025,y,.453),(.054,y,.427),(.055,y,.368)],.013,olive,True)
    sp=(-pi/24,.43,0)
    cyl('Cuello de vertido',(.104,-.004,.399),.035,.039,lip,sp)
    cyl('Tapón articulado',(.111,-.006,.425),.036,.019,steel,sp)
    box('Cierre rápido',(.116,-.040,.424),(.049,.019,.014),edge,.003,(0,.43,0))
    cyl('Pasador',(.114,-.047,.417),.0056,.039,steel,(0,pi/2,0),12)
    box('Placa de inventario',(.074,-.085,.123),(.081,.004,.024),lip,.004)
    txt('Inventario','ANUBIS',(.074,-.088,.124),.013,light)
    for i in range(18):
        x=rng.uniform(-.132,.132);z=rng.uniform(.035,.348)
        box('Desgaste de pintura',(x,-.082,z),(rng.uniform(.003,.011),.0013,.0014),steel,.0003,(0,rng.uniform(-1,1),0),1)

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

groups=[]
for fun,fn in [(radio,'radio-realista.glb'),(backpack,'mochila-realista.glb'),(can,'bidon-realista.glb')]:
    prior=set(bpy.context.scene.objects);fun();objs=[o for o in bpy.context.scene.objects if o not in prior]
    objs=combine(objs);export(fn,objs);groups.append(objs)

for group,shift in zip(groups,[-.49,0,.50]):
    for o in group:o.location.x+=shift
ground=mat('Fondo de estudio',(.155,.177,.151),.93)
box('Suelo',(0,0,-.032),(200,200,.06),ground,0)
def point(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def light_area(n,xyz,power,size):
    bpy.ops.object.light_add(type='AREA',location=xyz)
    o=bpy.context.object;o.name=n;o.data.energy=power;o.data.shape='DISK';o.data.size=size;point(o,(0,0,.24))
light_area('Luz principal',(-1.4,-2,2.2),265,1.8)
light_area('Relleno',(1.5,-.7,1.3),95,1.35)
light_area('Contorno',(0,1.4,1.5),180,1)
bpy.ops.object.camera_add(location=(.19,-2.50,1.18))
cam=bpy.context.object;point(cam,(0,0,.27));cam.data.type='ORTHO';cam.data.ortho_scale=1.63
s=bpy.context.scene;s.camera=cam;s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=False
s.world=bpy.data.worlds.new('Ambiente');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[1].default_value=.26
s.render.resolution_x=1050;s.render.resolution_y=650;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.filepath=os.path.join(OUT,'preview-lineup.png')
bpy.ops.render.render(write_still=True)
