# main_window.py (最终完美版)
import sys
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeView, QStackedWidget, QLineEdit, QTextEdit, QComboBox,
    QPushButton, QMenu, QMessageBox, QInputDialog, QLabel,
    QSplitter, QTextBrowser, QFormLayout
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon, QAction
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
# ★  补上这至关重要的一行！
from PySide6.QtCore import Qt
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★

from data_manager import load_data, save_data, generate_id
from command_runner import CommandRunner
from qt_material import apply_stylesheet, list_themes


# --- 后续所有代码都保持不变 ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("命令行工具箱")
        self.setWindowIcon(QIcon("icons/terminal.ico"))
        self.setGeometry(100, 100, 1000, 630)
        self.current_selected_item = None
        self.command_runner = None

        self.init_ui()
        self.create_theme_menu()
        
        self.load_and_display_data()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_splitter = QSplitter(Qt.Orientation.Horizontal) # 使用 Qt.Orientation
        main_layout.addWidget(main_splitter)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.tree_view = QTreeView()
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(['分组和项目'])
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu) # 使用 Qt.ContextMenuPolicy
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        self.tree_view.selectionModel().selectionChanged.connect(self.on_item_selected)
        left_layout.addWidget(self.tree_view)
        self.stacked_widget = QStackedWidget()
        self.home_page = QWidget()
        home_layout = QVBoxLayout(self.home_page)
        welcome_label = QLabel("<h1>欢迎使用命令行工具箱</h1><p>← 在左侧选择或创建命令</p><p>可在顶部菜单栏切换主题</p>")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # 使用 Qt.AlignmentFlag
        home_layout.addWidget(welcome_label)
        self.editor_log_page = QWidget()
        editor_log_layout = QVBoxLayout(self.editor_log_page)
        right_splitter = QSplitter(Qt.Orientation.Vertical) # 使用 Qt.Orientation
        editor_area = QWidget()
        editor_layout = QFormLayout(editor_area)
        editor_layout.setContentsMargins(5, 10, 5, 5)
        editor_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.save_button = QPushButton("💾 保存更改")
        self.execute_button = QPushButton("▶️ 立即执行")
        self.id_label = QLabel()
        top_row_layout = QHBoxLayout()
        top_row_layout.addWidget(self.id_label)
        top_row_layout.addStretch()
        top_row_layout.addWidget(self.save_button)
        top_row_layout.addWidget(self.execute_button)
        editor_layout.addRow("ID:", top_row_layout)
        self.name_edit = QLineEdit()
        self.command_edit = QTextEdit()
        self.command_edit.setAcceptRichText(False)
        self.shell_combo = QComboBox()
        self.shell_combo.addItems(["cmd", "PowerShell"])
        self.workdir_edit = QLineEdit()
        self.workdir_edit.setPlaceholderText("留空则使用程序默认目录")
        editor_layout.addRow("名称:", self.name_edit)
        editor_layout.addRow("命令:", self.command_edit)
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("运行环境:"))
        config_layout.addWidget(self.shell_combo)
        config_layout.addSpacing(20)
        config_layout.addWidget(QLabel("工作目录:"))
        config_layout.addWidget(self.workdir_edit, 1)
        editor_layout.addRow(config_layout)
        self.output_browser = QTextBrowser()
        self.output_browser.setPlaceholderText("命令执行输出将显示在这里...")
        right_splitter.addWidget(editor_area)
        right_splitter.addWidget(self.output_browser)
        right_splitter.setSizes([350, 350])
        editor_log_layout.addWidget(right_splitter)
        self.save_button.clicked.connect(self.save_item_details)
        self.execute_button.clicked.connect(self.execute_current_command)
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.editor_log_page)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(self.stacked_widget)
        main_splitter.setSizes([300, 900])
        
    def create_theme_menu(self):
        menu_bar = self.menuBar()
        theme_menu = menu_bar.addMenu("主题 (Theme)")
        for theme in list_themes():
            action = QAction(theme, self)
            action.triggered.connect(lambda checked=False, t=theme: self.switch_theme(t))
            theme_menu.addAction(action)

    def switch_theme(self, theme_name):
        app_instance = QApplication.instance()
        if app_instance:
            apply_stylesheet(app_instance, theme=theme_name)

    def append_output(self, text):
        self.output_browser.append(text.strip())
        self.output_browser.verticalScrollBar().setValue(self.output_browser.verticalScrollBar().maximum())
    def on_command_finished(self, return_code):
        self.append_output(f"\n--- 命令执行完毕, 返回码: {return_code} ---")
        self.execute_button.setEnabled(True)
        self.command_runner = None
    def load_and_display_data(self):
        self.data = load_data()
        self.tree_model.clear()
        self.tree_model.setHorizontalHeaderLabels(['分组和项目'])
        root_node = self.tree_model.invisibleRootItem()
        for group_data in self.data['groups']:
            group_item = QStandardItem(group_data['name'])
            group_item.setData(group_data['id'], Qt.ItemDataRole.UserRole)
            group_item.setData('group', Qt.ItemDataRole.UserRole + 1)
            group_item.setEditable(False)
            for item_data in group_data['items']:
                command_item = QStandardItem(item_data['name'])
                command_item.setData(item_data['id'], Qt.ItemDataRole.UserRole)
                command_item.setData('item', Qt.ItemDataRole.UserRole + 1)
                command_item.setEditable(False)
                group_item.appendRow(command_item)
            root_node.appendRow(group_item)
        self.tree_view.expandAll()
    def on_item_selected(self, selected, deselected):
        indexes = selected.indexes()
        if not indexes:
            self.current_selected_item = None
            self.stacked_widget.setCurrentWidget(self.home_page)
            return
        index = indexes[0]
        item = self.tree_model.itemFromIndex(index)
        item_type = item.data(Qt.ItemDataRole.UserRole + 1)
        if item_type == 'item':
            self.current_selected_item = item
            self.stacked_widget.setCurrentWidget(self.editor_log_page)
            self.populate_editor(item)
        else:
            self.current_selected_item = None
            self.stacked_widget.setCurrentWidget(self.home_page)
    def populate_editor(self, item):
        item_id = item.data(Qt.ItemDataRole.UserRole)
        group_id = item.parent().data(Qt.ItemDataRole.UserRole)
        for g in self.data['groups']:
            if g['id'] == group_id:
                for i in g['items']:
                    if i['id'] == item_id:
                        self.id_label.setText(f"<font color='gray'>{i['id']}</font>")
                        self.name_edit.setText(i['name'])
                        self.command_edit.setText(i['command'])
                        self.shell_combo.setCurrentText(i['shell'])
                        self.workdir_edit.setText(i.get('working_dir', ''))
                        self.output_browser.clear()
                        break
                break
    def show_context_menu(self, position):
        menu = QMenu()
        index = self.tree_view.indexAt(position)
        item = self.tree_model.itemFromIndex(index)
        if not index.isValid():
            menu.addAction("➕ 创建新分组", self.create_group)
        else:
            item_type = item.data(Qt.ItemDataRole.UserRole + 1)
            if item_type == 'group':
                menu.addAction("📄 创建新项目", lambda: self.create_item(item))
                menu.addSeparator()
                menu.addAction("✏️ 重命名", lambda: self.rename_item(item))
                menu.addAction("🗑️ 删除分组", lambda: self.delete_group(item))
            elif item_type == 'item':
                menu.addAction("▶️ 执行", self.execute_current_command)
                menu.addSeparator()
                menu.addAction("✏️ 重命名", lambda: self.rename_item(item))
                menu.addAction("🗑️ 删除项目", lambda: self.delete_item(item))
        menu.exec(self.tree_view.viewport().mapToGlobal(position))
    def create_group(self):
        name, ok = QInputDialog.getText(self, "创建分组", "请输入分组名称 (可包含Emoji):", text="📁 新分组")
        if ok and name:
            new_group = {"id": generate_id(), "name": name, "items": []}
            self.data['groups'].append(new_group)
            save_data(self.data)
            self.load_and_display_data()
    def create_item(self, group_item):
        name, ok = QInputDialog.getText(self, "创建项目", "请输入项目名称 (可包含Emoji):", text="📜 新项目")
        if ok and name:
            group_id = group_item.data(Qt.ItemDataRole.UserRole)
            for g in self.data['groups']:
                if g['id'] == group_id:
                    new_item = { "id": generate_id(), "name": name, "command": "echo 'New Command'", "shell": "cmd", "working_dir": "" }
                    g['items'].append(new_item)
                    save_data(self.data)
                    self.load_and_display_data()
                    break
    def rename_item(self, item):
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, f"重命名", "请输入新名称:", text=old_name)
        if ok and new_name and new_name != old_name:
            item_id = item.data(Qt.ItemDataRole.UserRole)
            item_type = item.data(Qt.ItemDataRole.UserRole + 1)
            if item_type == 'group':
                for g in self.data['groups']:
                    if g['id'] == item_id: g['name'] = new_name; break
            elif item_type == 'item':
                parent_id = item.parent().data(Qt.ItemDataRole.UserRole)
                for g in self.data['groups']:
                    if g['id'] == parent_id:
                        for i in g['items']:
                            if i['id'] == item_id: i['name'] = new_name; break
                        break
            save_data(self.data)
            item.setText(new_name)
    def delete_group(self, group_item):
        reply = QMessageBox.question(self, "确认删除", f"确定要删除分组 '{group_item.text()}' 及其所有项目吗？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            group_id = group_item.data(Qt.ItemDataRole.UserRole)
            self.data['groups'] = [g for g in self.data['groups'] if g['id'] != group_id]
            save_data(self.data)
            self.load_and_display_data()
            self.stacked_widget.setCurrentWidget(self.home_page)
    def delete_item(self, item):
        reply = QMessageBox.question(self, "确认删除", f"确定要删除项目 '{item.text()}' 吗？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            item_id = item.data(Qt.ItemDataRole.UserRole)
            group_id = item.parent().data(Qt.ItemDataRole.UserRole)
            for g in self.data['groups']:
                if g['id'] == group_id:
                    g['items'] = [i for i in g['items'] if i['id'] != item_id]
                    break
            save_data(self.data)
            self.load_and_display_data()
            self.stacked_widget.setCurrentWidget(self.home_page)
    def save_item_details(self):
        if not self.current_selected_item: return
        item_id = self.current_selected_item.data(Qt.ItemDataRole.UserRole)
        group_id = self.current_selected_item.parent().data(Qt.ItemDataRole.UserRole)
        new_name = self.name_edit.text()
        for g in self.data['groups']:
            if g['id'] == group_id:
                for i in g['items']:
                    if i['id'] == item_id:
                        if i['name'] != new_name:
                            self.current_selected_item.setText(new_name)
                        i['name'] = new_name
                        i['command'] = self.command_edit.toPlainText()
                        i['shell'] = self.shell_combo.currentText()
                        i['working_dir'] = self.workdir_edit.text()
                        break
                break
        save_data(self.data)
        QMessageBox.information(self, "成功", "更改已保存！")
    def execute_current_command(self):
        if self.command_runner and self.command_runner.isRunning():
            QMessageBox.warning(self, "提示", "已有命令正在执行中，请稍候。")
            return
        if self.stacked_widget.currentWidget() != self.editor_log_page:
            QMessageBox.warning(self, "提示", "请先在左侧选择一个要执行的项目。")
            return
        self.output_browser.clear()
        self.append_output(f"--- 开始执行命令 ({self.shell_combo.currentText()}) ---")
        self.command_runner = CommandRunner( command=self.command_edit.toPlainText(), shell=self.shell_combo.currentText(), working_dir=self.workdir_edit.text() )
        self.command_runner.output_signal.connect(self.append_output)
        self.command_runner.finished_signal.connect(self.on_command_finished)
        self.command_runner.start()
        self.execute_button.setEnabled(False)
    def closeEvent(self, event):
        if self.command_runner and self.command_runner.isRunning():
            reply = QMessageBox.question(self, "确认", "命令仍在运行中，确定要关闭并终止它吗？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.command_runner.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()