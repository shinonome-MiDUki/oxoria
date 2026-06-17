# Oxoria API Documentation

---

## Table of Contents

1. [cv_api.py — `opencv_convert`](#cv_apipy--opencv_convert)
2. [std_cv_cmd.py — `CvProcessAPI`](#std_cv_cmdpy--cvprocessapi)
3. [std_menu_cmd.py — `StdMenuCmd`](#std_menu_cmdpy--stdmenucmd)
4. [canvas_api.py — `CanvasAPI`](#canvas_apipy--canvasapi)
5. [app_api.py — `AppAPI`](#app_apipy--appapi)
6. [resources_api.py — `ResourcesAPI`](#resources_apipy--resourcesapi)
7. [search_api.py — `SearchAPI`](#search_apipy--searchapi)

---

## cv_api.py — `opencv_convert`

### Overview

`opencv_convert` is a **decorator function** that bridges PySide6 canvas items and OpenCV-compatible NumPy arrays.  
It automatically extracts the pixmap from each selected canvas item, converts it to an RGBA NumPy array, passes it to the decorated function as `cv_img`, and writes the processed result back to the canvas.

### Usage

```python
@opencv_convert
def my_func(*args, cv_img: np.ndarray = None) -> np.ndarray:
    ...
```

### Behavior

| Step | Description |
|------|-------------|
| 1 | Retrieves all selected items via `CanvasAPI().get_selected()` |
| 2 | Converts each item's `base_pixmap` to `QImage.Format_RGBA8888` |
| 3 | Casts the image data to a `np.ndarray` of shape `(H, W, 4)` |
| 4 | Injects it into the decorated function as `cv_img` keyword argument |
| 5 | Converts the returned `np.ndarray` back to `QPixmap` |
| 6 | Writes the result back via `CanvasAPI().set_pixmap()` |

### Notes

> - The decorated function **must** accept `cv_img: np.ndarray = None` as a keyword argument and **must** return a `np.ndarray` of shape `(H, W, 4)` in RGBA format.
> - The decorator iterates over **all** selected items; every selected item will be processed independently.
> - No value is returned from the wrapper; the side effect is the canvas update.

---

## std_cv_cmd.py — `CvProcessAPI`

### Overview

`CvProcessAPI` provides a collection of OpenCV-based image processing operations applied to currently selected canvas items. All methods are decorated with `@opencv_convert` and `@classmethod`.

---

### `to_blackwhite`

Converts the selected image(s) to grayscale (black & white).

| | |
|---|---|
| **Signature** | `cls.to_blackwhite(cv_img: np.ndarray = None) -> np.ndarray` |
| **Arguments** | `cv_img` — injected automatically by `@opencv_convert`; do not pass manually |
| **Returns** | `np.ndarray` — RGBA image converted from grayscale |
| **Notes** | Uses `cv2.COLOR_BGRA2GRAY` then `cv2.COLOR_GRAY2RGBA` for round-trip conversion |

---

### `recover_color`

Returns the image unchanged. Intended to restore a previously processed image to its original state.

| | |
|---|---|
| **Signature** | `cls.recover_color(cv_img: np.ndarray = None) -> np.ndarray` |
| **Arguments** | `cv_img` — injected automatically by `@opencv_convert` |
| **Returns** | `np.ndarray` — original RGBA image as-is |
| **Notes** | This method is a pass-through; actual restoration depends on `base_pixmap` holding the original data |

---

### `denoise_img`

Applies colored non-local means denoising to the selected image(s).

| | |
|---|---|
| **Signature** | `cls.denoise_img(cv_img: np.ndarray = None) -> np.ndarray` |
| **Arguments** | `cv_img` — injected automatically by `@opencv_convert` |
| **Returns** | `np.ndarray` — denoised RGBA image |
| **Notes** | Uses `cv2.fastNlMeansDenoisingColored` with fixed parameters `(h=10, hColor=10, templateWindowSize=7, searchWindowSize=21)`. These are not currently configurable. |

---

### `custom_operation`

Executes an arbitrary OpenCV expression string and applies the result to the selected image(s).

| | |
|---|---|
| **Signature** | `cls.custom_operation(cv2_cmd: str, cv_img: np.ndarray = None) -> np.ndarray` |
| **Arguments** | `cv2_cmd: str` — a Python expression string; has access to `cv2`, `np`, and `cv_img` in its execution context |
| | `cv_img` — injected automatically by `@opencv_convert` |
| **Returns** | `np.ndarray` — result of the evaluated expression |

> ⚠️ **Security Warning:** This method uses `eval()` to execute the expression. Only pass trusted, validated strings. Never expose this to untrusted user input, as it can execute arbitrary code.

---

## std_menu_cmd.py — `StdMenuCmd`

### Overview

`StdMenuCmd` implements standard menu-bar commands (File menu operations, window management, etc.) for the Oxoria application. It relies on `CanvasAPI`, `ResourcesAPI`, and `AppAPI` internally.

---

### `__init__`

Initializes the command class and instantiates internal API objects.

| | |
|---|---|
| **Signature** | `__init__(self)` |
| **Returns** | `None` |

---

### `save_as`

Opens a Save dialog and saves the current canvas to a new `.oxoria` file chosen by the user.

| | |
|---|---|
| **Signature** | `save_as(self) -> None` |
| **Returns** | `None` |
| **Notes** | Requires `UI_Var.MAIN_WINDOW` to be set. The `.oxoria` suffix is enforced regardless of the user's input. Updates `GBVar.OPENED_FILE`. |

---

### `save_file`

Saves the current canvas to the already-opened file. Falls back to `save_as()` if no file is currently open.

| | |
|---|---|
| **Signature** | `save_file(self) -> None` |
| **Returns** | `None` |

---

### `open_resource`

Opens a file picker dialog and loads the chosen file onto the canvas as a resource.

| | |
|---|---|
| **Signature** | `open_resource(self) -> None` |
| **Returns** | `None` |
| **Notes** | Accepts all file types. Requires `UI_Var.MAIN_WINDOW` to be set. |

---

### `new_canvas`

Saves the current file and then clears the canvas.

| | |
|---|---|
| **Signature** | `new_canvas(self) -> None` |
| **Returns** | `None` |
| **Notes** | Calls `save_file()` before clearing, so unsaved work is preserved. |

---

### `open_oxoria_file`

Opens a `.oxoria` project file selected by the user. If a file is already open, `new_canvas()` is called first.

| | |
|---|---|
| **Signature** | `open_oxoria_file(self) -> None` |
| **Returns** | `None` |
| **Notes** | Requires `UI_Var.MAIN_WINDOW` to be set. |

---

### `export_canvas`

Exports the current canvas as an `.oxoarchive` file (zip-based bundle) to a user-selected path.

| | |
|---|---|
| **Signature** | `export_canvas(self) -> None` |
| **Returns** | `None` |
| **Notes** | Requires `UI_Var.MAIN_WINDOW` to be set. The `.oxoarchive` suffix is enforced. |

---

### `new_window`

Opens a new application window.

| | |
|---|---|
| **Signature** | `new_window(self) -> None` |
| **Returns** | `None` |

---

### `quit_app`

Saves the current file and then quits the application.

| | |
|---|---|
| **Signature** | `quit_app(self) -> None` |
| **Returns** | `None` |

---

### `force_quit_app`

Quits the application immediately without saving.

| | |
|---|---|
| **Signature** | `force_quit_app(self) -> None` |
| **Returns** | `None` |
| **Notes** | ⚠️ Any unsaved changes will be lost. |

---

### `test`

Prints a test message to stdout. Used for development/debugging.

| | |
|---|---|
| **Signature** | `test(self) -> None` |
| **Returns** | `None` |

---

## canvas_api.py — `CanvasAPI`

### Overview

`CanvasAPI` provides the primary interface for canvas state management, including saving/loading project files, managing items on the scene, and exporting/importing canvas archives.

---

### `__init__`

| | |
|---|---|
| **Signature** | `__init__(self)` |
| **Returns** | `None` |

---

### `make_oxoria_file`

Serializes the current canvas scene into a dictionary suitable for JSON export.

| | |
|---|---|
| **Signature** | `make_oxoria_file(self) -> dict` |
| **Returns** | `dict` — keys are item pointers; values contain `size_h`, `size_w`, `pos_x`, `pos_y` |
| **Notes** | Only `ImageItem` instances are included. Returns early if `UI_Var.MAIN_CANVAS` is `None`. |

---

### `save_oxoria_file`

Serializes and saves the current canvas to a `.oxoria` JSON file.

| | |
|---|---|
| **Signature** | `save_oxoria_file(self, saving_path: str) -> None` |
| **Arguments** | `saving_path: str` — absolute or relative path to write the file |
| **Returns** | `None` |
| **Notes** | Updates `GBVar.OPENED_FILE` upon completion. |

---

### `open_oxoria_file`

Loads a `.oxoria` project file and restores all image items to the canvas.

| | |
|---|---|
| **Signature** | `open_oxoria_file(self, opening_path: str \| Path) -> None` |
| **Arguments** | `opening_path: str \| Path` — path to the `.oxoria` file |
| **Returns** | `None` |
| **Notes** | Silently returns if the path does not exist, is not `.oxoria`, or cannot be parsed. Only items whose pointers exist in the current resource profile are restored. Updates `GBVar.OPENED_FILE`. |

---

### `open_resource_on_canvas`

Opens an image file and places it onto the canvas.

| | |
|---|---|
| **Signature** | `open_resource_on_canvas(self, img_path: str \| Path) -> None` |
| **Arguments** | `img_path: str \| Path` — path to the image file |
| **Returns** | `None` |

---

### `clear_canvas`

Removes all items from the canvas scene and resets `GBVar.OPENED_FILE`.

| | |
|---|---|
| **Signature** | `clear_canvas(self) -> None` |
| **Returns** | `None` |
| **Notes** | ⚠️ This is destructive. Call `save_file()` before invoking if preservation is needed. |

---

### `wrap_canvas`

Packages the current canvas and its associated image resources into an `.oxoarchive` file.

| | |
|---|---|
| **Signature** | `wrap_canvas(self, archive_path: str \| Path) -> None` |
| **Arguments** | `archive_path: str \| Path` — destination path for the archive |
| **Returns** | `None` |
| **Notes** | Creates a temporary directory `temp_export/` under `GBVar.DATA_DIR`, builds a zip archive, then renames it to `.oxoarchive`. The temp directory is removed after archiving. Only resources referenced by the current canvas are included. |

---

### `delete_item`

Removes a list of `ImageItem` instances from the canvas scene.

| | |
|---|---|
| **Signature** | `delete_item(self, items_to_delete: list[ImageItem]) -> None` |
| **Arguments** | `items_to_delete: list[ImageItem]` — list of items to remove |
| **Returns** | `None` |

---

### `get_selected`

Returns a list of currently selected items on the canvas.

| | |
|---|---|
| **Signature** | `get_selected(self) -> list[ImageItem]` |
| **Returns** | `list[ImageItem]` — currently selected scene items |

---

### `group_selected`

Groups all currently selected items into a single `QGraphicsItemGroup`.

| | |
|---|---|
| **Signature** | `group_selected(self) -> None` |
| **Returns** | `None` |

---

### `is_anything_selected`

Returns whether any item is currently selected on the canvas.

| | |
|---|---|
| **Signature** | `is_anything_selected(self) -> bool` |
| **Returns** | `bool` — `True` if at least one item is selected |

---

### `set_to_origin`

Resets the canvas view transform, centers on the origin, and applies a default zoom scale of `0.15`.

| | |
|---|---|
| **Signature** | `set_to_origin(self) -> None` |
| **Returns** | `None` |

---

### `set_pixmap`

Replaces the pixmap of an `ImageItem` on the canvas, updating both `base_pixmap` and the displayed scaled version.

| | |
|---|---|
| **Signature** | `set_pixmap(self, pixmap: QPixmap, image_item: ImageItem) -> None` |
| **Arguments** | `pixmap: QPixmap` — new pixmap to assign |
| | `image_item: ImageItem` — the target canvas item |
| **Returns** | `None` |

---

## app_api.py — `AppAPI`

### Overview

`AppAPI` handles application-level operations such as launching subprocesses and managing the application lifecycle.

---

### `__init__`

| | |
|---|---|
| **Signature** | `__init__(self)` |
| **Returns** | `None` |

---

### `run_capture_monitor`

Launches the screen capture monitor as a background process, if not already running.

| | |
|---|---|
| **Signature** | `run_capture_monitor(self) -> None` |
| **Returns** | `None` |
| **Notes** | Checks running processes via `psutil` before launching to prevent duplicate instances. The monitor script path is resolved relative to the module's location. |

---

### `open_new_window`

Opens a new Oxoria application window as an independent subprocess.

| | |
|---|---|
| **Signature** | `open_new_window(self) -> None` |
| **Returns** | `None` |
| **Notes** | Resolves and launches `__main__.py` in the application root directory. Prints an error to stdout if the entry script is not found. |

---

### `quit_app`

Quits the main Qt application.

| | |
|---|---|
| **Signature** | `quit_app(self) -> None` |
| **Returns** | `None` |
| **Notes** | Calls `GBVar.MAIN_APP.quit()`. Does nothing if `MAIN_APP` is `None`. |

---

## resources_api.py — `ResourcesAPI`

### Overview

`ResourcesAPI` manages the local image resource library: importing, profiling, tagging, and searching image assets identified by perceptual hash pointers.

---

### `__init__`

| | |
|---|---|
| **Signature** | `__init__(self, data_path: str \| None = None)` |
| **Arguments** | `data_path: str \| None` — override for the data directory; defaults to `GBVar.DATA_DIR` |
| **Returns** | `None` |
| **Notes** | On macOS (`Darwin`), sets `OMP_NUM_THREADS=1` to avoid OpenMP conflicts. |

---

### `clone_resource_to_repo`

Copies an image file into the local resource library directory.

| | |
|---|---|
| **Signature** | `clone_resource_to_repo(self, original_path: str, new_path: str) -> None` |
| **Arguments** | `original_path: str` — source file path |
| | `new_path: str` — destination filename (relative to `resources_lib/`) |
| **Returns** | `None` |
| **Notes** | Skips the copy if the destination already exists. |

---

### `check_exists`

Checks whether an image (by hash or path) already exists in the resource library.

| | |
|---|---|
| **Signature** | `check_exists(self, img_hash: str \| None, img_path: str \| None, tolerance: float = 0) -> tuple[str \| None, bool \| None]` |
| **Arguments** | `img_hash: str \| None` — precomputed hash; if `None`, computed from `img_path` |
| | `img_path: str \| None` — image file path; used to compute hash if `img_hash` is `None` |
| | `tolerance: float` — similarity tolerance for fuzzy matching; `0` = exact match (default: `0`) |
| **Returns** | `tuple[str \| None, bool \| None]` — `(hash_value, exists_flag)`; both `None` if neither argument is provided |

---

### `get_resources_profile`

Returns the full resource profile dictionary from `resources_profile.json`.

| | |
|---|---|
| **Signature** | `get_resources_profile(self) -> dict` |
| **Returns** | `dict` — all resource entries; empty dict if the profile file does not exist |

---

### `make_resource_profile`

Constructs a profile dictionary for a new resource (does not write to disk).

| | |
|---|---|
| **Signature** | `make_resource_profile(self, img_path: str, name: str = None, memo: str = None, tags: list[str] = None, make_clone_path: bool = True) -> dict` |
| **Arguments** | `img_path: str` — path to the image |
| | `name: str \| None` — display name; defaults to the filename stem |
| | `memo: str \| None` — free-text memo; defaults to `""` |
| | `tags: list[str] \| None` — list of tag strings; defaults to `[]` |
| | `make_clone_path: bool` — if `True`, stores only the filename (not the full path) in the profile (default: `True`) |
| **Returns** | `dict` — profile with keys `path`, `name`, `memo`, `tags` |

---

### `write_resource_profile`

Writes or updates a single resource entry in `resources_profile.json`.

| | |
|---|---|
| **Signature** | `write_resource_profile(self, pointer: str, profile: dict, merge: bool = False) -> bool` |
| **Arguments** | `pointer: str` — unique hash identifier for the resource |
| | `profile: dict` — profile data; must contain a `"path"` key |
| | `merge: bool` — if `True`, merges with the existing profile instead of replacing (default: `False`) |
| **Returns** | `bool` — `True` on success; `False` if `"path"` is missing from `profile` |

---

### `import_resource`

Imports an image into the resource library: adds its hash, writes its profile, and optionally copies the file.

| | |
|---|---|
| **Signature** | `import_resource(self, img_hash: str \| None, img_path: str \| None, profile: dict, skip_existencce_check: bool = True, tolerance: float = 0, make_clone: bool = True) -> bool` |
| **Arguments** | `img_hash: str \| None` — precomputed hash; computed from `img_path` if `None` |
| | `img_path: str \| None` — source image path |
| | `profile: dict` — resource profile dictionary |
| | `skip_existencce_check: bool` — if `True`, skips duplicate detection (default: `True`) |
| | `tolerance: float` — hash similarity tolerance for duplicate check (default: `0`) |
| | `make_clone: bool` — if `True`, copies the file into the repository (default: `True`) |
| **Returns** | `bool` — `True` on success; `False` if the resource already exists (when check is enabled) or if hash/path are both `None` |
| **Notes** | Note: the parameter name `skip_existencce_check` contains a typo (`existencce`) — use it as-is. |

---

### `pointer_to_path`

Resolves a resource pointer (hash) to its absolute file path.

| | |
|---|---|
| **Signature** | `pointer_to_path(self, pointer: str) -> str \| None` |
| **Arguments** | `pointer: str` — resource hash |
| **Returns** | `str \| None` — absolute path string, or `None` if not found |

---

### `path_to_pointer`

Finds the resource pointer associated with a stored relative path.

| | |
|---|---|
| **Signature** | `path_to_pointer(self, path: str) -> str \| None` |
| **Arguments** | `path: str` — relative path as stored in the profile |
| **Returns** | `str \| None` — pointer string, or `None` if not found |

---

### `name_to_path`

Looks up the relative path for a resource by its display name.

| | |
|---|---|
| **Signature** | `name_to_path(self, name: str) -> str \| None` |
| **Arguments** | `name: str` — display name of the resource |
| **Returns** | `str \| None` — relative path string, or `None` if not found |

---

### `filter_pointer_with_tag`

Returns all resource pointers that have the specified tag.

| | |
|---|---|
| **Signature** | `filter_pointer_with_tag(self, tag: str) -> list[str]` |
| **Arguments** | `tag: str` — tag string to filter by |
| **Returns** | `list[str]` — list of matching pointer strings |

---

### `filter_pointer_with_category`

Returns all resource pointers matching the specified category.

| | |
|---|---|
| **Signature** | `filter_pointer_with_category(self, category: str) -> list[str]` |
| **Arguments** | `category: str` — category value to filter by |
| **Returns** | `list[str]` — list of matching pointer strings |

---

### `filter_pointer_with_memo` *(Not implemented)*

| | |
|---|---|
| **Signature** | `filter_pointer_with_memo(self, kw: str)` |
| **Notes** | ⚠️ Method body is `pass`; not yet implemented. |

---

### `edit_memo`

Updates the memo field of a resource profile in place.

| | |
|---|---|
| **Signature** | `edit_memo(self, pointer: str, memo_text: str) -> None` |
| **Arguments** | `pointer: str` — resource hash |
| | `memo_text: str` — new memo content |
| **Returns** | `None` |

---

### `edit_tags`

Appends or removes tags from a resource's profile.

| | |
|---|---|
| **Signature** | `edit_tags(self, pointer: str, tags: list[str], mode: str = "append") -> None` |
| **Arguments** | `pointer: str` — resource hash |
| | `tags: list[str]` — tags to add or remove |
| | `mode: str` — `"append"` adds new tags (deduplicates); `"remove"` removes specified tags (default: `"append"`) |
| **Returns** | `None` |
| **Notes** | Silently returns if `pointer` is not in the current profile or if `mode` is unrecognized. |

---

## search_api.py — `SearchAPI`

### Overview

`SearchAPI` provides both semantic (vector-based) and fuzzy string-based search over the resource library's keywords and names.

---

### `__init__`

| | |
|---|---|
| **Signature** | `__init__(self)` |
| **Returns** | `None` |
| **Notes** | Initializes `UseVector`, `SearchBase`, and `FaissIndexBase` internally. |

---

### `append_search_base`

Adds a keyword to the FAISS vector index and the in-memory search base.

| | |
|---|---|
| **Signature** | `append_search_base(self, kw: str) -> None` |
| **Arguments** | `kw: str` — keyword string to index |
| **Returns** | `None` |

---

### `semantic_search_kw`

Searches for the most semantically similar keywords to the query using the FAISS index.

| | |
|---|---|
| **Signature** | `semantic_search_kw(self, kw: str, return_num: int = 3) -> list[str]` |
| **Arguments** | `kw: str` — query keyword |
| | `return_num: int` — maximum number of results to return (default: `3`) |
| **Returns** | `list[str]` — list of matching keyword strings; may be shorter than `return_num` if the search base is small |
| **Notes** | Uses a distance cutoff of `0.65`; results below this threshold are excluded. |

---

### `semantic_search_kw_to_pointer`

Performs semantic search and maps the results back to resource pointers.

| | |
|---|---|
| **Signature** | `semantic_search_kw_to_pointer(self, kw: str, return_num: int = 3) -> list[str]` |
| **Arguments** | `kw: str` — query keyword |
| | `return_num: int` — number of results to return (default: `3`) |
| **Returns** | `list[str \| None]` — list of length `return_num`; positions without a matching pointer contain `None` |
| **Notes** | Matches are made by comparing search results against the `"memo"` field of each resource profile. |

---

### `distance_search_kw`

Searches for resources by fuzzy string matching on display names using `difflib`.

| | |
|---|---|
| **Signature** | `distance_search_kw(self, kw: str, return_num: int = 3, cutoff: float = 0.5) -> list[str]` |
| **Arguments** | `kw: str` — query string |
| | `return_num: int` — maximum number of results (default: `3`) |
| | `cutoff: float` — minimum similarity score `[0.0, 1.0]`; results below this are discarded (default: `0.5`) |
| **Returns** | `list[str]` — list of resource pointer strings matching the name query |
| **Notes** | The `cutoff` parameter in the function signature is accepted but the internal `difflib.get_close_matches` call currently hardcodes `cutoff=0.5`, ignoring the passed value. |