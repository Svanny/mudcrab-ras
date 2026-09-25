"""Capture a reproducible four-view animation using FreeCAD's own renderer."""
from pathlib import Path
import json
from PySide import QtCore
import FreeCADGui as Gui

def capture(explorer,folder):
    e=explorer;folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    e.timer.stop();e.tour_btn.setChecked(False);e.running=False
    modes=['water','waste','electrical','air'];state={'frame':0};per_mode=24
    timer=QtCore.QTimer(e);e._capture_timer=timer
    def frame():
        i=state['frame']
        if i>=per_mode*len(modes):
            timer.stop();e.select_mode('water');e.iso();e.running=True;e.play.setText('Pause animation')
            e.doc.recompute();e.doc.save();e.timer.start();e.status.setText('LIVE · WATER')
            (folder/'complete.json').write_text(json.dumps({'frames':i,'fps':8,'modes':modes}))
            return
        mode=modes[i//per_mode]
        if i%per_mode==0:
            e.select_mode(mode);e.iso();e.anim.phase=0
        e.anim.update(.32);e.view.redraw()
        width,height=e.view.getSize()
        e.view.saveImage(str(folder/f'{i:03d}.png'),width,height,'Current')
        if i%per_mode==0:e.snapshot()
        e.status.setText(f'Capturing tour preview · {i+1}/{per_mode*len(modes)}')
        state['frame']+=1
    timer.timeout.connect(frame);timer.start(25)
