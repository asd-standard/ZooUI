# OCR Screenshot Feature — Crash Investigation Summary

## The Problem

The OCR screenshot feature segfaults when run in the GUI integration test in isolation:

- **`--only-step 53`**: C++ segfault during or after OCR capture — no Python traceback
- **`--start-step 53`**: C++ segfault at `__action_confirm_quit` during application shutdown

When run as part of the **full test suite** (`python main.py`), everything works — no crashes.

## What We've Tried

### 1. Initial Implementation (synchronous `grab()` + dialog)
**qzui.py**: `self.grab()` called directly in `mouseReleaseEvent`  
**mainwindow.py**: Dialog opens synchronously in signal handler  
**Result**: Segfault during `dialog.exec()` (nested event loop inside `processEvents()`)

### 2. Deferred Capture (QTimer.singleShot 0ms)
**qzui.py**: `QtCore.QTimer.singleShot(0, lambda: self._do_ocr_capture(...))`  
**Result**: Same crash — 0ms timer fires during `processEvents()`, dialog opens in nested loop

### 3. Stop Paint Timer Before Dialog
**mainwindow.py**: `zui._QZUI__timer.stop()` before `dialog._run_dialog()`  
**Result**: Segfault still — expose events (not timer-driven) trigger paintEvent during dialog

### 4. TileManager.purge() on new_scene
**mainwindow.py**: `TileManager.purge()` in `__action_new_scene` before creating new scene  
**Result**: No improvement — stale cache wasn't the issue

### 5. TileManager.pause()/resume() in _do_ocr_capture
**qzui.py**: `TileManager.pause()` before grab, `resume()` after  
**Result**: No improvement — `pause()` doesn't interrupt mid-`_load()` provider threads

### 6. QTimer Delay (50ms instead of 0ms)
**qzui.py**: `QtCore.QTimer.singleShot(50, ...)`  
**Result**: Still crashes — 50ms doesn't guarantee the timer fires after `processEvents()` returns

### 7. Warm Up StringInputDialog
**test/ocr_screenshot.py**: Import and create `OpenNewStringInputDialog()` instance before OCR mode  
**Result**: No improvement — paint infrastructure already initialized

### 8. Remove Dialog Entirely (Direct `__open_media`)
**mainwindow.py**: `uri = "string:ffffff:" + text; self.__open_media(uri)` — no dialog, no modal  
**Result**: `--only-step 53` works, but `--start-step 53` still segfaults at quit

### 9. shutdown_threads() on new_scene + close_tab
**mainwindow.py**: `zui.scene.shutdown_threads()` before replacing scene in `__action_new_scene` and `_close_tab`  
**Result**: Reduced parallel layout workers from 8→4, but quit still crashes

### 10. shutdown_threads() + TileManager.shutdown() at quit
**mainwindow.py**: Iterate all tabs and shutdown scene threads + tile manager at quit  
**Result**: Still segfaults at quit — crash in `dialog.exec()` of quit confirmation dialog

### 11. Synchronous Capture (No QTimer) with No Dialog
**qzui.py**: Direct `self._do_ocr_capture()` in `mouseReleaseEvent` — no deferral  
**mainwindow.py**: No dialog — direct `__open_media`  
**Result**: `--only-step 53` works, but `--start-step 53` still segfaults at quit

## Current State

The implementation is back to: QTimer 0ms deferral + StringInputDialog. The crashes are:

| Mode | Crash location | Traceback |
|------|---------------|-----------|
| `--only-step 53` | C++ paint engine during OCR | No Python frames |
| `--start-step 53` | `__action_confirm_quit` → `dialog.exec()` | Faulthandler shows C++ segfault |

## Why the Full Suite Works

The full test suite has 51 steps before the OCR test. During those steps:

1. **Step 1**: Loads test scene with 6 images + string object (tile cache populated, paint engine exercised)
2. **Steps 2-51**: Repeated new scenes, media loads, zoom, pan, dialogs, keyboard shortcuts — hundreds of paint/event cycles
3. **Step 52**: PDF loaded and paged through — tile providers have been busy for minutes
4. **Step 90** (after OCR): Complete workflow — loads test scene images, zooms 5 steps, pans, saves, zooms out 10 steps

### Key Differences: Full Suite vs Isolation

| Factor | Full Suite | Isolation |
|--------|-----------|-----------|
| Paint cycles before OCR | 200+ | ~5 |
| Tile cache state | Hot (all tiles cached) | Cold (loading on demand) |
| Parallel layout workers | Single scene's 4 workers | Multiple scenes' workers possible |
| Qt paint engine | Warmed up | Cold |
| `_run()` caller | Steps 1-51, then 52, then 53 | Step 53 only |
| Time between steps | Never — sequential calls via `step_func(self.ctx)` | Direct test call |

## Architecture of the Test Runner

```
setup()
  ├── QApplication()
  ├── MainWindow().show()
  ├── processEvents() + wait(1000ms)         ← window shown
  ├── trigger_action(ctx, "new_scene")       ← initial blank scene
  └── wait(2000ms)

run(start_step=...)
  ├── for each step in self.steps:
  │     step_func(self.ctx)                  ← direct function call, NO event loop processing between steps
  │
  └── Exception handling: prints warning, continues to next step

teardown()
  └── window.close() + processEvents()
```

The test steps are **synchronous function calls** — no Qt event loop iterations between steps (except what the steps themselves call via `wait()`/`processEvents()`).

In the full suite, the cumulative effect of 51 steps means:
- ~500 `wait()` calls, each calling `QTest.qWait(ms)` which processes events
- Dozens of `processEvents()` calls
- Multiple `wait_for_image_load()` calls (500ms each)
- Timer-based steps (FPS setting, zoom/move loops)

This creates a well-exercised Qt event loop with thousands of paint/event cycles, a toasty tile cache, and a stable paint engine.

In isolation, the setup creates the window, shows it briefly (1 second), then immediately runs the OCR step. The paint engine has barely initialized, the tile cache is empty, and everything is happening in rapid succession.

## Current Code State

### qzui.py (OCR capture)
```python
# mouseReleaseEvent:
QtCore.QTimer.singleShot(0, lambda: self._do_ocr_capture(x1, y1, x2, y2))

# _do_ocr_capture:
timer_active = self.__timer.isActive()
if timer_active: self.__timer.stop()
try:
    pixmap = self.grab()
    cropped = pixmap.copy(x1, y1, x2 - x1, y2 - y1)
    self.ocr_region_selected.emit(cropped.toImage())
finally:
    if timer_active:
        self.__timer.start(int(1000 / self.framerate), self)
```

### mainwindow.py (OCR handler)
```python
def __handle_ocr_region(self, image):
    ... # pytesseract OCR
    if not text: text = "no text detected"
    dialog = DialogWindows.open_new_string_input_dialog(initial_text=text)
    ok, uri = dialog._run_dialog()
    if ok and uri: self.__open_media(uri)
```

### mainwindow.py (cleanup on new_scene)
```python
def __action_new_scene(self):
    ...
    zui.scene.shutdown_threads()    # shuts down old scene's layout workers
    zui.scene = Scene.new(...)
```

### mainwindow.py (cleanup on close_tab)
```python
def _close_tab(self, index):
    ...
    scene.shutdown_threads()
    TileManager.purge()
    ...
```

### mainwindow.py (cleanup on quit)
```python
def __action_confirm_quit(self):
    ...
    if response == QDialog.Accepted:
        for zui in self.__zui_tabs:
            zui.scene.shutdown_threads()
        QApplication.closeAllWindows()
```

### guiintegration/test/ocr_screenshot.py
```python
# Steps: new_scene → open PDF → wait → click → zoom 12x → pan left 5x → pan down 12x
# → repaint settle → trigger_action("ocr_screenshot") → repaint settle
# → simulate_mouse_drag(top-left area) → wait 2s
```

## Hypothesis

The C++ crash is a **cold-start race condition** in the Qt paint engine. When running in isolation:

1. `QWidget.grab()` (via `_do_ocr_capture`) forces a synchronous window surface capture
2. The window surface may not have completed its initial paint cycle
3. The tile provider threads are actively loading/caching QImage objects
4. The QImage shared-data pointer (implicit sharing) is read by the paint engine while being written by a provider thread
5. Use-after-free or double-free in Qt's C++ paint engine → segfault

In the full suite, the paint engine is fully initialized, the tile cache is hot, and no provider writes occur during `grab()` → no crash.

The `--start-step 53` quit crash is a different issue: the quit dialog's QDialog.exec() processes pending events, one of which triggers a paint on the still-active scene. But by now the scene's layout workers have been shut down, tile providers are potentially stopped, and the paint might reference freed objects.

## Next Steps to Investigate

1. Use `gdb` with `core` dump to get a C++ backtrace of the actual segfault location
2. Add explicit `zui.repaint()` + `app.processEvents(QEventLoop.AllEvents, 500)` before entering OCR mode to ensure complete paint initialization
3. Pre-load and discard a dummy QImage from the tile system to warm the cache before OCR
4. Replace `grab()` with direct scene rendering to a QPixmap (bypassing window surface entirely)
5. Add `zui.scene.render()` call during `setup()` to warm the paint engine before any test steps
