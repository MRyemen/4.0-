""""

Author:Dvir Zilber

Program name:Web_server.py

Description: A server that recives a client, recives an html request and sends back the correct file in the web root based on the command

"""


import socket
import os
import logging

# Constants
QUEUE_SIZE = 5
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2
WEB_ROOT = r'C:\webroot\webroot'

# Mappings for Content-Type headers [cite: 17]
CONTENT_TYPES = {
    'html': 'text/html; charset=utf-8',
    'jpg': 'image/jpeg',
    'css': 'text/css',
    'js': 'text/javascript; charset=UTF-8',
    'txt': 'text/plain',
    'ico': 'image/x-icon',
    'gif': 'image/jpeg',
    'png': 'image/png'
}


def get_file_data(file_path):
    """Reads file content in binary mode."""
    with open(file_path, 'rb') as f:
        return f.read()


def validate_http_request(request):
    """
    Validates GET request format: 'GET URI HTTP/1.1\r\n'.
    """
    try:
        decoded_request = request.decode()
        lines = decoded_request.split("\r\n")
        if len(lines) < 1:
            return False, None

        parts = lines[0].split(" ")
        if len(parts) != 3:
            logging.error(f"request is invalid!: {parts}")
            return False, None


        method, resource, version = parts
        if method == "GET" and version == "HTTP/1.1":
            logging.info(f"request is valid: {resource}")
            return True, resource

        return False, None 
    except Exception:
        return False, None


def handle_client_request(resource, client_socket):
    """Generates and sends the HTTP response."""

    # 1. Handle special URIs
    if resource == '/':
        resource = '/index.html'
        logging.info(f"index is: {resource}")

    if resource == '/forbidden':
        client_socket.send("HTTP/1.1 403 FORBIDDEN\r\n\r\n".encode())
        logging.info(f"response is: {resource}")
        return
    if resource == '/moved':
        client_socket.send("HTTP/1.1 302 MOVED TEMPORARILY\r\nLocation: /\r\n\r\n".encode())
        logging.info(f"response is: {resource}")
        return
    if resource == '/error':
        client_socket.send("HTTP/1.1 500 INTERNAL SERVER ERROR\r\n\r\n".encode())
        logging.info(f"response is: {resource}")
        return
    else:
        resource = resource

    # 2. Check if file exists in WEB_ROOT
    file_path = os.path.join(WEB_ROOT, resource.lstrip('/'))
    if not os.path.isfile(file_path):
        client_socket.send("HTTP/1.1 404 NOT FOUND\r\n\r\n".encode())
        return

    # 3. Determine Content-Type 
    file_extension = file_path.split('.')[-1].lower()
    content_type = CONTENT_TYPES.get(file_extension, 'application/octet-stream')

    # 4. Read data and build response [cite: 16, 18, 48]
    data = get_file_data(file_path)
    header = f"HTTP/1.1 200 OK\r\n"
    header += f"Content-Type: {content_type}\r\n"
    header += f"Content-Length: {len(data)}\r\n"
    header += "\r\n"

    client_socket.send(header.encode() + data)
    logging.info(f"file + headers were sent successfully: {header}")


def handle_client(client_socket):
    """Main client loop."""
    try:
        while True:
            client_request = client_socket.recv(1024)
            if not client_request:
                break

            is_valid, resource = validate_http_request(client_request)

            if is_valid:
                print(f"Valid request for: {resource}")
                handle_client_request(resource, client_socket)
            else:
                # Remove the [cite: 10] from this line in your code
                client_socket.send("HTTP/1.1 400 BAD REQUEST\r\n\r\n".encode())
                break
    except socket.timeout:
        print("Connection timed out.")
    finally:
        client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print(f"Server listening on port {PORT}...")
        logging.error(f"Server listening on port {PORT}...")


        while True:
            client_socket, addr = server_socket.accept()
            # Remove the [cite: 40] from this line in your code
            client_socket.settimeout(SOCKET_TIMEOUT)
            handle_client(client_socket)
    except Exception as e:
        print(f"Server Error: {e}")
        logging.error(f"Server Error: {e}")
    finally:
        server_socket.close()


if __name__ == "__main__":
    """
    Configures the logging settings and starts the main server loop.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=
        [
            logging.FileHandler('logg_of_server'),
            # logging.StreamHandler() (only when there is a need to show the logs to the user)
        ]
    )
    main()


