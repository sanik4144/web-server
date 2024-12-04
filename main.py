import socket
import json
import os
from urllib.parse import unquote

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8080

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def send_response(client_socket, status_code, content_type, content):
    response = f'HTTP/1.1 {status_code}\r\n'
    response += f'Content-Type: {content_type}\r\n'
    response += 'Access-Control-Allow-Origin: *\r\n'
    response += f'Content-Length: {len(content)}\r\n'
    response += '\r\n'
    response += content
    client_socket.sendall(response.encode())

def handle_request(client_socket, request):
    headers = request.split('\r\n')
    first_line = headers[0].split()
    
    if len(first_line) < 2:
        send_response(client_socket, '400 Bad Request', 'text/plain', 'Bad Request')
        return

    http_method, path = first_line[0], unquote(first_line[1])
    
    if http_method == 'GET':
        if path == '/':
            with open('index.html', 'r') as file:
                content = file.read()
            send_response(client_socket, '200 OK', 'text/html', content)
        elif path == '/book':
            try:
                with open('book.json', 'r') as file:
                    content = file.read()
                send_response(client_socket, '200 OK', 'application/json', content)
            except FileNotFoundError:
                send_response(client_socket, '404 Not Found', 'text/plain', 'Book data not found')
            except json.JSONDecodeError:
                send_response(client_socket, '500 Internal Server Error', 'text/plain', 'Invalid JSON data')
        elif path == '/books':
            with open('books.html', 'r') as file:
                content = file.read()
            send_response(client_socket, '200 OK', 'text/html', content)
        elif path.startswith('/api/book/'):
            book_id = path.split('/')[-1]
            books = load_json('book.json')['books']
            book = next((b for b in books if str(b['id']) == book_id), None)
            if book:
                content = json.dumps(book)
                send_response(client_socket, '200 OK', 'application/json', content)
            else:
                send_response(client_socket, '404 Not Found', 'text/plain', 'Book not found')
        else:
            send_response(client_socket, '404 Not Found', 'text/plain', 'Page not found')
    else:
        send_response(client_socket, '405 Method Not Allowed', 'text/plain', 'Method not allowed')

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(1)

    print(f'Listening on port {SERVER_PORT} ...')

    while True:
        client_socket, client_address = server_socket.accept()
        try:
            request = client_socket.recv(1024).decode()
            handle_request(client_socket, request)
        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    run_server()

