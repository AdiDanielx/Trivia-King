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
                print(f"Received offer from server '{msg[3].decode('utf-8')}' at address {addr[0]}, attempting to connect...")
                return addr,msg[2] #return tuple of server ip and dedicated port
            else:
                return addr,msg

    def connect_to_game(self,addr):
        server_ip, server_port = addr
        self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_tcp.connect((server_ip, server_port))
        self.conn_tcp.send(self.player_name.encode('utf-8'))
        players_mes = self.conn_tcp.recv(self.buff_size).decode().strip()
        print(players_mes)

        self.playing = True
        try:
            while True:
                data = self.conn_tcp.recv(self.buff_size).decode().strip()
                if not data:
                    break
                print(data)
                player_input = input("Your answer (T/F): ").strip().lower()
                while player_input not in['t','y','1','f','n','0']:
                    player_input = input("please enter a valid input : ").strip().lower()
                self.conn_tcp.sendall(player_input.encode('utf-8'))
                data = self.conn_tcp.recv(self.buff_size).decode().strip()
                round = self.conn_tcp.recv(self.buff_size).decode().strip()
                print(round)

        except Exception as e:
            print(f"Error receiving/sending data: {e}")

    def set_player_name(self, name):
        self.player_name = name

    def start(self):
        self.set_player_name(input("Enter your name: "))
        details = self.listen_for_offers()
        self.connect_to_game((details[0][0],details[1]))


    


c=Client() 
# c1=Client() 
c.start() 
       