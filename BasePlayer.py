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
        """
        Initialize the BasePlayer with default settings for network communication and player configuration.

        Args:
            bot (bool): Determines if the player is a bot or a real person.
        """
        self.udp_port = 13117  # UDP port number for listening
        self.buff_size = 1024  # Buffer size for socket communication
        self.magic_cookie = 0xabcddcba  # Magic cookie to identify valid messages
        self.message_type = 0x2  # Message type identifier
        self.udp_format = 'IbH32s'  # Format for unpacking UDP messages
        self.player_name = None  # Name of the player, initialized to None
        self.listen = True  # Control flag for the listening loop
        self.bot = bot  # Flag to determine if the player is a bot
        # Create a UDP socket for listening to broadcast messages
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set the socket to reuse the address
        self.listen_socket.bind(('', self.udp_port))  # Bind the socket to all interfaces
        
        
    def listen_for_offers(self):
        """
        Listen for broadcast offers from servers and validate them.
        """
        try:
            print(bcolors.LIGHTPURPLE + bcolors.BOLD + "Client started, listening for offer requests")
            while self.listen:  # Keep listening while the listen flag is True
                # Receive data from the network
                data, addr = self.listen_socket.recvfrom(self.buff_size)
                # Unpack the data according to the specified format
                msg = struct.unpack(self.udp_format, data)
                # Check if the message is valid
                if msg[0] == self.magic_cookie and msg[1] == self.message_type:
                    print(bcolors.LIGHT2 + f"Received offer from server '{msg[3].decode('utf-8')}' at address {addr[0]}, attempting to connect...")
                    return addr, msg[2]  # Return server address and TCP port
                else:
                    return addr, msg
        except (ConnectionRefusedError, ConnectionResetError):
            print("Error: Failed to connect to the server.")
            self.listen = True
            if hasattr(self, 'conn_tcp'):
                self.conn_tcp.close()
  
    def connect_to_game(self, addr):
        """
        Connect to the game server using the provided address and establish a TCP connection.
    
        This method attempts to establish a TCP connection to the server using the address obtained
        from a UDP broadcast message. It sends the player's name to the server and awaits a response
        that typically includes information about other players in the game.
    
        Args:
            addr (tuple): A tuple containing the server's IP address and TCP port number.
        """
        try:
            # Unpack the address into IP and port components
            server_ip, server_port = addr
            # Create a TCP socket for communication with the server
            self.conn_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect the TCP socket to the server using the provided IP address and port
            self.conn_tcp.connect((server_ip, server_port))
            # Send the player's name encoded as UTF-8 bytes to the server
            self.conn_tcp.send(self.player_name.encode('utf-8'))
    
            # Wait for a message from the server and decode it
            players_mes = self.conn_tcp.recv(self.buff_size).decode().strip()
            # Print the message received from the server, likely containing game details or other player info
            print(players_mes)
        except Exception as e:
            # If an exception occurs (e.g., connection issues), close the TCP connection
            self.conn_tcp.close()
            # Reset the listening flag to True to allow reconnection attempts
            self.listen = True

    def questions_answer(self):
        """
        Handles the interactive part of the game where questions are received and answers are sent back to the server.
    
        This method continuously receives questions from the server over an established TCP connection. It processes
        each question and allows the player (or bot) to respond. If the game concludes or if a disconnect occurs,
        it appropriately handles the closure and restarts listening for new offers.
        """
        try:
            # Stop listening for new game offers while in a game session
            self.listen = False
            while True:
                # Receive and decode the question from the server
                question = self.conn_tcp.recv(self.buff_size).decode().strip()
                # Check if the game over message has been received
                if "Game over" in question:
                    print(f"\n{question}")  # Print the game over message
                    # Receive any follow-up message after game over
                    mesg_over = self.conn_tcp.recv(self.buff_size).decode().strip()
                    print(mesg_over)  # Print the follow-up message
                    print(f"\n{bcolors.LIGHTPURPLE}+{bcolors.BOLD}Server disconnected, listening for offer requests...")
                    # Set the listening flag back to True to listen for new offers
                    self.listen = True
                    # Close the TCP connection since the game is over
                    self.conn_tcp.close()
                    break  # Break the loop to end the session
                print(question)  # Print the received question
                # Check if the player is not a bot to receive input from the console
                if not self.bot:
                    try:
                        # Prompt the user for input with a timeout of 10 seconds
                        player_input = inputimeout(prompt='', timeout=10)
                        # Validate the player input to be one of the acceptable responses
                        if player_input not in ['t', 'y', '1', 'f', 'n', '0']:
                            player_input = '-1'  # Set invalid inputs to '-1'
                    except TimeoutOccurred:
                        player_input = '-1'  # Set input to '-1' if input timeout occurs
                    # Send the player's input back to the server encoded in UTF-8
                    self.conn_tcp.sendall(player_input.encode('utf-8'))
                else:
                    # If the player is a bot, randomly select an acceptable response
                    random_char = random.choice(['t', 'y', '1', 'f', 'n', '0'])
                    # Send the bot's response back to the server encoded in UTF-8
                    self.conn_tcp.sendall(random_char.encode('utf-8'))
                # Receive and decode the server's response to the player's answer
                mesage2 = self.conn_tcp.recv(self.buff_size).decode().strip()
                print(mesage2)  # Print the server's response
        except Exception:
            # Close the TCP connection in case of an exception (e.g., disconnection, error)
            self.conn_tcp.close()
            # Set the listening flag back to True to allow reconnecting for new game offers
            self.listen = True

    def play(self):
        """
        Main loop for the player that listens for server offers, connects to the game,
        and handles gameplay until the session ends.
    
        Continuously listens for server broadcast offers. When an offer is received,
        connects to the server using TCP, sets the player's name, and starts answering questions.
        If an exception occurs during connection or gameplay, it handles the disconnection and resets the listener.
        """
        while True:
            # Listen for broadcast offers from the server
            details = self.listen_for_offers()
            # Decide if the player is a bot, and generate or select a name accordingly
            if self.bot:
                self.player_name = self.generate_bot_name()  # Generate a unique bot name
            else:
                self.player_name = random.choice(names)  # Randomly choose a name from the predefined list
            print(bcolors.light + f"Name of your player: {self.player_name}")  # Print the player's name
    
            try:
                # Try to remove the selected name from the list to prevent re-use
                names.remove(self.player_name)
            except ValueError:
                # If the name is not in the list, just pass
                pass
    
            try:
                # Try to connect to the game server with the provided details (IP and port)
                self.connect_to_game((details[0][0], details[1]))
                # Begin answering questions from the server
                self.questions_answer()
            except Exception as e:
                # Handle any exceptions, typically network errors, by closing the TCP connection
                self.conn_tcp.close()
                # Reset the listen flag to True to start listening for offers again
                self.listen = True
    
    def generate_bot_name(self):
        """
        Generates a unique name for a bot player using a predefined prefix and a random suffix.
    
        Returns:
            str: The generated unique bot name.
        """
        prefix = "BOT"  # Define the prefix for bot names
        suffix_length = 6  # Define the length of the random suffix
        # Generate a random string of lowercase letters of defined length
        suffix = ''.join(random.choices(string.ascii_lowercase, k=suffix_length))
        # Return the concatenated prefix and suffix as the bot name
        return prefix + suffix
    
