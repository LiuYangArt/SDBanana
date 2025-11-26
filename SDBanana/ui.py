##########################################################################
# SDBanana UI Components
##########################################################################

from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton, QComboBox, QLineEdit


class SDBananaPanel(QWidget):
    """
    SDBanana 主面板
    包含两个 Tab: 图像生成和设置
    """
    
    def __init__(self, parent=None):
        super(SDBananaPanel, self).__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建标题
        title_label = QLabel("🍌 SD Banana - AI Image Generation")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 创建 Tab 控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
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
        """)
        
        # 创建 Tab1 - 图像生成
        tab1 = self.create_generation_tab()
        self.tab_widget.addTab(tab1, "Generate")
        
        # 创建 Tab2 - 设置
        tab2 = self.create_settings_tab()
        self.tab_widget.addTab(tab2, "Settings")
        
        main_layout.addWidget(self.tab_widget)
        
        self.setLayout(main_layout)
        self.setMinimumSize(400, 500)
    
    def create_generation_tab(self):
        """创建图像生成 Tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Prompt 输入区域
        prompt_label = QLabel("Prompt:")
        prompt_label.setStyleSheet("color: #cccccc; font-weight: bold; padding: 5px;")
        layout.addWidget(prompt_label)
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Enter your image generation prompt here...")
        self.prompt_input.setMinimumHeight(150)
        self.prompt_input.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.prompt_input)
        
        # 占位：图像尺寸选择
        size_label = QLabel("Image Size:")
        size_label.setStyleSheet("color: #cccccc; font-weight: bold; padding: 5px; padding-top: 15px;")
        layout.addWidget(size_label)
        
        self.size_combo = QComboBox()
        self.size_combo.addItems(["1024x1024", "1024x2048", "2048x2048", "4096x4096"])
        self.size_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #cccccc;
            }
        """)
        layout.addWidget(self.size_combo)
        
        # Generate 按钮
        self.generate_button = QPushButton("🎨 Generate Image")
        self.generate_button.setMinimumHeight(40)
        self.generate_button.setStyleSheet("""
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
        """)
        self.generate_button.clicked.connect(self.on_generate_clicked)
        layout.addWidget(self.generate_button)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 状态信息
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #888888;
                padding: 5px;
                font-style: italic;
            }
        """)
        layout.addWidget(self.status_label)
        
        tab.setLayout(layout)
        return tab
    
    def create_settings_tab(self):
        """创建设置 Tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # API Provider 设置
        provider_label = QLabel("API Provider:")
        provider_label.setStyleSheet("color: #cccccc; font-weight: bold; padding: 5px;")
        layout.addWidget(provider_label)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "GPTGod NanoBanana Pro",
            "Yunwu Gemini",
            "Custom"
        ])
        self.provider_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.provider_combo)
        
        # API Base URL
        url_label = QLabel("API Base URL:")
        url_label.setStyleSheet("color: #cccccc; font-weight: bold; padding: 5px; padding-top: 15px;")
        layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://api.example.com/v1")
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.url_input)
        
        # API Key
        key_label = QLabel("API Key:")
        key_label.setStyleSheet("color: #cccccc; font-weight: bold; padding: 5px; padding-top: 15px;")
        layout.addWidget(key_label)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter your API key...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.key_input)
        
        # Model
        model_label = QLabel("Model:")
        model_label.setStyleSheet("color: #cccccc; font-weight: bold; padding: 5px; padding-top: 15px;")
        layout.addWidget(model_label)
        
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("gemini-3-pro-image-preview")
        self.model_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.model_input)
        
        # Save 按钮
        save_button = QPushButton("💾 Save Settings")
        save_button.setMinimumHeight(40)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #34c759;
            }
            QPushButton:pressed {
                background-color: #218838;
            }
        """)
        save_button.clicked.connect(self.on_save_settings_clicked)
        layout.addWidget(save_button)
        
        # 添加弹性空间
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def on_generate_clicked(self):
        """Generate 按钮点击事件（占位）"""
        self.status_label.setText("Generate functionality coming soon...")
        print("Generate button clicked - placeholder")
    
    def on_save_settings_clicked(self):
        """Save Settings 按钮点击事件（占位）"""
        print("Save settings button clicked - placeholder")
        # TODO: 实现设置保存功能
