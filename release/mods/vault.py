import hashlib
import base64
import os

# 模块元数据，供 main.py 自动扫描
__info__ = {
    "help": "安全加密与编解码",
    "alias": ["v"]
}

def setup_args(parser):
    """定义命令行参数模式"""
    parser.add_argument("action", choices=["md5", "sha256", "base64", "decode"], nargs="?", help="操作类型")
    parser.add_argument("--data", help="要处理的内容")

def run_vault(args, tools):
    Fore = tools["Fore"]
    
    # 尝试导入交互库（已在 core/deps.py 中安装）
    try:
        import questionary
    except ImportError:
        questionary = None

    print(f"{Fore.CYAN}🔐 DevBox Vault - 安全辅助工具")
    print("-" * 62)

    # 1. 获取操作类型 (Action)
    action = getattr(args, 'action', None)
    if not action and questionary:
        action = questionary.select(
            "请选择操作类型:",
            choices=["md5", "sha256", "base64", "decode"]
        ).ask()

    # 2. 获取数据 (Data)
    data = getattr(args, 'data', None)
    if not data and questionary:
        data = questionary.text("请输入要处理的字符串:").ask()

    # 3. 严谨性检查
    if not action or not data:
        print(f"{Fore.RED}⚠️ 操作取消：未提供必要的信息。")
        return

    # 4. 执行逻辑
    try:
        print(f"\n处理结果 ({action}):")
        if action == "md5":
            res = hashlib.md5(data.encode()).hexdigest()
            print(f"{Fore.GREEN}{res}")
        
        elif action == "base64":
            res = base64.b64encode(data.encode()).decode()
            print(f"{Fore.GREEN}{res}")
        
        elif action == "decode":
            # 增加 Base64 解码的健壮性
            try:
                res = base64.b64decode(data.encode()).decode()
                print(f"{Fore.GREEN}{res}")
            except:
                print(f"{Fore.RED}错误：输入的不是有效的 Base64 字符串。")
        
        elif action == "sha256":
            res = hashlib.sha256(data.encode()).hexdigest()
            print(f"{Fore.GREEN}{res}")
            
    except Exception as e:
        print(f"{Fore.RED}执行失败: {e}")
    
    print("-" * 62)