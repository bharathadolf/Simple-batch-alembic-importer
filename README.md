# Simple Batch Alembic Importer

A lightweight Python / PySide2 tool for **SideFX Houdini** to batch import and organize multiple Alembic (`.abc`) cache files in one go.

![Demo](assets/demo.gif)

*(Full 1080p recording available in the repo: [Alembic importer.mp4](Alembic%20importer.mp4))*

---

## Why I Built This

I developed this tool while doing some freelance pipeline work for a small animation & VFX studio in Hyderabad. 

Their layout and lighting artists were receiving shots with dozens of separate Alembic caches (characters, props, crowd, environment elements). Bringing them into Houdini manually one by one, setting paths, building subnets, and renaming nodes to match their internal pipeline standards was tedious and eating up too much production time.

On top of that, cache directories often had simulation scratch files, velocity passes, and proxies dumped in the same folders (`_sim`, `_vel`, `_proxy`) that the lighting team didn't want in their scene. 

This tool automates that entire handoff: point it to a folder, filter out unwanted passes, sanitize names according to Houdini syntax, and bring everything in organized cleanly under a central `SCENE` null.

---

## Features

- **Drag & Drop Folder Loading:** Drag a shot or cache folder straight from your OS file explorer into the dialog, or use the Browse button.
- **Recursive Scanning:** Finds all `.abc` files in subdirectories automatically.
- **Pattern & Keyword Filtering:**
  - Wildcard pattern matching (e.g. `*char*` or `shot_020_*`).
  - Exclusion list (defaults to `_sim, _vel, _proxy`) so artists don't accidentally pull in heavy simulation or proxy data.
- **Studio Naming Sanitization:** Automatically cleans up file basenames into valid Houdini node names (strips illegal characters, prefixes digits with underscores).
- **Import Modes:**
  - Standard **Alembic Archive** (`alembicarchive`) for layout/lighting.
  - **ROP Alembic** (`rop_alembic`) if you need output nodes for caching or processing.
- **Subnet Organization:** Groups each imported asset inside its own subnet container and runs an auto-layout so the network editor stays clean.
- **Auto-connect to SCENE Null:** Automatically looks for (or creates) an `/obj/SCENE` null node and wires all imported nodes/subnets into it.
- **Duplicate & Reload Handling:**
  - Option to skip already imported files.
  - Option to reload existing nodes (updates the path and hits reload on the node).
- **Dry Run Mode:** Test your filter settings first without creating any nodes in your scene. The log will print exactly what would be imported, reloaded, or skipped.
- **File Metadata Preview:** Click any file in the list to check its size (MB) and last modified timestamp before importing.

---

## Installation & Running in Houdini

You don't need any complex installation. Just run the script inside Houdini.

### Option 1: Add it as a Shelf Tool (Recommended)

1. Right-click on any shelf in Houdini and choose **New Tool...**
2. Name it `batch_alembic_importer` and set the label to `Alembic Importer`.
3. Under the **Script** tab, set the language to **Python** and add:

```python
import sys

# Update this path to where you cloned or saved the folder
tool_dir = r"D:/Alembic Importer"

if tool_dir not in sys.path:
    sys.path.append(tool_dir)

import Alembic_importer
Alembic_importer.show_alembic_import_tool()
```

4. Hit **Apply** and click the new shelf button to open the window.

### Option 2: Python Source Editor / Python Shell

You can also paste the contents of `Alembic_importer.py` into Houdini's **Python Source Editor** (**Windows > Python Source Editor**) or run it directly from the **Python Shell**:

```python
exec(open(r"D:/Alembic Importer/Alembic_importer.py").read())
```

---

## Typical Workflow

1. Paste or drag your cache folder into the **Base Folder** field.
2. (Optional) Adjust your **File Pattern** and **Exclude Keywords** if you only want specific assets.
3. Click **Scan Folder**.
4. Check or uncheck files from the list as needed.
5. Choose your options:
   - Keep **Group in Subnets** checked if you want each asset inside a subnet.
   - Turn on **Dry Run** if you want to inspect the log before modifying your scene.
6. Click **Import**.

---

## Requirements

- **SideFX Houdini:** Tested on Houdini 18.5, 19.x, and 20.x
- **Python:** Python 3 (standard with modern Houdini installs)
- **GUI:** PySide2 (comes built-in with Houdini)
- **OS:** Windows, Linux, macOS

---

## License

MIT License. Feel free to modify and use it in your own personal or studio pipelines.
