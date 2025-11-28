from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QTextEdit,
    QPushButton,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QMessageBox,
    QInputDialog,
)
from PySide6.QtCore import QThread, Signal
from .providers import ProviderManager
from .presets import PresetManager
from .generator import ImageGenerator
from .importer import ImageImporter
from .exporter import NodeExporter
from .settings import SettingsManager
import os


class GenerationWorker(QThread):
    """
    Worker thread for image generation to prevent UI freezing.
    """

    finished = Signal(bool, str)

    def __init__(
        self,
        generator,
        prompt,
        provider_name,
        resolution,
        search_web,
        debug_mode,
        input_image_path,
    ):
        super().__init__()
        self.generator = generator
        self.prompt = prompt
        self.provider_name = provider_name
        self.resolution = resolution
        self.search_web = search_web
        self.debug_mode = debug_mode
        self.input_image_path = input_image_path

    def run(self):
        try:
            success, result = self.generator.generate_image(
                self.prompt,
                self.provider_name,
                resolution=self.resolution,
                search_web=self.search_web,
                debug_mode=self.debug_mode,
                input_image_path=self.input_image_path,
            )
            self.finished.emit(success, str(result))
        except Exception as e:
            self.finished.emit(False, str(e))


class SDBananaPanel(QWidget):
    """
    SDBanana Main Panel
    Contains two tabs: Generate and Settings
    """

    def __init__(self, parent=None):
        super(SDBananaPanel, self).__init__(parent)
        self.provider_manager = ProviderManager()
        self.preset_manager = PresetManager()
        self.image_generator = ImageGenerator(self.provider_manager)
        self.importer = ImageImporter()
        self.exporter = NodeExporter()

        self.settings_manager = SettingsManager()
        self.current_settings = self.settings_manager.settings
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        # Main Layout
        main_layout = QVBoxLayout()

        # Title
        title_label = QLabel("🍌 SD Banana by LiuYang")
        title_label.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """
        )
        main_layout.addWidget(title_label)

        # Tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #444444;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #1e1e1e;
                color: #cccccc;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #3e3e3e;
            }
        """
        )

        # Tab 1 - Generate
        tab1 = self.create_generation_tab()
        self.tab_widget.addTab(tab1, "Generate")

        # Tab 2 - Settings
        tab2 = self.create_settings_tab()
        self.tab_widget.addTab(tab2, "Settings")

        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)
        self.setMinimumSize(450, 650)

    def create_generation_tab(self):
        """Create Generation Tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # --- Presets Section ---
        # First row: Label and ComboBox
        preset_row1 = QWidget()
        preset_row1_layout = QHBoxLayout(preset_row1)
        preset_row1_layout.setContentsMargins(0, 0, 0, 0)

        preset_label = QLabel("Prompt Presets:")
        preset_label.setStyleSheet("color: #cccccc; font-weight: bold;")
        preset_row1_layout.addWidget(preset_label)

        self.preset_combo = QComboBox()
        self.preset_combo.setStyleSheet(self._get_combo_style())
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        preset_row1_layout.addWidget(self.preset_combo, 1)

        # Add arrow indicator
        arrow_label = QLabel("▼")
        arrow_label.setStyleSheet("color: #888888; font-size: 10px; padding-left: 2px;")
        preset_row1_layout.addWidget(arrow_label)

        layout.addWidget(preset_row1)

        # Second row: Buttons
        preset_row2 = QWidget()
        preset_row2_layout = QHBoxLayout(preset_row2)
        preset_row2_layout.setContentsMargins(0, 5, 0, 0)

        btn_style = """
            QPushButton {
                background-color: #444444;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                text-align: left;
                padding-left: 10px;
            }
            QPushButton:hover { background-color: #555555; }
        """

        self.btn_add_preset = QPushButton("+")
        self.btn_add_preset.setFixedWidth(30)
        self.btn_add_preset.setStyleSheet(btn_style)
        self.btn_add_preset.clicked.connect(self.on_add_preset)
        preset_row2_layout.addWidget(self.btn_add_preset)

        self.btn_save_preset = QPushButton("Save")
        self.btn_save_preset.setFixedWidth(60)
        self.btn_save_preset.setStyleSheet(btn_style)
        self.btn_save_preset.clicked.connect(self.on_save_preset)
        preset_row2_layout.addWidget(self.btn_save_preset)

        self.btn_rename_preset = QPushButton("Rename")
        self.btn_rename_preset.setFixedWidth(70)
        self.btn_rename_preset.setStyleSheet(btn_style)
        self.btn_rename_preset.clicked.connect(self.on_rename_preset)
        preset_row2_layout.addWidget(self.btn_rename_preset)

        self.btn_del_preset = QPushButton("Del")
        self.btn_del_preset.setFixedWidth(50)
        self.btn_del_preset.setStyleSheet(btn_style)
        self.btn_del_preset.clicked.connect(self.on_delete_preset)
        preset_row2_layout.addWidget(self.btn_del_preset)

        preset_row2_layout.addStretch()

        layout.addWidget(preset_row2)

        # Prompt Input
        prompt_label = QLabel("Prompt:")
        prompt_label.setStyleSheet("color: #cccccc; font-weight: bold; padding: 5px;")
        layout.addWidget(prompt_label)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "Enter your image generation prompt here..."
        )
        self.prompt_input.setMinimumHeight(150)
        self.prompt_input.setStyleSheet(
            """
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """
        )
        layout.addWidget(self.prompt_input)

        # Generate Button Area
        gen_group = QWidget()
        gen_layout = QHBoxLayout(gen_group)
        gen_layout.setContentsMargins(0, 10, 0, 10)

        self.generate_button = QPushButton("🎨 Generate Image")
        self.generate_button.setMinimumHeight(40)
        self.generate_button.setStyleSheet(
            """
            QPushButton {
                background-color: #0066cc;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0077ee;
            }
            QPushButton:pressed {
                background-color: #0055aa;
            }
            QPushButton:disabled {
                background-color: #444444;
                color: #888888;
            }
        """
        )
        self.generate_button.clicked.connect(self.on_generate_clicked)
        gen_layout.addWidget(self.generate_button, 2)

        # Regenerate and Load Last Prompt buttons removed

        layout.addWidget(gen_group)

        # Resolution
        res_group = QWidget()
        res_layout = QHBoxLayout(res_group)
        res_layout.setContentsMargins(0, 0, 0, 0)

        res_label = QLabel("Output Resolution:")
        res_label.setStyleSheet("color: #cccccc; font-weight: bold;")
        res_layout.addWidget(res_label)

        self.res_combo = QComboBox()
        self.res_combo.addItems(["1K", "2K", "4K"])
        self.res_combo.setStyleSheet(self._get_combo_style())
        res_layout.addWidget(self.res_combo)

        # Add arrow indicator
        arrow_label = QLabel("▼")
        arrow_label.setStyleSheet("color: #888888; font-size: 10px; padding-left: 2px;")
        res_layout.addWidget(arrow_label)

        # Search Web Toggle removed

        res_layout.addStretch()

        layout.addWidget(res_group)

        # Test Import Button
        self.test_import_btn = QPushButton("Test Import Last Generated Image")
        self.test_import_btn.clicked.connect(self.on_test_import_clicked)
        self.test_import_btn.setVisible(self.current_settings.get("debug_mode", False))
        layout.addWidget(self.test_import_btn)

        # Export Selected Nodes Button
        self.export_nodes_btn = QPushButton("Export Selected Nodes (WebP)")
        self.export_nodes_btn.clicked.connect(self.on_export_nodes_clicked)
        self.export_nodes_btn.setVisible(self.current_settings.get("debug_mode", False))
        layout.addWidget(self.export_nodes_btn)

        # Spacer
        layout.addStretch()

        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #888888;
                padding: 5px;
                font-style: italic;
            }
        """
        )
        layout.addWidget(self.status_label)

        # Populate Presets
        self.refresh_presets_ui()

        tab.setLayout(layout)
        return tab

    def create_settings_tab(self):
        """Create Settings Tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # --- Provider Section ---
        provider_group = QWidget()
        provider_layout = QHBoxLayout(provider_group)
        provider_layout.setContentsMargins(0, 0, 0, 0)

        provider_label = QLabel("Provider:")
        provider_label.setStyleSheet("color: #cccccc; font-weight: bold;")
        provider_layout.addWidget(provider_label)

        self.provider_combo = QComboBox()
        self.provider_combo.setStyleSheet(self._get_combo_style())
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo, 1)  # Stretch factor 1

        # Add arrow indicator
        arrow_label = QLabel("▼")
        arrow_label.setStyleSheet("color: #888888; font-size: 10px; padding-left: 2px;")
        provider_layout.addWidget(arrow_label)

        # Provider Actions
        btn_style = """
            QPushButton {
                background-color: #444444;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                text-align: left;
                padding-left: 10px;
            }
            QPushButton:hover { background-color: #555555; }
        """

        self.btn_add = QPushButton("+")
        self.btn_add.setFixedWidth(30)
        self.btn_add.setStyleSheet(btn_style)
        self.btn_add.clicked.connect(self.on_add_provider)
        provider_layout.addWidget(self.btn_add)

        self.btn_save = QPushButton("Save")
        self.btn_save.setFixedWidth(50)
        self.btn_save.setStyleSheet(btn_style)
        self.btn_save.clicked.connect(self.on_save_provider)
        provider_layout.addWidget(self.btn_save)

        self.btn_del = QPushButton("Del")
        self.btn_del.setFixedWidth(40)
        self.btn_del.setStyleSheet(btn_style)
        self.btn_del.clicked.connect(self.on_delete_provider)
        provider_layout.addWidget(self.btn_del)

        layout.addWidget(provider_group)

        # Test Connection Button (Separate row for better visibility)
        self.btn_test = QPushButton("Test Connection")
        self.btn_test.setStyleSheet(btn_style)
        self.btn_test.clicked.connect(self.on_test_connection)
        layout.addWidget(self.btn_test)

        # --- Fields ---
        # API Key
        key_label = QLabel("API Key:")
        key_label.setStyleSheet("color: #cccccc; font-weight: bold; padding-top: 10px;")
        layout.addWidget(key_label)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter your API key...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setStyleSheet(self._get_input_style())
        layout.addWidget(self.key_input)

        # Base URL
        url_label = QLabel("Base URL:")
        url_label.setStyleSheet("color: #cccccc; font-weight: bold; padding-top: 10px;")
        layout.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://api.example.com/v1")
        self.url_input.setStyleSheet(self._get_input_style())
        layout.addWidget(self.url_input)

        # Model
        model_label = QLabel("Model ID:")
        model_label.setStyleSheet(
            "color: #cccccc; font-weight: bold; padding-top: 10px;"
        )
        layout.addWidget(model_label)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("gemini-3-pro-image-preview")
        self.model_input.setStyleSheet(self._get_input_style())
        layout.addWidget(self.model_input)

        # --- Debug ---
        self.chk_debug = QCheckBox("Enable Debug Mode (Log prompts & keep temp images)")
        self.chk_debug.setStyleSheet(
            """
            QCheckBox {
                color: #cccccc;
                padding-top: 15px;
                padding-bottom: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """
        )
        self.chk_debug.setChecked(self.current_settings.get("debug_mode", False))
        self.chk_debug.stateChanged.connect(self.on_debug_changed)
        layout.addWidget(self.chk_debug)

        self.chk_save_images = QCheckBox("Save Generated Images")
        self.chk_save_images.setStyleSheet(
            """
            QCheckBox {
                color: #cccccc;
                padding-top: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """
        )
        self.chk_save_images.setChecked(
            self.current_settings.get("save_generated_images", False)
        )
        self.chk_save_images.stateChanged.connect(self.on_save_images_changed)
        layout.addWidget(self.chk_save_images)

        # Spacer
        layout.addStretch()

        # Populate Providers
        self.refresh_providers_ui()

        tab.setLayout(layout)
        return tab

    def _get_combo_style(self):
        return """
            QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px 8px;
            }
            QComboBox::drop-down {
                width: 0px;
                border: none;
            }
        """

    def _get_input_style(self):
        return """
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
            }
        """

    # --- Provider Event Handlers ---

    def refresh_providers_ui(self):
        """Reload provider list into combo box"""
        self.provider_combo.blockSignals(True)
        self.provider_combo.clear()
        names = self.provider_manager.get_all_names()
        self.provider_combo.addItems(names)

        # Try to restore saved selection first
        saved_provider = self.current_settings.get("selected_provider")
        index = -1

        if saved_provider:
            index = self.provider_combo.findText(saved_provider)

        # If saved provider not found or doesn't exist, use first provider
        if index < 0 and self.provider_combo.count() > 0:
            index = 0

        if index >= 0:
            self.provider_combo.setCurrentIndex(index)

        self.provider_combo.blockSignals(False)
        self.on_provider_changed()  # Update fields

    def on_provider_changed(self):
        """Update input fields when provider selection changes"""
        name = self.provider_combo.currentText()
        provider = self.provider_manager.get_provider(name)
        if provider:
            self.key_input.setText(provider.get("apiKey", ""))
            self.url_input.setText(provider.get("baseUrl", ""))
            self.model_input.setText(provider.get("model", ""))

        # Save selected provider to settings
        if name:
            self.current_settings["selected_provider"] = name
            self.settings_manager.set("selected_provider", name)

    def on_add_provider(self):
        text, ok = QInputDialog.getText(
            self, "Add Provider", "Enter new provider name:"
        )
        if ok and text:
            success, msg = self.provider_manager.add_provider(text)
            if success:
                self.refresh_providers_ui()
                # Select the new one
                index = self.provider_combo.findText(text)
                if index >= 0:
                    self.provider_combo.setCurrentIndex(index)
            else:
                QMessageBox.warning(self, "Error", msg)

    def on_save_provider(self):
        name = self.provider_combo.currentText()
        if not name:
            return

        success, msg = self.provider_manager.update_provider(
            name, self.key_input.text(), self.url_input.text(), self.model_input.text()
        )
        if success:
            QMessageBox.information(self, "Success", "Provider configuration saved!")
        else:
            QMessageBox.warning(self, "Error", msg)

    def on_delete_provider(self):
        name = self.provider_combo.currentText()
        if not name:
            return

        if self.provider_combo.count() <= 1:
            QMessageBox.warning(self, "Warning", "Cannot delete the last provider.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            success, msg = self.provider_manager.delete_provider(name)
            if success:
                self.refresh_providers_ui()
            else:
                QMessageBox.warning(self, "Error", msg)

    def on_test_connection(self):
        name = self.provider_combo.currentText()
        if not name:
            return

        # Use current values from inputs, not just saved ones
        temp_config = {
            "name": name,
            "apiKey": self.key_input.text(),
            "baseUrl": self.url_input.text(),
            "model": self.model_input.text(),
        }

        self.status_label.setText("Testing connection...")
        QtWidgets.QApplication.processEvents()  # Force UI update

        success, msg = self.provider_manager.test_connection(temp_config)

        self.status_label.setText("Ready")

        if success:
            QMessageBox.information(self, "Connection Successful", msg)
        else:
            QMessageBox.critical(self, "Connection Failed", msg)

    def on_debug_changed(self, state):
        is_checked = state == QtCore.Qt.Checked
        self.current_settings["debug_mode"] = is_checked
        self.settings_manager.set("debug_mode", is_checked)

        # Toggle visibility of debug buttons
        if hasattr(self, "test_import_btn"):
            self.test_import_btn.setVisible(is_checked)
        if hasattr(self, "export_nodes_btn"):
            self.export_nodes_btn.setVisible(is_checked)

        if is_checked:
            print("Debug Mode Enabled")

    def on_save_images_changed(self, state):
        is_checked = state == QtCore.Qt.Checked
        self.current_settings["save_generated_images"] = is_checked
        self.settings_manager.set("save_generated_images", is_checked)
        if is_checked:
            print("Save Generated Images Enabled")

    # --- Preset Event Handlers ---

    def refresh_presets_ui(self):
        current_text = self.preset_combo.currentText()
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        names = self.preset_manager.get_all_names()
        self.preset_combo.addItems(names)

        index = self.preset_combo.findText(current_text)
        if index >= 0:
            self.preset_combo.setCurrentIndex(index)

        self.preset_combo.blockSignals(False)

    def on_preset_changed(self):
        name = self.preset_combo.currentText()
        prompt = self.preset_manager.get_prompt(name)
        if prompt:
            self.prompt_input.setText(prompt)

    def on_add_preset(self):
        text, ok = QInputDialog.getText(self, "Add Preset", "Enter new preset name:")
        if ok and text:
            success, msg = self.preset_manager.add_preset(
                text, self.prompt_input.toPlainText()
            )
            if success:
                self.refresh_presets_ui()
                index = self.preset_combo.findText(text)
                if index >= 0:
                    self.preset_combo.setCurrentIndex(index)
            else:
                QMessageBox.warning(self, "Error", msg)

    def on_save_preset(self):
        name = self.preset_combo.currentText()
        if not name:
            return

        success, msg = self.preset_manager.update_preset(
            name, self.prompt_input.toPlainText()
        )
        if success:
            QMessageBox.information(self, "Success", "Preset saved!")
        else:
            QMessageBox.warning(self, "Error", msg)

    def on_rename_preset(self):
        old_name = self.preset_combo.currentText()
        if not old_name:
            return

        new_name, ok = QInputDialog.getText(
            self, "Rename Preset", "Enter new name:", text=old_name
        )
        if ok and new_name:
            success, msg = self.preset_manager.rename_preset(old_name, new_name)
            if success:
                self.refresh_presets_ui()
                index = self.preset_combo.findText(new_name)
                if index >= 0:
                    self.preset_combo.setCurrentIndex(index)
            else:
                QMessageBox.warning(self, "Error", msg)

    def on_delete_preset(self):
        name = self.preset_combo.currentText()
        if not name:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            success, msg = self.preset_manager.delete_preset(name)
            if success:
                self.refresh_presets_ui()
            else:
                QMessageBox.warning(self, "Error", msg)

    # --- Generation Event Handlers ---

    def on_generate_clicked(self):
        prompt = self.prompt_input.toPlainText()
        if not prompt:
            QMessageBox.warning(self, "Warning", "Please enter a prompt.")
            return

        provider_name = self.provider_combo.currentText()
        if not provider_name:
            QMessageBox.warning(self, "Warning", "Please select a provider.")
            return

        self.status_label.setText("Checking selection...")
        QtWidgets.QApplication.processEvents()

        # Check for selected nodes for Image-to-Image
        selected_nodes = self.exporter.get_selected_nodes()
        input_image_path = None

        if selected_nodes:
            self.status_label.setText("Exporting selected node(s)...")
            QtWidgets.QApplication.processEvents()

            success, result = self.exporter.export_selected_nodes()
            if success and result:
                # result is a list of file paths
                input_image_path = result[0]  # Use the first exported image
                print(f"DEBUG: Using input image: {input_image_path}")
            else:
                # Export failed, ask user if they want to continue with text-to-image
                reply = QMessageBox.question(
                    self,
                    "Export Failed",
                    f"Failed to export selected node for Image-to-Image:\n{result}\n\nContinue with Text-to-Image generation?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    self.status_label.setText("Ready")
                    return
                # If Yes, input_image_path remains None, proceeds as Text-to-Image

        self.status_label.setText("Generating image (Async)...")
        self.generate_button.setEnabled(False)
        self.generate_button.setText("⏳ Generating...")

        # Create and start worker
        self.worker = GenerationWorker(
            self.image_generator,
            prompt,
            provider_name,
            resolution=self.res_combo.currentText(),
            search_web=False,
            debug_mode=self.chk_debug.isChecked(),
            input_image_path=input_image_path,
        )
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.start()

    def on_generation_finished(self, success, result):
        """Handle completion of image generation"""
        self.generate_button.setEnabled(True)
        self.generate_button.setText("🎨 Generate Image")
        self.status_label.setText("Ready")

        # Retrieve input_image_path from the worker to clean it up if needed
        input_image_path = self.worker.input_image_path

        if success:
            # Import to SD
            import_success, import_msg = self.importer.import_image(result)

            # Cleanup Generated Image if "Save Generated Images" is False
            if not self.chk_save_images.isChecked():
                try:
                    if os.path.exists(result):
                        os.remove(result)
                except Exception as e:
                    print(f"Error deleting generated image: {e}")

            # Cleanup Input Image (Always cleanup temp export)
            if input_image_path and os.path.exists(input_image_path):
                try:
                    os.remove(input_image_path)
                    print(f"DEBUG: Deleted temp input image: {input_image_path}")
                except Exception as e:
                    print(f"Error deleting temp input image: {e}")

            # Show simple success message
            if import_success:
                QMessageBox.information(self, "Success", "Image generation completed!")
            else:
                QMessageBox.warning(
                    self, "Warning", f"Image generated but import failed:\n{import_msg}"
                )
        else:
            QMessageBox.critical(self, "Error", f"Generation failed:\n{result}")

    def on_test_import_clicked(self):
        """Test import handler - imports the last generated image"""
        # Find the most recent image in the output directory
        output_dir = self.image_generator.output_dir
        if not os.path.exists(output_dir):
            QMessageBox.warning(self, "Warning", "No generated images found.")
            return

        import glob

        images = glob.glob(os.path.join(output_dir, "sd_banana_*.png")) + glob.glob(
            os.path.join(output_dir, "sd_banana_*.webp")
        )

        if not images:
            QMessageBox.warning(self, "Warning", "No generated images found.")
            return

        # Sort by modification time, get the latest
        images.sort(key=os.path.getmtime, reverse=True)
        latest_image = images[0]

        # Import it
        success, msg = self.importer.import_image(latest_image)

        if success:
            QMessageBox.information(
                self, "Success", f"Imported:\n{latest_image}\n\n{msg}"
            )
        else:
            QMessageBox.critical(self, "Error", f"Import failed:\n{msg}")

    def on_export_nodes_clicked(self):
        """Handler for Export Selected Nodes button"""
        success, result = self.exporter.export_selected_nodes()

        if success:
            # result is list of files
            msg = f"Successfully exported {len(result)} images:\n" + "\n".join(result)
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.warning(self, "Export Failed", result)
