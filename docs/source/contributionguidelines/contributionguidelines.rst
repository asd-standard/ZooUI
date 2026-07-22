.. ZooUI contribution instruction file,

Contribution Guidelines
=======================

**Note:** Before reading this section, it is recommended to read the
:doc:`Code Style Guidelines <codestyle>` first, which covers coding conventions,
naming rules, type hints, docstring format, and code quality checks that all
contributions must follow.

Welcome to the ZooUI contribution guidelines! We appreciate your interest in
contributing to this project.

Project Expectations
--------------------

**Important Notice**: This is an open-source project maintained on a voluntary
basis. Please do not expect:

- Bug fixing on demand
- Feature requests to be implemented by maintainers

However, contributions are welcome at any level, including:

- Feature implementations
- Bug fixes
- Test improvements
- Documentation enhancements

All contributions will be reviewed as soon as possible. Forking the repository
is encouraged for any purpose that respect the GNU General Public License v3 terms.

Getting Started with Contributing
---------------------------------

1. **Fork the Repository**

   Start by forking the ZooUI repository on GitHub to your own account.

2. **Clone Your Fork**

   .. code-block:: bash

      git clone https://github.com/YOUR_USERNAME/pyzui.git
      cd zooui

3. **Set Up the Development Environment**

   Follow the installation instructions in the :doc:`../gettingstarted/installation` section:

   - Install Miniconda and create a Python 3.12.12 environment:

     .. code-block:: bash

        conda create -n <env-name> python=3.12.12
        conda activate <env-name>

   - Install core dependencies from the default Anaconda channel:

     .. code-block:: bash

        conda install pyside6=6.7.2 pillow=12.0.0 pyvips=3.0.0

   - Install additional dependencies from conda-forge:

     .. code-block:: bash

        conda install -c conda-forge poppler=24.12.0

   - Install testing dependencies:

     .. code-block:: bash

        conda install pytest

    - Install linting and type-checking tools from conda-forge:

      .. code-block:: bash

         conda install -c conda-forge ruff mypy pre-commit

    - Install the pre-commit hooks (one-time setup):

      .. code-block:: bash

         pre-commit install

4. **Create a Feature Branch**

   .. code-block:: bash

      git checkout -b feature/your-feature-name

   The type of feature you are implementing determines how you should structure
   your code and tests. There are three main scenarios:

   **Scenario A: Adding a New Class or Method to an Existing Module**

   When adding a new class or method to an existing ``.py`` module (e.g., adding
   a new ``CacheTileProvider`` class to ``tileproviders/`` or adding a new
   ``merge_tiles()`` method to ``tile.py``):

   - Locate the corresponding test file that already exists for the module
     (e.g., ``test/unittest/tilesystem/test_tile.py``)
   - Add new test methods to the existing test class, or create a new test class
     within the same test file if testing a new class
   - Follow the existing test structure in that file

   *Guidelines for adding test methods:*

   .. code-block:: python

       # In test/unittest/tilesystem/test_tile.py
       # If adding a new method 'merge()' to the Tile class:

       class TestTile:
           """Existing test class for Tile"""

           # ... existing tests ...

           def test_merge_two_tiles(self):
               """
               Scenario: Merge two tiles horizontally

               Given two tiles of equal height
               When merge is called with horizontal orientation
               Then a new tile with combined width is returned
               """
               # Test implementation

           def test_merge_with_none_tile(self):
               """
               Scenario: Merge with None tile

               Given a valid tile and a None value
               When merge is called
               Then it should handle the None gracefully
               """
               # Test implementation

       # If adding a new class 'TileBatch' to tile.py:

       class TestTileBatch:
           """
           Feature: Tile Batch Operations

           The TileBatch class manages collections of tiles for batch processing.
           """

           def test_init(self):
               """
               Scenario: Initialize a tile batch

               Given a list of tiles
               When a TileBatch is created
               Then it should store all tiles
               """
               # Test implementation

   **Scenario B: Modifying an Existing Class or Method**

   When modifying the behavior of an existing class or method (e.g., changing
   how ``Tile.crop()`` handles edge cases, or adding parameters to an existing
   method):

   - First, run the existing tests to understand current expected behavior
   - Determine if existing tests need modification:

     * **Modify existing tests** when the expected behavior changes (e.g., a
       method now returns a different type, or handles inputs differently)
     * **Add new tests** when you're adding new functionality without changing
       existing behavior (e.g., adding optional parameters with default values)
     * **Do both** when the modification changes some behaviors and adds new ones

   *Guidelines for modifying existing test methods:*

   .. code-block:: python

       # BEFORE: Original test for crop method
       def test_crop(self):
           """
           Scenario: Crop a tile to smaller region
           ...
           """
           t = Tile(qimage)
           cropped = t.crop((10, 10, 50, 50))
           assert cropped.size == (40, 40)

       # AFTER: If crop() now accepts an optional 'mode' parameter
       # Update docstring to reflect new behavior
       def test_crop(self):
           """
           Scenario: Crop a tile to smaller region with default mode

           Given a tile with size 100x100
           When cropping to region (10, 10, 50, 50) without specifying mode
           Then the default mode should be used
           And the new tile size should be 40x40
           """
           t = Tile(qimage)
           cropped = t.crop((10, 10, 50, 50))  # Uses default mode
           assert cropped.size == (40, 40)

       # ADD: New test for the new parameter
       def test_crop_with_clamp_mode(self):
           """
           Scenario: Crop with clamp mode enabled

           Given a tile with size 100x100
           When cropping with mode='clamp'
           Then pixels outside bounds should be clamped
           """
           t = Tile(qimage)
           cropped = t.crop((10, 10, 150, 150), mode='clamp')
           assert cropped.size == (90, 90)  # Clamped to available size

   *When to modify vs. add tests:*

   +----------------------------------+----------------------------------+
   | Modify Existing Tests            | Add New Tests                    |
   +==================================+==================================+
   | Return type changes              | New optional parameters with     |
   |                                  | default values                   |
   +----------------------------------+----------------------------------+
   | Method signature changes         | New edge case handling           |
   | (required parameters)            |                                  |
   +----------------------------------+----------------------------------+
   | Exception types change           | Additional validation added      |
   +----------------------------------+----------------------------------+
   | Core algorithm changes affecting | Performance optimizations        |
   | output                           | (behavior unchanged)             |
   +----------------------------------+----------------------------------+

   **Scenario C: Creating a Completely New Module**

   When creating a new ``.py`` module (e.g., ``zooui/tilesystem/tileoptimizer.py``):

   - Create a corresponding test file mirroring the source structure
   - Include all necessary imports and fixtures
   - Create test classes for each class in the module
   - Ensure comprehensive coverage from the start

   *Guidelines for creating a new test module:*

   .. code-block:: python

       # File: test/unittest/tilesystem/test_tileoptimizer.py

       """
       Unit Tests: Tile Optimizer
       ==========================

       This module contains unit tests for the TileOptimizer class
       which handles tile compression and quality optimization.
       """
       import pytest
       from unittest.mock import Mock, patch, MagicMock
       from PIL import Image

       from zooui.tilesystem.tileoptimizer import TileOptimizer, OptimizationResult


       class TestTileOptimizer:
           """
           Feature: Tile Optimization

           The TileOptimizer class provides methods for optimizing tile
           storage size while maintaining visual quality.
           """

           def test_init(self):
               """
               Scenario: Initialize tile optimizer with default settings

               Given no parameters
               When a TileOptimizer is instantiated
               Then it should use default quality settings
               """
               optimizer = TileOptimizer()
               assert optimizer.quality == 85
               assert optimizer.format == 'jpg'

           def test_init_with_custom_quality(self):
               """
               Scenario: Initialize with custom quality

               Given a quality parameter of 95
               When a TileOptimizer is instantiated
               Then it should use the specified quality
               """
               optimizer = TileOptimizer(quality=95)
               assert optimizer.quality == 95

           def test_optimize_reduces_size(self):
               """
               Scenario: Optimize a tile reduces file size

               Given a tile with unoptimized data
               When optimize is called
               Then the resulting tile should have smaller size
               """
               # Test implementation

           def test_optimize_invalid_input(self):
               """
               Scenario: Handle invalid input gracefully

               Given None as input
               When optimize is called
               Then it should raise ValueError
               """
               optimizer = TileOptimizer()
               with pytest.raises(ValueError):
                   optimizer.optimize(None)


       class TestOptimizationResult:
           """
           Feature: Optimization Result Container

           The OptimizationResult class holds the outcome of tile optimization
           including the optimized tile and metadata.
           """

           def test_init(self):
               """
               Scenario: Create optimization result

               Given an optimized tile and metadata
               When an OptimizationResult is created
               Then it should store all provided data
               """
               # Test implementation

   *Checklist for new test modules:*

   - [ ] File path mirrors source path (``zooui/x/y.py`` -> ``test/unittest/x/test_y.py``)
   - [ ] Module docstring describes what is being tested
   - [ ] All necessary imports are included
   - [ ] Test class for each public class in the source module
   - [ ] ``test_init`` method for each class testing instantiation
   - [ ] Tests for all public methods
   - [ ] Tests for error conditions and edge cases
   - [ ] BDD-style docstrings for all test classes and methods
   - [ ] Mocks used appropriately for external dependencies

5. **Make Your Changes**

   Follow the coding conventions in the :doc:`Code Style Guidelines <codestyle>`.

6. **Run Tests**

   Ensure all tests pass before submitting:

   .. code-block:: bash

      pytest test/unittest/
      pytest test/integrationtest/

7. **Submit a Pull Request**

   Push your changes and create a pull request against the main branch.

Testing Requirements
--------------------

All contributions must include appropriate tests. The project uses pytest as
the testing framework.

Test Structure
^^^^^^^^^^^^^^

Tests are organized in two directories:

- ``test/unittest/``: Unit tests for individual components
- ``test/integrationtest/``: Integration tests for component interactions

The test directory structure mirrors the source code structure:

::

    test/
    ├── unittest/
    │   ├── conftest.py
    │   ├── tilesystem/
    │   │   ├── test_tile.py
    │   │   ├── test_tilemanager.py
    │   │   ├── tileproviders/
    │   │   │   ├── test_statictileprovider.py
    │   │   │   └── ...
    │   │   └── ...
    │   ├── objects/
    │   │   └── ...
    │   └── ...
    └── integrationtest/
        ├── test_tiling_pipeline.py
        └── ...

Test Docstring Format
^^^^^^^^^^^^^^^^^^^^^

Tests should use BDD-style (Behavior-Driven Development) docstrings:

**For Test Classes:**

.. code-block:: python

    class TestClassName:
        """
        Feature: Feature Name

        Description of what feature or component is being tested.
        """

**For Test Methods:**

.. code-block:: python

    def test_method_name(self):
        """
        Scenario: Description of the scenario

        Given some initial condition
        When some action is performed
        Then some expected result occurs
        And additional assertions if needed
        """

**Example:**

.. code-block:: python

    class TestTile:
        """
        Feature: Tile Image Operations

        The Tile class wraps image data (PIL or QImage) and provides operations
        for manipulating tiles including cropping, resizing, saving, and rendering.
        """

        def test_crop(self):
            """
            Scenario: Crop a tile to smaller region

            Given a tile with size 100x100
            When cropping to region (10, 10, 50, 50)
            Then a new Tile instance should be returned
            And the new tile size should be 40x40
            """
            qimage = QtGui.QImage(100, 100, QtGui.QImage.Format_RGB32)
            t = Tile(qimage)
            cropped = t.crop((10, 10, 50, 50))
            assert isinstance(cropped, Tile)
            assert cropped.size == (40, 40)

Testing Routine for Development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When developing, follow this testing routine:

1. **Before Making Changes:**

   Run the existing test suite to ensure everything passes:

   .. code-block:: bash

      pytest test/unittest/ -v
      pytest test/integrationtest/ -v

2. **During Development:**

   Run specific tests related to your changes:

   .. code-block:: bash

      # Run tests for a specific module
      pytest test/unittest/tilesystem/test_tile.py -v

      # Run tests matching a pattern
      pytest -k "test_crop" -v

3. **Before Submitting:**

   Run the complete test suite:

   .. code-block:: bash

      pytest test/ -v

   Ensure there are no failures or errors.

Test Requirements for Contributions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**For Bug Fixes:**

- Add a test that reproduces the bug (should fail before the fix)
- Ensure the test passes after the fix

**For New Features:**

- Add unit tests covering the new functionality
- Add integration tests if the feature interacts with multiple components
- Aim for comprehensive coverage of edge cases

**For Code Refactoring:**

- Ensure existing tests continue to pass
- Add tests for any previously untested behavior discovered during refactoring

Test Guidelines
^^^^^^^^^^^^^^^

1. **Use Mocking Appropriately:**

   - Use ``unittest.mock`` for isolating components
   - Mock external dependencies (file system, network, etc.)

   .. code-block:: python

       from unittest.mock import Mock, patch, MagicMock

       @patch('zooui.tilesystem.tileproviders.statictileprovider.Image.open')
       def test_load_success(self, mock_open):
           ...

2. **Use Fixtures:**

   - Define fixtures in ``conftest.py`` for shared test resources
   - Use pytest's built-in fixtures (``tmp_path``, ``tmpdir``, etc.)

   .. code-block:: python

       @pytest.fixture
       def temp_tilestore(tmp_path):
           """
           Fixture: Isolated Temporary Tile Store
           """
           ...

3. **Test Naming:**

   - Use descriptive names: ``test_<what>_<condition>_<expected>``
   - Examples: ``test_load_exceeds_maxtilelevel``, ``test_crop``,
     ``test_init_with_pil_image``

4. **Assertions:**

   - Use pytest assertions (``assert``) rather than unittest methods
   - Include descriptive messages for complex assertions

   .. code-block:: python

       assert result is None, "Should return None for invalid tilelevel"

Guidelines for Contributing to the Test Codebase
------------------------------------------------

When contributing tests, please follow these guidelines:

1. **Mirror the Source Structure:**

   Place tests in a location that mirrors the source code structure:

   - Source: ``zooui/tilesystem/tile.py``
   - Test: ``test/unittest/tilesystem/test_tile.py``

2. **One Test Class per Feature/Class:**

   Each test file should focus on testing a specific module or class.

3. **Test Independence:**

   - Tests should be independent and not rely on execution order
   - Use fixtures for setup and teardown
   - Clean up any created resources (files, directories, etc.)

4. **Test Both Success and Failure Cases:**

   - Test happy paths (expected usage)
   - Test error conditions and edge cases
   - Test boundary conditions

5. **Keep Tests Fast:**

   - Mock expensive operations (I/O, network, etc.)
   - Use small test data

6. **Document Test Purpose:**

   - Use BDD-style docstrings as shown above
   - Make the test's intent clear from its name and documentation

7. **Integration Tests:**

   For integration tests, document the components being tested and their
   interactions:

   .. code-block:: python

       class TestTilingPipelineEndToEnd:
           """
           Feature: Complete Tiling Pipeline

           The tiling system converts large images into pyramidal tile structures
           that enable efficient zooming and panning. This test suite validates
           the complete pipeline from image input to tile retrieval.
            """

Versioning and Release Workflow
--------------------------------

ZooUI uses **Semantic Versioning** (SemVer) in ``MAJOR.MINOR.PATCH`` format.
The single source of truth for the version is ``zooui/__init__.py`` →
``__version__``.

**Version bump criteria:**

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - **PATCH** (0.4.0 → 0.4.1)
     - **MINOR** (0.4.0 → 0.5.0)
   * - Bug fixes
     - Major new features (new modules)
   * - Minor new features (no new modules)
     - New capabilities (new modules)
   * - Internal refactors
     - New architectures (e.g. process pools)
   * - Type annotations and code quality
     - New subsystems
   * - Documentation improvements
     -
   * - Minor UI elements and enhancements
     -

A **minor feature** extends behaviour within existing modules (e.g. adding
methods to an existing class, new menu items, keyboard shortcuts). A **major
feature** introduces new Python modules or packages under ``zooui/`` and
requires significant new infrastructure.

**MAJOR** (0.x.y → 1.0.0): Breaking changes to config format, data file format,
or public API.

**Release workflow:**

1. Update ``CHANGELOG.md``: move entries from ``[Unreleased]`` to a new version
   heading with the release date

2. Run the bump script. This updates **three** locations automatically:

   - ``zooui/__init__.py`` — the canonical ``__version__`` string
   - ``data/home.pzs`` — the version text displayed in the default scene

   .. code-block:: bash

      python scripts/bump_version.py patch   # for fixes
      python scripts/bump_version.py minor   # for features
      python scripts/bump_version.py major   # for breaking changes

3. Use ``--tag`` to also create an annotated git tag in one step:

   .. code-block:: bash

      python scripts/bump_version.py minor --tag

4. Push the tag upstream:

   .. code-block:: bash

      git push origin vX.Y.Z

**Keep ``CHANGELOG.md`` updated** as you work — add entries under
``[Unreleased]`` at the top of the file following the
`Keep a Changelog <https://keepachangelog.com/en/1.1.0/>`_ format. This
ensures the changelog is ready when it is time to cut a release.

Submitting Your Contribution
----------------------------

1. Ensure all tests pass (``pytest test/unittest/``)
2. Ensure ruff reports no issues (``ruff check``)
3. Ensure ruff-format reports no changes (``ruff format --check``)
4. Ensure your code follows the coding conventions in the :doc:`Code Style Guidelines <codestyle>`
5. Ensure all new code has docstrings and type hints
6. Update ``CHANGELOG.md`` under ``[Unreleased]`` with your changes
7. Create a pull request with a clear description of your changes
8. Be responsive to feedback during the review process

Thank you for contributing to ZooUI!

Contributing to Documentation
-----------------------------

Documentation is a critical part of ZooUI that helps users understand and
effectively use the software. This section covers guidelines for contributing
to the Sphinx-based documentation in the ``./docs/`` directory.

**Documentation Structure:**

- **Source files**: RST (``.rst``) files in ``docs/source/`` directory
- **Configuration**: ``docs/source/conf.py`` for Sphinx settings
- **Build output**: HTML files in ``docs/build/html/``
- **Auto-generated API docs**: Created from Python docstrings using Sphinx extensions

**Sphinx Extensions Used:**

ZooUI documentation uses the following Sphinx extensions:

- ``sphinx.ext.autodoc``: Automatically documents Python docstrings
- ``sphinx.ext.autosummary``: Creates summary tables for modules
- ``sphinx.ext.napoleon``: Supports Google/NumPy-style docstrings
- ``sphinx.ext.viewcode``: Adds links to highlighted source code

These extensions automatically generate API documentation from Python docstrings
following the formats described in the :doc:`Code Style Guidelines <codestyle>`.

Documentation Quality Standards
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Clarity and Completeness:**

- Write for the target audience (users, developers, or contributors)
- Cover all relevant aspects without assuming prior knowledge
- Use simple, direct language avoiding unnecessary jargon
- Include practical examples for complex concepts

**Examples and Use Cases:**

- Provide real-world examples from the ZooUI codebase
- Include complete, tested code snippets
- Document edge cases and common pitfalls
- Show before/after comparisons when demonstrating improvements

**Consistency with Existing Documentation:**

- Follow established patterns in existing documentation files
- Use consistent terminology (e.g., "tile" not "image chunk")
- Maintain the same heading hierarchy and formatting style
- Cross-reference related documentation sections appropriately

**Proper RST Formatting:**

- Use RST directives correctly (``.. code-block::``, ``.. note::``, ``.. warning::``)
- Ensure heading underline lengths match title length exactly
- Use consistent indentation (3 spaces for directives, 4 spaces for code blocks)
- Include descriptive alt text for images and diagrams
- Use backticks for inline code references

**Accuracy and Verification:**

- Ensure documentation matches actual code behavior
- Test code examples before including them
- Verify command-line instructions work as described
- Update documentation when related code changes

**Accessibility and Navigation:**

- Use meaningful section titles that describe content
- Include table of contents for longer documents
- Add cross-references (``:doc:``, ``:ref:``) to related content
- Ensure documentation builds without warnings

Documentation Workflow
^^^^^^^^^^^^^^^^^^^^^^^

**1. Set Up Documentation Environment:**

.. code-block:: bash

   # Navigate to documentation directory
   cd docs/

   # Install Sphinx via conda (recommended)
   conda install sphinx

   # Alternatively install via pip
   # pip install sphinx

   # Build documentation locally to verify current state
   make clean
   make html

**2. Make Documentation Changes:**

- Edit RST (``.rst``) files in ``docs/source/`` directory
- Follow RST syntax and project conventions
- Use existing documentation as reference for style
- Keep changes focused and manageable

**3. Build and Test Documentation:**

.. code-block:: bash

   # Build HTML documentation
   make html

   # Check for warnings or errors in the output
   # Address any Sphinx warnings before submitting

   # Open built documentation in browser to verify
   # Linux:
   xdg-open build/html/index.html

   # macOS:
   open build/html/index.html

   # Windows:
   start build/html/index.html

**4. Verify Build Quality:**

- [ ] Documentation builds without warnings
- [ ] All internal links work correctly
- [ ] Code examples are accurate and tested
- [ ] Formatting is consistent with existing docs
- [ ] Cross-references are properly linked
- [ ] Images and diagrams display correctly

**5. Deploy to GitHub Pages (Optional):**

For maintainers or those with push access, documentation can be deployed to
GitHub Pages using ``ghp-import``:

.. code-block:: bash

   # Install ghp-import
   conda install ghp-import

   # Build documentation
   make clean
   make html

   # Deploy to gh-pages branch
   ghp-import -n -p -f build/html

   # The documentation will be available at:
   # https://[username].github.io/pyzui/

**Note:** GitHub Pages deployment requires appropriate repository permissions
and is typically handled by project maintainers.

**6. Types of Documentation Contributions:**

**Minor Improvements:**
- Fix typos, grammar, or formatting issues
- Update outdated information
- Improve clarity of existing content
- Fix broken links or references

**Moderate Enhancements:**
- Add missing documentation for existing features
- Improve examples or add new ones
- Reorganize content for better flow
- Add diagrams or visual aids

**Major Contributions:**
- Create new documentation sections or tutorials
- Implement documentation automation
- Improve documentation infrastructure
- Add comprehensive API documentation

**7. Submission Process:**

Documentation contributions follow the same submission process as code
contributions (fork, branch, pull request). Ensure your documentation:

- Builds successfully with ``make html``
- Follows the quality standards above
- Maintains consistency with existing documentation
- Includes appropriate examples and cross-references

Thank you for contributing to ZooUI!
