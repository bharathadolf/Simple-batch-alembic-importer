import hou
import os
import re
from PySide2 import QtWidgets, QtCore, QtGui


class AlembicImportTool(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(AlembicImportTool, self).__init__(parent)

        self.setWindowTitle("Enhanced Alembic Import Tool")
        self.resize(750, 600)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # =====================================
        # 1. FOLDER SELECTION
        # =====================================
        folder_layout = QtWidgets.QHBoxLayout()
        self.folder_edit = DropLineEdit(self)
        self.folder_edit.setPlaceholderText("Drag or select a folder containing Alembic files...")
        self.browse_btn = QtWidgets.QPushButton("📁 Browse")
        self.browse_btn.setFixedWidth(100)

        self.browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(self.browse_btn)

        main_layout.addLayout(folder_layout)

        # =====================================
        # 2. FILTER SETTINGS (Collapsible Group)
        # =====================================
        filter_group = QtWidgets.QGroupBox("🔍 Filter Settings")
        filter_group.setCheckable(True)
        filter_group.setChecked(False)  # collapsed by default
        filter_layout = QtWidgets.QFormLayout()

        self.filter_edit = QtWidgets.QLineEdit("*")
        self.filter_edit.setToolTip("Wildcard pattern, e.g., *hero*.abc")
        filter_layout.addRow("File Pattern:", self.filter_edit)

        self.exclude_edit = QtWidgets.QLineEdit("_sim,_vel,_proxy")
        self.exclude_edit.setToolTip("Comma-separated keywords to exclude")
        filter_layout.addRow("Exclude Keywords:", self.exclude_edit)

        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)

        # =====================================
        # 3. FILE LIST + SELECT/DESELECT
        # =====================================
        list_group = QtWidgets.QGroupBox("📁 Alembic Files to Import")
        list_layout = QtWidgets.QVBoxLayout()

        self.file_list = QtWidgets.QListWidget()
        self.file_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.file_list.setAlternatingRowColors(True)
        list_layout.addWidget(self.file_list)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        self.select_all_btn = QtWidgets.QPushButton("✅ Select All")
        self.deselect_all_btn = QtWidgets.QPushButton("❌ Deselect All")
        self.select_all_btn.setFixedWidth(120)
        self.deselect_all_btn.setFixedWidth(120)
        self.select_all_btn.clicked.connect(self.select_all_files)
        self.deselect_all_btn.clicked.connect(self.deselect_all_files)
        btn_row.addWidget(self.select_all_btn)
        btn_row.addWidget(self.deselect_all_btn)
        list_layout.addLayout(btn_row)

        list_group.setLayout(list_layout)
        main_layout.addWidget(list_group)

        # =====================================
        # 4. PREVIEW & METADATA
        # =====================================
        preview_group = QtWidgets.QGroupBox("📊 Metadata Preview")
        preview_layout = QtWidgets.QVBoxLayout()

        self.metadata_label = QtWidgets.QLabel("No file selected")
        self.metadata_label.setWordWrap(True)
        preview_layout.addWidget(self.metadata_label)

        self.thumbnail_label = QtWidgets.QLabel("🖼️ No preview available")
        self.thumbnail_label.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail_label.setStyleSheet("border: 1px solid #555; background:#2a2a2a;")
        self.thumbnail_label.setMinimumHeight(100)
        preview_layout.addWidget(self.thumbnail_label)

        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)

        # Connect preview update
        self.file_list.currentItemChanged.connect(self.update_preview)

        # =====================================
        # 5. IMPORT OPTIONS
        # =====================================
        options_group = QtWidgets.QGroupBox("⚙️ Import Options")
        options_layout = QtWidgets.QGridLayout()

        self.subnet_cb = QtWidgets.QCheckBox("Group in Subnets")
        self.subnet_cb.setChecked(True)
        options_layout.addWidget(self.subnet_cb, 0, 0)

        self.avoid_dupes_cb = QtWidgets.QCheckBox("Avoid Duplicates")
        self.avoid_dupes_cb.setChecked(True)
        options_layout.addWidget(self.avoid_dupes_cb, 0, 1)

        self.reload_dupes_cb = QtWidgets.QCheckBox("Reload Existing")
        self.reload_dupes_cb.setChecked(False)
        options_layout.addWidget(self.reload_dupes_cb, 1, 0)

        self.create_rop_cb = QtWidgets.QCheckBox("Create ROP Alembic (instead of Archive)")
        options_layout.addWidget(self.create_rop_cb, 1, 1)

        self.dry_run_cb = QtWidgets.QCheckBox("🧪 Dry Run (Simulate Only)")
        self.dry_run_cb.setChecked(False)
        options_layout.addWidget(self.dry_run_cb, 2, 0, 1, 2)

        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # =====================================
        # 6. LOG & PROGRESS
        # =====================================
        self.log_box = QtWidgets.QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(90)
        self.log_box.setStyleSheet("font-size: 11px; color: #ccc; background:#1e1e1e;")
        main_layout.addWidget(self.log_box)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(10)
        main_layout.addWidget(self.progress_bar)

        # =====================================
        # 7. ACTION BUTTONS (Bottom Row)
        # =====================================
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()

        self.scan_btn = QtWidgets.QPushButton("🔍 Scan Folder")
        self.scan_btn.clicked.connect(self.scan_folder)
        self.scan_btn.setStyleSheet("padding: 6px; min-width: 100px;")

        self.cancel_btn = QtWidgets.QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("padding: 6px; min-width: 90px;")

        self.import_btn = QtWidgets.QPushButton("🚀 Import")
        self.import_btn.clicked.connect(self.import_selected)
        self.import_btn.setStyleSheet("font-weight: bold; background-color: #3a6b8b; color: white; padding: 6px; min-width: 100px;")

        button_layout.addWidget(self.scan_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.import_btn)

        main_layout.addLayout(button_layout)

        # Connect folder change to auto-scan (optional)
        self.folder_edit.textChanged.connect(self.on_folder_changed)

    def browse_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Base Folder")
        if folder:
            self.folder_edit.setText(folder)

    def on_folder_changed(self):
        # Optional: auto-scan when folder is pasted or dropped
        pass

    def select_all_files(self):
        for i in range(self.file_list.count()):
            self.file_list.item(i).setCheckState(QtCore.Qt.Checked)

    def deselect_all_files(self):
        for i in range(self.file_list.count()):
            self.file_list.item(i).setCheckState(QtCore.Qt.Unchecked)

    def scan_folder(self):
        self.file_list.clear()
        base_folder = self.folder_edit.text().strip()
        if not base_folder or not os.path.isdir(base_folder):
            self.log("❌ Invalid folder path")
            return

        pattern_text = self.filter_edit.text().strip()
        exclude_keys = [k.strip().lower() for k in self.exclude_edit.text().split(",") if k.strip()]

        if pattern_text == "*":
            pattern_regex = r".*\.abc$"
        else:
            pattern_regex = pattern_text.replace(".", "\\.").replace("*", ".*") + r"\.abc$"

        try:
            re.compile(pattern_regex)
        except Exception as e:
            self.log(f"❌ Invalid filter pattern: {e}")
            return

        alembic_files = []
        for root, dirs, files in os.walk(base_folder):
            for f in files:
                if not f.lower().endswith(".abc"):
                    continue
                if not re.search(pattern_regex, f, re.IGNORECASE):
                    continue
                if any(key in f.lower() for key in exclude_keys):
                    continue
                alembic_files.append(os.path.join(root, f))

        if not alembic_files:
            self.log("⚠️ No matching Alembic files found.")
            return

        for path in alembic_files:
            item = QtWidgets.QListWidgetItem(os.path.basename(path))
            item.setData(QtCore.Qt.UserRole, path)
            item.setCheckState(QtCore.Qt.Checked)
            self.file_list.addItem(item)

        self.log(f"✅ Found {len(alembic_files)} matching file(s).")

    def update_preview(self, current, previous):
        if not current:
            self.metadata_label.setText("No file selected")
            self.thumbnail_label.setText("🖼️ No preview available")
            return

        path = current.data(QtCore.Qt.UserRole)
        if not os.path.exists(path):
            self.metadata_label.setText("File not found")
            return

        stat = os.stat(path)
        size_mb = stat.st_size / (1024 * 1024)
        mtime = QtCore.QDateTime.fromSecsSinceEpoch(int(stat.st_mtime)).toString("yyyy-MM-dd hh:mm")

        node_type = "ROP Alembic" if self.create_rop_cb.isChecked() else "Alembic Archive"
        metadata = f"""
        <b>🔤 Name:</b> {os.path.basename(path)}<br>
        <b>📦 Size:</b> {size_mb:.2f} MB<br>
        <b>🕒 Modified:</b> {mtime}<br>
        <b>🛠️ Type:</b> {node_type}
        """
        self.metadata_label.setText(metadata)
        self.thumbnail_label.setText("🖼️ Preview not available")

    def sanitize_node_name(self, name):
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        if not name or name[0].isdigit():
            name = "_" + name
        return name

    def import_selected(self):
        selected_items = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                selected_items.append((item.data(QtCore.Qt.UserRole), item.text()))

        if not selected_items:
            self.log("⚠️ No files selected.")
            return

        obj = hou.node("/obj")
        if not obj:
            self.log("❌ Could not find /obj context")
            return

        scene_null = obj.node("SCENE")
        if not scene_null and not self.dry_run_cb.isChecked():
            scene_null = obj.createNode("null", node_name="SCENE")
            scene_null.moveToGoodPosition()

        existing_nodes = {node.name(): node for node in obj.children()} if self.avoid_dupes_cb.isChecked() else {}
        imported = reloaded = skipped = 0

        self.progress_bar.setMaximum(len(selected_items))
        self.progress_bar.setValue(0)

        for idx, (path, display_name) in enumerate(selected_items):
            if not os.path.exists(path):
                self.log(f"❌ Not found: {path}")
                continue

            base_name = os.path.splitext(os.path.basename(path))[0]
            safe_name = self.sanitize_node_name(base_name)

            action = "import_new"
            if safe_name in existing_nodes:
                node = existing_nodes[safe_name]
                is_rop = "rop_alembic" == node.type().name()
                is_archive = "alembicarchive" in node.type().name()
                if self.reload_dupes_cb.isChecked():
                    if self.create_rop_cb.isChecked() and is_rop:
                        action = "reload_rop"
                    elif not self.create_rop_cb.isChecked() and is_archive:
                        action = "reload_archive"
                    else:
                        action = "skip_mismatch"
                else:
                    action = "skip_duplicate"

            # Dry Run: Just log
            if self.dry_run_cb.isChecked():
                msg_map = {
                    "import_new": "🆕 Would import",
                    "reload_rop": "🔄 Would reload ROP",
                    "reload_archive": "🔄 Would reload archive",
                    "skip_duplicate": "⏭️ Would skip (exists)",
                    "skip_mismatch": "⚠️ Would skip (type mismatch)"
                }
                self.log(f"{msg_map[action]}: {safe_name}")
            else:
                try:
                    if action == "reload_rop":
                        node.parm("filename").set(path)
                        node.parm("execute").pressButton()
                        reloaded += 1
                        self.log(f"🔄 Reloaded ROP: {safe_name}")
                    elif action == "reload_archive":
                        node.parm("fileName").set(path)
                        node.parm("reload").pressButton()
                        reloaded += 1
                        self.log(f"🔄 Reloaded Archive: {safe_name}")
                    elif action == "import_new":
                        if self.create_rop_cb.isChecked():
                            node = obj.createNode("rop_alembic", node_name=safe_name)
                            node.parm("filename").set(path)
                        else:
                            node = obj.createNode("alembicarchive", node_name=safe_name)
                            node.parm("fileName").set(path)
                        node.moveToGoodPosition()

                        if self.subnet_cb.isChecked():
                            subnet = obj.createNode("subnet", node_name=f"{safe_name}_subnet")
                            subnet.setName(f"{safe_name}_subnet", unique_name=True)
                            subnet.moveToGoodPosition()
                            node.setParent(subnet)
                            node.setPosition([0, 0])
                            subnet.layoutChildren()
                            if scene_null:
                                subnet.setNextInput(scene_null)
                        else:
                            if scene_null:
                                node.setNextInput(scene_null)

                        imported += 1
                        self.log(f"✅ Imported: {safe_name}")
                    else:
                        skipped += 1
                        self.log(f"{msg_map[action]}: {safe_name}")
                except Exception as e:
                    self.log(f"❌ Error: {safe_name} → {e}")

            self.progress_bar.setValue(idx + 1)
            QtWidgets.QApplication.processEvents()

        if self.dry_run_cb.isChecked():
            self.log(f"🧪 Dry Run Complete: {imported + reloaded + skipped} files analyzed.")
        else:
            self.log(f"🎉 Done: {imported} imported, {reloaded} reloaded, {skipped} skipped.")

    def log(self, message):
        timestamp = QtCore.QTime.currentTime().toString("hh:mm:ss")
        self.log_box.append(f"[{timestamp}] {message}")
        self.log_box.ensureCursorVisible()


# ================================
# Drag & Drop LineEdit
# ================================
class DropLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super(DropLineEdit, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            if os.path.isdir(url.toLocalFile()):
                event.acceptProposedAction()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0]
        path = url.toLocalFile()
        if os.path.isdir(path):
            self.setText(path)


# ================================
# Launch Function
# ================================
def show_alembic_import_tool():
    parent = hou.ui.mainQtWindow()
    dialog = AlembicImportTool(parent)
    dialog.show()
    return dialog


# Run
show_alembic_import_tool()