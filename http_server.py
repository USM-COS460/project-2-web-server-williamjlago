import socket
import mimetypes
import sys
import os

def safe_join(root, path):
    # Normalize path and ensure it does not escape the web root
    path = path.lstrip('/')
    full_path = os.path.normpath(os.path.join(root, path))
    abs_root = os.path.abspath(root)
    abs_full = os.path.abspath(full_path)
    if not abs_full.startswith(abs_root):
        return None
    return abs_full

def handle_request(conn, docroot):
    request = conn.recv(2048).decode('utf-8', errors='replace')
    lines = request.splitlines()
    if not lines:
        return

    request_line = lines[0]
    parts = request_line.split()
    if len(parts) != 3:
        response_body = "Malformed request line"
        response = (
                "HTTP/1.1 400 Bad Request\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "Content-Type: text/plain\r\n"
                "\r\n"
                + response_body
        )
        conn.sendall(response.encode('utf-8'))
        return

    method, path, versions = parts

    # Only worried about handling GET
    if method != "GET":
        response_body = "501 Not Implemented"
        response = (
                "HTTP/1.1 501 Not Implemented\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "Content-Type: text/plain\r\n"
                "\r\n"
                + response_body
        )
        conn.sendall(response.encode('utf-8'))
        return

    # Handle root request
    if path == "/":
        path = "/index.html"

    full_path = safe_join(docroot, path)
    if full_path is None or not os.path.exists(full_path):
        response_body = "404 Not Found"
        response = (
                "HTTP/1.1 404 Not Found\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "Content-Type: text/plain\r\n"
                "\r\n"
                + response_body
        )
        conn.sendall(response.encode('utf-8'))
        return

    # Serve file
    with open(full_path, 'rb') as f:
        content = f.read()

    mimetype, _ = mimetypes.guess_type(full_path)
    if mimetype is None:
        mimetype = "application/octet-stream"

    header = (
        "HTTP/1.1 200 OK\r\n"
        f"Content-Length: {len(content)}\r\n"
        f"Content-Type: {mimetype}\r\n"
        "\r\n"
    )

    conn.sendall(header.encode('utf-8') + content)

def serve(docroot, host='0.0.0.0', port=3377):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"Serving files from {docroot} on {host}:{port}...")

    while True:
        conn, addr = s.accept()
        handle_request(conn, docroot)
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python http_server.py <port> <docroot>")
        sys.exit(1)
    port = int(sys.argv[1])
    docroot = sys.argv[2]
    serve(docroot, port=port)