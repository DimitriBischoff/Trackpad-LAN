# coding: utf-8

import asyncio
from websockets import serve, WebSocketServerProtocol, exceptions as WsExceptions
from datetime import datetime
import win32api, win32con
import time
import struct
import http.server
import socketserver
import io
from qrcode import QRCode


MOUSE_EVENT_DOWN = [win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_MIDDLEDOWN, win32con.MOUSEEVENTF_RIGHTDOWN]
MOUSE_EVENT_UP = [win32con.MOUSEEVENTF_LEFTUP, win32con.MOUSEEVENTF_MIDDLEUP, win32con.MOUSEEVENTF_RIGHTUP]

def debug(*args):
    print(f'[{datetime.now()}]', *args, flush=True)


class WebSocketServer:
    def __init__(self, port):
        self.port = port
        self.server = None

    def mouse(self, raw):
        x, y = struct.unpack('bb', raw)
        # debug(x, y)
        _x, _y = win32api.GetCursorPos()
        win32api.SetCursorPos((_x + x, _y + y))

    def click(self, raw):
        button, down = struct.unpack('B?', raw)
        # debug(raw, button, down)
        win32api.mouse_event(MOUSE_EVENT_DOWN[button] if down else MOUSE_EVENT_UP[button], 0, 0)

    def keyboard(self, raw):
        key, down = struct.unpack('B?', raw)
        # debug(raw, key, down)
        if down:
            win32api.keybd_event(key, 0, 0, 0)
        else:
            win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0) 

    async def handle(self, ws, path):
        # debug(f'nouvelle connexion: [{path}] - {ws}')
        commands = [self.mouse, self.click, self.keyboard, debug]
        try:
            async for raw in ws:
                try:
                    # debug(raw)
                    commands[raw[0]](raw[1:])
                except Exception as e:
                    debug(f'error user: {e}')
        except Exception as e:
            # debug(f'error system: {e}')
            pass
            

    def run(self):
        debug(f'Server websocket run :{self.port}')
        self.server = serve(self.handle, '0.0.0.0', self.port)
        asyncio.get_event_loop().run_until_complete(self.server)

    def wait(self):
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            pass


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        with open('index.html', 'rb') as file:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(file.read())
    def log_message(self, format, *args):
        return

def run_server_http(port):
    import threading

    debug("version: 0.1.0")
    httpd = socketserver.TCPServer(("0.0.0.0", port), Handler)
    th = threading.Thread(target=httpd.serve_forever)
    th.start()
    debug(f'Server http run: {port}')
    return httpd, th

def qrcode(url):
    qr = QRCode()
    qr.add_data(url)
    f = io.StringIO()
    qr.print_ascii(out=f, invert=True)
    f.seek(0)
    return f.read()


if __name__ == '__main__':
    import socket

    httpd, th = run_server_http(6660)
    ws = WebSocketServer(6661)
    url = f'http://{socket.gethostbyname_ex(socket.gethostname())[-1][-1]}:6660'

    ws.run()
    debug("Trackpad-LAN ready")
    debug(url)
    print(qrcode(url))
    ws.wait()
    httpd.shutdown()
    th.join()
