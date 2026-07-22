# Changelog

All notable changes to ZooUI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2026-07-22
### Added
- **Per-page PDF support** — PDFs are now rendered as individually tiled pages
  instead of one merged vertical scroll. Each page is rasterized as a separate
  PPM and tiled independently, enabling page-by-page navigation.
- **`PdfMediaObject`** — new class extending `TiledMediaObject` that manages
  multi-page PDFs. Supports page navigation with smart alignment: forward
  (`Ctrl+↓`) aligns the new page's top-left to the viewport, backward
  (`Ctrl+↑`) aligns the bottom‑right. Ctrl+Alt+G opens a go‑to‑page dialog.
  A lazy 2‑page tiling buffer tiles the current page and the next page in
  the background for instant forward navigation.
- **Large PDF page selection dialog** — PDFs larger than 2 MB no longer get
  silently skipped. A dialog shows the page count (via `pdfinfo`) and asks
  which page to open first.
- `TiledMediaObject` gains `deferred` init parameter and `_reset_for_page()`
  method to support subclass-based page switching.
- `ConversionHandle` gains `page_count` property for multi‑page converters.
- `_BlockingConverter` dummy class prevents premature `__run_tiler()` calls
  while `PdfMediaObject` manages page‑specific tiling externally.
- GUI integration test step 52: PDF page navigation (forward, backward,
  go‑to‑page dialog) with visual position marker.
- `data/test_pdf.pdf` — minimal 3‑page PDF for integration testing.
- PDF page navigation documentation in the user interface reference and
  a new :doc:`pdfmediaobject` technical documentation page.

### Changed
- `PDFConverter` now outputs per‑page PPM files (`page_0000.ppm`,
  `page_0001.ppm`, …) to an output directory instead of merging all pages
  into a single vertical PPM. The old `__merge()` method has been removed.
  The constructor's second argument is now an output **directory** (`outdir`).
- `submit_pdf_conversion(infile, outdir)` updated: second argument is a
  directory path, not a file path.
- `MainWindow.__open_media()` routes `.pdf` files to `PdfMediaObject` instead
  of `TiledMediaObject`.
- Removed `MAX_PDF_SIZE_BYTES` (2 MB hard limit). Replaced by the >2 MB page
  selection dialog.
- `TiledMediaObject.__loaded` and `__try_load` renamed to `_loaded` and
  `_try_load` (protected) for subclass access.
- Updated unit and integration tests for all changed components (56 new
  unit tests, 3 integration test fixes).
- Documentation: `convertersystem.rst` updated for per‑page PPM output;
  `windowsystem.rst` updated to remove `MAX_PDF_SIZE_BYTES`;
  `objectsystem.rst` updated with `PdfMediaObject` in hierarchy tree.

## [0.5.4] - 2026-07-22
### Added
- **Home Point feature** — quick-save and restore the current scene view
  position and zoom level. Two new Actions menu items: *Set Home Point*
  (`Ctrl+Shift+H`) and *Go to Home Point* (`Ctrl+J`), plus direct keyboard
  shortcuts `Home` (go) and `Shift+Home` (set). A cyan expanding crosshair
  pulse animation at the viewport centre confirms when a home point is saved.
  The home point is per-tab and is cleared when a new scene is loaded.
- Home Point documentation in the user interface reference and the window system
  technical documentation.
- Tests for the home point feature: 9 unit tests (QZUI), 4 integration tests
  (Scene round‑trip), and 1 GUI integration step.

### Changed
- About dialog: project URL updated to `https://asd-standard.github.io/ZooUI/`;
  original URL moved under the copyright line as a historical reference.

### Fixed
- `TileManager._shutdown_threads()` now uses `getattr` guards so it is safe
  when cache objects are mocked as plain `dict` in unit tests. All 40
  tilemanager tests pass again.

## [0.5.3] - 2026-07-17
### Added
- Usage Instructions dialog under Help menu, automatically displaying content
  from `docs/source/usageinstructions/userinterface.rst` converted to HTML via
  docutils

### Changed
- Project renamed from **PyZUI** to **ZooUI**. All package imports (`pyzui` →
  `zooui`), GPL headers, runtime paths (`~/.pyzui/` → `~/.zooui/`),
  environment variable (`PYZUI_MP_CONTEXT` → `ZOOUI_MP_CONTEXT`), Qt
  application identity, logger prefix, conda environment name, launcher script,
  desktop entry, config files, Sphinx documentation, and build spec were
  renamed across ~260 files. Old project URLs (`github.com/davidar/pyzui`,
  `da.vidr.cc/projects/pyzui/`) preserved as historical references.

### Fixed
- **Segfault when loading the home scene after opening media files.** The
  `DynamicTileProvider._load()` method called `QtGui.QImage(filename)` from a
  background daemon thread (`TileProvider`), which is undefined behavior in Qt
  and caused a segmentation fault when a `ProcessPoolExecutor` (from VIPS image
  conversions) was active with its feeder/handler threads. Fixed by using
  `PIL.Image.open()` instead, matching the `StaticTileProvider` pattern. The
  PIL→QImage conversion now happens safely via `ImageQt.ImageQt()` (raw bytes,
  thread-safe per Qt documentation) in `Tile.__init__`.
- Home scene camera position drifting on first launch when window size differs
  from the scene default (1280×720). The `viewport_size` setter in `Scene` calls
  `zoom()` to scale content on resize, which corrupts the `.pzs` file's
  zoomlevel and origin before the zoom-in animation runs. Fixed in `QZUI` by:
  - Saving the file's zoomlevel/origin before `viewport_size` assignment and
    restoring them afterwards in both the deferred (`_run_pending_animation`)
    and synchronous (`__set_scene`) paths.
  - Using `isVisible()` instead of just `width>0` to decide when to defer the
    animation, so it always runs at the final widget size instead of the
    intermediate QTabWidget layout size.
- `bump_version.py` screenshot capture corrupting `data/home.pzs` by silently
  auto-saving viewport-adjusted state back to disk. Fixed by calling
  `zui.scene.disable_autosave()` immediately after loading the scene.
- `data/home.pzs` restored to correct zoom/origin values
  (`-5.0  620.0  300.0`).

## [0.5.2] - 2026-05-27
### Added
- Ctrl+Enter keyboard shortcut in all 4 input dialogs (new string, modify string,
  SVG picker, modify SVG) via QShortcut — accepts the dialog, equivalent to
  clicking OK
- GUI integration test helper `accept_open_dialog_via_ctrl_enter()` in
  `scene_helpers.py` for scheduling dialog acceptance via Ctrl+Enter key simulation
- GUI integration test steps for Ctrl+Enter dialog acceptance:
  - Step 38: New string dialog — types "test string" into QTextEdit, then accepts
  - Step 39: SVG picker dialog — selects first SVG shape, then accepts
  - Step 48: String modification dialog (right-click) — accepts via Ctrl+Enter
  - Step 49: SVG modification dialog (right-click) — accepts via Ctrl+Enter
- Documented Ctrl+Enter shortcut in `userinterface.rst` and `svgfeatures.rst`
- `data/zooui.desktop` file for freedesktop desktop integration, enabling proper
  application icon display on Linux desktop environments (KDE, GNOME, etc.)

### Fixed
- TileProvider `_load` result check (`if tile:` → `if tile is not None:`) to avoid
  PIL Image truthiness issues with Pillow >= 10.0 where `bool(Image)` raises
  TypeError, which silently killed the daemon provider thread and prevented tiles
  from entering the cache
- Hardcoded `../../data` relative paths in `test_vipsconverter.py` and
  `test_ppm.py` replaced with `os.path.dirname(__file__)`-based paths,
  fixing `FileNotFoundError` when running `pytest ./test -v` from project root
- Unit test `test_init_needs_tiling` now mocks `converterrunner.submit_vips_conversion`
  to prevent real `ProcessPoolExecutor` usage and `BrokenProcessPool` cascading
- Added `test/conftest.py` with autouse fixture that resets the converter process
  pool after each test, preventing `BrokenProcessPool` from leaking across tests
- `TestProviderRequestQueue` integration tests now use `cache_ready()` helper to
  properly synchronize with the provider thread's cache insertion, fixing race
  condition in `test_provider_processes_all_queued_requests` and
  `test_duplicate_requests_consolidated_by_cache_check`
- Application icon not persisting on KDE panel: added `setDesktopFileName`,
  `setApplicationName`, and `setApplicationDisplayName` calls after QApplication
  creation in `main.py` so the desktop environment can match the running app to
  its `.desktop` file and display the correct icon

### Changed
- Split contribution guidelines into two focused documents:
  `contributionguidelines/codestyle.rst` (code style, naming, formatting,
  quality checks, docstring conventions) and `contributionguidelines/
  contributionguidelines.rst` (workflow, testing requirements, versioning,
  contributing to documentation), with cross-references between them

## [0.5.1] - 2026-05-12
### Changed
- GUI integration test restructured from single `gui_integration.py` (1196 lines) to
  `guiintegration/` package with 47+ per-feature test modules, reusable test
  utilities (`qt_simulation`, `scene_helpers`, `image_creation`, `temp_dirs`),
  dedicated `conf.py` and `logger.py`, and `--list-steps`/`--start-step`
  CLI support in main orchestrator
- Documentation massively expanded: added new rst modules for backup, config,
  logger, objects, tilesystem, windows, and converters subsystems; major
  restructuring and expansion of objectsystem, tiledmediaobject, tilingsystem,
  windowsystem, convertersystem, projectstructure docs; new SVG and string
  rendering ecosystem reference documentation; new SVG features usage guide
- Logger system: `LoggerConfig.initialize()` now re-entrant for runtime
  reconfiguration; `log_dir` supports tilde expansion (`~/logs`);
  `LOGGING.md` reference guide created

## [0.5.0] - 2026-05-10
### Added
- Configuration management system (ConfigManager) with JSON config files,
  validation, merge overrides, and example config (`zooui_config_example.json`)
- Autosave/backup system with per-scene directories, configurable interval,
  rotation, and expiration; AutosaveSettingsDialog for user control
- Zoom limits manager to prevent crashes at extreme zoom levels;
  ZoomSettingsDialog for user control
- SVG elongation: interactive resizing of arrows (Ctrl+Wheel), squares, circles,
  triangles, and sticks via mouse wheel with modifier keys
- SVG caching system for embedded SVGs with startup cache cleanup
- Copy/paste support within scenes (Ctrl+C / Ctrl+V) via SceneClipboardManager
- Import scene from file (appends to current scene)
- New tab / close tab for managing multiple scenes independently
- Render order toggle: switch between smaller-on-top and larger-on-top via View
  menu (Ctrl+R) or `render.order` config key (`smaller_on_top` / `larger_on_top`)
- Parallel text rendering for improved zoom performance (SceneParallelRenderer)
  with priority-based batcher for worker pool tasks
- Version bump utility script (`scripts/bump_version.py`) with automatic
  home.png screenshot capture after version update
- Embedded SVG support in scene (.pzs) files
- Application icon loading
- Comprehensive command-line arguments: autosave control (interval, max backups,
  expire days, disable), zoom defaults, cleanup control, logging flags
- Build configuration (`pyproject.toml`) and pre-commit hooks (ruff linter +
  formatter)
- Launcher script (`zooui.sh`) with conda environment integration
- AGENTS.md agent guidelines for AI-assisted development
- Shutdown orchestration: unified thread cleanup before Qt destruction
- SVG picker and modifier dialog windows
- Scene selection persistence across save/load
- New SVG and image data assets in data/SVG/

### Changed
- `main.py` fully rewritten with ConfigManager, CL argument processing,
  proper shutdown flow
- Scene constructor now accepts configuration dict (autosave, render order,
  zoom settings)
- Scene module refactored: utilities extracted to `sceneutils/` (autosave,
  clipboard, parallel renderer, priority batcher)
- Object utilities extracted to `objectsutils/` with `ZoomManager` class
- `QZUI` constructor expanded (config, autosave_config parameters; default
  framerate 10→20; default zoom sensitivity 10→50)
- `Scene.render()` rewritten with parallel rendering support and sort optimization
- Import organization standardized across all modules (stdlib → third-party
  → local)
- Comprehensive type annotations added across all modules
- Docstrings rewritten and expanded across all modules
- `zooui/__init__.py` `__all__` flattened (removed hierarchical nesting)

### Fixed
- Thread safety: `__objects_lock` consistently used for all scene object iteration
- Qt threading errors during Python garbage collection (proper `__del__` cleanup)
- Autosave timer properly stopped on scene replacement to prevent log noise
- Focus out event resets keyboard modifiers and rectangle drawing state

### Removed
- `data/02_green_gradient.png` and `data/06_cyan_circles.png` (replaced with
  new data/SVG/ assets)
- `test/unittest/.coverage` file from git tracking
- SVGRectangle module (replaced with dedicated SVG elongation utilities)

## [0.4.0] - 2026-03-03
### Added
- Process pooling system for tiler object calls
- Thread pooling system for tiler tile creation loop (`__load_row_from_file`)
- Comprehensive integration tests for concurrent stress
- Tiler runner module with parallel execution support

## [0.3.2] - 2026-02-27
### Added
- Mediaobject bulk selection via control-click / left-click drag
- GUI integration test for bulk selection behavior
### Fixed
- Lazy attribute resolution edge case
### Removed
- Dead thread inheritance from converter classes

## [0.3.1] - 2026-02-24
### Added
- Comprehensive logging integration tests
- Comprehensive logger unit tests
### Fixed
- Logging: `set_level()` now updates all handlers, console enabled by default
- Split-loop bug in string mediaobject processing
- Cache invalidation after `modifyStringMediaObject` call
- Color selection logic in UI dialogs

## [0.3.0] - 2026-02-20
### Added
- Hybrid rendering system for StringMediaObject (CPU-efficient caching)
### Changed
- Rendering pipeline for text objects now uses cached QImages

## [0.2.2] - 2026-02-18
### Changed
- Renamed `converter_runner` module to `converterrunner`
- Moved tilestore cleanup to application shutdown for faster startup
### Added
- Comprehensive type annotations for all tilesystem modules
- Comprehensive type annotations for all windows module classes

## [0.2.1] - 2026-01-16
### Added
- File extension filter in Open Media Directory dialog
- PDF size limit validation in Open Media Directory
### Fixed
- Pytest hang: changed default multiprocessing context to `fork`
- Auto-detect safe multiprocessing context based on thread state
### Removed
- `__pycache__` files from git tracking

## [0.2.0] - 2026-01-10
### Added
- Process-based parallel conversion for converters (ProcessPoolExecutor, `spawn` context)
- `converter_runner` module with `ConversionHandle` progress tracking
- Pause/resume mechanism for TileProvider and TileManager
### Changed
- TiledMediaObject conversion now uses process-based parallelism instead of threads
### Removed
- `disk_lock` from PDFConverter (no longer needed with process isolation)
- `test_converter_pipeline.py` (replaced with integration test)

## [0.1.5] - 2026-01-07
### Added
- `ModifyTiledMediaObjectDialog` for image manipulation
- Unit test for render order verification
- Integration tests for save/load round-trip scene preservation
### Fixed
- Rendering order: smaller objects now render on top of larger ones (reversed z-order)
- Selection now returns topmost (smallest) object at click position
- Scene loading: `autofit=False` to preserve saved zoomlevel from `.pzs` files

## [0.1.4] - 2025-12-16
### Added
- GitHub Actions CI workflow for Sphinx documentation
- README.md with project description and contribution guidelines
### Fixed
- Sphinx documentation warnings
- Code quality warnings identified by pyflakes
### Changed
- Restructured documentation into logical sections (getting started, technical, testing)
- Reorganized project files into standard layout

## [0.1.3] - 2025-11-19
### Added
- Sphinx documentation system with autodoc support
- Documentation for all core modules (19+ modules documented)
- Scene class documentation expanded
### Changed
- Updated magickconverter, pdfconverter, and tiler with code improvements

## [0.1.2] - 2025-10-28
### Removed
- Old LaTeX documentation (`doc/` directory including manual.tex)
- `COPYING.txt` (replaced with GPLv3 license header)
### Changed
- Updated `__init__.py` metadata (author, maintainer, license fields)

## [0.1.1] - 2025-05-29
### Added
- Dialog windows system for user interaction
### Changed
- Major restructure: moved all modules into `zooui/` package
- MainWindow and QZUI widget refinements
- MediaObject class hierarchy improvements

## [0.1.0] - 2025-03-13
### Added
- Initial release with Zooming User Interface framework
- Tile system: tile cache, tile manager, tile providers (static, dynamic, OSM, Mandelbrot, fern)
- Media object types: tiled media, string media, SVG media
- Scene management with object sorting (`__sort_objects`)
- Converter system: VIPS, PDF, ImageMagick converters
- PPM image format support
- Tile store with persistent caching
