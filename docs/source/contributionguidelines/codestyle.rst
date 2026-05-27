.. PyZUI code style guidelines file,

Code Style Guidelines
=====================

This document describes the coding conventions, formatting rules, and quality
checks that all contributions to the PyZUI codebase must follow.

Code Style
----------

The project follows these code style conventions:

**Indentation:**

- Use 4 spaces for indentation (no tabs)

**Line Length:**

- Keep lines reasonably short, preferably under 80-100 characters
- Use line continuation with backslash (``\``) or parentheses for long lines

**Imports:**

- Group imports in the following order:

  1. Standard library imports
  2. Third-party imports (PySide6, PIL, etc.)
  3. Local application imports

- Example:

  .. code-block:: python

      import math
      from threading import Thread
      from typing import Optional, Tuple, Any

      from PIL import Image
      from PySide6 import QtCore, QtGui

      from .tileprovider import TileProvider
      from .. import tilestore as TileStore

**Blank Lines:**

- Two blank lines between top-level definitions (classes, functions)
- One blank line between method definitions within a class
- Use blank lines sparingly within functions to separate logical sections

Naming Conventions
------------------

**Modules:**

- Use concatenated lowercase words with no separators (e.g., ``tileprovider.py``, ``dynamictileprovider.py``, ``converterrunner.py``)

**Classes:**

- Use PascalCase (e.g., ``TileManager``, ``PhysicalObject``, ``StaticTileProvider``)

**Functions and Methods:**

- Use snake_case (e.g., ``get_tile``, ``load_tile``, ``cut_tile``)
- Private methods use double underscore prefix (e.g., ``__damp``, ``__displacement``)
- Protected methods use single underscore prefix (e.g., ``_load``, ``_scanchunk``)

**Variables:**

- Use snake_case (e.g., ``tile_id``, ``media_id``, ``tile_path``)
- Private instance variables use underscore prefix (e.g., ``self._x``, ``self._progress``)
- Module-level private variables use double underscore (e.g., ``__tilecache``)

**Constants:**

- Use UPPER_SNAKE_CASE for constants (e.g., ``damping_factor`` is an exception
  as a class attribute)

**Parameters:**

- Use descriptive names that indicate purpose (e.g., ``tile_id``, ``media_id``,
  ``filename``, ``bbox``)

Formatting Requirements
-----------------------

File Headers
^^^^^^^^^^^^

All source files in ``./pyzui`` should include the GPL license header:

.. code-block:: python

     ## PyZUI - Python Zooming User Interface
    ## Copyright (C) 2009  David Roberts <d@vidr.cc>
    ##
    ## This program is free software; you can redistribute it and/or
    ## modify it under the terms of the GNU General Public License
    ## ...

Module Docstrings
^^^^^^^^^^^^^^^^^

Each module should have a docstring at the top (after the license header)
describing its purpose:

.. code-block:: python

    """A threaded media converter (abstract base class)."""

Comments
^^^^^^^^

- Use ``##`` for inline comments explaining formulas or complex logic
- Use ``#`` for standard code comments
- Write comments that explain *why*, not *what*

Code Quality Checks
-------------------

All contributions must pass the project's automated code quality checks
before submission. These tools catch bugs, enforce style, and verify type
correctness.

Ruff (Linter + Formatter)
^^^^^^^^^^^^^^^^^^^^^^^^^^

Ruff enforces code style, import ordering, and catches common bugs. It
replaces multiple tools (flake8, isort, pyupgrade, etc.) in a single
fast pass.

**Run the linter:**

.. code-block:: bash

   # Check for issues (source code only, test/ and scripts/ excluded)
   conda run -n <env-name> ruff check

   # Auto-fix safe issues
   conda run -n <env-name> ruff check --fix

   # Auto-fix all issues (including unsafe)
   conda run -n <env-name> ruff check --fix --unsafe-fixes

**Run the formatter:**

.. code-block:: bash

   # Format code
   conda run -n <env-name> ruff format

   # Check formatting without applying
   conda run -n <env-name> ruff format --check

**Configuration**: ``pyproject.toml`` under the ``[tool.ruff]`` section.
Enabled rules include pycodestyle (E/W), Pyflakes (F), import sorting
(I), pep8-naming (N), pyupgrade (UP), flake8-bugbear (B),
comprehensions (C4), simplify (SIM), Ruff-specific (RUF), and
performance (PERF). Line length is set to 120 characters. The
``test/`` and ``scripts/`` directories are excluded.

Mypy (Type Checker)
^^^^^^^^^^^^^^^^^^^

Mypy verifies that type annotations are correct and consistent. The
codebase uses gradual typing (``disallow_untyped_defs = false``) with
``check_untyped_defs = true`` to check function bodies even without
complete signatures.

**Run the type checker:**

.. code-block:: bash

   # Check all source files
   conda run -n <env-name> mypy --explicit-package-bases --follow-imports=skip pyzui/

   # Check a single file
   conda run -n <env-name> mypy pyzui/path/to/file.py

**Note**: Mypy is run manually, not in pre-commit. Per-file overrides in
``pyproject.toml`` suppress known false positives from name-mangling,
class aliases, and third-party stubs (PySide6, pyvips).

**Configuration**: ``pyproject.toml`` under the ``[tool.mypy]`` section.

Pre-Commit (Automated Hooks)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pre-commit runs ruff and ruff-format automatically before every commit,
preventing style issues from entering the repository.

**Setup (one-time, after ``pre-commit install`` above):**

   The ``pre-commit install`` command in step 3 registers the hooks with
   your local ``.git`` directory. They will run automatically on every
   ``git commit``.

**Run manually on all files:**

.. code-block:: bash

   conda run -n <env-name> pre-commit run --all-files

**Configuration**: ``.pre-commit-config.yaml``. Current hooks are ruff
(checks + autofix) and ruff-format.

Coding Conventions
------------------

The following coding conventions must be followed for all contributions to the
``./pyzui`` codebase and the ``./test`` codebase.

Docstring Format
^^^^^^^^^^^^^^^^

All classes, methods, functions, and properties must have docstrings following
the project's established format. The docstring format includes:

**For Classes:**

.. code-block:: python

    class ClassName:
        """
        Constructor :
            ClassName(param1, param2)
        Parameters :
            param1 : type
            param2 : type

        ClassName(param1, param2) --> ReturnType

        Description of what the class does and its purpose.

        Additional notes, implementation details, or ASCII diagrams
        as needed.
        """

**For Methods and Functions:**

.. code-block:: python

    def method_name(self, param1: type, param2: type) -> ReturnType:
        """
        Method :
            ClassName.method_name(param1, param2)
        Parameters :
            param1 : type
            param2 : type

        ClassName.method_name(param1, param2) --> ReturnType

        Description of what the method does.

        Additional implementation notes if needed.
        """

**For Properties:**

.. code-block:: python

    @property
    def property_name(self) -> type:
        """
        Property :
            ClassName.property_name
        Parameters :
            None

        ClassName.property_name --> type

        Description of what the property represents.
        """

**For Module-Level Functions:**

.. code-block:: python

    def function_name(param1: type, param2: type) -> ReturnType:
        """
        Function :
            function_name(param1, param2)
        Parameters :
            param1 : type
                - Description of parameter (optional)
            param2 : type
                - Description of parameter (optional)

        function_name(param1, param2) --> ReturnType

        Description of what the function does.
        """

Type Hints
^^^^^^^^^^

**All methods, functions, and class attributes must include type hints.**

- Use standard Python typing module for complex types:

  .. code-block:: python

      from typing import Optional, Tuple, Any, List, Dict

- Type hints are required for:

  - All function/method parameters
  - All function/method return types
  - Class attributes where appropriate

- Examples:

  .. code-block:: python

      def method(self, param: str, value: int) -> bool:
          ...

      def get_data(self) -> Tuple[int, int, int]:
          ...

      def process(self, items: Optional[List[str]] = None) -> None:
          ...

Docstring and Type Hint Requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Every class, method, function, and property - whether public or private -
must have:**

1. A complete docstring following the format above
2. Type hints for all parameters and return values

This applies to:

- Public methods (e.g., ``get_tile``)
- Private methods (e.g., ``__damp``, ``_load``)
- Properties (e.g., ``moving``, ``size``)
- Module-level functions (e.g., ``init``, ``merged``)
- Class definitions

Variable Type Annotations
^^^^^^^^^^^^^^^^^^^^^^^^^

**All variables must include type annotations.**

This applies to:
- Module-level variables (global to the module)
- Class attributes (instance variables)
- Local variables when their type is not obvious from context

**When to use Optional:**

Use ``Optional[Type]`` when a variable can legitimately be ``None``:
- Variables initialized as ``None`` that will be assigned later
- Function parameters with default value ``None``
- Return values that may be ``None`` to indicate absence of result

**Example from tilemanager.py (lines 44-53):**

.. code-block:: python

    # Module-level variables with Optional type annotations
    __tilecache: Optional["TileCache"] = None
    __temptilecache: Optional["TileCache"] = None
    __tp_static: Optional["StaticTileProvider"] = None
    __logger: Optional["Logger"] = None

    # Non-optional variables with specific types
    __tp_dynamic: Dict[str, "FernTileProvider"] = {}
    __cleanup_enabled: bool = False
    __cleanup_max_age_days: int = 3
    __cleanup_executed: bool = False

**When to use Any:**

Use ``Any`` sparingly and only when:
- The variable can legitimately be any type (e.g., accepts multiple image formats)
- Working with dynamically typed data or third-party libraries
- As a temporary measure during refactoring (with a ``# TODO`` comment)

**Avoid ``Any`` when:**
- The type is known or can be inferred
- Using union types (``Union[Type1, Type2]``) would be more precise
- The variable has a specific, known type

**Example from tile.py (line 43):**

.. code-block:: python

    # Accepts any image type (PIL Image, QImage, ImageQt, etc.)
    def __init__(self, image: Any) -> None:  # type: ignore[no-untyped-def]
        """
        Constructor:
            Tile(image)
        Parameters:
            image : Any
        """
        if image.__class__ is ImageQt or type(image) is QtGui.QImage:
            self.__image = image
        elif isinstance(image, Image.Image):
            self.__image = ImageQt.ImageQt(image)

**Instance Variable Type Annotations:**

Annotate instance variables in ``__init__`` method:

.. code-block:: python

    # From mainwindow.py (lines 72-76)
    def __init__(self):
        self.__logger: "Logger" = get_logger("MainWindow")
        self.__prev_dir: str = ''
        self.__action: Dict[ActionKey, QtGui.QAction] = {}
        self.__menu: Dict[MenuKey, QtWidgets.QMenu] = {}

**Guidelines:**

1. **Annotate at declaration**: Add type annotations when variables are declared
2. **Be specific**: Use the most precise type possible (avoid ``Any`` when possible)
3. **Match initialization**: Ensure initial value matches the type annotation
4. **Use forward references**: For types imported under TYPE_CHECKING, use string literals
5. **Document with comments**: Use comments to explain complex type annotations if needed

TYPE_CHECKING for Type-Only Imports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When type annotations require imports that would create circular dependencies
or are only needed for type checking (not at runtime), use the ``TYPE_CHECKING``
constant with forward references:

1. Import ``TYPE_CHECKING`` from the ``typing`` module
2. Place type-only imports under ``if TYPE_CHECKING:`` blocks
3. Use forward references (quoted type names) in annotations
4. Keep runtime imports outside the ``TYPE_CHECKING`` block

**When to use TYPE_CHECKING vs forward references:**

- Use ``TYPE_CHECKING`` imports + forward references for:
  * Types from modules that would cause circular imports
  * External library types only used in annotations
  * Cross-module class references

- Use simple forward references (without TYPE_CHECKING) for:
  * Self-references within the same class definition

**Example from the codebase:**

.. code-block:: python

    # File: pyzui/tilesystem/tileproviders/dynamictileprovider.py
    from typing import TYPE_CHECKING, Optional, Tuple, Any
    from PySide6 import QtGui

    if TYPE_CHECKING:
        from PySide6.QtGui import QImage
        from .tileprovider import TileID

    TileID = Tuple[str, int, int, int]

    class DynamicTileProvider:
        def _load(self, tile_id: TileID) -> Optional['QImage']:
            """
            Load a tile, returning QImage or None.

            Uses forward reference 'QImage' in annotation while
            QImage import is under TYPE_CHECKING for IDE support.
            """
            # Runtime code uses QtGui.QImage, not the TYPE_CHECKING import
            return QtGui.QImage(filename) if os.path.exists(filename) else None

**Guidelines:**

1. **TYPE_CHECKING block placement**: Immediately after imports, before any code
2. **Indentation**: 4 spaces for the ``if TYPE_CHECKING:`` block
3. **Import grouping**: Group related TYPE_CHECKING imports logically
4. **Forward references**: Always use quotes for types imported under TYPE_CHECKING
5. **Runtime code**: Use fully qualified names (e.g., ``QtGui.QImage``) not TYPE_CHECKING imports


QPainter and Qt Paint Events
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When overriding ``paintEvent`` on any ``QWidget`` subclass (including
dialog helpers that monkey-patch ``paintEvent`` on a bare ``QWidget``),
the QPainter **must** be explicitly ended.

.. code-block:: python

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), color)
        painter.end()  # REQUIRED — see below

**Why this matters:**

An unended QPainter left active on its paint device keeps the underlying
C++ paint engine resources alive.  After the application has run for
hours or days, accumulated paint events with dangling C++ painter state
corrupt Qt's internal paint engine.  The next paint event that
constructs a new QPainter — including events triggered by simple user
actions like opening a dialog via a keyboard shortcut — can then
trigger a ``SIGSEGV`` (segmentation fault) crash with no Python
traceback.

**Rules:**

1. Every ``paintEvent`` override must call ``painter.end()`` before
   returning, including every ``return`` statement inside the function.

2. For simple paint events, place ``painter.end()`` as the last
   statement.

3. For paint events with multiple exit points, either:

   a. Call ``painter.end()`` before each ``return``, or
   b. Wrap the body in ``try`` / ``finally``::

          def paintEvent(self, event):
              painter = QPainter(self)
              try:
                  ...
              finally:
                  painter.end()

4. **Do not** rely on Python's reference counting or the QPainter
   destructor — at process exit the destructor may run after Qt's C++
   internals have already been partially torn down, which is the exact
   scenario that triggers the segfault.

**Affected code (fixed in 2026-05):**

- ``stringinputdialog.py`` — color-square ``paintEvent``
- ``modifystringdialog.py`` — color-square ``paintEvent``
- ``modifysvginputdialog.py`` — color-square **and** SVG preview ``paintEvent``
- ``svgpickerinputdialog.py`` — color-square **and** SVG button ``paintEvent``
