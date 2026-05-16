"""
PyInstaller 打包配置文件
"""
import sys
import os

block_cipher = None

if getattr(sys, 'frozen', False):
    root_dir = os.path.dirname(sys.executable)
else:
    root_dir = os.getcwd()

a = Analysis(
    ['run.py'],
    pathex=[root_dir],
    binaries=[],
    datas=[
        ('app/templates', 'app/templates'),
        ('app/static', 'app/static'),
    ],
    hiddenimports=[
        'fastapi', 'uvicorn', 'sqlalchemy', 'jinja2',
        'openpyxl', 'pandas', 'pydantic', 'pydantic_settings',
        'python_multipart', 'pystray', 'PIL',
        'app.core.config', 'app.models.database',
        'app.api.routes', 'app.services.integrity_service',
    ],
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
    [],
    exclude_binaries=True,
    name='廉政意见智答系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/static/favicon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='廉政意见智答系统',
)
