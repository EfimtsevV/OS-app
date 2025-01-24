import socket
import tkinter as tk
import threading
import time

SERVER1 = ('127.0.0.1', 8081)
SERVER2 = ('127.0.0.1', 8082)
PERIODIC_REQUEST_INTERVAL = 5

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Client Application")
        self.server1_socket = None
        self.server2_socket = None
        self.periodic_request = False

        self.setup_ui()

    def setup_ui(self):
        self.control_frame = tk.LabelFrame(self.root, text="Server Controls")
        self.control_frame.pack(padx=10, pady=5, fill="both")

        self.connect_both_btn = tk.Button(self.control_frame, text="Connect to Both Servers", command=self.connect_both_servers)
        self.connect_both_btn.pack(side="left", padx=5, pady=5)

        self.disconnect_both_btn = tk.Button(self.control_frame, text="Disconnect from Both Servers", command=self.disconnect_both_servers)
        self.disconnect_both_btn.pack(side="left", padx=5, pady=5)

        self.connect_server1_btn = tk.Button(self.control_frame, text="Connect to Server 1", command=lambda: self.connect_server(SERVER1, "Server 1"))
        self.connect_server1_btn.pack(side="left", padx=5, pady=5)

        self.connect_server2_btn = tk.Button(self.control_frame, text="Connect to Server 2", command=lambda: self.connect_server(SERVER2, "Server 2"))
        self.connect_server2_btn.pack(side="left", padx=5, pady=5)

        self.disconnect_server1_btn = tk.Button(self.control_frame, text="Disconnect from Server 1", command=lambda: self.disconnect_server(self.server1_socket, "Server 1"))
        self.disconnect_server1_btn.pack(side="left", padx=5, pady=5)

        self.disconnect_server2_btn = tk.Button(self.control_frame, text="Disconnect from Server 2", command=lambda: self.disconnect_server(self.server2_socket, "Server 2"))
        self.disconnect_server2_btn.pack(side="left", padx=5, pady=5)

        self.periodic_frame = tk.LabelFrame(self.root, text="Periodic Requests")
        self.periodic_frame.pack(padx=10, pady=5, fill="both")

        self.periodic_start_btn = tk.Button(self.periodic_frame, text="Start Periodic Requests", command=self.start_periodic_requests)
        self.periodic_start_btn.pack(side="left", padx=5, pady=5)

        self.periodic_stop_btn = tk.Button(self.periodic_frame, text="Stop Periodic Requests", command=self.stop_periodic_requests)
        self.periodic_stop_btn.pack(side="left", padx=5, pady=5)

        self.interaction_frame = tk.LabelFrame(self.root, text="Server Interaction")
        self.interaction_frame.pack(padx=10, pady=5, fill="both")

        self.get_info_both_btn = tk.Button(self.interaction_frame, text="Get Info from Both Servers", command=self.get_info_both_servers)
        self.get_info_both_btn.pack(side="left", padx=5, pady=5)

        self.get_info_server1_btn = tk.Button(self.interaction_frame, text="Get Info from Server 1", command=lambda: self.get_info_from_server(self.server1_socket, "Server 1"))
        self.get_info_server1_btn.pack(side="left", padx=5, pady=5)

        self.get_info_server2_btn = tk.Button(self.interaction_frame, text="Get Info from Server 2", command=lambda: self.get_info_from_server(self.server2_socket, "Server 2"))
        self.get_info_server2_btn.pack(side="left", padx=5, pady=5)

        self.log_frame = tk.LabelFrame(self.root, text="Logs and Responses")
        self.log_frame.pack(padx=10, pady=5, fill="both")

        self.log_textbox = tk.Text(self.log_frame, height=15, width=50, state="disabled")
        self.log_textbox.pack(padx=5, pady=5)

    def log_message(self, message: str):
        self.log_textbox.config(state="normal")
        self.log_textbox.insert(tk.END, f"{message}\n")
        self.log_textbox.see(tk.END)
        self.log_textbox.config(state="disabled")

    def connect_server(self, server_address: tuple, label: str):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(server_address)
            self.log_message(f"Connected to {label}")
            if label == "Server 1":
                self.server1_socket = sock
            elif label == "Server 2":
                self.server2_socket = sock
            return sock
        except ConnectionRefusedError:
            self.log_message(f"Failed to connect to {label}")
            return None

    def disconnect_server(self, sock, label):
        if sock:
            try:
                self.send_request(sock, 'DISCONNECT')
                sock.close()
                self.log_message(f"Disconnected from {label}")
                if label == "Server 1":
                    self.server1_socket = None
                elif label == "Server 2":
                    self.server2_socket = None
            except Exception as e:
                self.log_message(f"Error disconnecting from {label}: {e}")

    def send_request(self, sock, request):
        try:
            sock.send(request.encode())
            response = sock.recv(1024).decode()
            return response
        except (BrokenPipeError, ConnectionResetError):
            self.log_message("Lost connection to the server")
            return ""

    def connect_both_servers(self):
        if not self.server1_socket:
            self.server1_socket = self.connect_server(SERVER1, "Server 1")
        else:
            self.log_message("Already connected to Server 1")

        if not self.server2_socket:
            self.server2_socket = self.connect_server(SERVER2, "Server 2")
        else:
            self.log_message("Already connected to Server 2")

    def disconnect_both_servers(self):
        if self.server1_socket:
            self.disconnect_server(self.server1_socket, "Server 1")
            self.server1_socket = None
        else:
            self.log_message("Not connected to Server 1")

        if self.server2_socket:
            self.disconnect_server(self.server2_socket, "Server 2")
            self.server2_socket = None
        else:
            self.log_message("Not connected to Server 2")

    def get_info_both_servers(self):
        if self.server1_socket:
            info = self.send_request(self.server1_socket, 'GET_INFO')
            self.log_message(f"Server 1 Info: {info}")
        else:
            self.log_message("Not connected to Server 1")

        if self.server2_socket:
            info = self.send_request(self.server2_socket, 'GET_INFO')
            self.log_message(f"Server 2 Info: {info}")
        else:
            self.log_message("Not connected to Server 2")

    def get_info_from_server(self, sock, label):
        if sock:
            info = self.send_request(sock, 'GET_INFO')
            self.log_message(f"{label} Info: {info}")
        else:
            self.log_message(f"Not connected to {label}")

    def start_periodic_requests(self):
        if not self.periodic_request:
            self.periodic_request = True
            threading.Thread(target=self.periodic_request_thread, daemon=True).start()
            self.log_message("Started periodic requests")
        else:
            self.log_message("Periodic requests already running")

    def stop_periodic_requests(self):
        if self.periodic_request:
            self.periodic_request = False
            self.log_message("Stopped periodic requests")
        else:
            self.log_message("Periodic requests not running")

#Доп задание 1-2
    def periodic_request_thread(self):
        while self.periodic_request:
            if self.server1_socket:
                info = self.send_request(self.server1_socket, 'GET_INFO_PERIODIC')
                if info != "NO_UPDATE":
                    self.log_message(f"Periodic Update from Server 1: {info}")
            if self.server2_socket:
                info = self.send_request(self.server2_socket, 'GET_INFO_PERIODIC')
                if info != "NO_UPDATE":
                    self.log_message(f"Periodic Update from Server 2: {info}")
            time.sleep(PERIODIC_REQUEST_INTERVAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
    