import socket
import threading
import os
import platform
import json
import psutil
import platform
import subprocess
import ctypes

def get_keyboard_layout():
    system_name = platform.system()
    layout = None
    print(system_name)
    if system_name == "Windows":
        # Для Windows используем WinAPI
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        thread_id = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), None)
        keyboard_layout = user32.GetKeyboardLayout(thread_id)
        layout = hex(keyboard_layout & 0xFFFFFFFF)
        if layout == "0x4090409":
            layout = "US"
        elif layout == "0x4190419":
            layout = "RU"
        print(layout)
    elif system_name == "Linux":
        # Для Linux используем subprocess для вызова `setxkbmap`
        try:
            result = subprocess.run(['setxkbmap', '-query'], stdout=subprocess.PIPE, text=True)
            for line in result.stdout.splitlines():
                if line.startswith("layout:"):
                    layout = line.split(":")[1].strip()
                    break
        except FileNotFoundError:
            layout = "setxkbmap utility not found"

    if layout:
        return f"Current keyboard layout: {layout}"
    else:
        return "Unable to determine keyboard layout"

HOST = '127.0.0.1'
PORT = 8082
LOG_SERVER_ADDRESS = ('127.0.0.1', 6000)

def get_data() -> dict:
    return {
        "layout":  get_keyboard_layout(),
        "os_version": platform.version(),
    }

def send_log(message):
    try:
        log_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log_socket.connect(LOG_SERVER_ADDRESS)
        log_socket.send(message.encode())
        log_socket.close()
    except Exception as e:
        print(f"Error sending log: {e}")

def handle_client(client_socket, addr_id):
    last_request_state = {}
    if not last_request_state.get(addr_id):
        last_request_state[addr_id] = {}
    send_log(f"Connection established with {addr_id}")

    while True:
        data_ = get_data()
        try:
            print(last_request_state)
            print(data_)
            request = client_socket.recv(1024).decode()
            send_log(f"Sent request from {addr_id}: {request}")
            if request == 'GET_INFO_PERIODIC':
                if data_ != last_request_state[addr_id]:
                    last_request_state[addr_id] = data_
                    print(last_request_state)
                    client_socket.send(json.dumps(data_).encode())
                else:
                    client_socket.send("NO_UPDATE".encode())

            elif request == 'GET_INFO':
                client_socket.send(json.dumps(data_).encode())

            elif request == 'DISCONNECT':
                client_socket.close()
                send_log(f"Connection closed with {addr_id}")
                break
        except ConnectionResetError:
            break

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    send_log(f"Server started on {HOST}:{PORT}")
    print(f"Server started on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        send_log(f"Client connected: {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr[1]))
        client_thread.start()

if __name__ == '__main__':
    server()
