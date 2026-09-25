"""One-click FreeCAD flow explorer, inspection controls and guided animation."""
from pathlib import Path
import time
import csv
import html
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore,QtGui,QtWidgets
from .catalog import ROUTES,MODES,HEX,EQUIPMENT,COLORS
from .animation import Animator
from .presentation import configure_view,overview,top,front,skid

STYLE='''
QWidget#RASContent {background:#f5f8fa;color:#132d39;}
QLabel {color:#163442;background:transparent;}
QLabel#Kicker {color:#607987;font-size:10px;font-weight:600;letter-spacing:2px;}
QLabel#Heading {font-size:25px;font-weight:700;color:#123d4b;}
QPushButton {background:#ffffff;color:#244b5b;border:1px solid #c9d7de;border-radius:7px;padding:9px 8px;font-size:12px;}
QPushButton:hover {background:#e4edf2;border-color:#7498a7;}
QPushButton:checked {background:#193f50;color:white;border-color:#193f50;}
QPushButton#Primary {background:#163f50;color:#ffffff;border:0;}
QComboBox {background:white;color:#183644;border:1px solid #c5d4dd;border-radius:5px;padding:7px;font-size:12px;}
QTextBrowser {background:white;color:#264857;border:1px solid #d7e1e7;border-radius:7px;padding:7px;font-size:12px;}
QCheckBox {color:#315664;font-size:12px;padding:3px;}
QSlider::groove:horizontal {background:#d2e0e6;height:5px;border-radius:2px;}
QSlider::handle:horizontal {background:#245c72;width:16px;margin:-5px 0;border-radius:7px;}
QToolTip {background:#193f50;color:white;padding:6px;}
'''

class Explorer(QtWidgets.QDockWidget):
    def __init__(self,doc,root):
        super().__init__('RAS • Flow explorer',Gui.getMainWindow())
        self.setObjectName('RASFlowExplorer');self.doc=doc;self.doc_name=doc.Name;self.root=Path(root);self._disposed=False
        self.view=Gui.getDocument(doc.Name).activeView();configure_view(self.view);self.anim=Animator(self.view)
        self.mode='water';self.running=True;self.tour=False;self.speed=1;self.route_key=None
        self.last=time.monotonic();self.tour_elapsed=0;self.seconds=0
        self.setMinimumWidth(310);self.setMaximumWidth(380)
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        body=QtWidgets.QWidget();body.setObjectName('RASContent');self.setWidget(body)
        lay=QtWidgets.QVBoxLayout(body);lay.setContentsMargins(16,16,16,12);lay.setSpacing(9)
        def label(text,name=None):
            ob=QtWidgets.QLabel(text)
            if name:ob.setObjectName(name)
            ob.setWordWrap(True);lay.addWidget(ob);return ob
        label('MUDCRAB  /  LFS-10M','Kicker');label('Flow atlas','Heading')
        label('Explore the system in three dimensions.','Kicker')
        grid=QtWidgets.QGridLayout();self.buttons={}
        for i,key in enumerate(('water','waste','electrical','air')):
            btn=QtWidgets.QPushButton(MODES[key][0]);btn.setCheckable(True)
            btn.setToolTip('Isolate '+key+' paths; keep equipment for context.')
            btn.toggled.connect(lambda checked,k=key:self.select_mode(k) if checked else None)
            grid.addWidget(btn,i//2,i%2);self.buttons[key]=btn
        lay.addLayout(grid)
        overview=QtWidgets.QPushButton('00 / All systems');overview.setCheckable(True)
        overview.toggled.connect(lambda checked:self.select_mode('all') if checked else None);lay.addWidget(overview);self.buttons['all']=overview
        self.title=label('Normal recirculation');self.title.setStyleSheet('font-weight:700;font-size:16px;padding-top:4px;')
        self.route=QtWidgets.QComboBox();self.route.setMaxVisibleItems(16)
        self.route.currentIndexChanged.connect(self.route_changed);lay.addWidget(self.route)
        self.info=QtWidgets.QTextBrowser();self.info.setOpenExternalLinks(False);self.info.setMinimumHeight(145);self.info.setMaximumHeight(200);lay.addWidget(self.info)
        row=QtWidgets.QHBoxLayout()
        self.play=QtWidgets.QPushButton('Pause animation');self.play.setObjectName('Primary');self.play.clicked.connect(self.toggle_play);row.addWidget(self.play)
        self.tour_btn=QtWidgets.QPushButton('Guided tour');self.tour_btn.setCheckable(True);self.tour_btn.toggled.connect(self.toggle_tour);row.addWidget(self.tour_btn);lay.addLayout(row)
        speedrow=QtWidgets.QHBoxLayout();self.speed_label=QtWidgets.QLabel('Speed  1.00×');speedrow.addWidget(self.speed_label)
        slider=QtWidgets.QSlider(QtCore.Qt.Horizontal);slider.setRange(25,200);slider.setValue(100);slider.valueChanged.connect(self.set_speed);speedrow.addWidget(slider);lay.addLayout(speedrow)
        self.labels=QtWidgets.QCheckBox('Show equipment labels');self.labels.setChecked(True);self.labels.toggled.connect(self.apply_visibility);lay.addWidget(self.labels)
        self.ghost=QtWidgets.QCheckBox('Transparent equipment');self.ghost.setChecked(True);self.ghost.toggled.connect(self.apply_visibility);lay.addWidget(self.ghost)
        cameras=QtWidgets.QHBoxLayout()
        for text,cmd in [('3D',self.iso),('Top',self.top),('Front',self.front),('Skid',self.skid)]:
            b=QtWidgets.QPushButton(text);b.clicked.connect(cmd);cameras.addWidget(b)
        lay.addLayout(cameras)
        row=QtWidgets.QHBoxLayout()
        for text,cmd in [('Save image',self.snapshot),('Evidence / holds',self.evidence)]:
            b=QtWidgets.QPushButton(text);b.clicked.connect(cmd);row.addWidget(b)
        lay.addLayout(row)
        self.status=label('LIVE · direction markers are illustrative','Kicker')
        label('Conceptual routing · source gaps retained\nClick a component to inspect its function.','Kicker')
        lay.addStretch(1);body.setStyleSheet(STYLE)
        Gui.getMainWindow().addDockWidget(QtCore.Qt.RightDockWidgetArea,self)
        self.timer=QtCore.QTimer(self);self.timer.setInterval(33);self.timer.timeout.connect(self.tick)
        self.select_mode('water');self.timer.start();Gui.Selection.addObserver(self)

    def activate_document(self):
        mdi=Gui.getMainWindow().findChild(QtWidgets.QMdiArea)
        if mdi:
            for sub in mdi.subWindowList():
                if sub.windowTitle().startswith(self.doc_name+' :'):
                    mdi.setActiveSubWindow(sub);break
        App.setActiveDocument(self.doc_name)

    def select_mode(self,key,tour=False):
        self.activate_document()
        if not tour:
            self.tour=False;self.tour_btn.setChecked(False)
        self.mode=key;self.route_key=None
        if self.doc.getObject('AtlasMode'):
            self.doc.AtlasMode.LabelText=[MODES[key][0]+' / '+MODES[key][1]]
            self.doc.AtlasMode.ViewObject.TextColor=COLORS.get(key,(.14,.32,.39))
        for k,btn in self.buttons.items():
            btn.blockSignals(True);btn.setChecked(k==key);btn.blockSignals(False)
        self.title.setText(MODES[key][1]);self.title.setStyleSheet(f'font-weight:700;font-size:16px;color:{HEX[key]};padding-top:4px;')
        self.route.blockSignals(True);self.route.clear();self.route.addItem('All paths in this view',None)
        for r in ROUTES:
            if key=='all' or r['layer']==key:self.route.addItem(r['title'],r['key'])
        self.route.blockSignals(False);self.update_info();self.apply_visibility()
        if hasattr(self,'status'):self.status.setText('GUIDED TOUR · '+key.upper() if self.tour else ('LIVE' if self.running else 'PAUSED')+' · '+key.upper())

    def route_changed(self,index):
        self.route_key=self.route.itemData(index);self.tour=False;self.tour_btn.setChecked(False)
        self.update_info();self.apply_visibility()

    def update_info(self):
        if self.route_key:
            r=next(r for r in ROUTES if r['key']==self.route_key)
            title,description,source=r['title'],r['detail'],r['source']
            self.info.setHtml(f'<b>{html.escape(title)}</b><p>{html.escape(description)}</p><p style="color:#738895">SOURCE · {html.escape(source)}</p>')
        else:
            _,title,description,note=MODES[self.mode]
            self.info.setHtml(f'<b>{html.escape(description)}</b><p>{html.escape(note)}</p>')

    def apply_visibility(self,*unused):
        if self.doc_name not in App.listDocuments():return
        for layer in ('water','waste','electrical','air'):
            group=self.doc.getObject('Flow_'+layer)
            group.Visibility=True
            for obj in group.Group:
                visible=self.mode in ('all',layer)
                if self.route_key:
                    visible=visible and (obj.Name==self.route_key or obj.Name in ('Arrow_'+self.route_key,'Text_'+self.route_key,'Boundary_'+self.route_key))
                obj.Visibility=visible
        self.doc.EquipmentLabels.Visibility=self.labels.isChecked()
        for obj in self.doc.EquipmentLabels.Group:obj.Visibility=self.labels.isChecked()
        for obj in self.doc.Equipment.Group:
            if hasattr(obj,'BaseTransparency'):
                original=obj.BaseTransparency
                obj.ViewObject.Transparency=max(original,60) if self.ghost.isChecked() and obj.Service not in ('BASE','SKID') else original
        self.anim.set_mode(self.mode,self.route_key);self.view.redraw()

    def toggle_play(self):
        self.running=not self.running;self.play.setText('Pause animation' if self.running else 'Play animation')
        self.status.setText(('LIVE' if self.running else 'PAUSED')+' · '+self.mode.upper())

    def toggle_tour(self,checked):
        self.tour=checked;self.tour_elapsed=0
        if checked:
            self.running=True;self.play.setText('Pause animation');self.select_mode('water',tour=True)

    def set_speed(self,value):
        self.speed=value/100;self.speed_label.setText(f'Speed  {self.speed:.2f}×')

    def tick(self):
        now=time.monotonic();dt=min(now-self.last,.15);self.last=now
        if self.doc_name not in App.listDocuments():self.dispose();return
        if self.running:
            self.seconds+=dt;self.anim.update(dt*self.speed)
            if self.tour:
                self.tour_elapsed+=dt
                if self.tour_elapsed>=9:
                    keys=['water','waste','electrical','air'];self.tour_elapsed=0
                    key=keys[(keys.index(self.mode)+1)%4] if self.mode in keys else 'water'
                    self.select_mode(key,tour=True)

    def iso(self):
        self.activate_document();overview(self.view)
    def top(self):self.activate_document();top(self.view)
    def front(self):self.activate_document();front(self.view)
    def skid(self):self.activate_document();skid(self.view)

    def snapshot(self):
        path=self.root/'previews'/('RAS_'+self.mode+'.png');path.parent.mkdir(exist_ok=True)
        width,height=self.view.getSize()
        self.view.redraw()
        self.view.saveImage(str(path),width,height,'Current')
        self.status.setText('Saved: previews/'+path.name)

    def evidence(self):
        dlg=QtWidgets.QDialog(self);dlg.setWindowTitle('RAS / evidence and open holds');dlg.resize(840,560)
        lay=QtWidgets.QVBoxLayout(dlg);text=QtWidgets.QTextBrowser();lay.addWidget(text)
        parts=['<h2>Reading this model</h2><p>Native equipment geometry is simplified. All routing and animation are conceptual. Only the skid nominal envelope is dimensioned from the manual. Two representative banks are shown; box count is not an inventory.</p>',
               '<p><b>Source keys:</b> M = manufacturer manual PDF page; E = photo-evidence PDF page. Revision 2 keeps C (confirmed), R (reconstructed) and OPEN evidence holds separate.</p>',
               '<p><b>Water:</b> M4 sequence. <b>Waste:</b> W02 independent services. <b>Air:</b> G01 distinct LP-100 and ozone circuits. <b>Power:</b> E01 functional allocation; E02 printed branch register is not terminal wiring.</p><h3>Open evidence register</h3>']
        with (self.root/'evidence'/'open_evidence_holds.csv').open() as f:
            rows=list(csv.reader(f))
        parts.append('<table border="1" cellpadding="6">')
        for i,row in enumerate(rows):
            tag='th' if i==0 else 'td';parts.append('<tr>'+''.join(f'<{tag}>{html.escape(cell)}</{tag}>' for cell in row)+ '</tr>')
        parts.append('</table>');text.setHtml(''.join(parts));dlg.show();self._evidence_dialog=dlg

    def addSelection(self,doc_name,obj_name,sub_name,point):
        if doc_name!=self.doc.Name:return
        ob=self.doc.getObject(obj_name)
        if ob and hasattr(ob,'Description') and ob.Description:
            self.info.setHtml(f'<b>{html.escape(ob.Label)}</b><p>{html.escape(ob.Description)}</p><p style="color:#738895">SOURCE · {html.escape(ob.Evidence)}</p>')
    def clearSelection(self,*args):pass
    def removeSelection(self,*args):pass
    def setSelection(self,*args):pass

    def dispose(self):
        if self._disposed:return
        self._disposed=True
        self.timer.stop();self.anim.dispose()
        try:Gui.Selection.removeObserver(self)
        except (RuntimeError,ReferenceError):pass
    def closeEvent(self,event):
        self.dispose();super().closeEvent(event)
