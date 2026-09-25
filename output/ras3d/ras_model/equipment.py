"""Recognizable, simplified equipment based on manual plan and E10 photograph."""
import Part
from .geometry import box,cylinder,pipe,feature,label,V
from .catalog import EQUIPMENT

def build(doc,group,labels):
    def add(key,shape,color='body',transparency=0,suffix=''):
        title,detail,source,position=EQUIPMENT[key]
        ob=feature(doc,group,key+suffix,shape,color,transparency,key,detail,source)
        ob.Label=title if not suffix else title+' / '+suffix
        return ob
    # Nominal skid footprint is the only source-supported dimensioned envelope.
    feature(doc,group,'Skid',box(3100,450,0,2000,1210,100),'body',0,'SKID',
            'Nominal skid footprint 2000 × 1210 mm; source overall height 2200 mm. Equipment solids simplified.', 'M3')
    for x in (3190,4950):
        feature(doc,group,'SkidFoot',box(x,520,-75,90,1000,75),'frame')
    for key,x in [('RACK_A',100),('RACK_B',1390)]:
        frame=[]; trays=[]; grilles=[]
        for xx in (x,x+860):
            for yy in (570,1150): frame.append(box(xx,yy,70,38,38,1550))
        for tier in range(4):
            z=180+tier*350
            frame.append(box(x,570,z-30,900,630,30))
            for col in range(3):
                xx=x+25+col*286
                outer=box(xx,600,z,263,565,270)
                inner=box(xx+13,613,z+18,237,539,280)
                trays.append(outer.cut(inner))
                # Raised edge and vent slits make each culture box legible.
                for offset in (60,105,150,195):
                    grilles.append(box(xx+offset,593,z+100,40,9,12))
        add(key,Part.makeCompound(trays),'rack',28)
        add(key,Part.makeCompound(frame),'frame',0,'Frame')
        add(key,Part.makeCompound(grilles),'dark',0,'Vents')
    # Biological/UV basin with three open compartments.
    for key,x,width in [('BIO1',3115,655),('BIO2',3780,640),('UV',4430,655)]:
        outer=box(x,1130,110,width,515,1010)
        inner=box(x+20,1150,135,width-40,475,1020)
        add(key,outer.cut(inner),'body',64)
        add(key,box(x+27,1157,655,width-54,461,5),(0.59,0.76,0.80),75,'WaterLevelIllustration')
    # UV lamps share a single chamber; no false serial UV reactor chain.
    lamps=[]; caps=[]
    for x in (4550,4755,4960):
        lamps.append(cylinder(30,770,(x,1390,280)))
        caps.append(cylinder(49,85,(x,1390,1050)))
    add('UV',Part.makeCompound(lamps),(0.53,0.45,0.78),30,'LampSleeves')
    add('UV',Part.makeCompound(caps),'frame',0,'ThreeCaps')
    # Skimmer platform, reaction column and cup.
    stand=[box(3160,475,550,600,585,55)]
    for x in (3160,3710):
        for y in (475,1010):stand.append(box(x,y,100,45,45,450))
    add('SK101',Part.makeCompound(stand),'body',0,'Stand')
    wall=cylinder(215,1100,(3450,760,610)).cut(cylinder(200,1100,(3450,760,625)))
    add('SK101',wall,'body',32)
    bands=[cylinder(240,35,(3450,760,z)) for z in (600,1680)]
    add('SK101',Part.makeCompound(bands),'frame',0,'Flanges')
    cup=cylinder(230,425,(3450,760,1740)).cut(cylinder(215,430,(3450,760,1755)))
    add('SK101',cup,(.65,.80,.86),65,'CollectionCup')
    add('SK101',cylinder(75,360,(3450,760,1710)),(.70,.82,.87),48,'FoamRiser')
    add('SK101',cylinder(246,24,(3450,760,2165)),'frame',0,'CupRim')
    # Filter vessel approximated by cylindrical belly and domed shoulders.
    barrel=cylinder(260,485,(4110,780,280))
    bottom=Part.makeSphere(260,V(4110,780,340))
    top=Part.makeSphere(260,V(4110,780,720))
    vessel=barrel.fuse(bottom).fuse(top)
    add('F101',vessel,(.42,.50,.48),16)
    add('F101',cylinder(280,75,(4110,780,105)),'dark',0,'Base')
    add('F101',cylinder(100,150,(4110,780,960)),'body',0,'Multiport')
    add('F101',box(4090,760,1110,42,205,32),'dark',0,'Handle')
    # Front and rear pumps, basket strainers, motors and fins.
    for key,y in [('P101',620),('P102',990)]:
        parts=[box(4620,y-130,105,455,245,40),cylinder(105,190,(4730,y,250),(1,0,0)),cylinder(110,165,(4940,y,145))]
        add(key,Part.makeCompound(parts),'dark')
        motor=[cylinder(95,190,(4560,y,255),(1,0,0))]
        for xx in range(4570,4740,25):motor.append(cylinder(106,8,(xx,y,255),(1,0,0)))
        add(key,Part.makeCompound(motor),(.19,.35,.54),0,'Motor')
        add(key,cylinder(108,20,(4940,y,310)),(.58,.72,.73),40,'StrainerLid')
    # Ozone under skimmer stand.
    add('OZ101',box(3290,590,110,295,300,370),(.50,.54,.55))
    add('OZ101',box(3325,581,360,225,12,86),'dark',0,'LocalControls')
    # External air pump on rear ledge.
    add('A101',box(4180,1030,1210,340,230,200),(.20,.42,.36))
    fins=[box(xx,1020,1240,10,250,130) for xx in range(4210,4500,40)]
    add('A101',Part.makeCompound(fins),'frame',0,'CoolingRibs')
    # Panel with 6 indicators, 5 selector knobs and UV display.
    add('CP101',box(4760,1120,1210,370,110,420),'body')
    add('CP101',box(4780,1104,1230,330,14,380),'dark',0,'Face')
    controls=[]
    for z in (1550,1400):
        for x in (4840,4945,5050):controls.append(cylinder(21,12,(x,1103,z),(0,-1,0)))
    add('CP101',Part.makeCompound(controls),(.23,.68,.48),0,'SixIndicators')
    knobs=[]
    for x,z in [(4840,1480),(5050,1480),(4840,1310),(4945,1310),(5050,1310)]:
        knobs.append(cylinder(20,22,(x,1100,z),(0,-1,0)))
    add('CP101',Part.makeCompound(knobs),'frame',0,'FiveSelectors')
    add('CP101',box(4900,1080,1460,88,20,45),(.63,.82,.90),0,'UVController')
    # Persistent labels: visible even without the animation macro.
    for key,(title,detail,source,pos) in EQUIPMENT.items():
        short=title.replace(' | representative bank',' / schematic').replace(' | ',' / ')
        label(doc,labels,'Tag_'+key,short,pos,size=11)
