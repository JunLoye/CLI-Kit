import json
import os

__info__ = {
    "help": "JSON 格式化、美化与校验工具",
    "alias": ["json", "format"]
}

def setup_args(parser):
    parser.add_argument("--file", help="要处理的 JSON 文件路径")
    parser.add_argument("--indent", type=int, default=4, help="缩进空格数")

def run_jsonpad(args, tools):
    import questionary
    Fore = tools["Fore"]

    print(f"{Fore.CYAN}📦 DevBox JsonPad - 数据美化工具")
    print("-" * 62)

    # 1. 获取输入源
    source_type = None
    json_data = None
    
    file_path = getattr(args, 'file', None)
    if not file_path:
        source_type = questionary.select(
            "请选择输入方式:",
            choices=["剪贴板读取", "手动输入", "选择文件"]
        ).ask()
    
    # 2. 获取 JSON 内容
    try:
        if source_type == "剪贴板读取":
            import pyperclip
            raw_content = pyperclip.paste()
        elif source_type == "手动输入":
            raw_content = questionary.text("请粘贴 JSON 字符串:").ask()
        elif source_type == "选择文件" or file_path:
            path = file_path if file_path else questionary.text("请输入文件路径:").ask()
            with open(path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
        
        # 3. 解析与美化
        parsed = json.loads(raw_content)
        formatted = json.dumps(parsed, indent=getattr(args, 'indent', 4), ensure_ascii=False)
        
        print(f"\n{Fore.GREEN}✅ 格式化成功:")
        print(formatted)
        print("-" * 62)
        
        # 4. 后续操作
        action = questionary.select(
            "处理完成，您想？",
            choices=["复制到剪贴板", "保存到文件", "退出"]
        ).ask()
        
        if action == "复制到剪贴板":
            import pyperclip
            pyperclip.copy(formatted)
            print("已复制！")
        elif action == "保存到文件":
            save_path = questionary.text("输入保存文件名:", default="output.json").ask()
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(formatted)
            print(f"已保存至 {save_path}")
            
    except json.JSONDecodeError as e:
        print(f"{Fore.RED}❌ JSON 格式错误: {e}")
    except Exception as e:
        print(f"{Fore.RED}⚠️ 运行错误: {e}")