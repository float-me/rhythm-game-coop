import socket
import select

class Server:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print("서버가 클라이언트의 연결을 기다리고 있습니다.")
        self.client_socket, addr = self.server_socket.accept()
        print(f"{addr}에서 연결되었습니다.")
        self.client_socket.setblocking(0)  # 클라이언트 소켓을 비블로킹 모드로 설정

    def handle_client(self):
        ready_to_read, _, _ = select.select([self.client_socket], [], [], 0)
        if ready_to_read:
            data = self.client_socket.recv(1024)
            if data:
                return data
            else:
                print("클라이언트로부터 연결이 끊겼습니다.")
                self.close_connection()

    def send_data(self, data:str):
        self.client_socket.sendall(data)

    def close_connection(self):
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()

class Client:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_server()
        self.socket.setblocking(0)  # 소켓을 비블로킹 모드로 설정

    def connect_to_server(self):
        self.socket.connect((self.host, self.port))

    def send_data(self, data:str):
        try:
            self.socket.sendall(data)
            return 1
        except:
            self.close_connection()
            return 0

    def receive_data(self):
        try:
            ready_to_read, _, _ = select.select([self.socket], [], [], 0)
            if ready_to_read:
                data = self.socket.recv(1024)
                if data:
                    print(data.decode())
                return data.decode() if data else None
        except Exception as e:
            print(f"오류 발생: {e}")
            return None

    def close_connection(self):
        self.socket.close()

