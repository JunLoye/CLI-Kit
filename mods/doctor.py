import socket
import time
import requests
from concurrent.futures import ThreadPoolExecutor

__info__ = {
    "help": "网络医生：检查 GitHub、Google、NPM 等开发环境连通性",
    "alias": ["dr", "netcheck"]  # 将这里的 checkup 改为 netcheck，避免与 env_check 冲突
}

def setup_args(parser):
    """该模块主要通过交互式或直接运行"""
    parser.add_argument("--timeout", type=int, default=5, help="请求超时时间")

def check_service(name, url, timeout):
    """检查单个服务的响应速度"""
    start = time.time()
    try:
        # 使用 head 请求减少流量消耗
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        elapsed = (time.time() - start) * 1000
        if response.status_code < 400:
            return name, True, f"{elapsed:.0f}ms", response.status_code
        else:
            return name, True, f"{elapsed:.0f}ms (状态码: {response.status_code})", response.status_code
    except requests.exceptions.Timeout:
        return name, False, "超时", None
    except Exception:
        return name, False, "不可达", None

def run_doctor(args, tools):
    Fore = tools["Fore"]
    timeout = getattr(args, 'timeout', 5)

    print(f"{Fore.CYAN}🩺 CLI-Kit 网络医生 - 正在诊断开发环境连通性...")
    print("-" * 62)

    # 待检查的核心开发者服务
    services = [
        ("GitHub", "https://github.com"),
        ("Google", "https://www.google.com"),
        ("PyPI (Python)", "https://pypi.org"),
        ("NPM (Node)", "https://registry.npmjs.org"),
        ("Docker Hub", "https://hub.docker.com"),
        ("GitHub Raw", "https://raw.githubusercontent.com"),
        ("Baidu (Base)", "https://www.baidu.com")
    ]

    # 使用线程池并发检查，提高效率
    print(f"{'服务名称':<15} | {'状态':<10} | {'响应延迟 / 错误原因':<25}")
    print("-" * 62)

    with ThreadPoolExecutor(max_workers=len(services)) as executor:
        futures = [executor.submit(check_service, name, url, timeout) for name, url in services]
        
        success_count = 0
        for future in futures:
            name, is_up, msg, code = future.result()
            
            if is_up:
                status_icon = f"{Fore.GREEN}● 在线"
                success_count += 1
                color_msg = f"{Fore.WHITE}{msg}"
            else:
                status_icon = f"{Fore.RED}○ 离线"
                color_msg = f"{Fore.YELLOW}{msg}"
            
            print(f"{name:<15} | {status_icon:<10} | {color_msg}")

    print("-" * 62)

    # 结果总结与建议
    if success_count == len(services):
        print(f"{Fore.GREEN}✅ 所有核心开发服务均可访问，您的网络环境非常完美！")
    elif success_count > 0:
        print(f"{Fore.YELLOW}⚠️  部分服务访问受限。")
        # 针对中国开发者常见的 GitHub/Google 失败提供建议
        if "不可达" in str(futures):
            print(f"{Fore.CYAN}💡 建议: 检测到部分国际服务连接失败，请检查您的代理设置或加速器。")
    else:
        print(f"{Fore.RED}❌ 网络连接似乎存在严重问题，请检查路由器或网线。")
    
    print("-" * 62)