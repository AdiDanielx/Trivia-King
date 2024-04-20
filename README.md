# Trivia King 👑 - Networked Trivia Game

## Introduction
Welcome to Trivia King 👑! This repository contains a client-server application that implements a trivia contest where players receive random true or false facts and must answer correctly as quickly as possible.

This application is designed with full compatibility in mind, meaning that any client can connect to any server, and all components are expected to work together seamlessly.

## Features
- A server application that broadcasts its presence and handles incoming client connections and game logic.
- A client application that listens for server offers, connects to the server, and interacts with the trivia game.
- For teams with three members, a bot application is also provided, which simulates a player using automated responses.

## How to Run
1. Start the server:
    ```
    python Server.py
    ```
   The server will begin broadcasting its presence.

2. Start the client(s):
    ```
    python Client.py
    ```
   The client will connect to the server and wait for the game to start.

3. (Optional) Start the bot client(s):
    ```
    python BOT.py
    ```
   The bot will act as an automated player in the game.

## Suggested Architecture
- **Client**: A single-threaded application with states for looking for a server, connecting to a server, and playing the game.
- **Server**: A multi-threaded application that waits for client connections and then shifts to game mode.
- **Bot Client**: Behaves similarly to the standard client but provides automated responses.

## Packet Formats
- **UDP Broadcasts**: Sent on port 13117 with a specific message format including a magic cookie, message type, server name, and TCP port.
- **TCP Data**: No specific packet format. Clients send their team name followed by a newline, then simply send and receive data to and from the server.

## Dependencies
- Python 3.x
- Additional libraries: `inputimeout`

To install the dependencies, run:

```shell
pip install inputimeout
```

## Error Handling
The application includes robust error handling to deal with network issues, message corruption, server timeouts, and unexpected client behavior.

## Game Customization
You can customize the trivia questions by editing the question list within the server application.

## Statistics
At the end of each game, the server can output interesting statistics such as the best team ever to play, the most commonly typed character, and more.

## Repository Structure
- `Server.py`: The server application code.
- `Client.py`: The client application code.
- `BOT.py`: The bot application code for automated responses.
- `BasePlayer.py`: The base class for client and bot functionality.
- `Colors.py`: Utility for colored console output.

