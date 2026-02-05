import os
import requests
import sys

__info__ = {
    "help": "插件商店",
    "alias": ["market", "install", "upgrade"]
}

# 1. 链路配置
# 原生 GitHub 地址
MANIFEST_URL = "https://raw.githubusercontent.com/JunLoye/CLI-Kit-Mods/main/manifest.json"
RAW_BASE_URL = "https://raw.githubusercontent.com/JunLoye/CLI-Kit-Mods/main"

# JSDelivr 加速镜像转换逻辑：
# 将 raw.githubusercontent.com/user/repo/main/file 
# 替换为 fastly.jsdelivr.net/gh/user/repo@main/file

def get_safe_content(url, timeout=8):
    """
    严谨的多链路请求逻辑。
    如果原生 GitHub 访问失败（如 10054），自动切换至镜像加速链路。
    """
    # 构造镜像 URL
    mirror_url = url.replace("https://raw.githubusercontent.com/", "https://fastly.jsdelivr.net/gh/")\
                    .replace("/main/", "@main/")
    
    # 尝试链路 A (原生)
    try:
        res = requests.get(url, timeout=timeout)
        res.raise_for_status()
        return res
    except Exception:
        # 尝试链路 B (镜像)
        try:
            return requests.get(mirror_url, timeout=timeout)
        except Exception as e:
            raise ConnectionError(f"所有下载链路均不可达 (10054/Timeout)。具体错误: {e}")

def run_store(args, tools):
    import questionary
    Fore = tools["Fore"]
    
    # 获取根目录逻辑
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__ + "/../"))
    
    mods_dir = os.path.join(base_dir, "mods")
    if not os.path.exists(mods_dir):
        os.makedirs(mods_dir)

    print(f"{Fore.CYAN}🛒 CLI-Kit 插件商店 (多链路加速版)")
    print("-" * 62)

    # --- 逻辑 A: 一键更新所有已安装插件 (--all) ---
    if getattr(args, 'all', False):
        print(f"{Fore.YELLOW}📡 正在同步云端清单进行全量对比...")
        try:
            response = get_safe_content(MANIFEST_URL)
            cloud_plugins = {p['name']: p for p in response.json().get("plugins", [])}
            
            local_files = [f[:-3] for f in os.listdir(mods_dir) if f.endswith(".py") and not f.startswith("__")]
            if not local_files:
                print(f"{Fore.WHITE}未发现本地插件，无需更新。")
                return

            updated_count = 0
            for name in local_files:
                if name in cloud_plugins:
                    p = cloud_plugins[name]
                    print(f"正在更新 {name:<12} ... ", end="", flush=True)
                    try:
                        content_res = get_safe_content(f"{RAW_BASE_URL}/{p['file']}")
                        with open(os.path.join(mods_dir, f"{name}.py"), "w", encoding="utf-8") as f:
                            f.write(content_res.text)
                        print(f"{Fore.GREEN}OK")
                        updated_count += 1
                    except:
                        print(f"{Fore.RED}FAILED")
            
            print("-" * 62)
            print(f"{Fore.GREEN}✅ 一键更新完成，共同步 {updated_count} 个插件。")
            return
        except Exception as e:
            print(f"{Fore.RED}❌ 更新失败: {e}")
            return

    # --- 逻辑 B: 商店交互浏览 ---
    manual_url = getattr(args, 'url', None)
    if manual_url:
        target_url = manual_url
        filename = manual_url.split("/")[-1]
    else:
        print("📡 正在获取在线插件列表 (正在尝试镜像加速)...")
        try:
            response = get_safe_content(MANIFEST_URL)
            data = response.json()
            plugins = data.get("plugins", [])
            
            if not plugins:
                print(f"{Fore.YELLOW}商店空空如也...")
                return

            choices = [f"{p['name']:<12} | {p['desc']}" for p in plugins]
            choices.append("取消退出")

            selected = questionary.select(
                "请选择要安装/更新的插件:",
                choices=choices,
                style=questionary.Style([('pointer', 'fg:cyan bold'), ('highlighted', 'fg:cyan bold')])
            ).ask()

            if not selected or "取消退出" in selected: return
            
            name = selected.split('|')[0].strip()
            p_data = next(p for p in plugins if p['name'] == name)
            filename = f"{name}.py"
            target_url = f"{RAW_BASE_URL}/{p_data['file']}"
        except Exception as e:
            print(f"{Fore.RED}❌ 无法获取清单: {e}")
            return

    # 下载执行
    save_path = os.path.join(mods_dir, filename)
    if os.path.exists(save_path) and not manual_url:
        # 交互式模式下如果文件存在，提醒更新
        if not questionary.confirm(f"插件 {filename} 已存在，是否重新下载覆盖?").ask():
            return

    print(f"📥 正在获取 {filename} ...")
    try:
        content_res = get_safe_content(target_url)
        content = content_res.text
        
        # 严谨性检查
        if "def " not in content and "__info__" not in content:
            raise ValueError("内容校验失败：下载的文件不符合插件规范。")

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"{Fore.GREEN}✅ 成功！已存入 mods/{filename}")
    except Exception as e:
        print(f"{Fore.RED}❌ 下载中断: {e}")