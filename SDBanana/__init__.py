##########################################################################
# SDBanana Plugin for Substance 3D Designer
# AI Image Generation using Nano Banana API
##########################################################################

# 首先导入 SD API 模块
import sd
from sd.api.sdapplication import SDApplication
from sd.api.qtforpythonuimgrwrapper import QtForPythonUIMgrWrapper

# 然后导入本地模块
from .ui import SDBananaPanel

# 全局变量
PANEL_INSTANCE = None
CALLBACK_ID = None


def initializeSDPlugin():
    """
    插件初始化函数
    Substance Designer 会在加载插件时调用此函数
    """
    global PANEL_INSTANCE, CALLBACK_ID
    
    # 获取应用上下文
    ctx = sd.getContext()
    app: SDApplication = ctx.getSDApplication()
    ui_mgr: QtForPythonUIMgrWrapper = app.getQtForPythonUIMgr()
    
    # 创建停靠窗口容器
    # newDockWidget 返回一个容器 widget，需要传入 identifier 和 title
    dock_widget = ui_mgr.newDockWidget(
        "com.sdbanana.panel",              # identifier
        "SD Banana - AI Image Generation"  # title
    )
    
    # 创建并设置插件面板到停靠窗口
    PANEL_INSTANCE = SDBananaPanel(parent=dock_widget)
    
    # 将面板设置为停靠窗口的内容
    from PySide6.QtWidgets import QVBoxLayout
    layout = QVBoxLayout()
    layout.addWidget(PANEL_INSTANCE)
    layout.setContentsMargins(0, 0, 0, 0)
    dock_widget.setLayout(layout)
    
    print("SDBanana 插件已加载")


def uninitializeSDPlugin():
    """
    插件卸载函数
    Substance Designer 会在卸载插件时调用此函数
    """
    global PANEL_INSTANCE, CALLBACK_ID
    
    # 清理资源
    if PANEL_INSTANCE:
        PANEL_INSTANCE.deleteLater()
        PANEL_INSTANCE = None
    
    print("SDBanana 插件已卸载")
