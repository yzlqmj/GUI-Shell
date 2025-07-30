# command_runner.py (V3 - 修复编码问题)
import subprocess
from PySide6.QtCore import QThread, Signal
import locale
import re


class CommandRunner(QThread):
    output_signal = Signal(str)
    finished_signal = Signal(int)

    def __init__(self, command, shell, working_dir=None):
        super().__init__()
        self.command = command
        self.shell = shell
        self.working_dir = working_dir
        self.process = None
        # 正则表达式用于移除ANSI颜色代码
        self.ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def run(self):
        # 根据shell选择执行方式和编码
        if self.shell == "cmd":
            shell_executable = "cmd.exe"
            # 在Windows的cmd中，中文环境通常使用GBK系列编码。'mbcs'是Python中对当前系统ANSI代码页的别名。
            encoding = "mbcs"
            full_command = [shell_executable, "/c", self.command]
        else:  # PowerShell
            shell_executable = "powershell.exe"
            # 对于PowerShell，尝试使用系统首选编码，这通常能更好地处理本地化字符
            encoding = locale.getpreferredencoding(False)
            full_command = [shell_executable, "-Command", self.command]

        try:
            self.process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.working_dir or None,
                creationflags=subprocess.CREATE_NO_WINDOW,
                encoding=encoding,  # 使用上面确定的编码
                errors="replace",  # 如果有无法解码的字符，用'?'替换
            )

            for line in iter(self.process.stdout.readline, ""):
                # 移除ANSI颜色代码
                cleaned_line = self.ansi_escape_pattern.sub('', line)
                self.output_signal.emit(cleaned_line)

            self.process.stdout.close()
            return_code = self.process.wait()
            self.finished_signal.emit(return_code)

        except FileNotFoundError:
            self.output_signal.emit(
                f"错误: 无法找到执行程序 '{shell_executable}'。请确保它在系统的PATH中。\n"
            )
            self.finished_signal.emit(-1)
        except Exception as e:
            self.output_signal.emit(f"执行出错: {e}\n")
            self.finished_signal.emit(-1)

    def stop(self):
        if self.process and self.process.poll() is None:
            # 终止进程及其所有子进程（在Windows上更有效）
            subprocess.run(
                f"taskkill /F /PID {self.process.pid} /T",
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
