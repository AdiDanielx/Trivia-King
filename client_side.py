import socket
import struct
class Client:
    def __init__(self):
        self.udp_port = 13117
        self.buff_size = 1024
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.udp_format = 'IbH32s'
        self.player_name = None
        self.playing = False
        
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(('', self.udp_port))

    def listen_for_offers(self):
        print("Client started, listening for offer requests")
        while True:
            data, addr = self.listen_socket.recvfrom(self.buff_size)
            msg = struct.unpack(self.udp_format, data)
            if msg[0] == self.magic_cookie and msg[1] == self.message_type:
                print(f"Received offer from server '{msg[3].decode('utf-8')}' at address {addr[0]}, attempting to connect")
                return addr,msg[2] #return tuple of server ip and dedicated port
            else:
                print('sddff')
                return

    def connect_to_game(self,addr):
        # self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.conn_tcp.connect(addr)
        # self.playing = True
        server_ip, server_port = addr
        self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_tcp.connect((server_ip, server_port))
        self.conn_tcp.sendall(self.player_name.encode('utf-8'))
        self.playing = True

    def set_player_name(self, name):
        self.player_name = name

    def start(self):
        self.set_player_name(input("Enter your name: "))
        details = self.listen_for_offers()
        print(details)
        print((details[0][0],details[1]))
        self.connect_to_game((details[0][0],details[1]))


    


c=Client() 
c1=Client() 
c.start() 
       
