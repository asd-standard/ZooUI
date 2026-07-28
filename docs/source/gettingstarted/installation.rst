ZooUI Installation
==================

ZooUI can be installed via pip or conda. Pip is the simplest method; conda
provides tighter control over dependency versions and handles system C libraries
automatically.

System Dependencies (all methods)
---------------------------------

ZooUI requires the following system libraries to be installed:

- **libvips** — the C library for image processing (required)
- **poppler-utils** — for PDF support (optional)
- **qt6-wayland** — native Wayland rendering (optional, Linux only)

pip Install
-----------

Clone the repository and install in editable mode::

    git clone https://github.com/asd-standard/ZooUI.git
    cd ZooUI
    pip install -e .

Install the system C library that pyvips binds to:

  **Debian / Ubuntu**::

      sudo apt install libvips42 poppler-utils

  **Fedora**::

      sudo dnf install vips poppler-utils

  **macOS (Homebrew)**::

      brew install vips poppler

After installation, launch with::

    zooui

or::

    zooui-gui

Or via the module::

    python -m zooui

The application creates its configuration and data directories automatically
on first launch (following the `XDG Base Directory specification`_):

- Config: ``~/.config/zooui/config.json``
- Backups: ``~/.local/share/zooui/backups/``
- Tile cache: ``~/.cache/zooui/tilestore/``
- SVG cache: ``~/.cache/zooui/svg/``
- Logs: ``~/.local/state/zooui/logs/``

.. _XDG Base Directory specification: https://specifications.freedesktop.org/basedir-spec/latest/

conda Install
-------------

Create and activate a conda environment::

    conda create -n zooui python=3.12
    conda activate zooui

Install core Python dependencies from default channels::

    conda install pyside6=6.7.2 pillow=12.0.0

Install system-level packages from conda-forge::

    conda install -c conda-forge pyvips=3.0.0 libvips poppler=24.12.0

Optional Wayland support::

    conda install -c conda-forge qt6-wayland=6.7.2

Then install ZooUI from the source checkout (editable install)::

    pip install -e /path/to/zooui

Launch with::

    zooui

From Source
-----------

Clone the repository and install in editable mode::

    git clone https://github.com/asd-standard/ZooUI.git
    cd ZooUI
    pip install -e .

Install the required system libraries (see System Dependencies above).

To run without installing::

    python main.py

Build the documentation::

    cd docs
    make clean
    make html

Python Dependencies (summary)
-----------------------------

+------------------+--------------------+
| Package          | Version            |
+==================+====================+
| PySide6          | ≥ 6.7              |
+------------------+--------------------+
| Pillow           | ≥ 12.0             |
+------------------+--------------------+
| pyvips           | ≥ 3.0              |
+------------------+--------------------+
| platformdirs     | ≥ 3                |
+------------------+--------------------+

Platform Support
----------------

ZooUI is tested on:

- **Linux** (Debian 13, AArch64) — primary development platform
- **Windows** (Windows 11, WSL) — via PyInstaller standalone executable or WSL
- **macOS** — untested; Qt/PySide6 should work, but native library installation
  paths may differ

Running ZooUI
=============

After installation, launch from the command line::

    zooui
    python -m zooui

If running from a source checkout without pip install, the root ``main.py``
script can be used (it is a thin launcher that delegates to :mod:`zooui.app`)::

    python main.py

The application can also be started via::

    zooui-gui       # same as 'zooui' on Linux, avoids console window on Windows
    python -m zooui # module entry point (pip install only)

ZooUI is not tied to the current working directory — it resolves paths using
XDG standards and packaged data, so it can be launched from any location.
