"""Create the editable native FreeCAD document and four independent layers."""
from pathlib import Path
import json
import FreeCAD as App
import FreeCADGui as Gui
import Part
from .catalog import ROUTES,COLORS
from .geometry import feature,label,pipe,arrow,sample,box,V
from .equipment import build as equipment_build

DOC_NAME='Mudcrab_RAS_Flows'
FILE_NAME='Mudcrab_RAS_Flows.FCStd'

def build(root):
    root=Path(root)
    doc=App.newDocument(DOC_NAME)
    doc.Label='MUDCRAB / RAS flow atlas'
    info=doc.addObject('App::FeaturePython','SchematicBasis')
    info.Label='00 · READ ME / evidence & scope'
    for name,value in {
      'Basis':'Revision 2 process audit, equipment manual and reference photographs; 25 Sep 2026.',
      'Geometry':'Skid nominal 2000 × 1210 × 2200 mm. Other sizes, levels and all routes are schematic. Rack boxes are representative.',
      'Flow':'Arrow speed is illustrative, not hydraulic, electrical or gas simulation. Waste services are not simultaneous operating instructions.',
      'Sources':'M = 10m3 Integrated system User Manual.pdf; E = mudcrab_realife_evidences.pdf; revision 2 sheets W01–W04/G01/E01–E02.',
      'OpenHolds':'H01–H12 retained in evidence/open_evidence_holds.csv. No complete drain outfall, actual wiring, gas treatment or automatic interlocks invented.',
      'Animation':'Run Launch_RAS.FCMacro beside this file to open the flow explorer. Static layers and direction arrows work without the macro.',
      'Version':'1.0'
    }.items(): info.addProperty('App::PropertyString',name,'Read me'); setattr(info,name,value)
    equipment=doc.addObject('App::DocumentObjectGroup','Equipment'); equipment.Label='01 · Equipment / simplified reconstruction'
    labels=doc.addObject('App::DocumentObjectGroup','EquipmentLabels'); labels.Label='02 · Equipment labels'
    equipment_build(doc,equipment,labels)
    # Slim individual plinths visually group the two banks without inventing a building.
    for x in (60,1350):
        feature(doc,equipment,'RackPlinth',box(x,530,0,980,700,60),(.84,.88,.89),0,'BASE')
    group_index={}
    for i,(key,title) in enumerate([('water','WATER / normal recirculation'),('waste','WASTE / service interfaces'),('electrical','ELECTRICAL / functional supply'),('air','AIR / aeration + separate ozone')],3):
        group=doc.addObject('App::DocumentObjectGroup','Flow_'+key)
        group.Label=f'{i:02d} · {title}'; group_index[key]=group
    for r in ROUTES:
        g=group_index[r['layer']]; radius=19 if r['layer']=='water' else 15
        if r['layer']=='electrical': radius=12
        ob=feature(doc,g,r['key'],pipe(r['points'],radius,r['dashed']),r['color'],0,r['layer'],r['detail'],r['source'])
        ob.Label=r['title']; ob.ViewObject.DisplayMode='Flat Lines'
        for name,value in [('RouteKey',r['key']),('RouteData',json.dumps(r['points'])),('Layer',r['layer'])]:
            ob.addProperty('App::PropertyString',name,'Flow');setattr(ob,name,value)
        # Persist static direction arrows for native .FCStd viewing.
        pt,di=sample(r['points'],.52)
        ar=feature(doc,g,'Arrow_'+r['key'],arrow(pt,di,85),r['color'],0,r['layer'],r['detail'],r['source'])
        ar.ViewObject.DisplayMode='Flat Lines'
        if r['label']:
            txt,pos=r['label']; label(doc,g,'Text_'+r['key'],txt,pos,r['color'],10)
        if r['layer']=='waste' or r['key']=='A03':
            pt=V(*r['points'][-1])
            marker=Part.makeTorus(42,5,pt)
            feature(doc,g,'Boundary_'+r['key'],marker,r['color'],0,r['layer'],'Open interface; destination unverified.',r['source'])
    doc.recompute()
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    doc.recompute()
    doc.saveAs(str(root/FILE_NAME))
    return doc

def load_or_build(root):
    root=Path(root)
    for doc in App.listDocuments().values():
        if doc.Name==DOC_NAME or (doc.FileName and Path(doc.FileName)==root/FILE_NAME):
            App.setActiveDocument(doc.Name);return doc
    if (root/FILE_NAME).exists(): return App.openDocument(str(root/FILE_NAME))
    return build(root)
