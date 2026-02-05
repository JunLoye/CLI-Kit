import time
import sys
import os

__info__ = {
    "help": "沉浸式专注倒计时",
    "alias": ["tick", "timer"]
}

def setup_args(parser):
    """定义命令行参数模式"""
    parser.add_argument("--work", type=float, help="专注时间 (分钟)")

def format_time(seconds):
    """将秒数格式化为 mm:ss"""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def run_zentick(args, tools):
    """执行主逻辑"""
    import questionary
    Fore = tools["Fore"]
    Style = tools["Style"]
    notification = tools["notification"]
    
    # --- 1. 参数自适应获取 ---
    work_mins = getattr(args, 'work', None)
    
    # 如果命令行没有传 --work 参数，则发起交互式询问
    if work_mins is None:
        choice = questionary.select(
            "想要专注多久?",
            choices=[
                "25 分钟 (标准番茄钟)",
                "45 分钟 (深度思考)",
                "60 分钟 (极客模式)",
                "自定义"
            ],
            style=questionary.Style([
                ('pointer', 'fg:cyan bold'),
                ('highlighted', 'fg:cyan bold'),
            ])
        ).ask()
        
        if not choice: return  # 用户取消操作
        
        if "25" in choice: work_mins = 25
        elif "45" in choice: work_mins = 45
        elif "60" in choice: work_mins = 60
        else:
            val = questionary.text("请输入分钟数 (例如 10):").ask()
            # 严谨校验：确保输入的是数字
            if val and val.replace('.', '', 1).isdigit():
                work_mins = float(val)
            else:
                print(f"{Fore.RED}⚠️ 输入无效，将使用默认值 25 分钟。")
                work_mins = 25

    total_seconds = int(work_mins * 60)
    
    # --- 2. 界面初始化 ---
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.CYAN}┌────────────────────────────────────────────────────────────┐")
    print(f"│                ⏳ DevBox - ZenTick 专注模式                │")
    print(f"└────────────────────────────────────────────────────────────┘")
    print(f" 🎯 目标时长 : {work_mins} 分钟")
    print(f" 🔔 提醒状态 : 已开启桌面通知")
    print(f" 🛑 退出操作 : 按 Ctrl+C 放弃本次专注")
    print("-" * 62)

    # 发送启动通知
    try:
        notification.notify(
            title="ZenTick 启动",
            message=f"专注之旅开始：预计时长 {work_mins} 分钟",
            timeout=5
        )
    except Exception:
        pass # 防止某些系统环境通知权限报错

    # --- 3. 核心倒计时循环 ---
    start_time = time.time()
    try:
        while True:
            elapsed = int(time.time() - start_time)
            remaining = total_seconds - elapsed
            
            if remaining <= 0:
                break
                
            progress = elapsed / total_seconds
            bar_length = 35
            filled_length = int(bar_length * progress)
            
            # 构建进度条视觉效果
            bar = "█" * filled_length + "─" * (bar_length - filled_length)
            
            # 最后 60 秒变红，增加紧迫感
            timer_color = Fore.RED if remaining <= 60 else Fore.GREEN
            
            # 使用 \r 刷新行，\033[K 清除残留字符
            sys.stdout.write(
                f"\r {Fore.WHITE}[{bar}] "
                f"{timer_color}{format_time(remaining)} "
                f"{Fore.WHITE}({int(progress * 100)}%) \033[K"
            )
            sys.stdout.flush()
            
            time.sleep(0.5) # 平滑刷新频率

        # --- 4. 任务完成处理 ---
        sys.stdout.write(f"\r {Fore.GREEN}[{'█' * 35}] 00:00 (100%) \n")
        print("-" * 62)
        print(f"\n{Fore.GREEN}{Style.BRIGHT} 🎉 恭喜！您已成功完成本次专注任务。")
        
        try:
            notification.notify(
                title="专注达成！",
                message=f"已完成 {work_mins} 分钟专注，喝口水休息一下吧。",
                timeout=10
            )
        except Exception:
            pass

    except KeyboardInterrupt:
        actual_time = int(time.time() - start_time)
        print(f"\n\n{Fore.YELLOW} [系统] 专注被中断。")
        print(f" {Fore.WHITE} 本次有效专注时长: {format_time(actual_time)}")
        sys.exit(0)