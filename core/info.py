import os
import sys
import platform

def get_status():
    """返回核心运行状态摘要"""
    return {
        "os": platform.system(),
        "ver": platform.python_version(),
        "pid": os.getpid()
    }

def print_detailed_report(root_path):
    """打印详细的系统报告"""
    print(f"系统节点: {platform.node()}")
    print(f"处理器: {platform.processor()}")
    print(f"Python 路径: {sys.executable}")