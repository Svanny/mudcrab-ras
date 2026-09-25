"""Evidence, styling and schematic layout. Coordinates are millimetres, not as-built routing."""
COLORS = {
    'water': (0.03, 0.43, 0.92), 'waste': (0.92, 0.25, 0.08),
    'electrical': (0.94, 0.64, 0.04), 'air': (0.01, 0.67, 0.49),
    'ozone': (0.65, 0.25, 0.85), 'overflow': (0.83, 0.29, 0.37),
    'body': (0.80, 0.85, 0.86), 'frame': (0.30, 0.38, 0.43),
    'dark': (0.12, 0.20, 0.26), 'rack': (0.35, 0.57, 0.69),
    'sand': (0.76, 0.66, 0.43), 'label': (0.10, 0.17, 0.22),
}
HEX = {'water':'#0871eb','waste':'#dc4518','electrical':'#b57600','air':'#009d77','all':'#245363'}
MODES = {
 'water': ('01 / WATER', 'Normal recirculation',
   'Crab boxes → inlet pump → sand filter → skimmer → BIO-1 → BIO-2 → UV → outlet pump → boxes.',
   'Blue arrows follow the manufacturer’s process order. Physical routes and box distribution are schematic. 6–10 m³/h is package throughput, not stored water volume.'),
 'waste': ('02 / WASTE', 'Discharge & cleaning services',
   'Orange: bottom purge, multiport waste, cup discharge, biological cleaning and sand removal. Rose: separate high-level overflow.',
   'Service previews are shown together for explanation; they are not simultaneous normal operation. Each path stops at its own open interface. External destinations and valve mapping remain H08.'),
 'electrical': ('03 / ELECTRICAL', 'Supply & functional loads',
   '220 V AC / 50 Hz supply → panel → two pumps, UV assemblies, LP-100 and ozone unit.',
   'Dashed amber links identify functional loads, not verified wiring or AC current direction. Package input: 1.8 kW. Terminal assignments, protection, earth path and branch mapping remain H06/H09.'),
 'air': ('04 / AIR + OZONE', 'Two separate gas services',
   'Green: external LP-100 aeration → BIO-2. Violet: ozone unit → skimmer gas intake.',
   'The ozone unit’s local AIR PUMP control is distinct from the external LP-100. Diffuser geometry and hose paths are schematic. Off-gas and residual-oxidant treatment remain H05.'),
 'all': ('00 / OVERVIEW', 'Four systems, one model',
   'Blue water · orange waste · amber power · green air · violet ozone.',
   'Choose a system to isolate it. Animated markers explain direction or functional delivery; their speed is illustrative. Geometry is a schematic reconstruction, not an installation drawing.'),
}
EQUIPMENT = {
 'RACK_A': ('CULTURE A | representative bank', 'Individual crab boxes receive water from a high header and discharge to a lower collector. Two banks are illustrated; rendered boxes are representative, not an installed count.', 'C: E2; M11. Geometry/quantity: OPEN H07.', (400,460,1790)),
 'RACK_B': ('CULTURE B | representative bank', 'Second representative bank. Box dimensions, operating volumes and branch flows are not established.', 'C: E2; OPEN H07/H10.', (1690,460,1790)),
 'P102': ('P-102 | inlet pump', 'Rear pump with basket strainer, reconstructed as inlet duty: culture return to sand filter. Complete plate is unreadable; no front-pump ratings are copied.', 'R: M4–5; E7,10. OPEN H01/H06.', (5230,970,390)),
 'F101': ('F-101 | sand filter', 'Pressure sand filter with multiport. Manufacturer sand charge: 22 kg. Normal FILTER service leads to the skimmer. Waste outlet identification is reconstructed.', 'C: M4,6–7; E4–5. R: port identification. OPEN H10.', (4060,290,1160)),
 'SK101': ('SK-101 | protein skimmer', 'Mixing/reaction column with foam collection cup. Water continues to BIO-1; collected foam is a separate waste service. Two other manual waste stubs remain unidentified.', 'C: M4–5,7–8,15; E10. OPEN H05/H08.', (3050,740,2410)),
 'BIO1': ('BIO-1 | first chamber', 'First biological chamber in manufacturer sequence. Internal media, fill and operating level are unspecified. Rendered internals are schematic.', 'C: M4,14–15. OPEN H02.', (3040,1770,1250)),
 'BIO2': ('BIO-2 | aerated chamber', 'Second biological chamber receives external air-pump service. Bubbles illustrate aeration; diffuser hardware and airflow remain unknown.', 'C: M4,14–15. OPEN H02/H04.', (3780,1770,1250)),
 'UV': ('UV | three lamp assemblies', 'Three lamp assemblies in final treatment chamber. Source does not establish three serial hydraulic reactors. Lamp life: 8,000 h; watts, drivers and dose unverified.', 'C: E11–12; M8–9. OPEN H03.', (4550,1770,1250)),
 'P101': ('P-101 | outlet STP50', 'Front STP50 returns treated water to culture supply. Plate: 0.37 kW input, 0.25 kW output, 2.0 A; rated 6 m³/h at 7 m. Pump duty is reconstructed.', 'C: E6–7; R: M4–5/E10. OPEN H06.', (4950,150,390)),
 'A101': ('A-101 | LP-100', 'External aerator serving BIO-2. LP-100 is the model name, not an established wattage or airflow. Separate from ozone unit local AIR PUMP control.', 'C: E8–10; M4. OPEN H04.', (4310,1120,1770)),
 'OZ101': ('OZ-101 | ozone unit', 'Ozone generator with local timer and OZONE / AIR PUMP controls. Gas service to skimmer is documented; installed hose trace, dose and off-gas handling are not.', 'C: E3,10; M4,7. OPEN H05.', (2950,190,610)),
 'CP101': ('CP-101 | control panel', 'Six indicator lenses, five selector knobs and one UV controller window. Seven printed circuit branches cannot be uniquely mapped to installed loads.', 'C: M16; E10. OPEN H06/H09.', (5090,1440,1740)),
}
# Every route is a conceptual process connection; positions are chosen for legibility.
ROUTES=[]
def route(key, layer, title, pts, detail, source, color=None, dashed=False, label=None):
    ROUTES.append(dict(key=key,layer=layer,title=title,points=pts,detail=detail,source=source,
                       color=color or layer,dashed=dashed,label=label))

route('W01','water','01 • Culture return → inlet pump',[(550,520,220),(550,140,220),(5330,140,220),(5330,990,220),(4940,990,220)],'Used culture water enters the rear inlet-duty pump. Collector geometry is illustrative.','M4; E2; R: E7,10; H07/H10',label=('RETURN', (2030,70,260)))
route('W01B','water','Culture B → return collector',[(1840,520,220),(1840,140,220)],'Second bank joins the culture return.','E2; H07/H10')
route('W02','water','02 • Inlet pump → sand filter',[(4740,990,310),(4580,990,310),(4580,780,1120),(4240,780,1120),(4110,780,1020)],'Inlet pump feeds multiport PUMP connection.','M4,6; R: E5,10')
route('W03','water','03 • Sand filter → skimmer',[(4030,780,1050),(3940,780,1050),(3940,440,1240),(3450,440,1240),(3450,760,1000)],'Normal FILTER mode passes through the sand bed and returns to the skimmer.','M4,6–7; R: port trace')
route('W04','water','04 • Skimmer → BIO-1',[(3450,970,880),(3450,1160,880),(3440,1360,820)],'Skimmer treated-water outlet continues into the first biological chamber.','M4')
route('W05','water','05 • BIO-1 → BIO-2',[(3440,1360,820),(4080,1360,820)],'Biological treatment sequence; partition apertures and levels are not dimensioned.','M4; H02')
route('W06','water','06 • BIO-2 → UV chamber',[(4080,1360,820),(4780,1360,820)],'Aerated biological chamber passes water to the chamber containing three UV assemblies.','M4; E11–12; H02/H03')
route('W07','water','07 • UV → outlet pump',[(4780,1360,820),(5250,1360,820),(5250,620,300),(4940,620,300)],'Final treated water reaches front outlet-duty pump.','M4; R: E7,10')
route('W08','water','08 • Outlet pump → high supply header',[(4740,620,310),(4590,620,310),(4590,80,310),(4590,-20,1940),(380,-20,1940),(380,600,1940)],'Pressurized culture supply header from front STP50. External pipe sizing is unresolved.','M4; E2; R: E6–7; H10',label=('CULTURE SUPPLY',(1950,-20,2040)))
route('W09A','water','09 • Supply → culture A',[(380,600,1940),(720,600,1940),(720,710,1510),(720,710,420),(550,520,220)],'Representative distribution through the bank; detailed branch plumbing and box flow are not asserted.','E2; M11; H07')
route('W09B','water','09 • Supply → culture B',[(1670,-20,1940),(1670,600,1940),(2010,600,1940),(2010,710,1510),(2010,710,420),(1840,520,220)],'Representative high supply and low return serving the second bank.','E2; M11; H07')
route('D01','waste','Culture bottom-discharge interface',[(550,520,180),(550,320,180),(100,320,180),(100,-560,180)],'Manual describes pond bottom draining one unit at a time. Rack adaptation and outfall are unresolved.','M14; H07/H08',label=('CULTURE PURGE / H08',(0,-680,160)))
route('D02','waste','Multiport WASTE interface',[(4110,540,1090),(4110,220,1090),(4110,220,120),(4110,-510,120)],'BACKWASH, RINSE or WASTE outlet; preview does not set the valve or prescribe a two-pump sequence.','M6–7; R: E5,10; H08/H11',label=('FILTER WASTE / H08',(3870,-630,160)))
route('D03','waste','Foam-cup discharge interface',[(3450,510,2030),(3450,330,2030),(2880,330,2030),(2880,-480,2030),(2880,-480,170)],'Functional cup discharge only. Not identified with either ambiguous manual skimmer waste stub.','M7,15; H08',label=('CUP / H08',(2630,-640,140)))
route('D04','waste','Biological cleaning → common waste interface',[(4070,1180,170),(4070,1770,170),(5350,1770,170),(5350,-380,170)],'Illustrative manifold association; individual chamber-to-valve connections are unverified. Skid common waste connection is diameter 50 mm.','M3–5,15; H08',dashed=True,label=('SKID WASTE / H08',(5200,-530,150)))
route('D05','waste','Separate high-level overflow interface',[(5090,1470,970),(5610,1470,970),(5610,-100,970),(5610,-100,150)],'Separate overflow function. Pipe diameter, capacity and final destination are unknown.','M5; H08/H10',color='overflow',label=('OVERFLOW / H08',(5550,-250,130)))
route('D06','waste','Sand-removal service interface',[(4110,500,270),(4400,500,270),(4400,-800,150)],'Spent sand and wash water during media replacement. No receiving container is established.','M6; E5; H08',label=('SAND / H08',(4320,-950,150)))
route('D07','waste','Unidentified skimmer waste stubs',[(3260,760,1020),(2940,760,1020),(2940,160,1020)],'Manual shows two Waste outlet stubs, but their cup/body functions are unresolved. One boundary marker represents the unresolved pair, not a merged pipe.','M5; H08',dashed=True,label=('STUB ID / H08',(2580,50,1010)))
route('E00','electrical','Supply → panel',[(5880,1860,2400),(5130,1860,2400),(4950,1860,1500),(4950,1220,1500)],'Manufacturer assembly supply: 220 V AC, 50 Hz, 1.8 kW input. Protection and PE path are not defined here.','M3,16; H09',dashed=True,label=('220 V AC · 50 Hz',(5240,1880,2470)))
for key,title,end,detail in [
 ('E01','Panel → outlet pump',(4780,620,320),'STP50 front pump: 0.37 kW input, 2.0 A. Supplier Pump1 match reconstructed.'),
 ('E02','Panel → inlet pump',(4780,990,320),'Rear pump present; model, watts and current unresolved.'),
 ('E03','Panel → UV assemblies',(4780,1400,1150),'Three lamps visible; ballast allocation and input watts unresolved.'),
 ('E04','Panel → external LP-100',(4340,1130,1390),'Functional supply association only; control-branch identity and electrical ratings unresolved.'),
 ('E05','Panel → ozone unit',(3450,700,430),'Ozone unit has its own timer and two local controls; no common aerator circuit inferred.')]:
 route(key,'electrical',title,[(4950,1220,1500),(4950,1920,1740),(end[0],1920,1740),(end[0],end[1],1740),end],detail,'M16; E3,6–12; H06/H09',dashed=True)
route('A01','air','LP-100 → BIO-2 aeration',[(4340,1130,1390),(4200,1130,1390),(4080,1130,1390),(4080,1420,1390),(4080,1420,320)],'External air pump supplies the second biological chamber. Green rising bubbles depict aeration, with no assumed diffuser design.','M4; E8–10; H02/H04',label=('AERATION',(3650,1420,1740)))
route('A02','air','Ozone unit → skimmer intake',[(3450,700,430),(3100,700,430),(3100,440,430),(3100,440,1100),(3450,440,1100),(3450,760,1100)],'Separate ozone service to skimmer gas intake; local internal air pump differs from LP-100.','M4,7; E3; H05',color='ozone',label=('OZONE GAS',(2930,320,1160)))
route('A03','air','Skimmer off-gas boundary',[(3450,760,2190),(3450,760,2600),(3940,760,2600)],'Undocumented exhaust/residual-treatment boundary. Dashed indicator is not a traced hose, installed vent or confirmed destructor.','H05',color='ozone',dashed=True,label=('OFF-GAS / H05',(3550,720,2980)))
route('W10','water','Optional makeup → culture units',[(20,1070,2520),(550,1070,2520),(550,900,1540)],'Preconditioned makeup water is introduced through culture units in the manual. This dashed service boundary is not a supplied tank, pump, automatic valve or traced tie-in.','M11; H07',dashed=True,label=('MAKEUP / H07',(-200,1130,2640)))
route('D01B','waste','Culture B bottom-discharge interface',[(1840,520,180),(1840,320,180),(1390,320,180),(1390,-560,180)],'Second bank purge shown as a separate conceptual boundary. External collection and rack adaptation are unresolved; this is not a simultaneous draining instruction.','M14; E2; H07/H08',label=('BANK B PURGE / H08',(1230,-750,120)))
