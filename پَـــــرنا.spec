# -*- mode: python ; coding: utf-8 -*-

hiddenimports = [
    'jdatetime', 'openpyxl', 'requests',
    'data_bridge', 'config', 'main',
    'core', 'core.browser_manager',
    'extractors', 'extractors.text_extractor',
    'extractors.pdf_extractor', 'extractors.image_ocr',
    'handlers', 'handlers.tracker', 'handlers.iframe_handlers',
    'handlers.file_menu', 'handlers.letter_operations',
    'processor', 'processor.processor',
    'utils', 'utils.helpers', 'utils.result_saver', 'utils.json_storage',
    'utils.stop_control', 'utils.progress_control',
    'ai', 'ai.ai_service', 'ai.runtime_setup',
    'selenium.webdriver.chrome.webdriver',
]

datas = [('icon.ico', '.'), ('ocr', 'ocr')]
binaries = []

a = Analysis(
    ['PyQt.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='پَـــــرنا',                
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                       
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                    
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
