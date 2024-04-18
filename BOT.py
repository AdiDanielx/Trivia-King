from BasePlayer import BasePlayer
import socket
import struct

class BOT(BasePlayer):
    def __init__(self):
        super().__init__(bot=True)


if __name__ == "__main__":
    B = BOT()
    B.play()
