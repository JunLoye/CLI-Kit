import string
import random
import uuid

__info__ = {
    "help": "随机密码/UUID/文本生成器",
    "alias": ["g"]
}

def setup_args(parser):
    parser.add_argument("type", choices=["pwd", "uuid", "str"], nargs="?", help="生成类型")
    parser.add_argument("--len", type=int, default=16, help="生成长度")

def run_gen(args, tools):
    import questionary
    Fore = tools["Fore"]

    print(f"{Fore.CYAN}🎲 DevBox Generator - 随机内容生成")
    
    g_type = getattr(args, 'type', None)
    if not g_type:
        g_type = questionary.select(
            "请选择生成类型:",
            choices=[
                questionary.Choice("🔐 强密码 (Password)", "pwd"),
                questionary.Choice("🆔 唯一标识 (UUID)", "uuid"),
                questionary.Choice("📝 随机字符串 (String)", "str")
            ]
        ).ask()

    if g_type == "uuid":
        res = str(uuid.uuid4())
    elif g_type == "pwd":
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        length = getattr(args, 'len', 16)
        res = "".join(random.choice(chars) for _ in range(length))
    else:
        length = getattr(args, 'len', 16)
        res = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    print("-" * 62)
    print(f"生成结果:\n{Fore.GREEN}{Style.BRIGHT if 'Style' in tools else ''}{res}")
    print("-" * 62)
    
    # 自动尝试复制到剪贴板
    try:
        import pyperclip
        pyperclip.copy(res)
        print(f"{Fore.WHITE}(已自动复制到剪贴板)")
    except:
        pass