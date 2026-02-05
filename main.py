import argparse
import sys
import importlib
import os
import platform

# --- 路径适配 ---
def get_root_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

ROOT_PATH = get_root_path()
sys.path.append(ROOT_PATH)

def discover_entities(folder_name):
    """通用遍历：扫描指定文件夹下的 py 脚本"""
    target_dir = os.path.join(ROOT_PATH, folder_name)
    if not os.path.exists(target_dir):
        try: os.makedirs(target_dir)
        except: pass
        return []
    return [f[:-3] for f in os.listdir(target_dir) 
            if f.endswith('.py') and not f.startswith('__')]

def main():
    # 1. 扫描文件夹
    core_names = discover_entities('core')
    mod_names = discover_entities('mods')
    
    system_tools = {}
    core_entities = {}  # 存放核心可执行组件
    mod_entities = {}   # 存放功能可执行组件
    
    parser = argparse.ArgumentParser(description="CLI-Kit")
    subparsers = parser.add_subparsers(dest="command")

    # 2. 加载 Core 组件 (支撑工具箱)
    if 'deps' in core_names:
        try:
            deps = importlib.import_module('core.deps')
            if hasattr(deps, 'ensure_dependencies'): deps.ensure_dependencies()
            if hasattr(deps, 'get_toolkit'): system_tools.update(deps.get_toolkit())
        except Exception as e: print(f"⚠️  Deps 加载失败: {e}")

    for name in core_names:
        try:
            mod = importlib.import_module(f'core.{name}')
            system_tools[name] = mod
            if hasattr(mod, "__info__") and hasattr(mod, f"run_{name}"):
                info = mod.__info__
                sub_p = subparsers.add_parser(name, help=info["help"], aliases=info.get("alias", []))
                if hasattr(mod, "setup_args"): mod.setup_args(sub_p)
                core_entities[name] = mod
        except Exception as e:
            if name != 'deps': print(f"⚠️  Core [{name}] 注册失败: {e}")

    # 3. 加载 Mods 插件
    for name in mod_names:
        try:
            mod = importlib.import_module(f"mods.{name}")
            if hasattr(mod, "__info__") and hasattr(mod, f"run_{name}"):
                info = mod.__info__
                sub_p = subparsers.add_parser(name, help=info["help"], aliases=info.get("alias", []))
                if hasattr(mod, "setup_args"): mod.setup_args(sub_p)
                mod_entities[name] = mod
        except Exception as e:
            print(f"⚠️  Mod [{name}] 注册失败: {e}")

    # 4. 交互界面
    if len(sys.argv) == 1:
        import questionary
        from colorama import Fore, init
        init(autoreset=True)

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Fore.CYAN}🛠️  CLI-Kit | Mods: {len(mod_entities)} | Core: {len(core_entities)}")
            print("-" * 62)
            
            choices = []
            
            # --- 第一部分：MODS (置顶) ---
            if mod_entities:
                # 【修复点】: 分隔符使用纯文本，不包含颜色代码
                choices.append(questionary.Separator("--- FUNCTIONAL MODS ---"))
                for name, mod in mod_entities.items():
                    info = mod.__info__
                    choices.append(f"{name:<12} | {info.get('help', '...')}")
            
            # --- 第二部分：CORE (置底) ---
            if core_entities:
                choices.append(questionary.Separator("--- SYSTEM CORE ---"))
                for name, mod in core_entities.items():
                    info = mod.__info__
                    choices.append(f"{name:<12} | {info.get('help', '...')}")
            
            choices.append(questionary.Separator("-" * 20))
            choices.append("EXIT: 退出程序")

            # 【严谨性提升】: 使用 Style 统一管理颜色，避免 ANSI 乱码
            custom_style = questionary.Style([
                ('pointer', 'fg:cyan bold'),     # 指针颜色
                ('highlighted', 'fg:cyan bold'), # 选中行颜色
                ('separator', 'fg:yellow'),      # 分隔符颜色 (这里统一设置)
                ('instruction', 'fg:white dim'), # 提示语颜色
            ])

            selected = questionary.select(
                "请选择工具:", 
                choices=choices,
                style=custom_style,
                use_indicator=True # 增加指示器增强视觉确认
            ).ask()

            if not selected or "EXIT:" in selected: break
            
            cmd_name = selected.split('|')[0].strip()
            all_executables = {**mod_entities, **core_entities}
            args = parser.parse_args([cmd_name])
            
            try:
                # 运行插件
                getattr(all_executables[cmd_name], f"run_{cmd_name}")(args, system_tools)
            except Exception as e:
                print(f"{Fore.RED}运行出错: {e}")
            
            input(f"\n{Fore.WHITE}执行完毕，按 Enter 返回主菜单...")
    else:
        # 命令行模式
        args = parser.parse_args()
        if args.command:
            all_executables = {**mod_entities, **core_entities}
            for name, mod in all_executables.items():
                info = mod.__info__
                if args.command == name or args.command in info.get("alias", []):
                    getattr(mod, f"run_{name}")(args, system_tools)
                    break

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit(0)