
import socket
import struct
import time
import random
import threading
import concurrent.futures
from Colors import bcolors
import csv
import os

class Server:

    def __init__(self):
        """
        Initializes the Server object with default values and sets up the initial configuration.
        """
        self.buff_size = 1024 # Buffer size for socket communication
        self.udp_port = 13117  # UDP port number
        self.magic_cookie = 0xabcddcba # Magic cookie for message validation
        self.message_type = 0x2 # Message type for offer request
        self.server_name = 'The Best Server In The World abc'  # Name of the server
        self.udp_format = 'IbH32' # Format for UDP message packing
        self.ip = socket.gethostbyname(socket.gethostname())# IP address of the server
        self.players = {} # Dictionary to store player connections
        self.round = 0 # Round number for trivia game
        self.keep_Sending = True  # Flag to control server broadcast
        self.num_question = -1 # Index to track current question
        self.players_copy = [] # Copy of player dictionary for manipulation
        self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket for player connections
        self.tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reusing the socket
        self.tcpSocket.bind((self.ip, 0))  # Bind the socket to the server IP and assign a port
        self.tcp_port = self.tcpSocket.getsockname()[1] # Extract the port number
        
         # List of trivia questions and answers
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
        """
        Initializes the UDP socket for server broadcast.
        """
        # Create a UDP socket
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set socket option to allow broadcasting
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


    def send_broadcast(self):
        """
        Sends broadcast messages to discover game servers on the network.
        """
        # Initialize the UDP socket for broadcasting
        self.udp_socket()
        # Print a message indicating server startup and IP address
        print(bcolors.LIGHTPURPLE +bcolors.BOLD+"Server started, listening on IP address " + self.ip)
        # Create the broadcast message packet
        message = struct.pack('IbH32s', self.magic_cookie, self.message_type, self.tcp_port, self.server_name.encode('utf-8'))
        # Continuously send broadcast messages while keep_Sending flag is True
        while self.keep_Sending:
            # Send the broadcast message
            self.broadcast_socket.sendto(message,("<broadcast>", self.udp_port))
            # Sleep for 1 second before sending the next broadcast message
            print("sent invite")
            time.sleep(1)
        

    def handle_client(self,conn,addr):
        """
        Handles incoming client connections and stores player information.
        """
        try:
            # Receive the player's name from the connection
            player_name = conn.recv(self.buff_size).decode()
            # Print a message indicating the connection of the player
            print(bcolors.BOLD+bcolors.light +f"Player connected: {player_name}")
            # Store the player's information in the players dictionary
            self.players[player_name] = conn
        # except ConnectionResetError:
        #     # Handle the case where the connection is reset
        #     # Find and remove the player from the players dictionary
        #     player_to_remove = [name for name, connection in self.players.items() if connection == conn]
        #     del self.players[player_to_remove[0]]
        except Exception as e:
            if e.winerror == 10038:  # An operation was attempted on something that is not a socket
                self.handle_disconnected_client(conn)

    def get_players(self):
        """
        Listens for incoming player connections and creates threads to handle each connection.
        """
        self.tcpSocket.listen()
        threads = []
        try:
            while True:
                conn, addr = self.tcpSocket.accept()
                if (len(self.players))>=1:
                    self.tcpSocket.settimeout(10) 
                t = threading.Thread(target=self.handle_client, args=(conn, addr))
                threads.append(t)
                t.start()
        except Exception as e:
            if e.winerror == 10038:  # An operation was attempted on something that is not a socket
                self.handle_disconnected_client(conn)
            self.start_trivia()

        for t in threads:
            t.join()
    
    def start_trivia(self):
        """
        Initiates the trivia game by sending questions to players and collecting their responses.
        """
        if len(self.players)<2:
            print(self.players)
            print("not enough players")
            self.listen = True
            self.get_players()
        try:
            self.round = 0
            self.keep_Sending = False
            self.broadcast_socket.close()
            self.players_copy = list(self.players.items())
            startMessage = self.start_message(self.players_copy)
            # print(startMessage)
            self.send_parallel(startMessage,self.players_copy)
            while True:
                # random.shuffle(self.questions)
                if self.num_question > len(self.questions)-1:
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
                
                
                results = self.send_parallel_and_recv(bcolors.PINK+send_q,self.players_copy,answer)
                round_results = ""
                for i in results[1]:
                    round_results +=f"{bcolors.RED}{i[0]} is incorrect!\n"
                    self.save_statistics(i[0], question, "Incorrect\n")
                for i in results[0]:
                    round_results +=f"{bcolors.GREEN}\n{i[0]} is correct!"
                    self.save_statistics(i[0], question, "Correct")
                    if len(results[0])==1:
                        round_results+=f" {bcolors.GREEN}{bcolors.BOLD}{i[0]} Wins!"
                self.send_parallel(round_results,self.players.items())
                
                if len(results[0])==1 or len(self.players_copy)==1:
                    if self.players_copy == results[0][0]:
                        end_mesg = bcolors.HEADER+f"Game over!\nCongratulations to the winner: {results[0][0][0]}"
                    else:
                        end_mesg = bcolors.HEADER+f"Game over!\nAll players have disconnected"
                    statistics = self.print_statistics()
                    self.send_parallel(end_mesg,self.players.items())
                    self.send_parallel(statistics,self.players.items())
                    self.game_over(self.players.items())
                    break

                if len(results[0])>1:
                    self.players_copy = [(player, conn) for player, conn in self.players_copy if player not in [p[0] for p in results[1]]]
        except (ConnectionResetError, ConnectionAbortedError) as e:
            
            print(f"Client disconnected")

                
    def game_over(self,players):
        for _,conn in players:
            conn.close()
        self.players = {}
        self.round = 0
        self.keep_Sending = True
        print( bcolors.RED+"Game over,sending out offer requests...")

    def start_message(self,players):
        welcome_string = f"\n{bcolors.BOLD+bcolors.WHITE}Welcome to {self.server_name} server, where we are answering trivia questions about Lionel Messi\n"
        player_list = "\n".join([f"Player {i+1}: {player[0]}" for i, player in enumerate(players)])
        welcome_string += f"{player_list}\n"
        welcome_string += "\n=="
        
        # print(welcome_string)
        return welcome_string

    def send_parallel_and_recv(self,string_send,players,answer):
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
                    print(f"Exception: {e}")
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
        except Exception as e:
            # conn.close()
            if e.winerror == 10038:  # An operation was attempted on something that is not a socket
                self.handle_disconnected_client(conn)

    def handle_disconnected_client(self, conn):
        """
        Handles the cleanup for a disconnected client.
        """
        # Find the player associated with the disconnected socket and remove them.
        player_to_remove = [name for name, player_conn in self.players.items() if player_conn == conn]
        if player_to_remove:
            del self.players[player_to_remove[0]]
            del self.players_copy[player_to_remove[0]]
        # Close the socket if it's not already closed.
            conn.close()
        print(f"Player {player_to_remove[0]} disconnected.")

    def get_message(self, conn,mesg):
        try:
            answer = conn.recv(self.buff_size).decode().strip().upper()
            return answer
        except Exception as e:
            if e.winerror == 10038:  # An operation was attempted on something that is not a socket
                self.handle_disconnected_client(conn)

            # conn.close()
            # for i, (_,connection1) in enumerate(self.players_copy):
            #     if connection1 == conn:
            #         connection1.close()
            #         del self.players_copy[i]

    def save_statistics(self,player_name, question, answer_status):
        file_exists = os.path.isfile('statistics.csv')

        with open('statistics.csv', 'a', newline='') as csvfile:
            fieldnames = ['Player', 'Question', 'Answer Status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({'Player': player_name, 'Question': question, 'Answer Status': answer_status})

    def print_statistics(self):
        # Initialize a dictionary to store statistics for each question
        question_stats = {}

        with open('statistics.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            # Iterate through each row in the CSV file
            for row in reader:
                # player = row['Player']
                question = row['Question']
                answer_status = row['Answer Status']

                # If the question is not already in the question_stats dictionary, initialize it
                if question not in question_stats:
                    question_stats[question] = {'Correct': 0, 'Incorrect': 0, 'Total': 0}

                # Update the correct or incorrect count based on the answer status
                if answer_status == 'Correct':
                    question_stats[question]['Correct'] += 1
                else:
                    question_stats[question]['Incorrect'] += 1

                # Update the total count
                question_stats[question]['Total'] += 1

        # Prepare the header for the table
        table_header = f"{bcolors.YELLOW}+--------------------------------------------------------------+------------+------------+-----------+\n"
        table_header += f"| {bcolors.WHITE}Question".ljust(65) + f"{bcolors.YELLOW}|{bcolors.WHITE} Correct (%)".ljust(12) + f"{bcolors.YELLOW}|{bcolors.WHITE} Incorrect (%)".ljust(14) + "|\n"
        table_header += f"{bcolors.YELLOW}+--------------------------------------------------------------+------------+------------+-----------+\n"
        # Initialize the table string with the header
        table_str = table_header

        # Iterate through the question_stats dictionary to populate the table
        question_number = 1
        for question, stats in question_stats.items():
            correct = stats['Correct']
            incorrect = stats['Incorrect']
            total = stats['Total']

            # Calculate percentages
            correct_percent = (correct / total) * 100 if total != 0 else 0
            incorrect_percent = (incorrect / total) * 100 if total != 0 else 0

            # Split the question into multiple lines if it's too long
            question_lines = [question[i:i+49] for i in range(0, len(question), 49)]
            first_line = True
            for line in question_lines:
                if first_line:
                    row = f"{bcolors.YELLOW}|"
                    table_header += f"{bcolors.YELLOW}| {bcolors.WHITE}Question".ljust(65) + f"{bcolors.YELLOW}| {bcolors.WHITE}Correct (%)".ljust(12) + f"{bcolors.YELLOW}| {bcolors.WHITE}Incorrect (%)".ljust(14) + f"{bcolors.YELLOW}|\n"
                    row = f"{bcolors.YELLOW}|{bcolors.WHITE}{question_number} " + line.ljust(62) +f"{bcolors.YELLOW}| " + f"{bcolors.WHITE}{correct_percent:.2f}%".ljust(12) + f"{bcolors.YELLOW}| " + f"{bcolors.WHITE}{incorrect_percent:.2f}%".ljust(14) + f"{bcolors.YELLOW}|\n"
                    first_line = False
                else:
                    row = f"{bcolors.YELLOW}| " + line.ljust(63) + f"{bcolors.YELLOW}|".ljust(16) + f"{bcolors.YELLOW}|".ljust(14) + "|\n"
                table_str += row
            question_number += 1
        table_str += f"{bcolors.YELLOW}+-------------------------------------------------+---------+---------+---------+\n"  # Table border

        return table_str


    def play(self):
        while True:
            self.keep_Sending = True
            broadcast_thread = threading.Thread(target=self.send_broadcast)
            listen_thread = threading.Thread(target=self.get_players)
            broadcast_thread.start()
            listen_thread.start()
            broadcast_thread.join()
            listen_thread.join()

if __name__ == "__main__":
    S = Server()
    S.play()