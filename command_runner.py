# command_runner.py (V3 - 修复编码问题)
import subprocess
from PySide6.QtCore import QThread, Signal
import sys

class CommandRunner(QThread):
    output_signal = Signal(str)
    finished_signal = Signal(int)

    def __init__(self, command, shell, working_dir=None):
        super().__init__()
        self.command = command
        self.shell = shell
        self.working_dir = working_dir
        self.process = None

    def run(self):
        # 根据shell选择执行方式和编码
        if self.shell == "cmd":
            shell_executable = "cmd.exe"
            # 在Windows的cmd中，中文环境通常使用GBK系列编码。'mbcs'是Python中对当前系统ANSI代码页的别名。
            # 这是解决cmd中文乱码的关键。
            encoding = 'mbcs'
            full_command = [shell_executable, "/c", self.command]
        else: # PowerShell
            shell_executable = "powershell.exe"
            # PowerShell  Core (v6+) 默认为 UTF-8，Windows PowerShell (v5.1) 可能不同，但UTF-8是更现代的选择。
            encoding = 'utf-8'
            full_command = [shell_executable, "-Command", self.command]

        try:
            self.process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.working_dir or None,
                creationflags=subprocess.CREATE_NO_WINDOW,
                encoding=encoding, # 使用上面确定的编码
                errors='replace' # 如果有无法解码的字符，用'?'替换
            )
            
            for line in iter(self.process.stdout.readline, ''):
                self.output_signal.emit(line)
            
            self.process.stdout.close()
            return_code = self.process.wait()
            self.finished_signal.emit(return_code)

        except FileNotFoundError:
            self.output_signal.emit(f"错误: 无法找到执行程序 '{shell_executable}'。请确保它在系统的PATH中。\n")
            self.finished_signal.emit(-1)
        except Exception as e:
            self.output_signal.emit(f"执行出错: {e}\n")
            self.finished_signal.emit(-1)

    def stop(self):
        if self.process and self.process.poll() is None:
            # 终止进程及其所有子进程（在Windows上更有效）
            subprocess.run(f"taskkill /F /PID {self.process.pid} /T", check=False, creationflags=subprocess.CREATE_NO_WINDOW)