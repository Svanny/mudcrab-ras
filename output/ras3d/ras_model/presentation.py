"""Per-document presentation. No persistent application preferences are changed."""
import FreeCAD as App
from .geometry import label
from .catalog import ROUTES

TAGS={
 'RACK_A':(['CULTURE A','Representative bank'],(-150,-140,2460)),
 'RACK_B':(['CULTURE B','Representative bank'],(1300,-140,2460)),
 'SK101':(['SK-101','Protein skimmer'],(2850,550,2540)),
 'BIO1':(['BIO-1','Biological'],(3360,2320,1700)),
 'BIO2':(['BIO-2','Aerated'],(4170,2320,1610)),
 'UV':(['UV','3 lamps'],(5000,2320,1510)),
 'F101':(['F-101','Sand filter'],(3950,-890,560)),
 'P101':(['P-101','Outlet pump'],(4700,-490,370)),
 'P102':(['P-102','Inlet pump'],(5490,940,410)),
 'A101':(['LP-100','Air pump'],(4080,1050,1710)),
 'OZ101':(['OZ-101','Ozone'],(2930,-240,590)),
 'CP101':(['CP-101','Control panel'],(5580,1150,2040)),
}

def style_document(doc):
    for key,(text,position) in TAGS.items():
        ob=doc.getObject('Tag_'+key)
        ob.LabelText=text;ob.Position=App.Vector(*position)
        ob.ViewObject.FontSize=20;ob.ViewObject.TextColor=(.10,.17,.22)
    for route in ROUTES:
        if route['label']:
            text,position=route['label']
            ob=doc.getObject('Text_'+route['key'])
            ob.Position=App.Vector(*position);ob.LabelText=[text]
    for ob in doc.Objects:
        if ob.Name.startswith('Text_'):ob.ViewObject.FontSize=18
        if hasattr(ob,'BaseTransparency') and ob.Name not in ('Skid',):
            ob.ViewObject.DisplayMode='Flat Lines'
    # Clearly mark conceptual scale in the document, with a short persistent header.
    if not doc.getObject('AtlasTitle'):
        label(doc,doc.EquipmentLabels,'AtlasTitle',['MUDCRAB  /  RAS','LFS-10M  ·  Process schematic'],(0,1200,3300),size=28)
        label(doc,doc.EquipmentLabels,'AtlasMode','01 / NORMAL WATER',(0,1200,3040),color='water',size=23)
        label(doc,doc.EquipmentLabels,'AtlasNote',['Representative geometry · routes not to scale'],(100,-950,-80),size=18)

    if not doc.getObject('AtlasMode'):
        label(doc,doc.EquipmentLabels,'AtlasMode','01 / NORMAL WATER',(0,1200,3040),color='water',size=23)

def configure_view(view):
    view.getViewer().setBackgroundColor(.94,.96,.975)

def frame(view,rotation,bounds):
    # Write camera fields directly: animated native view commands can otherwise
    # finish later and override a newly selected camera preset.
    view.getCameraNode().orientation=rotation.Q
    xs,ys,zs=bounds
    points=[App.Vector(x,y,z) for x in xs for y in ys for z in zs]
    projected=[rotation.inverted().multVec(p) for p in points]
    lo=[min(getattr(p,k) for p in projected) for k in ('x','y','z')]
    hi=[max(getattr(p,k) for p in projected) for k in ('x','y','z')]
    center=App.Vector((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,(lo[2]+hi[2])/2)
    width,height=view.getSize();aspect=max(1.0,width/max(1,height))
    camera=view.getCameraNode()
    camera.position=tuple(rotation.multVec(center+App.Vector(0,0,15000)))
    camera.height=max(hi[1]-lo[1],(hi[0]-lo[0])/aspect)*1.06
    camera.nearDistance=1;camera.farDistance=50000;camera.focalDistance=15000
    view.redraw()

BOUNDS=((-350,6400),(-1150,2400),(-120,3400))
def overview(view):
    rotation=App.Rotation(App.Vector(0,0,1),20).multiply(App.Rotation(App.Vector(1,0,0),60))
    frame(view,rotation,BOUNDS)

def top(view):frame(view,App.Rotation(),BOUNDS)
def front(view):frame(view,App.Rotation(App.Vector(1,0,0),90),BOUNDS)
def skid(view):
    rotation=App.Rotation(App.Vector(0,0,1),25).multiply(App.Rotation(App.Vector(1,0,0),55))
    frame(view,rotation,((2750,6000),(-1000,2400),(-120,2900)))
