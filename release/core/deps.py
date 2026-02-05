import sys
import subprocess
import importlib

REQUIRED_LIBS = {
    "plyer": "plyer",
    "ping3": "ping3",
    "colorama": "colorama",
    "qrcode": "qrcode",
    "PIL": "pillow",
    "psutil": "psutil",
    "questionary": "questionary"
}

def ensure_dependencies():
    missing = []
    for import_name, install_name in REQUIRED_LIBS.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing.append(install_name)
    
    if missing:
        print("="*60)
        print(" 🛠️  DevBox 环境自检：缺少必要组件")
        print(f" 缺失项目: {', '.join(missing)}")
        choice = input("\n 是否允许自动安装这些组件? (y/n): ").lower()
        if choice == 'y':
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
                print("✅ 安装成功，请重新运行程序。")
                sys.exit(0)
            except:
                print("❌ 自动安装失败，请手动执行 pip install。")
                sys.exit(1)
        else:
            sys.exit(1)

def get_toolkit():
    try:
        from colorama import init, Fore, Style
        import qrcode
        from plyer import notification
        from ping3 import ping
        init(autoreset=True)
        return {"Fore": Fore, "Style": Style, "qrcode": qrcode, "notification": notification, "ping": ping}
    except ImportError:
        return None