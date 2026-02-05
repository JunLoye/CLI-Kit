import time
import sys
import ctypes
import os

def is_admin():
    """检查是否拥有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        # 非 Windows 系统检查方式
        return os.getuid() == 0 if hasattr(os, 'getuid') else False

def run_netspeed(args, tools):
    ping = tools["ping"]
    Fore = tools["Fore"]
    
    # 严谨处理参数获取
    target = getattr(args, 'target', '114.114.114.114')
    
    print(f"{Fore.CYAN}┌────────────────────────────────────────────────────────────┐")
    print(f"│                🚀 DevBox - NetSpeed 网络监控               │")
    print(f"└────────────────────────────────────────────────────────────┘")
    
    # 权限检查提示
    if not is_admin():
        print(f"{Fore.YELLOW}[警告] 当前未以管理员身份运行。ICMP Ping 可能会失败。")
        print(f"{Fore.YELLOW}[建议] 请尝试使用 管理员模式(Windows) 或 sudo(Linux) 重新运行。")
        print("-" * 62)

    print(f" 🎯 监控目标: {target}")
    print(f" 🛑 停止操作: 按 Ctrl+C")
    print("-" * 62 + "\n")

    try:
        while True:
            # ping3.ping 返回值是秒(s)，None 表示失败
            try:
                delay = ping(target, timeout=2)
                
                if delay is None or delay is False:
                    print(f"{Fore.RED}● {time.strftime('%H:%M:%S')} | ❌ 请求超时或目标不可达")
                else:
                    ms = delay * 1000
                    # 根据延迟设置颜色
                    if ms < 50:
                        color = Fore.GREEN
                    elif ms < 150:
                        color = Fore.YELLOW
                    else:
                        color = Fore.RED
                        
                    print(f"{color}● {time.strftime('%H:%M:%S')} | 延迟: {ms:.2f} ms")
            
            except Exception as e:
                print(f"{Fore.RED}● 运行异常: {e}")
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[系统] 监控已停止。")