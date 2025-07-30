# main.py (最终美学定制版)
import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from qt_material import apply_stylesheet

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # ★ 1. 定义我们自己的样式覆盖规则 (QSS)
    # 这段代码的意思是：对于这四种控件，当它们获得焦点时，
    # 不要用主题默认的彩色边框，而是统一使用一个1像素宽、颜色为中性灰(#777)的边框。
    # 我们也让树状视图中被选中的项目背景色变成一个更低调的灰色。
    extra_qss = """
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QTextBrowser:focus {
            border: 1px solid #777;
        }
        QTreeView::item:selected {
            background-color: #555;
        }
    """
    
    # ★ 2. 在应用主题时，通过 extra 参数传入我们的覆盖规则
    apply_stylesheet(app, theme='dark_blue.xml', extra={'density_scale': '0', 'qss': extra_qss})
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())