from BasePlayer import BasePlayer
import socket
import struct
from Colors import bcolors
import threading
class BOT(BasePlayer):
    """
    BOT class that inherits from BasePlayer, tailored to operate as a bot within the game.
    
    This subclass is specifically designed to act as a bot in networked game sessions,
    automatically responding to game interactions using predefined logic rather than human input.
    """
    def __init__(self):
        """
        Initialize the BOT class by invoking the initializer of the BasePlayer with a bot flag.
        
        This constructor sets up the BOT as a bot player, enabling automatic behaviors for game interactions.
        """
        super().__init__(bot=True) # Call the parent class's initializer with the bot flag set to True

    def play_with_bots(self, num_bots):
        print(bcolors.OKBLUE + bcolors.BOLD + f"Creating {num_bots} bots...")
        threads = []
        for _ in range(num_bots):
            bot = BOT()
            thread = threading.Thread(target=bot.play)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()


if __name__ == "__main__":
    B = BOT() # Instantiate a BOT object
    num_bots = int(input("Enter the number of bots you want to play with: "))
    B.play_with_bots(num_bots)
