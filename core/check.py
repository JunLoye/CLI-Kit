import importlib
import os
import sys

__info__ = {
    "help": "系统自检：排查插件与核心组件的冲突与配置错误",
    "alias": ["verify", "debug"]
}

def setup_args(parser):
    """自检工具通常不需要额外参数"""
    pass

def run_check(args, tools):
    Fore = tools["Fore"]
    print(f"{Fore.CYAN}🔍 CLI-Kit 深度自检程序启动...")
    print("-" * 62)

    # 获取根目录
    if getattr(sys, 'frozen', False):
        root_dir = os.path.dirname(sys.executable)
    else:
        root_dir = os.path.dirname(os.path.abspath(__file__ + "/../"))

    # 定义扫描目标
    scan_targets = {
        "CORE 系统组件": os.path.join(root_dir, "core"),
        "MODS 功能插件": os.path.join(root_dir, "mods")
    }

    alias_map = {}
    errors = []
    success_count = 0

    for label, folder_path in scan_targets.items():
        if not os.path.exists(folder_path):
            continue

        print(f"正在扫描 {label}...")
        
        # 获取该目录下所有 .py 文件
        files = [f[:-3] for f in os.listdir(folder_path) 
                 if f.endswith('.py') and not f.startswith('__')]

        for name in files:
            # 确定导入路径
            prefix = "core" if "CORE" in label else "mods"
            import_path = f"{prefix}.{name}"
            
            try:
                # 动态加载并强制刷新模块
                mod = importlib.import_module(import_path)
                importlib.reload(mod)

                # 1. 检查是否为“可运行”组件 (带有 __info__ 的)
                if hasattr(mod, "__info__"):
                    info = mod.__info__
                    
                    # 检查执行函数是否存在
                    if not hasattr(mod, f"run_{name}"):
                        errors.append(f"[{label}] {name}: 缺失函数 run_{name}")
                        continue

                    # 2. 检查别名冲突 (全局范围)
                    aliases = info.get("alias", [])
                    for a in aliases:
                        if a in alias_map:
                            errors.append(f"[{label}] {name} 的别名 '{a}' 与 {alias_map[a]} 冲突")
                        else:
                            alias_map[a] = f"{label} 的 {name}"
                    
                    success_count += 1
                else:
                    # 如果是 core 组件但没有 __info__，视为纯工具类，不计入错误
                    if prefix == "mods":
                        errors.append(f"[MODS] {name}: 缺失 __info__ 元数据 (无法在菜单显示)")
            
            except Exception as e:
                errors.append(f"[{label}] {name} 编译/加载失败: {e}")

    # --- 报告输出 ---
    print("-" * 62)
    if not errors:
        print(f"{Fore.GREEN}✅ 自检通过！所有 {success_count} 个可执行组件状态健康。")
    else:
        print(f"{Fore.RED}❌ 发现 {len(errors)} 个潜在问题:")
        for err in errors:
            print(f"  - {err}")
    
    print("-" * 62)