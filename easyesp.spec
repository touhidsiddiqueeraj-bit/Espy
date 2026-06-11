# easyesp.spec
# Build command: pyinstaller easyesp.spec

import sys
from pathlib import Path

block_cipher = None

ROOT = Path.cwd()

a = Analysis(
    ['main.py'],
    pathex=[str(ROOT)],
    binaries=[
        ('tools/arduino-cli', 'tools'),
        ('tools/arduino-cli.exe', 'tools'),
    ],
    datas=[
        ('firmware/easyesp_base.bin', 'firmware'),

        # Top 20 bundled libraries (optional, arduino-cli downloads if missing)
        # ('arduino-data/', 'arduino-data'),
    ],
    hiddenimports=[
        'PyQt6.sip',
        'serial.tools.list_ports',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'scipy',
        'PIL', 'cv2', 'tkinter',
        'PyQt6.QtQml', 'PyQt6.QtQuick', 'PyQt6.QtWebEngine',
        'PyQt6.QtSvg', 'PyQt6.QtMultimedia', 'PyQt6.QtXml',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Platform-specific executable settings
if sys.platform == "linux":
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='EasyESP',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='assets/easyesp.png',
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='EasyESP',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='assets/easyesp.ico',
        version='version_info.txt',
    )
