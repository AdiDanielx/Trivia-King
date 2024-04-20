
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
        self.numPlayers = 0  # Number of players connected
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
        # Loop to keep broadcasting 
        while self.keep_Sending:
            # Send the broadcast message
            self.broadcast_socket.sendto(message,("<broadcast>", self.udp_port))
            # Wait a second before next broadcast
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
        except Exception as e: # Check if the error is a socket operation on non-socket
            if e.winerror == 10038:   # Handle client disconnection
                self.handle_disconnected_client(conn)

    def get_players(self):
        """
        Listens for incoming player connections and creates threads to handle each connection.
        """
        self.tcpSocket.listen() # Start listening for TCP connections
        threads = []
        try:
            while True:
                conn, addr = self.tcpSocket.accept()# Accept an incoming connection
                self.numPlayers+=1# Increment the player count
                if (self.numPlayers)>1:
                    self.tcpSocket.settimeout(10)  # Set a timeout for the socket
                t = threading.Thread(target=self.handle_client, args=(conn, addr))# Create a thread to handle the client
                threads.append(t) # Add thread to the list
                t.start()# Start the thread
        except Exception as e:
            if e.winerror == 10038:  # Check if the error is a socket operation on non-socke
                self.handle_disconnected_client(conn)# Handle client disconnection
            self.start_trivia()# Start trivia game

        for t in threads:
            t.join() # Wait for all threads to finish
    
    def start_trivia(self):
        """
        Initiates the trivia game by sending questions to players and collecting their responses.
        """
        try:
            # Stop broadcasting the server's availability
            self.keep_Sending = False
            # Make a copy of the players dictionary for manipulation during the game       
            self.players_copy = list(self.players.items())
            # Prepare the initial game message with player names
            startMessage = self.start_message(self.players_copy)
            # Send the start message to all players in parallel
            self.send_parallel(startMessage,self.players_copy)
            # Begin the main game loop
            while True:
                # Check if all questions have been asked, reset index if true
                if self.num_question > len(self.questions):
                    self.num_question=0
                # Move to the next question
                self.num_question +=1
                # Select the current question and its correct answer
                question, answer = self.questions[self.num_question]
                
                # Increment the round counter
                self.round += 1
                # Start building the question message to send to players
                send_q = f"Round {self.round}, played by "
                # Count the number of players currently in the game
                num_players = len(self.players_copy)
                # Append each player's name to the round introduction
                for i, (player, conn) in enumerate(self.players_copy):
                    if i == num_players - 1:
                        send_q += f"and {player}:"
                    else:
                        send_q += f"{player}, "
                 # Add the actual question to the message
                send_q += f"\nTrue or false: {question}\nYour answer True/False:"
                # Send the question to all players and receive their responses
                results = self.send_parallel_and_recv(bcolors.PINK+send_q,self.players_copy,answer)
                # Initialize a string to hold the results of the round
                round_results = ""
                # Append results for incorrect answers
                for i in results[1]:
                    round_results +=f"{bcolors.RED}{i[0]} is incorrect!\n"
                    # Save statistics for incorrect answers
                    self.save_statistics(i[0], question, "Incorrect\n")
                # Append results for correct answers
                for i in results[0]:
                    round_results += f"{bcolors.GREEN}\n{i[0]} is correct!"
                    # Save statistics for correct answers
                    self.save_statistics(i[0], question, "Correct")
                    # Check if there is a single winner
                    if len(results[0]) == 1:
                        round_results += f" {bcolors.GREEN}{bcolors.BOLD}{i[0]} Wins!"
                # Send the round results to all players
                self.send_parallel(round_results, self.players.items())
                
                # Check end conditions for the game
                if len(results[0])==1 or len(self.players_copy)==1:
                    # Determine the end game message based on the remaining players
                    if self.players_copy == results[0][0]:
                        end_mesg = bcolors.HEADER+f"Game over!\nCongratulations to the winner: {results[0][0][0]}"
                    else:
                        end_mesg = bcolors.HEADER+f"Game over!\nAll players have disconnected"
                    # Generate the final statistics of the game
                    statistics = self.print_statistics()
                    # Send the end game message and statistics to all players
                    self.send_parallel(end_mesg,self.players.items())
                    self.send_parallel(statistics,self.players.items())
                    # End the game and reset game state
                    self.game_over(self.players.items())
                    break
                
                # If multiple players remain correct, remove incorrect players from the next round
                if len(results[0])>1:
                    self.players_copy = [(player, conn) for player, conn in self.players_copy if player not in [p[0] for p in results[1]]]
        except (ConnectionResetError, ConnectionAbortedError) as e:
            # Log the client disconnection error
            print(f"Client disconnected")

                
    def game_over(self,players):
        """
        Resets the game state and closes all player connections when the game ends.
        """
        for _,conn in players:
            conn.close()# Close each player's connection
        self.keep_Sending = True # Reset the broadcasting flag to restart server advertisements
        self.players = {} # Clear the players dictionary
        self.round = 0 # Reset the round counter
        self.numPlayers = 0  # Reset the count of connected players
        print( bcolors.RED+"Game over,sending out offer requests...") # Print game over message

    def start_message(self,players):
        """
        Constructs the welcome message for players at the start of the game.
         """
         # Create the initial part of the welcome message
        welcome_string = f"\n{bcolors.BOLD+bcolors.WHITE}Welcome to {self.server_name} server, where we are answering trivia questions about Lionel Messi\n"
        # Generate a list of player names
        player_list = "\n".join([f"Player {i+1}: {player[0]}" for i, player in enumerate(players)])
        # Append the list of players to the welcome message
        welcome_string += f"{player_list}\n"
        # Append a separator line
        welcome_string += "\n=="
        # Return the complete welcome message
        return welcome_string

    def send_parallel_and_recv(self,string_send,players,answer):
        """
        Sends a message to all players in parallel and collects their responses.
         """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.send_parallel(string_send,players) # Send the initial message to all players
            # Create future tasks for receiving messages from players
            futures = {executor.submit(self.get_message, conn, string_send): (name,conn) for name, conn in players}
            correct = [] # List to store correct responses
            incorrect = []
            for future in concurrent.futures.as_completed(futures):
                name,conn = futures[future]
                try:
                    # Wait for the thread to finish and collect the result
                    result = future.result()  # This will wait for the thread to finish and return its result
                    # Check if the response is correct
                    if (result in ['t', 'y', '1'] and answer) or (result in ['f', 'n', '0'] and not answer):
                        correct.append((name,conn))  # Append to correct list if correct
                    else:
                        incorrect.append((name,conn)) # Append to incorrect list otherwise
                except Exception as e:
                    print(f"Exception: {e}")  # Handle any exceptions that occur
            return correct,incorrect # Return lists of correct and incorrect responses
    
    def send_parallel(self,string_send,players):
        """
        Sends a message to all connected players simultaneously using threads.
        """
        print(string_send) # Print the message for the server
        player_threads = []   # List to hold threads
        for _, conn in players:
            # Create a thread to send the message to each player
            t = threading.Thread(target=self.send_message, args=(conn, string_send))
            player_threads.append(t) # Append the thread to the list
            t.start() # Start the thread
        for t in player_threads:
            t.join() # Wait for all threads to finish
 
    def send_message(self, conn,mesg):
        """
        Sends a message over a given connection.
        """
        try:
            conn.send(mesg.encode()) # Encode and send the message
        except Exception as e:
            # Handle the exception if the socket operation fails
            if e.winerror == 10038:   # Check if the error is a socket operation on a non-socket
                self.handle_disconnected_client(conn) # Handle the disconnected client

    def handle_disconnected_client(self, conn):
        """
        Handles the cleanup for a disconnected client.
        """
        # Find and remove the disconnected player from the players dictionary
        player_to_remove = [name for name, player_conn in self.players.items() if player_conn == conn]
        if player_to_remove:
            del self.players[player_to_remove[0]] # Remove the player from dictionary
            conn.close()# Close the connection
        print(f"Player {player_to_remove[0]} disconnected.") # Print a message indicating player disconnection

    def get_message(self, conn,mesg):
        """
        Receives a message from a connection, handling disconnections.
        """
        try:
            # Receive, decode, and format the response
            answer = conn.recv(self.buff_size).decode().strip().upper()
            return answer # Return the processed response
        except Exception as e:
            if e.winerror == 10038:   # Check if the error is a socket operation on a non-socket
                self.handle_disconnected_client(conn) # Handle the disconnected client

    def save_statistics(self, player_name, question, answer_status):
        """
        Saves the trivia game statistics to a CSV file.
    
        Args:
            player_name (str): The name of the player.
            question (str): The trivia question asked.
            answer_status (str): The status of the answer ('Correct' or 'Incorrect').
    
        This function checks if the 'statistics.csv' file exists. If it does not exist,
        it creates the file and writes the header. Then, it appends the player's answer
        record to the CSV file.
        """
        # Check if the 'statistics.csv' file already exists in the current directory
        file_exists = os.path.isfile('statistics.csv')
    
        # Open the 'statistics.csv' file in append mode with no newline characters added automatically
        with open('statistics.csv', 'a', newline='') as csvfile:
            # Define the field names for the CSV columns
            fieldnames = ['Player', 'Question', 'Answer Status']
            # Create a DictWriter object that maps dictionaries onto output rows
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
            # Write a header row to the CSV file if it did not exist previously
            if not file_exists:
                writer.writeheader()
    
            # Write the player's answer record to the CSV file
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
        """
        Starts the server's main loop, managing the broadcasting to and listening for players.
    
        This method runs indefinitely, continuously starting threads for broadcasting the server's
        presence and listening for incoming player connections. It ensures the server is always ready
        to receive new players and provide information about its availability on the network.
        """
        while True:
             # Create a thread to handle broadcasting the server's availability to potential clients
            broadcast_thread = threading.Thread(target=self.send_broadcast)
             # Create a thread to listen for and handle incoming player connections
            listen_thread = threading.Thread(target=self.get_players)
            # Start the broadcasting thread
            broadcast_thread.start()
             # Start the listening thread
            listen_thread.start()
            # Wait for the broadcasting thread to finish
            broadcast_thread.join()
            # Wait for the listening thread to finish
            listen_thread.join()

if __name__ == "__main__":
    S = Server()
    S.play()
