from BasePlayer import BasePlayer
import socket
import struct

class Client(BasePlayer):
    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    C = Client()
    C.play()
