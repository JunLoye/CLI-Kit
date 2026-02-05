import json
import os
import webbrowser

__info__ = {
    "help": "快捷方式管理 (一键打开常用网页或目录)",
    "alias": ["go", "jump"]
}

CONFIG_FILE = "core/shortcuts.json"

def load_shortcuts():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_shortcuts(data):
    os.makedirs("core", exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def setup_args(parser):
    parser.add_argument("name", nargs="?", help="别名名称")

def run_shortcut(args, tools):
    import questionary
    Fore = tools["Fore"]
    shortcuts = load_shortcuts()

    print(f"{Fore.CYAN}🚀 DevBox ShortCut - 快捷导航")

    name = getattr(args, 'name', None)

    # 如果没带参数，列出所有别名
    if not name:
        if not shortcuts:
            print(f"{Fore.YELLOW}目前还没有快捷方式。")
            action = "添加新别名"
        else:
            options = list(shortcuts.keys()) + [questionary.Separator(), "添加新别名", "删除别名", "退出"]
            action = questionary.select("选择要执行的操作:", choices=options).ask()
        
        if action == "退出": return
        if action == "添加新别名":
            n = questionary.text("请输入别名:").ask()
            v = questionary.text("请输入目标 (URL 或 路径):").ask()
            if n and v:
                shortcuts[n] = v
                save_shortcuts(shortcuts)
                print(f"✅ 已添加 {n}")
            return
        elif action == "删除别名":
            del_n = questionary.select("选择要删除的别名:", choices=list(shortcuts.keys())).ask()
            if del_n:
                del shortcuts[del_n]
                save_shortcuts(shortcuts)
                print("已删除。")
            return
        else:
            name = action

    # 执行打开逻辑
    target = shortcuts.get(name)
    if target:
        print(f"正在跳转至: {target}")
        if target.startswith(("http://", "https://")):
            webbrowser.open(target)
        else:
            # 尝试作为目录打开
            os.startfile(target) if os.name == 'nt' else os.system(f"open {target}")
    else:
        print(f"{Fore.RED}错误: 找不到别名 '{name}'")