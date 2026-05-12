#!/usr/bin/env python3
"""
server.py — Hub local para Equity Risk Report
Corre con:  python3 server.py
Abre automáticamente en http://localhost:8080
"""

import os, json, threading, webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from actualizar_hub import scan          # reutiliza la lógica del scanner

PORT = 8080
BASE = os.path.dirname(os.path.abspath(__file__))


class HubHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE, **kwargs)

    def log_message(self, fmt, *args):
        # Silencia el log de cada request (deja sólo errores)
        if args and str(args[1]) not in ('200', '304'):
            super().log_message(fmt, *args)

    def end_headers(self):
        # Prevent browser from caching HTML files so changes are reflected immediately
        if self.path.endswith('.html') or self.path == '/' or '?' not in self.path:
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        if self.path == '/api/refresh':
            self._handle_refresh()
        else:
            super().do_GET()

    def _handle_refresh(self):
        try:
            reports = scan()
            body = json.dumps(reports, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
            print(f'  ↻  Refresh: {len(reports)} reporte(s) encontrado(s)')
        except Exception as e:
            err = json.dumps({'error': str(e)}).encode()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(err)))
            self.end_headers()
            self.wfile.write(err)
            print(f'  ✗  Error en refresh: {e}')


def main():
    os.chdir(BASE)
    url = f'http://localhost:{PORT}'
    try:
        server = HTTPServer(('localhost', PORT), HubHandler)
    except OSError:
        # Port already in use — server is already running, just open the browser
        print(f'\n  Hub ya estaba corriendo en {url}')
        webbrowser.open(url)
        return
    print(f'\n  Hub corriendo en {url}')
    print('  Ctrl+C para detener\n')
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Servidor detenido.')


if __name__ == '__main__':
    main()
