import socket
import threading
import os
import platform
import json
import psutil


HOST = '127.0.0.1'
PORT = 8081

LOG_SERVER_ADDRESS = ('127.0.0.1', 6000)


def get_data() -> dict:
    return {
        "server_pid": os.getpid(),
        "priority_process_num": psutil.Process(os.getpid()).nice(),
    }


def send_log(message):
    try:
        log_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log_socket.connect(LOG_SERVER_ADDRESS)
        log_socket.send(message.encode())
        log_socket.close()
    except Exception as e:
        print(f"Error sending log: {e}")



def handle_client(client_socket, addr_id: int):
    send_log(f"Connection established with {addr_id}")

    last_request_state = {}
    if not last_request_state.get(addr_id):
        last_request_state[addr_id] = {}

    while True:
        try:
            request = client_socket.recv(1024).decode()
            send_log(f"Sent request from {addr_id}: {request}")

            if request == 'GET_INFO_PERIODIC':
                if get_data() != last_request_state[addr_id]:
                    last_request_state[addr_id] = get_data().copy()
                    client_socket.send(json.dumps(get_data()).encode())
                else:
                    client_socket.send("NO_UPDATE".encode())

            elif request == 'GET_INFO':
                client_socket.send(json.dumps(get_data()).encode())
            elif request == 'DISCONNECT':
                client_socket.close()
                break
        except ConnectionResetError:
            break

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server1 started on {HOST}:{PORT}")
    send_log(f"Server started on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,addr[1]))
        client_thread.start()

if __name__ == '__main__':
    server()