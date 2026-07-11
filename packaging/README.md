# ZooUI Windows Packaging

This directory contains everything needed to produce a standalone Windows
executable with [PyInstaller](https://pyinstaller.org/).

> **Important:** The build **must** run on native Windows (CMD, PowerShell,
> or Anaconda Prompt), **not** inside WSL. PyInstaller cannot cross-compile
> Windows `.exe` files from a Linux environment.

## Windows Environment Setup

You need Python 3.12+ available on your Windows host (outside WSL).

### Option A: Miniconda (if you already use conda in WSL)

1. Download and install [Miniconda for Windows 64-bit](https://docs.conda.io/en/latest/miniconda.html#windows-installers)
2. Open **Anaconda Prompt** from the Start Menu
3. Create and activate a build environment:

```cmd
conda create -n zooui-build python=3.12 -y
conda activate zooui-build
pip install PySide6 Pillow pyvips pyinstaller
```

### Option B: Plain Python (lighter, no conda required)

1. Download [Python 3.12 for Windows](https://www.python.org/downloads/) — check "Add Python to PATH" during install
2. Open **Command Prompt** (or PowerShell):

```cmd
pip install PySide6 Pillow pyvips pyinstaller
```

### Project Location

The project directory must be accessible from native Windows. Two common setups:

| Your setup | What to do |
|---|---|
| Project lives in WSL filesystem (`~/Projects/zooui`) | Copy to Windows filesystem: `cp -r ~/Projects/zooui /mnt/c/Users/<you>/` |
| Project already on Windows drive (`/mnt/c/...`) | Already accessible from both — work from the same directory |

## Prerequisites

**Native Windows binaries** — place the following in `packaging/windeps/`:

| File | Source |
|---|---|
| `libvips-42.dll` + all deps | [libvips build-win64-mxe releases](https://github.com/libvips/build-win64-mxe/releases) — download `vips-dev-x64-all-*.zip`, copy **all DLLs from `bin/`** into `windeps/`. |
| `pdftoppm.exe` + Poppler DLLs | [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases) — copy `pdftoppm.exe` and all DLLs from `Library/bin/` into `windeps/`. |

## Quick Build

Open a native Windows terminal from the **project root** and run:

```cmd
packaging\build_windows.bat
```

Or manually:

```cmd
pip install pyinstaller
pyinstaller packaging\zooui.spec --clean --noconfirm
```

Output: `dist\zooui.exe`

## Files

| File | Purpose |
|---|---|
| `zooui.spec` | PyInstaller build recipe (entry point, data, binaries, hidden imports) |
| `hooks/hook-pyvips.py` | Ensures `libvips-42.dll` is found at runtime inside the frozen bundle |
| `build_windows.bat` | One-shot build script (verifies deps, installs PyInstaller, builds) |
| `windeps/` | Directory for native DLLs/EXEs required at build time |

## Size

The output `.exe` is approximately **150–200 MB**, mostly due to Qt6 binaries.

## Runtime Behaviour

- **Config**: `%USERPROFILE%\.zooui\config.json` (auto-created on first launch)
- **Backups**: `%USERPROFILE%\.zooui\backups\`
- **Logs**: `logs/` (relative to working directory)
- **Tilestore**: `%APPDATA%\zooui\tlestore\`

## Troubleshooting

**`libvips-42.dll not found` at runtime:**
Python must call `os.add_dll_directory(sys._MEIPASS)` before `import pyvips`.
This is handled by `hooks/hook-pyvips.py`. If it still fails, check that the
DLL is placed in `windeps/` before building.

**`pdftoppm.exe` not found:**
The PDF converter resolves the path via `sys._MEIPASS` when frozen. Ensure
`pdftoppm.exe` is in `windeps/` before building.

**Antivirus false positive:**
`--onefile` Python executables are occasionally flagged by AV software.
A code signing certificate mitigates this for release builds.
