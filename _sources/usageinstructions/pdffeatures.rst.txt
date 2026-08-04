.. ZooUI PDF Features Documentation

PDF Features
============

ZooUI provides support for multi‑page PDF documents, rendering each page as
an independently tiled object in the zooming user interface. This document
covers all PDF‑related features available to end users.

Overview
--------

PDF (Portable Document Format) files can be:

- Opened directly from the file system or file‑open dialog
- Rendered as individually tiled pages (one page visible at a time)
- Navigated with keyboard shortcuts
- Saved and restored across scene files

Key Features
------------

1. **Multi‑Page PDF Rendering**: Each page rasterised at 300 DPI and tiled independently
2. **Keyboard Page Navigation**: Ctrl+Up/Down to flip pages, Ctrl+Alt+G to jump to a specific page
3. **Scene Persistence**: PDF objects survive save/load and keep their current page
4. **Large PDF Page Selection**: PDFs over 2 MB prompt for a start page before loading
5. **Lazy Tiling Buffer**: Only the current and next page are tiled, saving memory for large documents
6. **Page Number Labels**: Optional ``N / total`` watermark on each page

Opening PDF Files
-----------------

**Method 1: File‑Open Dialog**

1. Open the File menu and choose Open, or press the Open toolbar button
2. Navigate to a ``.pdf`` file and confirm
3. The PDF opens at page 1 (or at the page you select, see below)

**Method 2: Drag and Drop**

Drag a ``.pdf`` file from your file manager into the ZooUI window.

**Large PDF Page Selection**

PDFs larger than 2 MB trigger a pre‑open dialog before conversion begins.
A spinbox lets you choose which page to open first.

The page count is obtained quickly from the file metadata via ``pdfinfo``,
so the conversion itself only starts after you confirm.

Page Navigation
---------------

When a PDF object is selected in the scene, three keyboard shortcuts are
available:

.. list-table::
   :header-rows: 1

   * - Key
     - Action
   * - ``Ctrl+↓``
     - Go to next page
   * - ``Ctrl+↑``
     - Go to previous page
   * - ``Ctrl+Alt+G``
     - Open go‑to‑page dialog

**Forward navigation (Ctrl+↓)** aligns the **top** of the new page with the
**top** of the viewport, so you start reading from the top.

**Backward navigation (Ctrl+↑)** aligns the **bottom** of the previous page
with the **bottom** of the viewport, simulating having just scrolled past it.

Both directions move only vertically — the horizontal view position stays
the same, so the view does not jump sideways.

Context Menu
~~~~~~~~~~~~

When a PDF object is right‑clicked, the context menu shows:

- **Zoom In / Zoom Out**: Resize the PDF preview
- **Modify**: Opens the Modify Tiled Media Object dialog, where you can crop,
  resize, or adjust the object's appearance
- **Remove**: Delete the PDF object from the scene
- **Page**: The current page number (read‑only, informational)

Scene Persistence
-----------------

PDF objects are **saved inside ``.pzs`` scene files**. When you save and
reload a scene:

- The PDF object reappears at the **same position and zoom level**
- The **current page** at save time is restored (the ``:page:N`` suffix in
  the media path remembers which page you were on)
- If the original PDF file has been moved or deleted, the object is
  silently skipped but the rest of the scene still loads

Performance
-----------

Large PDFs with many pages use a **lazy tiling buffer** to stay responsive:

- Only the **current page** and the **next page** are submitted for tiling
- Previously visited pages remain cached in the tilestore and are detected
  instantly on re‑visit
- Page‑switching feels instant in the forward direction because the next
  page's tiles are already on disk

Page Number Labels
------------------

By default, ZooUI draws a small ``"N / total"`` label in the bottom‑right
corner of every rasterised page. This is visible at all zoom levels and
helps orientation inside multi‑page documents.

The label has a semi‑transparent background so it never fully obscures the
PDF content underneath.

Customisation
~~~~~~~~~~~~~

Page numbering can be disabled in code when creating the PDF converter::

    converter = PDFConverter(pdf_path, outdir, page_numbering=False)

There is currently no GUI setting to toggle page numbering — it is enabled
by default.

Troubleshooting
---------------

**PDF Not Opening**

- Ensure ``pdftoppm`` (Poppler) and ``pdfinfo`` are installed on your system
- On Debian/Ubuntu: ``sudo apt install poppler-utils``
- On macOS: ``brew install poppler``
- On Windows: install `poppler for Windows`_ and add it to your ``PATH``

.. _poppler for Windows: https://github.com/oschwartz10612/poppler-windows/releases/

**PDF Opens but No Pages Render**

- Wait a few seconds — the first page needs time to rasterise and tile
- Very large PDFs (100+ pages) take longer; the dialog shows progress
- Check the log file under ``logs/`` for conversion errors

**Page Numbers Not Visible**

- Page numbering is applied during rasterisation. Re‑open the PDF to
  trigger a fresh conversion if you changed the setting.

See Also
--------

- :doc:`../usageinstructions/userinterface` — General keyboard shortcuts and UI overview
- :doc:`../technicaldocumentation/pdfmediaobject` — PdfMediaObject technical deep‑dive
- :doc:`../technicaldocumentation/convertersystem` — PDF conversion pipeline details
