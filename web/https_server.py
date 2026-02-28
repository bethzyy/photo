"""
照片整理工具 - HTTPS 服务器
用于支持手机端访问（File System Access API 需要 HTTPS）
"""

import http.server
import ssl
import socket
import sys
import os

PORT = 8443

def get_local_ip():
    """获取本机局域网 IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def generate_cert():
    """生成自签名证书"""
    cert_file = 'cert.pem'
    key_file = 'key.pem'

    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("使用已有证书")
        return True

    print("正在生成自签名证书...")

    try:
        from OpenSSL import crypto

        # 创建密钥
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 2048)

        # 创建证书
        cert = crypto.X509()
        cert.get_subject().CN = 'localhost'
        cert.get_subject().O = 'Photo Organizer'
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)  # 10年
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha256')

        # 添加 SAN 扩展以支持 IP 地址
        cert.add_extensions([
            crypto.X509Extension(b"subjectAltName", False,
                b"DNS:localhost,IP:127.0.0.1")
        ])

        # 保存
        with open(cert_file, 'wb') as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(key_file, 'wb') as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

        print("✓ 证书生成成功")
        return True

    except ImportError:
        print("正在安装 pyOpenSSL...")
        os.system(f'{sys.executable} -m pip install pyopenssl -q')
        return generate_cert()

    except Exception as e:
        print(f"✗ 证书生成失败: {e}")
        return False

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """添加 CORS 支持的请求处理器"""

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def main():
    print()
    print("╔════════════════════════════════════════╗")
    print("║   照片整理工具 - HTTPS 服务器          ║")
    print("╚════════════════════════════════════════╝")
    print()

    # 切换到脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # 生成证书
    if not generate_cert():
        print()
        print("无法生成证书，请尝试:")
        print("1. pip install pyopenssl")
        print("2. 或使用 ngrok: ngrok http 8080")
        return

    # 获取 IP
    local_ip = get_local_ip()

    print()
    print("┌────────────────────────────────────────┐")
    print("│  手机访问步骤:                         │")
    print("│  1. 确保手机和电脑在同一 WiFi          │")
    print("│  2. 在手机浏览器输入下方 HTTPS 地址    │")
    print("│  3. 会提示"不安全"，点击"高级"→继续   │")
    print("│  4. 然后就可以正常使用了               │")
    print("└────────────────────────────────────────┘")
    print()
    print("服务器地址:")
    print(f"  本地: https://localhost:{PORT}")
    print(f"  手机: https://{local_ip}:{PORT}")
    print()
    print("按 Ctrl+C 停止服务器")
    print("══════════════════════════════════════════")
    print()

    # 创建服务器
    server = http.server.HTTPServer(('0.0.0.0', PORT), CORSRequestHandler)

    # 配置 SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    server.socket = context.wrap_socket(server.socket, server_side=True)

    print(f"✓ HTTPS 服务器已启动在端口 {PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")

if __name__ == '__main__':
    main()
