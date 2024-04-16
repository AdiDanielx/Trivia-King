import socket
import struct

class BasePlayer():
    def __init__(self):
        self.udp_port = 13117
        self.buff_size = 1024
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.udp_format = 'IbH32s'
        self.player_name = None

        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(('', self.udp_port))
        
    def listen_for_offers(self):
        print("Client started, listening for offer requests")
        while self.listen:
            data, addr = self.listen_socket.recvfrom(self.buff_size)
            msg = struct.unpack(self.udp_format, data)
            if msg[0] == self.magic_cookie and msg[1] == self.message_type:
                print(f"Received offer from server '{msg[3].decode('utf-8')}' at address {addr[0]}, attempting to connect...")
                return addr,msg[2] #return tuple of server ip and dedicated port
            else:
                return addr,msg

    def connect_to_game(self, addr):
        server_ip, server_port = addr
        self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_tcp.connect((server_ip, server_port))
        self.conn_tcp.send(self.player_name.encode('utf-8') + b'\n')
        players_mes = self.conn_tcp.recv(self.buff_size).decode().strip()
        print(players_mes)
    
    def questions_answer (self):
        try:
            while True:
                pass
        except:
            pass


    def play(self):
        details = self.listen_for_offers()
        self.player_name = (input("Enter your name: "))
        self.connect_to_game((details[0][0],details[1]))
