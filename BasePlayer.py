import socket
import struct
import random
import threading
import time
from Colors import bcolors
import string
from inputimeout import inputimeout, TimeoutOccurred

names = ["Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry", "Ivy", "Jack", "Katie", "Leo", "Mia", "Noah", "Olivia", "Peter", "Quinn", "Rachel", "Sam", "Taylor",
                    "Sophia", "Ethan", "Isabella", "James", "Sophie", "Alexander", "Charlotte", "Michael", "Emily", "Jacob", "Lily", "Daniel", "Ava", "Matthew", "Madison", "William", "Emma", "Elijah", "Chloe", "Aiden"]

class BasePlayer():
    def __init__(self,bot=False):
        self.udp_port = 13117
        self.buff_size = 1024
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.udp_format = 'IbH32s'
        self.player_name = None
        self.listen = True
        self.bot = bot
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(('', self.udp_port))
        
        
    def listen_for_offers(self):
        try:
            print(bcolors.LIGHTPURPLE +bcolors.BOLD+"Client started, listening for offer requests")
            while self.listen:
                data, addr = self.listen_socket.recvfrom(self.buff_size)
                msg = struct.unpack(self.udp_format, data)
                if msg[0] == self.magic_cookie and msg[1] == self.message_type:
                    print(bcolors.LIGHT2+f"Received offer from server '{msg[3].decode('utf-8')}' at address {addr[0]}, attempting to connect...")
                    return addr,msg[2] #return tuple of server ip and dedicated port
                else:
                    return addr,msg
        except (ConnectionRefusedError, ConnectionResetError):
            print("Error: Failed to connect to the server.")
            self.listen = True
            if hasattr(self, 'conn_tcp'):
                self.conn_tcp.close()

    def connect_to_game(self, addr):
        try:
            server_ip, server_port = addr
            self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn_tcp.connect((server_ip, server_port))
            # self.conn_tcp.send(self.player_name.encode('utf-8') + b'\n')
            self.conn_tcp.send(self.player_name.encode('utf-8'))

            players_mes = self.conn_tcp.recv(self.buff_size).decode().strip()
            print(players_mes)
        except Exception as e:
            self.conn_tcp.close()
            self.listen= True


    def questions_answer(self):
        try:
            self.listen = False
            while True:
                question = self.conn_tcp.recv(self.buff_size).decode().strip()
                if "Game over" in question:
                    print(f"\n{question}")
                    mesg_over = self.conn_tcp.recv(self.buff_size).decode().strip()
                    print(mesg_over)
                    print(f"\n{bcolors.LIGHTPURPLE}+{bcolors.BOLD}Server disconnected, listening for offer requests...")
                    self.listen = True
                    self.conn_tcp.close()
                    break
                print(question)
                if self.bot == False:
                    # player_input = input().strip().lower()
                    try:
                        player_input = inputimeout(prompt='', timeout=10)
                        if player_input not in['t','y','1','f','n','0']:
                            player_input = '-1'
                    except TimeoutOccurred:
                        player_input = '-1'
                    self.conn_tcp.sendall(player_input.encode('utf-8'))
                else:
                    random_char = random.choice(['t', 'y', '1', 'f', 'n', '0'])
                    self.conn_tcp.sendall(random_char.encode('utf-8'))
                mesage2 = self.conn_tcp.recv(self.buff_size).decode().strip()
                print(mesage2)
        except Exception:
            self.conn_tcp.close()
            self.listen= True
            


    def play(self):
        while True:
            details = self.listen_for_offers()
            if self.bot == True:
                self.player_name = self.generate_bot_name()
            else:
                self.player_name= random.choice(names)
            print(bcolors.light +f"Name of your player : {self.player_name}")
            try:
                names.remove(self.player_name)
            except ValueError:
                pass
            try:
                self.connect_to_game((details[0][0],details[1]))
                self.questions_answer()
            except Exception as e:
                self.conn_tcp.close()
                self.listen= True
    def generate_bot_name(self):
        prefix = "BOT"
        suffix_length = 6  # You can adjust the length of the random suffix here
        suffix = ''.join(random.choices(string.ascii_lowercase, k=suffix_length))
        return prefix + suffix
