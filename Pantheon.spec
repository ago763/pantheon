# Build with: .venv\Scripts\python.exe -m PyInstaller Pantheon.spec --noconfirm
from pathlib import Path

root = Path(SPECPATH)
a = Analysis(
    [str(root / 'main.py')],
    pathex=[str(root)],
    binaries=[],
    datas=[(str(root / 'assets'), 'assets'), (str(root / 'data'), 'data')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'unittest'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='Pantheon', debug=False, strip=False, upx=False,
    console=False, disable_windowed_traceback=False,
)
