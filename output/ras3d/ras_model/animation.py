"""Coin scenegraph animation: no document recompute or CAD file mutation per frame."""
import math
from pivy import coin
from .catalog import ROUTES,COLORS
from .geometry import sample

class Animator:
    def __init__(self,view):
        self.view=view; self.root=coin.SoSeparator(); self.root.setName('RAS_Animation')
        pick=coin.SoPickStyle(); pick.style=coin.SoPickStyle.UNPICKABLE;self.root.addChild(pick)
        self.markers=[]; self.bubbles=[]; self.phase=0.0; self.active='water';self.route_key=None
        for route in ROUTES:
            count=3 if len(route['points'])>4 else 2
            for index in range(count):
                switch=coin.SoSwitch(); branch=coin.SoSeparator()
                trans=coin.SoTransform();branch.addChild(trans)
                mat=coin.SoMaterial();c=COLORS[route['color']]
                bright=tuple(min(1,v*.65+.30) for v in c)
                mat.diffuseColor=bright;mat.emissiveColor=tuple(v*.30 for v in bright);branch.addChild(mat)
                cone=coin.SoCone();cone.bottomRadius=39;cone.height=120;branch.addChild(cone)
                switch.addChild(branch);self.root.addChild(switch)
                self.markers.append((route,switch,trans,index/count))
        for i in range(16):
            switch=coin.SoSwitch(); branch=coin.SoSeparator();trans=coin.SoTranslation();branch.addChild(trans)
            mat=coin.SoMaterial();mat.diffuseColor=COLORS['air'];mat.emissiveColor=(0,.14,.10);branch.addChild(mat)
            sphere=coin.SoSphere();sphere.radius=12+(i%3)*3;branch.addChild(sphere)
            switch.addChild(branch);self.root.addChild(switch);self.bubbles.append((switch,trans,i))
        view.getSceneGraph().addChild(self.root)
        self.update(0)

    def set_mode(self,mode,route_key=None):
        self.active=mode;self.route_key=route_key;self.update(0)

    def visible(self,route):
        return (self.active=='all' or route['layer']==self.active) and (not self.route_key or route['key']==self.route_key)

    def update(self,dt):
        self.phase+=dt*.095
        for route,switch,trans,offset in self.markers:
            show=self.visible(route);switch.whichChild=0 if show else -1
            if not show:continue
            point,direction=sample(route['points'],(self.phase+offset)%1)
            trans.translation=point
            trans.rotation=coin.SbRotation(coin.SbVec3f(0,1,0),coin.SbVec3f(*direction))
        for switch,trans,i in self.bubbles:
            show=self.active in ('all','air') and self.route_key in (None,'A01')
            switch.whichChild=0 if show else -1
            if show:
                t=(self.phase*1.7+i/16)%1
                trans.translation=(3890+(i%4)*112+math.sin(t*8+i)*12,1260+(i//4)*84,330+t*680)

    def dispose(self):
        try:self.view.getSceneGraph().removeChild(self.root)
        except (RuntimeError,ReferenceError):pass
