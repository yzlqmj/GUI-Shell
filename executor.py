import subprocess
from PySide6.QtCore import QThread, Signal

class CommandExecutor(QThread):
    """
    在单独的线程中执行命令，以避免阻塞GUI。
    """
    execution_finished = Signal(str, str)  # Signal with stdout and stderr

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        """
        执行命令并发出带有输出的信号。
        """
        try:
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            stdout, stderr = process.communicate()
            self.execution_finished.emit(stdout, stderr)
        except Exception as e:
            self.execution_finished.emit('', str(e))
