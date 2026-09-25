"""Run with FreeCAD's Python (or FreeCADCmd) to export the native equipment.

FREECAD_LIB may point to FreeCAD's lib directory. Coordinates are transformed
from millimetres/Z-up to metres/Y-up in the browser. Half-millimetre quantization
is below the precision of this schematic. Face boundaries retain hard normals.
"""
import csv
import gzip
import importlib.util
import json
import os
from pathlib import Path
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'output/ras3d'
DEST = ROOT / 'src/data'
if os.environ.get('FREECAD_LIB'):
    sys.path.insert(0, os.environ['FREECAD_LIB'])
import FreeCAD as App


def load_catalog():
    spec = importlib.util.spec_from_file_location('catalog', NATIVE / 'ras_model/catalog.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def export():
    catalog = load_catalog()
    doc = App.openDocument(str(NATIVE / 'Mudcrab_RAS_Flows.FCStd'))
    with zipfile.ZipFile(NATIVE / 'Mudcrab_RAS_Flows.FCStd') as archive:
        styles = ET.fromstring(archive.read('GuiDocument.xml'))
    data = bytearray()
    meshes = []
    for obj in doc.Equipment.Group:
        if not hasattr(obj, 'Shape') or obj.Shape.isNull():
            continue
        vertices, indices = [], []
        for face in obj.Shape.Faces:
            points, triangles = face.tessellate(12)
            offset = len(vertices)
            vertices.extend(tuple(round(c * 2) for c in (p.x, p.y, p.z)) for p in points)
            indices.extend(offset + i for tri in triangles for i in tri)
        while len(data) % 4:
            data.append(0)
        position_offset = len(data)
        for point in vertices:
            data.extend(struct.pack('<hhh', *point))
        while len(data) % 4:
            data.append(0)
        index_offset = len(data)
        for index in indices:
            data.extend(struct.pack('<I', index))
        color_el = styles.find(f".//ViewProvider[@name='{obj.Name}']/Properties/Property[@name='ShapeColor']/PropertyColor")
        if color_el is not None:
            packed = int(color_el.attrib['value'])
        else:
            material = styles.find(f".//ViewProvider[@name='{obj.Name}']/Properties/Property[@name='ShapeAppearance']/MaterialList")
            # FreeCAD 1.1 material-list v3: count, ambient RGBA, diffuse RGBA.
            if material is None or material.attrib.get('version') != '3':
                raise ValueError(f'Unsupported material format: {obj.Name}')
            with zipfile.ZipFile(NATIVE / 'Mudcrab_RAS_Flows.FCStd') as archive:
                packed = struct.unpack_from('<I', archive.read(material.attrib['file']), 8)[0]
        color = [(packed >> shift) & 255 for shift in (24, 16, 8)]
        meshes.append(dict(name=obj.Name, service=obj.Service, color=color,
                           transparency=obj.BaseTransparency, positionOffset=position_offset,
                           vertexCount=len(vertices), indexOffset=index_offset, indexCount=len(indices)))
    with (NATIVE / 'evidence/open_evidence_holds.csv').open(encoding='utf-8-sig') as f:
        holds = list(csv.DictReader(f))
    tags = []
    for key, equipment in catalog.EQUIPMENT.items():
        ob = doc.getObject('Tag_' + key)
        tags.append(dict(key=key, text=list(ob.LabelText), position=list(ob.Position)))
    atlas = dict(version=1, meshes=meshes, routes=catalog.ROUTES, colors=catalog.COLORS,
                 modes=catalog.MODES, equipment=catalog.EQUIPMENT, tags=tags, holds=holds)
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / 'atlas.json').write_text(json.dumps(atlas, separators=(',', ':'), ensure_ascii=False) + '\n')
    with (DEST / 'equipment.mesh').open('wb') as f:
        f.write(gzip.compress(bytes(data), compresslevel=9, mtime=0))
    print(json.dumps(dict(meshes=len(meshes), triangles=sum(m['indexCount']//3 for m in meshes),
                          rawBytes=len(data), compressedBytes=(DEST/'equipment.mesh').stat().st_size)))
    App.closeDocument(doc.Name)


if __name__ == '__main__':
    export()
