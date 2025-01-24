#3 Доп задание
import socket
import threading
import os

LOG_HOST = '127.0.0.1'
LOG_PORT = 6000
LOG_FILE_PATH = 'server_log.txt'

def log_to_file(message):
    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(message + '\n')

def handle_log_client(client_socket, addr):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print('logged')
                log_to_file(f"{addr}: {message}")
        except ConnectionResetError:
            break

def log_server():
    log_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    log_server_socket.bind((LOG_HOST, LOG_PORT))
    log_server_socket.listen(5)
    print(f"Log Server started on host:port {LOG_HOST}:{LOG_PORT}")

    while True:
        client_socket, addr = log_server_socket.accept()
        print(f"Log Client connected: {addr}")
        log_thread = threading.Thread(target=handle_log_client, args=(client_socket, addr))
        log_thread.start()

if __name__ == '__main__':
    log_server()
