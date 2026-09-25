"""Entry point retained on FreeCADGui for the timer/widget lifetime."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets,QtCore
from .build import load_or_build
from .controller import Explorer
from .presentation import style_document

def launch(root):
    root=Path(root)
    old=getattr(Gui,'ras_explorer',None)
    if old:
        old.dispose();old.close();old.deleteLater()
    doc=load_or_build(root)
    style_document(doc)
    explorer=Explorer(doc,root);Gui.ras_explorer=explorer
    explorer.show();explorer.raise_();explorer.activate_document()
    # Hide competing work panels for this presentation; the model tree can be reopened via View > Panels.
    for dock in Gui.getMainWindow().findChildren(QtWidgets.QDockWidget):
        if dock.objectName() in ('Model','Combo View','Tasks','Report view','Python console'):
            dock.hide()
    def finish_layout():
        for dock in Gui.getMainWindow().findChildren(QtWidgets.QDockWidget):
            if dock.objectName() in ('Tasks','Python console','Model'):
                dock.hide()
        explorer.iso()
    QtCore.QTimer.singleShot(700,finish_layout)
    doc.recompute();doc.save()
    return explorer
