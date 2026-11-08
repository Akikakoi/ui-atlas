"""启动 UI Atlas 预览服务。

用法：
    python ui-atlas/serve.py          # 默认 8760 起，自动挑空闲端口，并打开浏览器
    python ui-atlas/serve.py 9000
环境变量 ATLAS_NO_BROWSER=1 可只起服务、不打开浏览器（测试用）。
"""

from __future__ import annotations

import os
import socket
import socketserver
import sys
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # ui-atlas/


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        pass


def pick_port(start: int = 8760, tries: int = 20) -> int:
    for port in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("端口都被占用了，请手动指定一个。")


def main(argv: list[str]) -> int:
    if not (ROOT / "index.html").is_file():
        print(f"找不到 ui-atlas/index.html（{ROOT}）")
        return 1
    start = 8760
    if len(argv) > 1:
        try:
            start = int(argv[1])
        except ValueError:
            print(f"端口参数不是数字：{argv[1]}")
            return 1
    port = pick_port(start)
    url = f"http://127.0.0.1:{port}/index.html"
    with socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler) as httpd:
        httpd.daemon_threads = True
        if os.environ.get("ATLAS_NO_BROWSER") != "1":
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        print("UI Atlas 已启动：")
        print(f"  {url}")
        print("Ctrl+C 或关闭窗口停止。")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
