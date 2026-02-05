import http.server
import socketserver
import socket
import os
import sys
import re
from urllib.parse import quote

class UploadHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            # 修复点 1: 使用 quote 处理文件名，防止空格导致网址断开
            items = []
            for f in os.listdir('.'):
                if os.path.isfile(f):
                    safe_name = quote(f)
                    items.append(f'<li><a href="{safe_name}">{f}</a></li>')
            files_list_html = "".join(items)

            # 修复点 2: 严格处理 f-string 中的大括号冲突
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>DevBox QuickServe</title>
                <style>
                    body { font-family: sans-serif; background: #f0f2f5; padding: 20px; }
                    .container { max-width: 500px; margin: auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
                    .upload-area { border: 2px dashed #ccd0d5; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }
                    input[type="submit"] { background: #1877f2; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
                    ul { word-wrap: break-word; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>🚀 QuickServe 双向传输</h2>
                    <div class="upload-area">
                        <form enctype="multipart/form-data" method="post">
                            <input name="file" type="file" required />
                            <br><br>
                            <input type="submit" value="上传到电脑" />
                        </form>
                    </div>
                    <h3>📂 目录文件列表</h3>
                    <ul>__FILES_LIST__</ul>
                </div>
            </body>
            </html>
            """
            # 使用 replace 替代 f-string 注入，彻底避免大括号解析错误
            final_html = html_template.replace("__FILES_LIST__", files_list_html)
            self.wfile.write(final_html.encode('utf-8'))
        else:
            return super().do_GET()

    def do_POST(self):
        try:
            content_type = self.headers.get('Content-Type')
            if not content_type or 'multipart/form-data' not in content_type:
                self.send_error(400, "非法提交")
                return

            boundary = content_type.split("boundary=")[1].encode()
            remainbytes = int(self.headers.get('Content-Length'))
            
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary not in line:
                self.send_error(400, "解析错误")
                return

            line = self.rfile.readline()
            remainbytes -= len(line)
            fn_match = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line.decode())
            if not fn_match:
                self.send_error(400, "无法识别文件名")
                return
            
            filename = os.path.basename(fn_match[0])
            line = self.rfile.readline()
            remainbytes -= len(line)
            line = self.rfile.readline()
            remainbytes -= len(line)

            with open(filename, 'wb') as f:
                preline = self.rfile.readline()
                remainbytes -= len(preline)
                while remainbytes > 0:
                    line = self.rfile.readline()
                    remainbytes -= len(line)
                    if boundary in line:
                        preline = preline[0:-1]
                        if preline.endswith(b'\r'):
                            preline = preline[0:-1]
                        f.write(preline)
                        break
                    else:
                        f.write(preline)
                        preline = line

            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        except Exception as e:
            self.send_error(500, f"Server Error: {e}")

    def log_message(self, format, *args):
        pass

def get_real_ip():
    """
    更严谨的 IP 获取逻辑，排除代理网卡产生的虚假 IP
    """
    import socket
    try:
        # 创建一个连接到公共 DNS 的 socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 尝试连接一个外部地址，这会触发操作系统选择真正的物理出口网卡
        s.connect(('114.114.114.114', 80))
        ip = s.getsockname()[0]
        s.close()
        
        # 兜底检查：如果是常见的代理虚假网段，则尝试备选方案
        if ip.startswith('198.18') or ip.startswith('127.'):
            raise Exception("Detected proxy or loopback IP")
            
        return ip
    except:
        # 备选方案：遍历所有网卡（需要适配不同系统，这里给出一个通用的简化逻辑）
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return '127.0.0.1'

def run_quickserve(args, tools):
    qrcode = tools["qrcode"]
    port = getattr(args, 'port', 8000)
    
    # 使用新逻辑获取真实 IP
    ip = get_real_ip()
    
    url = f"http://{ip}:{port}"
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"┌────────────────────────────────────────────────────────────┐")
    print(f"│                🚀 DevBox - QuickServe 运行中               │")
    print(f"└────────────────────────────────────────────────────────────┘")
    print(f" 🔗 访问地址: {url}")
    print("-" * 62)
    
    qr = qrcode.QRCode(version=1, box_size=1, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)
    
    with socketserver.TCPServer(("", port), UploadHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[系统] 服务已关闭。")