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
        player_name = conn.recv(self.buff_size).decode()
        print(f"Player connected: {player_name}")
        self.players[player_name] = conn
        conn.send(f"Welcome {player_name}, waiting for other players...\n".encode())

    def get_players(self):
        print("Waiting for players to join...")
        self.welcome_socket.listen()
        try:
            while True:
                conn, addr = self.welcome_socket.accept()
                self.welcome_socket.settimeout(10)
                t = Thread(target=self.handle_client, args=(conn, addr))
                t.start()
                # if len(self.players) >= 2:
                #     self.welcome_socket.settimeout(10)
                #     break
                # else:
                #     self.welcome_socket.settimeout(None)  # Remove the timeout
        except socket.timeout:
            # print("Timeout: Not enough players joined within 10 seconds.")
            self.send_questions()
    
    def send_questions(self):
        while True:
            if len(self.players) < 2:
                print("Not enough players. Game cannot start.")
                return

            random.shuffle(self.questions)
            question, answer = self.questions[0]
            self.questions = self.questions[1:] + [self.questions[0]]  # Rotate questions

            players_copy = list(self.players.items())  # Convert dict_items to list for compatibility with indexing
            player_threads = []
            correct_players = []

            for player, conn in players_copy:
                t = Thread(target=self.send_question_to_player, args=(conn, question, answer, correct_players))
                player_threads.append(t)
                t.start()

            # Wait for all player threads to finish
            for t in player_threads:
                t.join()

            # Remove players who didn't answer or answered incorrectly
            for player, conn in players_copy:
                if player not in correct_players:
                    print(f"Player {player} was eliminated.")
                    del self.players[player]
                    conn.send("You have been eliminated from the game.\n".encode())

            # Check if there are still players in the game
            if len(self.players) == 0:
                print("No more players remaining. Game over.")
                break

    # def send_question_to_player(self, conn, question):
    #     conn.send(f"True or false: {question}\n".encode())
    def send_question_to_player(self, conn, question, answer, correct_players):
        conn.send(f"True or false: {question}\n".encode())
        try:
            conn.settimeout(10)
            response = conn.recv(1024).decode().strip().lower()
            if (response == 't' and answer) or (response == 'f' and not answer):
                conn.send("Correct!\n".encode())
                correct_players.append(conn)
            else:
                conn.send("Incorrect!\n".encode())
        except socket.timeout:
            conn.send("Timeout! No answer received.\n".encode())

    def play(self):
        if self.keep_Sending==True:
            print('not enough players')
        else:
            print('game started')

    def start_game(self):
        broadcast_thread = Thread(target=self.send_broadcast)
        listen_thread = Thread(target=self.get_players)
        broadcast_thread.start()
        listen_thread.start()
        broadcast_thread.join()
        listen_thread.join()
        self.play()
    


