import subprocess
import os
import platform
import shutil

__info__ = {
    "help": "开发环境体检：一键检查 Node, Python, Docker 等版本",
    "alias": ["env", "checkup"]
}

def setup_args(parser):
    """该模块目前不需要额外参数，直接运行即可"""
    pass

def get_version(cmd):
    """
    尝试运行命令获取版本号。
    如果命令不存在，返回 None；否则返回版本号字符串。
    """
    # 查找命令是否存在
    if not shutil.which(cmd[0]):
        return None
    
    try:
        # 运行类似 'node -v' 的命令
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            shell=True if platform.system() == "Windows" else False,
            timeout=2
        )
        output = result.stdout.strip() or result.stderr.strip()
        # 简单清理输出，只取第一行（有些工具输出很长）
        return output.split('\n')[0] if output else "已安装 (未知版本)"
    except Exception:
        return "检查失败"

def run_env_check(args, tools):
    Fore = tools["Fore"]
    
    print(f"{Fore.CYAN}🛡️  CLI-Kit 环境体检报告")
    print(f"系统平台 : {platform.system()} {platform.release()}")
    print("-" * 62)

    # 待检查的工具列表：(工具名, 检查命令)
    checks = [
        ("Python", ["python", "--version"]),
        ("Node.js", ["node", "-v"]),
        ("NPM", ["npm", "-v"]),
        ("Docker", ["docker", "-v"]),
        ("Git", ["git", "--version"]),
        ("Java", ["java", "-version"]),
        ("Go", ["go", "version"]),
        ("Rust", ["rustc", "--version"]),
        ("MySQL", ["mysql", "--version"]),
        ("Redis", ["redis-server", "--version"]),
    ]

    print(f"{'工具项目':<15} | {'状态 / 版本号':<30}")
    print("-" * 62)

    found_count = 0
    for name, cmd in checks:
        version = get_version(cmd)
        if version:
            status = f"{Fore.GREEN}{version}"
            found_count += 1
        else:
            status = f"{Fore.RED}未安装"
        
        print(f"{name:<15} | {status}")

    print("-" * 62)
    print(f"📊 统计：已安装 {found_count} / 总计 {len(checks)}")
    
    # 额外逻辑：如果安装了 Node 但没安装 Docker，给个温馨提示
    if not any("docker" in str(c).lower() for n, c in checks if get_version(c)):
        print(f"\n{Fore.YELLOW}💡 提示: 您似乎还没有安装 Docker，在进行容器化开发时可能会用到。")

    print("-" * 62)