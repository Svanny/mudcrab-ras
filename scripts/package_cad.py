"""Build a small reproducible CAD download without previews or source PDFs."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'output/ras3d'
DEST = ROOT / 'public/downloads/Mudcrab_RAS_FreeCAD.zip'
files = [SOURCE / 'Mudcrab_RAS_Flows.FCStd', SOURCE / 'Launch_RAS.FCMacro', SOURCE / 'README.md']
files += sorted((SOURCE / 'ras_model').glob('*.py'))
files += sorted((SOURCE / 'evidence').glob('*.csv'))
files += [ROOT / 'LICENSE']
DEST.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(DEST, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for file in files:
        name = file.relative_to(SOURCE) if file.is_relative_to(SOURCE) else Path(file.name)
        info = zipfile.ZipInfo(str(Path('Mudcrab_RAS_FreeCAD') / name), (2026, 9, 25, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, file.read_bytes())
print(f'{DEST.name}: {DEST.stat().st_size:,} bytes')
