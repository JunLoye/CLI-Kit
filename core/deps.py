import sys
import subprocess
from colorama import Fore, Style

# 定义必须安装的库
REQUIRED_LIBS = {
    "questionary": "questionary",
    "colorama": "colorama",
    "requests": "requests",
    "ping3": "ping3",
    "plyer": "plyer",
    "psutil": "psutil"
}

def ensure_dependencies():
    """静默检查并安装缺失依赖"""
    for module_name, pip_name in REQUIRED_LIBS.items():
        try:
            __import__(module_name)
        except ImportError:
            print(f"📦 正在自动修复依赖: {pip_name}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name, "--quiet"])
            except Exception as e:
                print(f"❌ 自动修复失败，请手动执行: pip install {pip_name}")

def get_toolkit():
    """提供给所有插件的全局工具包"""
    from ping3 import ping
    from plyer import notification
    return {
        "Fore": Fore,
        "Style": Style,
        "ping": ping,
        "notification": notification,
        "libs": REQUIRED_LIBS  # 将依赖列表也暴露给工具箱
    }