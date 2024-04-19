import socket
import struct
import time
import random
import threading
import concurrent.futures
from Colors import bcolors

class Server:

    def __init__(self):
        # link_proto = 'eth1'
        self.buff_size = 1024
        self.udp_port = 13117
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.server_name = 'The Best Server In The World abc' 
        self.udp_format = 'IbH32'
        self.ip = socket.gethostbyname(socket.gethostname())
        self.players = {}
        self.round = 0
        self.keep_Sending = True
        self.num_question = -1
        self.numPlayers = 0
        self.players_copy = []
        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create new TCP socket IPv4
        self.tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allow reusing the socket
        self.tcpSocket.bind((self.ip, 0)) #bind the socket to the server ip and assign port
        self.tcp_port = self.tcpSocket.getsockname()[1] #extract the port numbber
        
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

    def udp_socket(self):
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def send_broadcast(self):
        self.udp_socket()
        print(bcolors.OKBLUE +bcolors.BOLD+"Server started, listening on IP address " + self.ip)
        message = struct.pack('IbH32s', self.magic_cookie, self.message_type, self.tcp_port, self.server_name.encode('utf-8'))
        while self.keep_Sending:
            self.broadcast_socket.sendto(message,("<broadcast>", self.udp_port))
            time.sleep(1)

    def handle_client(self,conn,addr):
        try:
            player_name = conn.recv(self.buff_size).decode()
            print(bcolors.HEADER +f"Player connected: {player_name}")
            self.players[player_name] = conn
        except ConnectionResetError:
            # conn.close()
            player_to_remove = [name for name, connection in self.players.items() if connection == conn]
            del self.players[player_to_remove[0]]
    def get_players(self):
        self.tcpSocket.listen()
        threads = []
        try:
            while True:
                conn, addr = self.tcpSocket.accept()
                self.numPlayers+=1
                if (self.numPlayers)>1:
                    self.tcpSocket.settimeout(10) 
                t = threading.Thread(target=self.handle_client, args=(conn, addr))
                threads.append(t)
                t.start()
        except:
            self.start_trivia()
        for i in threads:
            t.join()
    
    def start_trivia(self):
        self.keep_Sending = False
        self.players_copy = list(self.players.items())
        startMessage = self.start_message(self.players_copy)
        # print(startMessage)
        self.send_parallel(startMessage,self.players_copy)
        while True:
            # random.shuffle(self.questions)
            if self.num_question > len(self.questions):
                self.num_question=0
            self.num_question +=1
            question, answer = self.questions[self.num_question]
            # self.questions = self.questions[1:] + [self.questions[0]]  # Rotate questions

            self.round += 1
            send_q = f"Round {self.round}, played by "
            num_players = len(self.players_copy)
            for i, (player, conn) in enumerate(self.players_copy):
                if i == num_players - 1:
                    send_q += f"and {player}:"
                else:
                    send_q += f"{player}, "
            send_q += f"\nTrue or false: {question}\nYour answer True/False:"
            
            
            results = self.send_parallel_and_recv(bcolors.OKCYAN+send_q,self.players_copy,answer)
            round_results = ""
            for i in results[1]:
                round_results +=f"{i[0]} is incorrect!\n"
            for i in results[0]:
                round_results +=f"{i[0]} is correct!"
                if len(results[0])==1:
                    round_results+=f" {i[0]} Wins!"
            self.send_parallel(bcolors.OKGREEN+bcolors.BOLD+round_results,self.players.items())
            
            if len(results[0])==1 or len(self.players_copy)==1:
                end_mesg = bcolors.RED+f"Game over!\nCongratulations to the winner: {results[0][0][0]}"
                self.send_parallel(end_mesg,self.players.items())
                self.game_over(self.players.items())
                break

            if len(results[0])>1:
                self.players_copy = [(player, conn) for player, conn in self.players_copy if player not in [p[0] for p in results[1]]]
            
                
    def game_over(self,players):
        for _,conn in players:
            conn.close()
        self.keep_Sending = True
        self.players = {}
        self.round = 0
        self.numPlayers = 0
        print( bcolors.RED+"Game over,sending out offer requests...")

    def start_message(self,players):
        welcome_string = f"\n{bcolors.BOLD+bcolors.YELLOW}Welcome to {self.server_name} server, where we are answering trivia questions about Lionel Messi\n"
        player_list = "\n".join([f"Player {i+1}: {player[0]}" for i, player in enumerate(players)])
        welcome_string += player_list
        welcome_string += "\n=="
        # print(welcome_string)
        return welcome_string

    def send_parallel_and_recv(self,string_send,players,answer):
        # print(bcolors.YELLOW+string_send)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.send_parallel(string_send,players)
            futures = {executor.submit(self.get_message, conn, string_send): (name,conn) for name, conn in players}
            correct = []
            incorrect = []
            for future in concurrent.futures.as_completed(futures):
                name,conn = futures[future]
                try:

                    result = future.result()  # This will wait for the thread to finish and return its result
                    if (result in ['t', 'y', '1'] and answer) or (result in ['f', 'n', '0'] and not answer):
                        correct.append((name,conn))  # Store the result with its corresponding connection
                    else:
                        incorrect.append((name,conn))
                except Exception as e:
                    print(f"Exception: {e}")  # Handle exceptions here
            return correct,incorrect
    
    def send_parallel(self,string_send,players):
        print(string_send)
        player_threads = []           
        for _, conn in players:
            t = threading.Thread(target=self.send_message, args=(conn, string_send))
            player_threads.append(t)
            t.start()
        for t in player_threads:
            t.join()
 

    def send_message(self, conn,mesg):
        try:
            conn.send(mesg.encode())
        except ConnectionResetError:
            # conn.close()
            for i, (player,connection1) in enumerate(self.players_copy):
                if connection1 == conn:
                    del self.players_copy[i]


    def get_message(self, conn,mesg):
        try:
            answer = conn.recv(self.buff_size).decode().strip().upper()
            return answer
        except ConnectionResetError:
            # conn.close()
            for i, (player,connection1) in enumerate(self.players_copy):
                if connection1 == conn:
                    del self.players_copy[i]

    def play(self):
        while True:
            broadcast_thread = threading.Thread(target=self.send_broadcast)
            listen_thread = threading.Thread(target=self.get_players)
            broadcast_thread.start()
            listen_thread.start()
            broadcast_thread.join()
            listen_thread.join()

if __name__ == "__main__":
    S = Server()
    S.play()
