import socket
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
import sys

__info__ = {
    "help": "深度网络诊断 + 网址一键访问",
    "alias": ["scan", "check"]
}

def setup_args(parser):
    parser.add_argument("target", nargs="?", help="诊断目标 IP 或域名")
    parser.add_argument("--ports", help="端口范围 (如 80,443,3000)")

def check_http(target, port):
    """检查 Web 服务并返回状态码和完整 URL"""
    protocol = "https" if port == 443 else "http"
    url = f"{protocol}://{target}:{port}"
    try:
        req = Request(url, headers={'User-Agent': 'DevBox-Scanner'})
        with urlopen(req, timeout=1.5) as response:
            return response.getcode(), url
    except:
        return None, url

def check_port(target, port):
    """检查 TCP 端口是否开放"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.8)
            if s.connect_ex((target, port)) == 0:
                return port
    except:
        return None

def run_portscan(args, tools):
    import questionary
    Fore = tools["Fore"]
    ping_func = tools["ping"]

    print(f"{Fore.CYAN}🔍 DevBox PortScan Pro - 深度诊断与访问")
    
    target = getattr(args, 'target', None)
    if not target:
        target = questionary.text("请输入诊断目标:", default="127.0.0.1").ask()

    # 1. 动态选择检查项
    check_types = ["ping", "ports", "http"]
    if len(sys.argv) == 1:
        check_types = questionary.checkbox(
            "请选择检查项目:",
            choices=[
                questionary.Choice("Ping 测试 (ICMP)", "ping", checked=True),
                questionary.Choice("端口扫描与 Web 验证", "ports", checked=True),
            ]
        ).ask()

    print("-" * 62)

    # --- Ping 阶段 ---
    if "ping" in check_types:
        delay = ping_func(target, timeout=1)
        if delay:
            print(f"{Fore.GREEN}[在线] Ping 响应: {delay*1000:.2f} ms")
        else:
            print(f"{Fore.RED}[离线] ICMP 无响应")
        print()

    # --- 扫描阶段 ---
    port_input = getattr(args, 'ports', None)
    if not port_input:
        port_input = questionary.text("端口范围:", default="80,443,8000,8080,3000").ask()

    if port_input:
        ports = []
        for part in port_input.split(','):
            if '-' in part:
                s, e = map(int, part.split('-'))
                ports.extend(range(s, e + 1))
            else:
                ports.append(int(part))

        web_urls = [] # 用于存储发现的可用网址
        
        def diagnostic_worker(p):
            is_open = check_port(target, p)
            if is_open:
                code, url = check_http(target, p)
                return {"port": p, "code": code, "url": url}
            return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(diagnostic_worker, ports))
            
            for res in filter(None, results):
                status = f"{Fore.GREEN}[开放] 端口 {res['port']:<5}"
                if res['code']:
                    status += f" | {Fore.CYAN}HTTP {res['code']} | {res['url']}"
                    web_urls.append(res['url'])
                print(status)

        # --- 网址快捷访问逻辑 ---
        if web_urls:
            print("-" * 62)
            should_open = questionary.confirm("检测到 Web 服务，是否立即打开浏览器访问?").ask()
            if should_open:
                if len(web_urls) == 1:
                    webbrowser.open(web_urls[0])
                    print(f"✅ 已打开: {web_urls[0]}")
                else:
                    to_open = questionary.select(
                        "请选择要访问的网址:",
                        choices=web_urls
                    ).ask()
                    if to_open:
                        webbrowser.open(to_open)
                        print(f"✅ 已打开: {to_open}")
    
    print("-" * 62)