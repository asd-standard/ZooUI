PDF media object
=================

:class:`PdfMediaObject` extends :class:`TiledMediaObject` to render multi-page
PDF documents as individually tiled pages in the ZUI. Each page is rasterized
as a separate PPM by :doc:`PDFConverter <../technicaldocumentation/convertersystem>`,
tiled independently, and stored in the :doc:`tilestore <../zooui/tilestore>` under
per-page ``media_id`` values (``"doc.pdf:page:0"``, ``"doc.pdf:page:1"``, …).

Page Navigation
---------------

Three keyboard shortcuts control page navigation when a ``PdfMediaObject``
is the currently selected object:

.. list-table::
   :header-rows: 1

   * - Key
     - Action
     - Alignment
   * - ``Ctrl+↓``
     - Next page
     - Top of new page → top of viewport (vertical only)
   * - ``Ctrl+↑``
     - Previous page
     - Bottom of new page → bottom of viewport (vertical only)
   * - ``Ctrl+Alt+G``
     - Go-to-page dialog
     - Jumps to the specified page (top aligned)

The forward alignment (top) lets you read each page from the top.
The backward alignment (bottom) shows the bottom of the previous page,
simulating having just scrolled past it. Both directions are **vertical‑only**
— the horizontal position is kept unchanged (``move(0, dy)``), so the view
does not jump sideways when navigating pages. The go-to-page dialog uses
:class:`QInputDialog <PySide6.QtWidgets.QInputDialog>` with a spinbox
ranged from 1 to the total page count.

Application Flow
----------------

Here is the complete lifecycle of a ``PdfMediaObject``, from file opening to
rendering:

.. code-block:: text

    1. USER ACTION: Open a PDF file
       MainWindow.__open_media() detects .pdf extension
       └─→ PdfMediaObject(pdf_path, scene, autofit, start_page)

    2. PdfMediaObject.__init__()
       ├─ Calls TiledMediaObject.__init__(deferred=True) for clean setup
       ├─ Creates temp output directory (tempfile.mkdtemp)
       ├─ Submits PDF→per-page-PPM conversion to process pool
       │  future = converterrunner.submit_pdf_conversion(pdf_path, outdir)
       └─ Sets _media_id = "{pdf_path}:page:0"

    3. CONVERSION PHASE (process-based)
       PDFConverter runs in a separate process:
       ├─ pdftoppm rasterizes all pages at 300 DPI into tmpdir
       ├─ Per-page PPMs are copied to outdir:
       │  outdir/page_0000.ppm, outdir/page_0001.ppm, ...
       └─ page_count and page_paths are populated

    4. PAGE DISCOVERY (PdfMediaObject._on_conversion_complete)
       ├─ glob(glob) discovers page_*.ppm files
       ├─ Sets _page_count and _page_ppm_paths
       ├─ Clamps _start_page if beyond range
       ├─ Calls _reset_for_page(media_id_for_page_0)
       └─ Starts tiling with 2-page buffer (_maintain_buffer)

    5. LAZY TILING BUFFER
       _maintain_buffer() ensures the current page and the next page
       are submitted for tiling:
       ├─ _ensure_page_tiling(curr)  → submit_tiling(ppm, media_id, "png")
       └─ _ensure_page_tiling(curr+1) → submit_tiling(ppm, media_id, "png")

    6. RENDER LOOP (PdfMediaObject.render())
       ├─ _check_conversion_complete() — discover pages when conversion ends
       ├─ _check_page_tiling() — mark pages as tiled when tilers complete
       ├─ If current page not tiled: set _BlockingConverter dummy
       │  to prevent parent's __run_tiler() from firing on missing PPM
       └─ super().render() — delegates to TiledMediaObject's tileblock
          rendering pipeline

    7. PAGE SWITCHING (Ctrl+↑/↓ or go_to_page)
       ├─ change_page(delta) sets _pending_nav_direction
       ├─ _reset_for_page(new_media_id) resets tileblock caches,
       │  keeps dimensions from previous page for correct autofit bbox
       └─ _try_load() override applies smart alignment after autofit:
          • Forward (delta>0): move(0, -page_topleft.y) — top of page aligns to top of viewport
          • Backward (delta<0): move(0, viewport_h - page_bottomright.y) — bottom of page aligns to bottom of viewport

Lazy Tiling Buffer
------------------

Rather than tiling all pages at once (which would be slow for large PDFs),
only the current page and the next page are submitted for tiling. This
provides instant display on forward navigation because the next page's
tiles are already on disk.

.. code-block:: python

    def _maintain_buffer(self):
        for p in (self._current_page, self._current_page + 1):
            if 0 <= p < self._page_count:
                self._ensure_page_tiling(p)

Page state is tracked in three sets:
- ``_page_tiling``: pages with an active tiling job submitted
- ``_page_tiled``: pages whose tiles are confirmed on disk
- ``_page_tilers``: mapping of page index → active ``TilingHandle``

Previously visited pages that are still in the tilestore are detected via
``TileManager.tiled()`` and marked as tiled immediately.

_BlockingConverter Pattern
--------------------------

:class:`TiledMediaObject.render` falls through to :meth:`TiledMediaObject.__run_tiler`
when both ``__converter`` and ``__tiler`` are None. Since ``PdfMediaObject``
manages page-specific tiling externally (via :func:`tilerrunner.submit_tiling`),
it must prevent this fallthrough for pages that haven't been tiled yet.

The solution is :class:`_BlockingConverter`, a dummy sentinel whose
``progress`` attribute is always ``0.0``:

.. code-block:: python

    class _BlockingConverter:
        progress: float = 0.0

When a page is not yet tiled, ``PdfMediaObject.render()`` assigns the dummy
to ``_TiledMediaObject__converter`` before calling ``super().render()``.
The parent sees ``__converter.progress == 0.0`` and stays in the "loading"
state, showing the placeholder. Once the page's tiling completes, the dummy
is replaced with ``None`` and the parent loads the root tile normally.

Large PDF Page Selection
------------------------

PDFs larger than 2 MB trigger a pre‑open dialog before conversion begins.
The page count is quickly obtained by calling the ``pdfinfo`` command‑line
tool (part of Poppler, installed alongside ``pdftoppm``):

.. code-block:: python

    @staticmethod
    def _get_pdf_page_count(pdf_path: str) -> int | None:
        result = subprocess.run(["pdfinfo", pdf_path], ...)
        for line in result.stdout.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":", 1)[1].strip())
        return None

A :class:`QInputDialog <PySide6.QtWidgets.QInputDialog>` then asks the
user which page to open first. The selected page becomes the
``start_page`` parameter passed to ``PdfMediaObject``.

``_reset_for_page`` and ``deferred`` Init
-----------------------------------------

Two additions to :class:`TiledMediaObject` enable subclass‑based page
switching:

``deferred=True`` (constructor parameter)
    Skips the normal conversion/tiling setup in ``__init__``, allowing the
    subclass to manage its own pipeline.

``_reset_for_page(new_media_id)``
    Switches the underlying ``media_id`` and resets all tileblock caches
    (``_loaded``, ``__tileblock``, ``__converter``, ``__tiler``) **without**
    resetting the dimension data (``__width``, ``__height``,
    ``__aspect_ratio``, ``__maxtilelevel``). Keeping the old dimensions
    ensures the autofit bounding box in ``_try_load()`` uses the correct
    on‑screen size from the previous page, avoiding visual drift.

Scene Persistence
-----------------

``PdfMediaObject`` participates in the full save/load round‑trip through
``.pzs`` scene files. On save, it writes its class name and per‑page
``media_id``::

    PdfMediaObject    /path/to/doc.pdf:page:3    2.5    150.0    200.0

The ``media_id`` carries both the **original PDF path** and the **current
page number** (last seen before the save), using the format
``"{pdf_path}:page:{current_page}"``.

On scene load, :meth:`Scene._create_mediaobject_from_line` recognises the
``PdfMediaObject`` class name and:

1. Parses the ``media_id`` via :meth:`Scene._parse_pdf_media_id`, which
   splits at the **last** ``:page:`` delimiter to extract the file path
   and page number (using ``rsplit(":page:", 1)`` to handle paths that
   themselves contain ``:page:``).
2. Checks that the original PDF file still exists on disk.  If the file
   is gone, the object is **silently dropped** with a warning log and the
   rest of the scene still loads.
3. Creates a new ``PdfMediaObject(pdf_path, scene, autofit=False,
   start_page=page_number)``, preserving the saved zoomlevel, position,
   and page.

.. note::

   ``autofit=False`` is critical during load.  It prevents the zoomlevel
   from being recalculated when the actual image dimensions load,
   preserving the saved value exactly — the same pattern used by
   :class:`TiledMediaObject` scene persistence.

The per‑page tiles themselves are stored in the tilestore under
their ``media_id`` hashes (derived from ``sha1("pdf_path:page:N")``) and
are detected by ``TileManager.tiled()`` on reload, avoiding
re‑conversion. The PDF conversion pipeline re‑runs only if the tiles are
not yet cached.

PDF Page Numbering
------------------

When the PDFConverter rasterises a PDF, it can optionally draw a
``"N / total"`` page‑number label onto each PPM image in the
bottom‑right corner.  This is controlled by the ``page_numbering`` flag
(default ``True``):

.. code-block:: python

    converter = PDFConverter(pdf_path, outdir, page_numbering=True)

The label is rendered using PIL with a semi‑transparent background so
it never obscures content but remains readable against any PDF page
colour.

See Also
--------

- :doc:`../technicaldocumentation/tiledmediaobject` — Parent class
- :doc:`../technicaldocumentation/convertersystem` — PDF conversion pipeline
- :doc:`../technicaldocumentation/objectsystem` — Object system hierarchy
- :doc:`../zooui/converters/pdfconverter` — PDFConverter API reference
- :doc:`../zooui/tilestore` — Persistent tile storage
- :doc:`../usageinstructions/userinterface` — User interface keyboard shortcuts
