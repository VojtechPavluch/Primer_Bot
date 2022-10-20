# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('./driver/chromedriver.exe', './driver'), ('./images/png/001-check.png', './images/png'), ('./images/png/001-microscope.png', './images/png'), ('./images/png/001-rejected.png', './images/png'), ('./images/png/001-settings.png', './images/png'), ('./images/png/002-question-mark.png', './images/png')],
    datas=[('C:/Users/vojte/IDrive-Sync/Programming/Biology/designer.py', '.'), ('C:/Users/vojte/IDrive-Sync/Programming/Biology/filemanager.py', '.'), ('C:/Users/vojte/IDrive-Sync/Programming/Biology/ordermanager.py', '.'), ('C:/Users/vojte/IDrive-Sync/Programming/Biology/primer.py', '.'), ('C:/Users/vojte/IDrive-Sync/Programming/Biology/resource.py', '.'), ('C:/Users/vojte/IDrive-Sync/Programming/Biology/ui.py', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
