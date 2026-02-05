import os
import sys
import shutil
import subprocess

def build():
    # 1. 配置参数
    APP_NAME = "CLI-Kit"
    ENTRY_POINT = "main.py"
    DIST_DIR = "release"
    
    print(f"🚀 开始构建 {APP_NAME}...")

    # 2. 检查并清理旧的构建环境
    for folder in ['build', 'dist', DIST_DIR]:
        if os.path.exists(folder):
            shutil.rmtree(folder)

    # 3. 显式列出所有插件可能用到的库，强制 PyInstaller 打包
    # 这样即便 mods 是动态加载的，exe 内部也有运行环境
    hidden_imports = [
        "--hidden-import=questionary",
        "--hidden-import=colorama",
        "--hidden-import=ping3",
        "--hidden-import=plyer",
        "--hidden-import=psutil",
        "--hidden-import=pyperclip",
        "--hidden-import=qrcode",
        "--hidden-import=PIL",
        "--hidden-import=requests"
    ]

    # 4. 执行 PyInstaller 命令
    # --onefile: 单文件模式
    # --clean: 打包前清理缓存
    # --name: 指定 exe 名称
    build_cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--clean",
        f"--name={APP_NAME}",
        "--console" # 如果需要隐藏黑窗口可以改为 --windowed
    ] + hidden_imports + [ENTRY_POINT]

    try:
        subprocess.check_call(build_cmd)
        print(f"\n✅ 核心引擎 {APP_NAME}.exe 构建成功！")
    except subprocess.CalledProcessError:
        print("\n❌ 构建失败，请检查是否安装了 pyinstaller 及其依赖。")
        return

    # 5. 组装发布包目录结构
    print(f"📦 正在整理发布包...")
    os.makedirs(DIST_DIR, exist_ok=True)
    
    # 移动主程序
    shutil.move(os.path.join("dist", f"{APP_NAME}.exe"), os.path.join(DIST_DIR, f"{APP_NAME}.exe"))
    
    # 复制子文件夹（mods 和 core）
    # 我们只复制结构，因为 mods 是外置插件，用户可以后期自行添加
    if os.path.exists("mods"):
        shutil.copytree("mods", os.path.join(DIST_DIR, "mods"))
    if os.path.exists("core"):
        shutil.copytree("core", os.path.join(DIST_DIR, "core"))

    print(f"\n✨ 构建完成！请查看 '{DIST_DIR}' 文件夹。")
    print(f"提示: 将整个 '{DIST_DIR}' 拷贝到任何电脑即可直接运行。")

if __name__ == "__main__":
    build()