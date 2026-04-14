"""
DeskGenie production build script.

Steps:
  1. Build the React frontend  (npm run build)
  2. Run PyInstaller           (pyinstaller desktop/desktop.spec --clean)

Output: dist/DeskGenie/DeskGenie.exe  (plus supporting files in the same folder)

Usage (from project root):
    python desktop/build.py
"""

import subprocess
import sys
import os


def main() -> None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    # -----------------------------------------------------------------------
    # Step 1: Build React frontend
    # -----------------------------------------------------------------------
    print('=' * 60)
    print('Step 1/2: Building React frontend...')
    print('=' * 60)
    result = subprocess.run(
        ['npm', 'run', 'build'],
        cwd=os.path.join(project_root, 'frontend'),
        shell=True,   # needed on Windows for npm
    )
    if result.returncode != 0:
        print('\nERROR: Frontend build failed. Aborting.')
        sys.exit(1)
    print('Frontend build complete.\n')

    # -----------------------------------------------------------------------
    # Step 2: PyInstaller
    # -----------------------------------------------------------------------
    print('=' * 60)
    print('Step 2/2: Building desktop exe with PyInstaller...')
    print('=' * 60)
    result = subprocess.run(
        [sys.executable, '-m', 'PyInstaller', 'desktop/desktop.spec', '--clean', '-y'],
        cwd=project_root,
    )
    if result.returncode != 0:
        print('\nERROR: PyInstaller build failed.')
        sys.exit(1)

    exe_path = os.path.join(project_root, 'dist', 'DeskGenie', 'DeskGenie.exe')
    print('\n' + '=' * 60)
    print('Build complete!')
    print(f'Executable: {exe_path}')
    print('=' * 60)


if __name__ == '__main__':
    main()
