import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QTextEdit, QLineEdit,
    QDialog, QDialogButtonBox, QFormLayout, QLabel, QSplitter, QMessageBox,
    QToolBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction

import commands as cmd
from executor import CommandExecutor
from highlighter import ShellSyntaxHighlighter

class CommandDialog(QDialog):
    """用于添加和编辑命令的对话框。"""
    def __init__(self, parent=None, name='', command='', icon=''):
        super().__init__(parent)
        self.setWindowTitle('添加/编辑命令')

        self.name_input = QLineEdit(name)
        self.command_input = QLineEdit(command)
        self.icon_input = QLineEdit(icon)

        form_layout = QFormLayout()
        form_layout.addRow('名称:', self.name_input)
        form_layout.addRow('命令:', self.command_input)
        form_layout.addRow('图标 (可选):', self.icon_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def get_data(self):
        return self.name_input.text(), self.command_input.text(), self.icon_input.text()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('GUI Shell')
        self.setGeometry(100, 100, 800, 600)

        self.toolbar = self.addToolBar('常用命令')
        self.toolbar.setMovable(False)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # 创建左右分割的布局
        splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(splitter)

        # 左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.command_list = QListWidget()
        self.command_list.itemDoubleClicked.connect(self.execute_command)
        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton('添加')
        self.edit_button = QPushButton('编辑')
        self.delete_button = QPushButton('删除')
        
        self.add_button.clicked.connect(self.add_command)
        self.edit_button.clicked.connect(self.edit_command)
        self.delete_button.clicked.connect(self.delete_command)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)

        left_layout.addWidget(QLabel('已保存的命令:'))
        left_layout.addWidget(self.command_list)
        left_layout.addLayout(button_layout)

        # 右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.highlighter = ShellSyntaxHighlighter(self.output_area.document())
        
        right_layout.addWidget(QLabel('命令输出:'))
        right_layout.addWidget(self.output_area)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([250, 550])

        self.load_commands()

    def update_toolbar(self):
        self.toolbar.clear()
        commands = cmd.load_commands()
        for command_data in commands[:5]: # Show top 5
            action_text = f"{command_data.get('icon', '▶️')} {command_data['name']}"
            action = QAction(action_text, self)
            action.setToolTip(f"执行: {command_data['command']}")
            action.triggered.connect(lambda checked=False, cmd_str=command_data['command']: self.execute_command_string(cmd_str))
            self.toolbar.addAction(action)

    def load_commands(self):
        self.command_list.clear()
        commands = cmd.load_commands()
        for command_data in commands:
            item = QListWidgetItem(f"{command_data.get('icon', '')} {command_data['name']}")
            item.setData(Qt.UserRole, command_data)
            self.command_list.addItem(item)
        self.update_toolbar()

    def add_command(self):
        dialog = CommandDialog(self)
        if dialog.exec():
            name, command, icon = dialog.get_data()
            if name and command:
                cmd.add_command(name, command, icon)
                self.load_commands()

    def edit_command(self):
        selected_item = self.command_list.currentItem()
        if not selected_item:
            return
        
        command_data = selected_item.data(Qt.UserRole)
        dialog = CommandDialog(self, command_data['name'], command_data['command'], command_data.get('icon', ''))
        
        if dialog.exec():
            name, command, icon = dialog.get_data()
            if name and command:
                index = self.command_list.row(selected_item)
                cmd.update_command(index, name, command, icon)
                self.load_commands()

    def delete_command(self):
        selected_item = self.command_list.currentItem()
        if not selected_item:
            return

        command_data = selected_item.data(Qt.UserRole)
        reply = QMessageBox.question(self, '确认删除',
                                     f"您确定要删除命令 '{command_data['name']}' 吗?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            index = self.command_list.row(selected_item)
            cmd.delete_command(index)
            self.load_commands()

    def execute_command_string(self, command):
        self.output_area.clear()
        self.output_area.append(f'正在执行: {command}\n')
        
        self.executor = CommandExecutor(command)
        self.executor.execution_finished.connect(self.on_execution_finished)
        self.executor.start()

    def execute_command(self, item):
        command_data = item.data(Qt.UserRole)
        command = command_data['command']
        self.execute_command_string(command)

    def on_execution_finished(self, stdout, stderr):
        self.output_area.append('--- 执行完成 ---\n')
        if stdout:
            self.output_area.append('--- 标准输出 ---\n')
            self.output_area.append(stdout)
        if stderr:
            self.output_area.append('--- 标准错误 ---\n')
            self.output_area.append(stderr)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())