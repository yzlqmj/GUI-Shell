import json
import os

COMMANDS_FILE = 'commands.json'

def load_commands():
    """从 JSON 文件加载命令"""
    if not os.path.exists(COMMANDS_FILE):
        return []
    try:
        with open(COMMANDS_FILE, 'r', encoding='utf-8') as f:
            commands = json.load(f)
            return commands
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_commands(commands):
    """将命令保存到 JSON 文件"""
    with open(COMMANDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(commands, f, indent=4, ensure_ascii=False)

def add_command(name, command, icon=''):
    """添加一个新命令"""
    commands = load_commands()
    commands.append({'name': name, 'command': command, 'icon': icon})
    save_commands(commands)

def update_command(index, name, command, icon):
    """更新一个现有命令"""
    commands = load_commands()
    if 0 <= index < len(commands):
        commands[index] = {'name': name, 'command': command, 'icon': icon}
        save_commands(commands)

def delete_command(index):
    """删除一个命令"""
    commands = load_commands()
    if 0 <= index < len(commands):
        commands.pop(index)
        save_commands(commands)