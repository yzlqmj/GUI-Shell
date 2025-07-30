# data_manager.py
import json
import os
import uuid

DATA_FILE = 'data.json'

def generate_id():
    """生成唯一的ID"""
    return str(uuid.uuid4())

def load_data():
    """加载数据，如果文件不存在则创建默认结构"""
    if not os.path.exists(DATA_FILE):
        return {"favorites": [], "groups": []}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"favorites": [], "groups": []}

def save_data(data):
    """将数据保存到JSON文件"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)