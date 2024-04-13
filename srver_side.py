import socket
from datetime import datetime
import threading
import time
from threading import * 
import struct
import random

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

        self.questions = [
            ("Lionel Messi is the all-time top scorer for Barcelona.", True),
            ("Messi has won the FIFA Ballon d'Or award a record number of times.", True),
            ("Messi has won the UEFA Champions League with Barcelona multiple times.", True),
            ("Messi has won the Copa America with the Argentina national team.", True),
            ("Messi made his senior debut for Barcelona in 2004.", True),
            ("Messi has never played for any other professional club.", True),
            ("Messi is known for his exceptional dribbling skills.", True),
            ("Messi is the tallest player in the Barcelona squad.", False),
            ("Messi has represented Argentina in multiple FIFA World Cup tournaments.", True),
            ("Messi is the captain of the Argentina national team.", True),
            ("Messi's preferred playing position is striker.", False),
            ("Messi has won the FIFA Club World Cup with Barcelona.", True),
            ("Messi's jersey number at Barcelona is 10.", True),
            ("Messi has a lifetime contract with Barcelona.", False),
            ("Messi has scored over 700 career goals.", True),
            ("Messi has won the Copa del Rey with Barcelona.", True),
            ("Messi has played alongside Neymar and Luis Suárez in Barcelona's attack.", True),
            ("Messi has never received a red card in his professional career.", False),
            ("Messi's first professional contract with Barcelona was signed on a napkin.", True),
            ("Messi is the highest-paid football player in the world.", True),
        ]


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
        print("Waiting for players to join...")
        self.welcome_socket.listen()
        try:
            while True:
                conn, addr = self.welcome_socket.accept()
                self.welcome_socket.settimeout(10)
                player_name = conn.recv(self.buff_size).decode().strip()
                if player_name:
                    self.players[player_name] = conn
                    print(f"Player {len(self.players)}: {player_name}")
                    t = Thread(target=self.handle_client, args=(conn, addr))
                    t.start()
                    if len(self.players) >= 2:
                        self.welcome_socket.settimeout(10)
                        break
                    else:
                        self.welcome_socket.settimeout(None)  # Remove the timeout
            self.start()
        except socket.timeout:
            print("Timeout: Not enough players joined within 10 seconds.")

    def send_questions(self,player,addr):
        for question, answer in self.questions:
            # Randomly shuffle the questions for each round
            random.shuffle(self.questions)
            # Send the question to the player
            player.sendall(question.encode('utf-8') + b'\n')
            # Set a timeout for 10 seconds for the player to answer
            player.settimeout(10)
            try:
                # Receive the player's answer
                data = player.recv(1024).decode('utf-8').strip()
                # Check if the answer is correct
                if data.lower() == 't' and answer or data.lower() == 'f' and not answer:
                    player.sendall(b'Correct!\n')
                else:
                    player.sendall(b'Incorrect!\n')
            except socket.timeout:
                player.sendall(b'Timeout! No answer received.\n')

        # After all questions are answered, close the connection
        conn.close()

        
        
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
# print(a.subnet_broadcast_ip)ע
