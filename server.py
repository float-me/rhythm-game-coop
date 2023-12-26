import socket
import select

class Server:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None

    def accept_client(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print("서버가 클라이언트의 연결을 기다리고 있습니다.")
        self.client_socket, addr = self.server_socket.accept()
        self.server_socket.setblocking(0)  # 비블로킹 모드로 설정
        print(f"{addr}에서 연결되었습니다.")



    def handle_client(self):
        data = self.client_socket.recv(1024)
        if data:
            print(f"받은 데이터: {data.decode()}")
            self.client_socket.sendall(data)
        else:
            print("클라이언트로부터 연결이 끊겼습니다.")
            self.close_connection()
            

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
        self.socket.sendall(data.encode())

    def receive_data(self):
        try:
            ready_to_read, _, _ = select.select([self.socket], [], [], 0)
            if ready_to_read:
                data = self.socket.recv(1024)
                return data.decode() if data else None
        except Exception as e:
            print(f"오류 발생: {e}")
            return None

    def close_connection(self):
        if self.socket:
            self.socket.close()


if __name__ == "__main__":
    server = Server()
    server.accept_client()
    while server.client_socket:
        server.handle_client()
