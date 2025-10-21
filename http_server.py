import socket

def serve(host='0.0.0.0', port=3377):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"Serving HTTP on {host}:{port}...")

    while True:
        conn, addr = s.accept()
        request = conn.recv(2048).decode('utf-8', errors='replace')
        print(f"--- Request from {addr} ---\n{request}")

        # Split request into lines and parse
        lines = request.splitlines()
        if not lines:
            conn.close()
            continue
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
            conn.close()
            continue

        method, path, versions = parts

        # Only worried about handling GET
        if method != "GET":
            response_body = "Method not implemented"
            response = (
                "HTTP/1.1 501 Not Implemented\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "Content-Type: text/plain\r\n"
                "\r\n"
                + response_body
            )
            conn.sendall(response.encode('utf-8'))
            conn.close()
            continue

        # Acknowledge valid GET request
        response_body = f"{path} requested"
        response = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "Content-Type: text/plain\r\n"
            "\r\n"
            + response_body
        )
        conn.sendall(response.encode('utf-8'))
        conn.close()

serve()