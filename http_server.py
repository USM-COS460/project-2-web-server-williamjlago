import socket
import mimetypes
import threading
from datetime import datetime, timezone
import sys
import os

server_name = "LocalHTTPServer"

def send_response(conn, status, mimetype, body):
    dt = datetime.now(timezone.utc)
    timestamp = dt.strftime("%a, %d %b %Y %X GMT")
    header = (
            f"HTTP/1.1 {status}\r\n"
            f"Date: {timestamp}\r\n"
            f"Server: {server_name}/2.1\r\n"
            f"Content-Type: {mimetype}\r\n"
            f"Content-Length: {len(body)}\r\n"
            "\r\n"
    )
    conn.sendall(header.encode('utf-8') + body)
    return

def safe_join(root, path):
    # Normalize path and ensure it does not escape the server root
    path = path.lstrip('/')
    full_path = os.path.normpath(os.path.join(root, path))
    abs_root = os.path.abspath(root)
    abs_full = os.path.abspath(full_path)
    if not abs_full.startswith(abs_root):
        return None
    return abs_full

def handle_request(conn, addr, docroot):
    try:
        request = conn.recv(2048).decode('utf-8', errors='replace')
        lines = request.splitlines()
        if not lines:
            return

        request_line = lines[0]
        parts = request_line.split()
        if len(parts) != 3:
            code = "400 Bad Request"
            send_response(conn, code, "text/plain", f"{code}\r\n".encode('utf-8'))
            return

        method, path, versions = parts

        # Only worried about handling GET
        if method != "GET":
            code = "501 Not Implemented"
            send_response(conn, code, "text/plain", f"{code}\r\n".encode('utf-8'))
            return

        # Automatically display index.html if root requested
        if path == "/":
            path = "/index.html"

        full_path = safe_join(docroot, path)
        if full_path is None or not os.path.exists(full_path):
            code = "404 Not Found"
            send_response(conn, code, "text/plain", f"{code}\r\n".encode('utf-8'))
            return

        # Serve file
        code = "200 OK"
        with open(full_path, 'rb') as f:
            content = f.read()

        mimetype, _ = mimetypes.guess_type(full_path)
        if mimetype is None:
            mimetype = "application/octet-stream"

        send_response(conn, code, mimetype, content)
    finally:
        conn.close()
        print(f"Client {str(addr)} disconnected")

def serve(docroot, host='0.0.0.0', port=3377):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"Serving files from {docroot} on {host}:{port}...")

    while True:
        conn, addr = s.accept()
        print(f"Client {str(addr)} connected")
        thread = threading.Thread(target=handle_request, args=(conn, addr, docroot))
        print(f"Thread created for {str(addr)}; total threads: {str(threading.active_count())}")
        thread.start()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python http_server.py <port> <docroot>")
        sys.exit(1)
    port = int(sys.argv[1])
    docroot = sys.argv[2]
    serve(docroot, port=port)