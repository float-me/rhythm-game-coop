import socket
import select
import pygame
from classes import *
from color import *

'''서버에서 받은 정보로 그림을 그리는 클라이언트'''

class Render:
    def __init__(self):
        pygame.init()
        self.RES = self.WIDTH, self.HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT
        self.FPS = 60
        self.screen = pygame.display.set_mode(self.RES)
        self.drawing = Drawing(self.screen)
        self.clock = pygame.time.Clock()
        self.client = Client()

    def draw(self, drawing):
        self.screen.fill(WHITE)
        if drawing is not None:
            self.drawing.draw(drawing)

    def run(self):
        while True:
            self.draw(self.client.receive_data())  # 화면 그리기

            # fps 표시
            pygame.display.set_caption(str(self.clock.get_fps()))  # 현재 FPS를 창 제목으로 표시

            # 이벤트
            events = pygame.event.get()  # 이벤트 가져오기
            self.clock.tick(self.FPS)  # FPS 설정에 따라 시간 경과

            for event in events:
                if event.type == pygame.QUIT:
                    exit()

            
            pygame.display.flip()
            self.clock.tick(self.FPS)

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
            self.socket.sendall(data.encode())
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



if __name__ == "__main__":
    render = Render()
    Img()
    render.run()
