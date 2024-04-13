import socket
from datetime import datetime
import threading
import time
from threading import * 
import struct
class Server:
    link_proto = 'eth1'
    buff_size = 1024
    def __init__(self):
        self.udp_port = 13117

        #Message format
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.server_name = 'The Best Server In The World abc' 
        self.udp_format = 'IbH32'
        self.ip = socket.gethostbyname(socket.gethostname())
        self.players = {}
        
        #UDP socket
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.keep_Sending = True

        #TCP socket
        self.welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create new TCP socket IPv4
        self.welcome_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allow reusing the socket
        self.welcome_socket.bind((self.ip, 0)) #bind the socket to the server ip and assign port
        self.tcp_port = self.welcome_socket.getsockname()[1] #extract the port numbber


    def send_broadcast(self):
        print("Server started, listening on IP address " + self.ip)
        message = struct.pack('IbH32s', self.magic_cookie, self.message_type, self.tcp_port, self.server_name.encode('utf-8'))
        while self.keep_Sending:
            # self.broadcast_socket.sendto(message,(self.subnet_broadcast_ip, self.udp_port))
            self.broadcast_socket.sendto(message,('255.255.255.255', self.udp_port))
            time.sleep(1)
    
    def handle_client(self,conn,addr):
        print(f'new connetion{addr[0]}')
        print(conn)
        connected = True
        player_name = conn.recv(self.buff_size).decode()
        print(player_name)
    
    def get_players(self):
        time_lim = time.time()+10
        players_list = []
        self.welcome_socket.listen()
        while True:   
            if(time.time()>time_lim):
                break           
            conn,adrr = self.welcome_socket.accept()
            t = Thread(target=self.handle_client, args=(conn,adrr))
            players_list.append(t) 
            print(f'active connections: {threading.active_count()-2}')  
            t.start()
        self.keep_Sending = False
        print("starting game")

    def send_questions(self,player,addr):

        pass
        
    
    def play(self):
        if self.keep_Sending==True:
            print('not enough players')
        else:
            print('game started')


    def start(self):
        broardcast_thread = Thread(target = self.send_broadcast)
        listen_thread = Thread(target = self.get_players)
        broardcast_thread.start()
        listen_thread.start()
        broardcast_thread.join()
        listen_thread.join()
        self.play()


a= Server()
a.start()
# print(a.ip)
# print(a.subnet_broadcast_ip)