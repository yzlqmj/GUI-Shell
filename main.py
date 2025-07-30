# main.py (最终美学定制版)
import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from PySide6.QtCore import Qt
import os

if __name__ == "__main__":
    # 强制启用高DPI缩放，解决Windows 1080p 125%缩放问题
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # 关键步骤：为了获得最佳的明暗主题效果，强烈建议使用 Fusion 样式。
    # 某些原生系统样式可能不支持颜色方案切换。
    app.setStyle("Fusion")

    # 移除加载和设置自定义字体的代码，这部分功能将移至 main_window.py
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
