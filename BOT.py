from BasePlayer import BasePlayer
import socket
import struct

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


if __name__ == "__main__":
    B = BOT() # Instantiate a BOT object
    B.play()   # Start the bot's participation in the game
