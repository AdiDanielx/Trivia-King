import socket
from datetime import datetime
import threading
import time
from threading import * 
import struct

class Server:
    def get_local_ip():
        # Create a temporary socket to get the local IP address
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.connect(("8.8.8.8", 80))  # Connect to Google's DNS server
        local_ip = temp_socket.getsockname()[0]
        temp_socket.close()
        return local_ip
    
    def __init__(self):
        self.udp_port = 13117

        #Message format
        self.magic_cookie = 0xabcddcba
        self.message_type = 0x2
        self.server_name = 'The Best Server In The World abc' 
        self.udp_format = 'IbH'
        self.ip = self.get_local_ip()