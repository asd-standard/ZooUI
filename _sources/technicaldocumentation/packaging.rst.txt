Packaging System
================

ZooUI uses modern Python packaging standards (PEP 517 / PEP 660) with
``hatchling`` as the build backend. A single ``pyproject.toml`` defines build
configuration, dependency metadata, and entry points.

Build Configuration
-------------------

.. code:: toml

   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

   [project]
   name = "zooui"
   version = "X.Y.Z"
   requires-python = ">=3.12"
   dependencies = [
       "PySide6>=6.7",
       "Pillow>=12.0",
       "pyvips>=3.0",
       "platformdirs>=3",
   ]

   [project.scripts]
   zooui = "zooui.app:main"

   [project.gui-scripts]
   zooui-gui = "zooui.app:main"

The current release version is |release|.

Entry Points
------------

ZooUI provides three ways to launch the application:

``zooui`` / ``zooui-gui``
   Console-script and gui-script wrappers installed by pip into the user's
   ``PATH``.  Both call ``zooui.app:main()``.  On Windows, ``zooui-gui``
   suppresses the console window.

``python -m zooui``
   Module entry point via ``zooui/__main__.py``::

       import sys
       from zooui.app import main
       sys.exit(main())

``python main.py``
   Source-checkout launcher at the repository root.  A thin shim that imports
   from ``zooui.app``::

       from zooui.app import main

       if __name__ == "__main__":
           main()

The importable entry point lives in :mod:`zooui.app`.  All launch paths
converge on ``zooui.app.main()``.

System Dependency Check
-----------------------

Before any heavy imports (PySide6, pyvips), :func:`~zooui.app._check_system_deps`
verifies that ``libvips`` (the C library) is present and loadable via
:func:`ctypes.CDLL`.  If libvips is missing or broken (e.g., incompatible
conda channel mixing), the application exits with platform-specific install
instructions.

``pdftoppm`` is checked with :func:`shutil.which` and prints a warning only —
PDF viewing is optional.

Package Data
------------

All bundled data (icon, home scene, SVG shapes, test images) lives in
``zooui/data/``.  Because the data directory resides inside the package,
hatchling includes it in the wheel automatically — no ``force-include`` or
``MANIFEST.in`` chicanery is required.

Path Resolution (:mod:`zooui.utils._packaging`)
------------------------------------------------

The function :func:`~zooui.utils._packaging.data_dir` returns the absolute path
to the ``zooui/`` package directory, adapting to three runtime modes:

.. list-table::
   :header-rows: 1

   * - Mode
     - Resolution
     - Returns
   * - Source checkout
     - ``__file__`` relative (``utils/ → zooui/``)
     - ``<project>/zooui/``
   * - Pip install
     - :func:`importlib.resources.files`
     - ``<site-packages>/zooui/``
   * - Frozen (PyInstaller)
     - ``sys._MEIPASS``
     - extraction root

Callers append ``"data"`` to reach bundled resources::

    icon_path = os.path.join(data_dir(), "data", "icon.png")

Since the path resolution is centralized, switching between source, pip, and
frozen builds requires no changes to the rest of the codebase.

XDG Runtime Paths (:mod:`zooui.utils._xdg`)
--------------------------------------------

All writable user data follows the `XDG Base Directory`_ specification via
:mod:`platformdirs`, eliminating the legacy ``~/.zooui/`` dot-directory:

.. list-table::
   :header-rows: 1

   * - Purpose
     - XDG Variable
     - Default Path
   * - Config
     - ``$XDG_CONFIG_HOME``
     - ``~/.config/zooui/config.json``
   * - Backups, color history
     - ``$XDG_DATA_HOME``
     - ``~/.local/share/zooui/``
   * - Tile cache, SVG cache
     - ``$XDG_CACHE_HOME``
     - ``~/.cache/zooui/``
   * - Logs
     - ``$XDG_STATE_HOME``
     - ``~/.local/state/zooui/logs/``

The module :mod:`zooui.utils._xdg` exports purpose-named functions
(``get_config_file()``, ``get_data_dir()``, ``get_cache_dir()``,
``get_state_dir()``, ``get_colorstore_dir()``) so callers never need to
construct XDG paths manually.

Usage Instructions Embedding
----------------------------

The Help > Usage dialog displays RST content from an embedded Python module
(``zooui/resources/_usage_rst.py``) rather than reading a file from ``docs/``.
This ensures the dialog works in pip-installed environments where the
documentation tree is absent.

The embedded copy is kept in sync with the canonical source
(``docs/source/usageinstructions/userinterface.rst``) by the version bump
script (``scripts/bump_version.py``).  Sphinx-specific RST roles (``:kbd:``,
``:file:``, ``:doc:``, ``:ref:``) are automatically converted to standard
docutils markup during the sync via :func:`_sanitize_rst_for_dialog`.

Wheel and sdist
---------------

Build the distribution artifacts::

    python -m build

This produces::

    dist/zooui-0.6.2-py3-none-any.whl
    dist/zooui-0.6.2.tar.gz

The wheel is pure-Python (``py3-none-any``) — Qt binaries come from the
``PySide6`` dependency, not ZooUI itself.

The ``MANIFEST.in`` lists files for the source distribution::

    graft zooui
    include README.md
    include LICENSE
    include pyproject.toml
    global-exclude __pycache__
    global-exclude *.pyc

PyInstaller (Standalone Executable)
-----------------------------------

For standalone Windows builds, the ``packaging/`` directory contains a
PyInstaller workflow including a ``.spec`` file, DLL bundle directory, and
build script.  See ``packaging/README.md`` for details.

Release Workflow
----------------

1. Update ``CHANGELOG.md``
2. Bump version: ``python scripts/bump_version.py patch`` (or ``minor``)
3. Tag: ``python scripts/bump_version.py patch --tag``
4. Build: ``python -m build``
5. Upload: ``twine upload dist/*``

The bump script updates ``zooui/__init__.py``, ``pyproject.toml``,
``zooui/data/home.pzs``, and the embedded usage RST in one step.

.. _XDG Base Directory: https://specifications.freedesktop.org/basedir-spec/latest/
