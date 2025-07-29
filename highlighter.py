from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtCore import QRegularExpression

class ShellSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.highlighting_rules = []

        # 错误信息高亮
        error_format = QTextCharFormat()
        error_format.setForeground(QColor("red"))
        error_format.setFontWeight(700)
        self.highlighting_rules.append((QRegularExpression(r"error|错误|失败", QRegularExpression.CaseInsensitiveOption), error_format))

        # 成功信息高亮
        success_format = QTextCharFormat()
        success_format.setForeground(QColor("green"))
        self.highlighting_rules.append((QRegularExpression(r"success|成功|完成", QRegularExpression.CaseInsensitiveOption), success_format))
        
        # 警告信息高亮
        warning_format = QTextCharFormat()
        warning_format.setForeground(QColor("orange"))
        self.highlighting_rules.append((QRegularExpression(r"warning|警告", QRegularExpression.CaseInsensitiveOption), warning_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            it = expression.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)