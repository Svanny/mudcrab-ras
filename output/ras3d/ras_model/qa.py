"""Integration checks executed inside FreeCAD against the saved scene and live controller."""
import json
import time
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
from .catalog import ROUTES

def verify(explorer):
    e=explorer;d=e.doc;e.timer.stop();e.activate_document();results={}
    invalid=[]
    for ob in d.Objects:
        if hasattr(ob,'Shape') and (ob.Shape.isNull() or not ob.Shape.isValid()):invalid.append(ob.Name)
    assert not invalid,invalid
    results['solid_geometry']={'checked':sum(hasattr(o,'Shape') for o in d.Objects),'invalid':invalid}
    counts={}
    for layer in ('water','waste','electrical','air','all'):
        # setChecked models the accessibility action as well as keyboard/native toggles.
        if layer==e.mode:e.select_mode('all' if layer!='all' else 'water')
        e.buttons[layer].setChecked(True)
        assert e.mode==layer,(e.mode,layer)
        assert sum(b.isChecked() for b in e.buttons.values())==1
        for r in ROUTES:
            expected=layer in ('all',r['layer'])
            assert d.getObject(r['key']).Visibility==expected,(layer,r['key'])
        counts[layer]=sum(d.getObject(r['key']).Visibility for r in ROUTES)
    results['exclusive_views']=counts
    e.select_mode('water');e.route.setCurrentIndex(e.route.findData('W03'))
    assert [r['key'] for r in ROUTES if d.getObject(r['key']).Visibility]==['W03']
    results['single_route_isolation']='passed'
    e.select_mode('air');initial=e.anim.markers[-1][2].translation.getValue().getValue()
    phase=e.anim.phase;e.running=True;e.last=time.monotonic()-.08;e.tick()
    assert e.anim.phase>phase
    phase=e.anim.phase;e.toggle_play();e.last=time.monotonic()-.08;e.tick()
    assert e.anim.phase==phase
    e.toggle_play();e.set_speed(200)
    assert e.speed==2;e.set_speed(100)
    results['animation_play_pause_speed']='passed'
    e.labels.setChecked(False);assert all(not o.Visibility for o in d.EquipmentLabels.Group)
    e.labels.setChecked(True);assert all(o.Visibility for o in d.EquipmentLabels.Group)
    e.ghost.setChecked(False);assert d.SK101.ViewObject.Transparency==d.SK101.BaseTransparency
    e.ghost.setChecked(True);assert d.SK101.ViewObject.Transparency>=60
    results['labels_and_transparency']='passed'
    e.tour_btn.setChecked(True);assert e.tour and e.mode=='water'
    e.tour_elapsed=9;e.last=time.monotonic()-.08;e.tick();assert e.mode=='waste'
    e.tour_btn.setChecked(False);assert not e.tour
    results['guided_tour']='passed'
    e.iso();e.top();e.front();e.skid();e.iso()
    results['camera_presets']='passed'
    e.select_mode('water');e.running=True;e.play.setText('Pause animation')
    d.recompute();d.save();e.timer.start()
    results.update(objects=len(d.Objects),routes=len(ROUTES),freecad='.'.join(App.Version()[:3]),status='passed')
    path=e.root/'validation'/'integration_checks.json';path.write_text(json.dumps(results,indent=2))
    return results
