"""Small reusable FreeCAD solid and annotation helpers."""
import math
import FreeCAD as App
import Part
from .catalog import COLORS
V=App.Vector

def box(x,y,z,dx,dy,dz):
    return Part.makeBox(dx,dy,dz,V(x,y,z))

def cylinder(radius,height,pos,direction=(0,0,1)):
    return Part.makeCylinder(radius,height,V(*pos),V(*direction))

def segment(a,b,r):
    a,b=V(*a),V(*b); d=b-a
    return Part.makeCylinder(r,d.Length,a,d.normalize())

def pipe(points,radius=22,dashed=False):
    pieces=[]
    for a,b in zip(points,points[1:]):
        va,vb=V(*a),V(*b); delta=vb-va; length=delta.Length
        if length<.001: continue
        if dashed:
            direction=delta.normalize()
            for n in range(int(math.ceil(length/115))):
                start=n*115; end=min(start+72,length)
                if end>start: pieces.append(Part.makeCylinder(radius,end-start,va+direction*start,direction))
        else: pieces.append(segment(a,b,radius))
    if not dashed:
        pieces.extend(Part.makeSphere(radius,V(*p)) for p in points[1:-1])
    return Part.makeCompound(pieces)

def arrow(point,direction,size=75):
    p=V(*point); d=V(*direction).normalize()
    return Part.makeCone(size*.40,0,size,p-d*size*.5,d)

def sample(points,fraction):
    pts=[V(*p) for p in points]; lens=[(b-a).Length for a,b in zip(pts,pts[1:])]
    length=sum(lens); t=max(0,min(.999999,fraction))*length
    for a,b,ll in zip(pts,pts[1:],lens):
        if t<=ll and ll>0:
            d=(b-a).normalize(); p=a+d*t
            return (p.x,p.y,p.z),(d.x,d.y,d.z)
        t-=ll
    d=(pts[-1]-pts[-2]).normalize()
    return tuple(pts[-1]),tuple(d)

def feature(doc,group,name,shape,color='body',transparency=0,role='',detail='',source=''):
    obj=doc.addObject('Part::Feature',name)
    obj.Shape=shape; group.addObject(obj)
    obj.addProperty('App::PropertyString','Service','RAS').Service=role
    obj.addProperty('App::PropertyString','Description','RAS').Description=detail
    obj.addProperty('App::PropertyString','Evidence','RAS').Evidence=source
    obj.addProperty('App::PropertyInteger','BaseTransparency','RAS').BaseTransparency=transparency
    vo=obj.ViewObject
    vo.ShapeColor=COLORS.get(color,color); vo.LineColor=(.22,.30,.33)
    vo.Transparency=transparency; vo.DisplayMode='Flat Lines'; vo.LineWidth=1.0
    return obj

def label(doc,group,name,text,position,color='label',size=12):
    obj=doc.addObject('App::Annotation',name)
    obj.LabelText=text if isinstance(text,list) else [text]
    obj.Position=V(*position); group.addObject(obj)
    vo=obj.ViewObject; vo.FontName='Helvetica'; vo.FontSize=size
    vo.TextColor=COLORS.get(color,color)
    return obj
