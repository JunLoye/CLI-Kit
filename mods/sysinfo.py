import platform
import psutil
import shutil

def run_sysinfo(args, tools):
    Fore = tools["Fore"]
    
    # 获取系统基本信息
    uname = platform.uname()
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = shutil.disk_usage("/")

    print(f"{Fore.CYAN}🖥️  DevBox SysInfo - 系统状态报告")
    print("-" * 62)
    print(f"操作系统 : {uname.system} {uname.release} (v{uname.version})")
    print(f"处理器   : {uname.processor}")
    
    # 进度条显示函数
    def print_bar(label, percent, color):
        bar_len = 20
        filled = int(bar_len * percent / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"{label:<8} : {color}[{bar}] {percent}%")

    print_bar("CPU 负载", cpu_usage, Fore.GREEN if cpu_usage < 70 else Fore.RED)
    print_bar("内存占用", memory.percent, Fore.YELLOW)
    
    # 磁盘信息
    disk_p = (disk.used / disk.total) * 100
    print_bar("磁盘空间", round(disk_p, 1), Fore.BLUE)
    print(f"{Fore.WHITE}详情     : 已用 {disk.used//10**9}GB / 总共 {disk.total//10**9}GB")
    print("-" * 62)