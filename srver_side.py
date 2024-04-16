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

        self.round = 0

    def send_broadcast(self):
        print("Server started, listening on IP address " + self.ip)
        message = struct.pack('IbH32s', self.magic_cookie, self.message_type, self.tcp_port, self.server_name.encode('utf-8'))
        while self.keep_Sending:
            self.broadcast_socket.sendto(message,("<broadcast>", self.udp_port))
            time.sleep(1)
    
    def handle_client(self,conn,addr):
        player_name = conn.recv(self.buff_size).decode()
        print(f"Player connected: {player_name}")
        self.players[player_name] = conn
        

    def get_players(self):
        self.welcome_socket.listen()
        try:
            while True:
                self.welcome_socket.settimeout(10)
                conn, addr = self.welcome_socket.accept()
                t = Thread(target=self.handle_client, args=(conn, addr))
                t.start()
        except socket.timeout:
            self.send_questions()

    def send_questions(self):
        players_copy = list(self.players.items())  # Convert dict_items to list for compatibility with indexing
        player_threads = []           
        welcome_string = f"Welcome to {self.server_name} server, where we are answering trivia questions about Lionel Messi\n"
        i = 1
        for player, _ in players_copy:
            welcome_string += f"Player {i}: {player}\n"
            i += 1
        welcome_string += "=="
        # Send welcome string parallel to players
        for _, conn in players_copy:
            t = Thread(target=self.send_welcome_message, args=(conn, welcome_string))
            player_threads.append(t)
            t.start()        
        while True:
            if len(self.players) < 2:
                # print("Not enough players. Game cannot start.")
                return
            random.shuffle(self.questions)
            question, answer = self.questions[0]
            self.questions = self.questions[1:] + [self.questions[0]]  # Rotate questions


            correct_players = []
            incorrect_players = []


            num_players = len(self.players)
            j=0
            self.round +=1
            send_q = f"Round {self.round}, played by "
            for players,conn in self.players.items():
                j += 1
                if j == num_players:
                    send_q += f"and {players}:"
                elif j == num_players - 1:
                    send_q += f"{players} "
                else:
                    send_q += f"{players}, "

            for player, conn in players_copy:
                t = Thread(target=self.send_question_to_player, args=(conn, question, answer, correct_players,incorrect_players,send_q))
                player_threads.append(t)
                t.start()

            # Wait for all player threads to finish
            for t in player_threads:
                t.join()


            # Remove players who didn't answer or answered incorrectly
            for player, conn in players_copy:
                if conn not in correct_players:
                    # del self.players[player]
                    conn.send("You have been eliminated from the game.\n".encode())

            if len(self.players) == 1:
                winner = list(self.players.keys())[0]  # Get the name of the winner
                conn.send("won the game!".encode())
                print(f"Player {winner} won the game!")  # Announce the winner
                return

    def send_question_to_player(self, conn, question, answer, correct_players,incorrect_players,message):
        conn.send(f"{message}\n True or false: {question}\n".encode())
        try:
            conn.settimeout(10)
            response = conn.recv(1024).decode().strip().lower()
            if (response in ['t', 'y', '1'] and answer) or (response in ['f', 'n', '0'] and not answer):
                correct_players.append(conn)
            else:
                incorrect_players.append(conn)
        except socket.timeout:
            conn.send("Timeout! No answer received.\n".encode())

    def send_welcome_message(self, conn, welcome_string):
        conn.send(welcome_string.encode())

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
    


a= Server()
a.start_game()
# print(a.ip)
# print(a.subnet_broadcast_ip)
