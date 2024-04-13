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
            self.broadcast_socket.sendto(message,('<broadcast>', self.udp_port))
            time.sleep(1)
    
    def handle_client(self,conn,addr):
        print(f'new connetion {addr[0]}')
        connected = True
        player_name = conn.recv(self.buff_size).decode()
        self.players[player_name]=(conn,addr)
        print(self.players)
    
    def get_players(self):
        self.welcome_socket.listen()
        self.welcome_socket.settimeout(10)  # Set a timeout of 10 seconds for accepting connections
        while self.keep_Sending:
            try:
                conn, addr = self.welcome_socket.accept()
                self.welcome_socket.settimeout(10)
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()
                print(f'active connections: {threading.active_count()-3}')  
            except socket.timeout:
                for i in self.players.values():
                    i[0].send(f"Welcome to {self.server_name} server, where we are answering trivia questions about somthing. \n player1: {self.players.keys()}".encode('utf-8'))
                self.keep_Sending = False
                break
        self.keep_Sending = False

    def send_questions(self,player,addr):

        pass
        
    
    def play(self,round = 0):
        for name, (conn, addr) in self.players.items():
            try:
                conn.send("True or false: Aston Villa's current manager is Pep Guardiola\n".encode('utf-8'))
                print(f'Sent question to {name}')
                
                # Set a timeout for receiving the answer
                conn.settimeout(10)
                
                # Receive the answer from the client
                answer = "conn.accept()"
                if answer:
                    print(f'Received answer from {name}: {answer}')
                else:
                    print(f'No answer received from {name} within 10 seconds')
                
            except socket.timeout:
                print(f'No answer received from {name} within 10 seconds')




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