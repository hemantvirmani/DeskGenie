# PyInstaller spec for DeskGenie desktop app
# Run from the project root:  pyinstaller desktop/desktop.spec --clean

import os
from PyInstaller.utils.hooks import copy_metadata

block_cipher = None
project_root = os.path.abspath(os.path.join(SPECPATH, '..'))

# Packages that call importlib.metadata.version() at import time and need
# their .dist-info folder bundled alongside their code.
_metadata_packages = [
    'imageio',      # required by moviepy
    'moviepy',
    'langchain',
    'langchain_core',
    'langchain_google_genai',
    'langchain_anthropic',
    'langchain_community',
    'langchain_ollama',
    'langchain_huggingface',
    'fastapi',
    'uvicorn',
    'pywebview',
    'pystray',
]

_extra_datas = []
for pkg in _metadata_packages:
    try:
        _extra_datas += copy_metadata(pkg)
    except Exception:
        pass  # skip if package not installed

a = Analysis(
    [os.path.join(project_root, 'desktop', 'app.py')],
    pathex=[project_root],
    binaries=[],
    datas=[
        # React frontend build (must run `npm run build` first)
        (os.path.join(project_root, 'frontend', 'dist'), 'frontend/dist'),
        # Benchmark/data files
        (os.path.join(project_root, 'files'), 'files'),
        # Sample config
        (os.path.join(project_root, 'config.sample.json'), '.'),
        # Package metadata needed by importlib.metadata.version() at runtime
        *_extra_datas,
    ],
    hiddenimports=[
        # pywebview
        'webview',
        'webview.platforms.winforms',
        'webview.platforms.edgechromium',
        # pystray
        'pystray',
        'pystray._win32',
        # uvicorn internals
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        # FastAPI / Starlette
        'fastapi',
        'starlette',
        'starlette.routing',
        'starlette.middleware',
        'starlette.responses',
        # LangChain providers
        'langchain_google_genai',
        'langchain_anthropic',
        'langchain_community',
        'langchain_ollama',
        'langchain_huggingface',
        # Google GenAI
        'google.genai',
        'google.genai.types',
    ],
    hookspath=[],
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
    name='DeskGenie',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # windowed — no console; CLI mode allocates one via AllocConsole()
    icon=None,       # icon is generated at runtime; set a .ico path here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DeskGenie',
)
