# Multiplayer Number Guessing Game
# This contains both server and client code

# ----- SERVER CODE -----
# server.py
import socket
import threading
import random
import json
import time

class GameServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.clients = {}  # {client_id: {'socket': socket, 'username': username}}
        self.client_counter = 0
        self.target_number = random.randint(1, 100)
        self.current_player = 0
        self.game_started = False
        self.players_ready = 0
        self.lock = threading.Lock()
        
    def start(self):
        """Start the server and listen for connections"""
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")
        print(f"The target number is: {self.target_number}")
        
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                client_id = self.client_counter
                self.client_counter += 1
                
                print(f"New connection from {address}, assigned ID: {client_id}")
                
                # Start a new thread to handle this client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_id)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.server_socket.close()
    
    def handle_client(self, client_socket, client_id):
        """Handle communication with a client"""
        try:
            # First message should be the username
            username_data = client_socket.recv(1024).decode('utf-8')
            username = json.loads(username_data).get('username', f"Player_{client_id}")
            
            with self.lock:
                self.clients[client_id] = {
                    'socket': client_socket,
                    'username': username,
                    'guesses': 0
                }
                
                # Notify all clients about the new player
                self.broadcast({
                    'type': 'player_joined',
                    'username': username,
                    'message': f"{username} has joined the game!",
                    'player_count': len(self.clients)
                })
                
                # Tell this client about the game state
                self.send_message(client_id, {
                    'type': 'welcome',
                    'message': f"Welcome {username}! Waiting for more players to join...",
                    'player_count': len(self.clients),
                    'game_started': self.game_started
                })
            
            # Main client communication loop
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                message = json.loads(data)
                message_type = message.get('type', '')
                
                if message_type == 'ready':
                    with self.lock:
                        self.players_ready += 1
                        if self.players_ready >= 2 and self.players_ready == len(self.clients):
                            self.start_game()
                        else:
                            self.broadcast({
                                'type': 'waiting',
                                'message': f"{username} is ready! ({self.players_ready}/{len(self.clients)})",
                                'ready_count': self.players_ready,
                                'total_players': len(self.clients)
                            })
                
                elif message_type == 'guess' and self.game_started:
                    current_player_id = list(self.clients.keys())[self.current_player]
                    
                    if client_id != current_player_id:
                        self.send_message(client_id, {
                            'type': 'error',
                            'message': "It's not your turn!"
                        })
                        continue
                    
                    guess = message.get('guess')
                    try:
                        guess = int(guess)
                        self.handle_guess(client_id, guess)
                    except ValueError:
                        self.send_message(client_id, {
                            'type': 'error',
                            'message': "Please enter a valid number!"
                        })
                
                elif message_type == 'chat':
                    chat_message = message.get('message', '')
                    self.broadcast({
                        'type': 'chat',
                        'username': username,
                        'message': chat_message
                    })
        
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
        finally:
            # Clean up when client disconnects
            self.handle_disconnect(client_id)
    
    def handle_disconnect(self, client_id):
        """Handle client disconnection"""
        with self.lock:
            if client_id not in self.clients:
                return
                
            username = self.clients[client_id]['username']
            try:
                self.clients[client_id]['socket'].close()
            except:
                pass
                
            del self.clients[client_id]
            print(f"Client {username} (ID: {client_id}) disconnected")
            
            # Notify remaining clients
            self.broadcast({
                'type': 'player_left',
                'username': username,
                'message': f"{username} has left the game!",
                'player_count': len(self.clients)
            })
            
            # If game was started and not enough players, reset the game
            if self.game_started and len(self.clients) < 2:
                self.reset_game()
    
    def start_game(self):
        """Start the game when enough players are ready"""
        with self.lock:
            self.game_started = True
            self.target_number = random.randint(1, 100)
            print(f"Game started! Target number: {self.target_number}")
            
            # Reset player statistics
            for client_data in self.clients.values():
                client_data['guesses'] = 0
            
            # Randomly choose first player
            self.current_player = random.randint(0, len(self.clients) - 1)
            current_player_id = list(self.clients.keys())[self.current_player]
            current_player_name = self.clients[current_player_id]['username']
            
            # Notify all clients that the game has started
            self.broadcast({
                'type': 'game_started',
                'message': f"The game has started! {current_player_name} goes first.",
                'current_player': current_player_name
            })
    
    def reset_game(self):
        """Reset the game state"""
        with self.lock:
            self.game_started = False
            self.players_ready = 0
            self.target_number = random.randint(1, 100)
            
            self.broadcast({
                'type': 'game_reset',
                'message': "The game has been reset. Type 'ready' when you're ready to play again."
            })
    
    def handle_guess(self, client_id, guess):
        """Handle a player's guess"""
        with self.lock:
            username = self.clients[client_id]['username']
            self.clients[client_id]['guesses'] += 1
            guesses = self.clients[client_id]['guesses']
            
            if guess == self.target_number:
                # Player won
                self.broadcast({
                    'type': 'game_won',
                    'message': f"{username} guessed the correct number {self.target_number} in {guesses} tries!",
                    'winner': username,
                    'target_number': self.target_number
                })
                # Reset the game after a short delay
                threading.Timer(5.0, self.reset_game).start()
            elif guess < self.target_number:
                self.broadcast({
                    'type': 'guess_result',
                    'username': username,
                    'guess': guess,
                    'message': f"{username} guessed {guess} - Too low!"
                })
                self.next_player()
            else:  # guess > self.target_number
                self.broadcast({
                    'type': 'guess_result',
                    'username': username,
                    'guess': guess,
                    'message': f"{username} guessed {guess} - Too high!"
                })
                self.next_player()
    
    def next_player(self):
        """Move to the next player's turn"""
        with self.lock:
            self.current_player = (self.current_player + 1) % len(self.clients)
            current_player_id = list(self.clients.keys())[self.current_player]
            current_player_name = self.clients[current_player_id]['username']
            
            self.broadcast({
                'type': 'next_turn',
                'message': f"It's {current_player_name}'s turn!",
                'current_player': current_player_name
            })
    
    def send_message(self, client_id, message):
        """Send a message to a specific client"""
        try:
            self.clients[client_id]['socket'].sendall(json.dumps(message).encode('utf-8'))
        except (ConnectionResetError, BrokenPipeError):
            self.handle_disconnect(client_id)
    
    def broadcast(self, message):
        """Send a message to all connected clients"""
        disconnected = []
        
        for client_id, client_data in self.clients.items():
            try:
                client_data['socket'].sendall(json.dumps(message).encode('utf-8'))
            except (ConnectionResetError, BrokenPipeError):
                disconnected.append(client_id)
        
        # Handle any disconnections outside the loop to avoid modifying during iteration
        for client_id in disconnected:
            self.handle_disconnect(client_id)

# This block allows you to run the server directly
if __name__ == "__main__":
    server = GameServer()
    server.start()


# ----- CLIENT CODE -----
# client.py
import socket
import threading
import json
import sys
import os

class GameClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.connected = False
        self.is_my_turn = False
    
    def connect(self, username):
        """Connect to the game server"""
        try:
            self.socket.connect((self.host, self.port))
            self.username = username
            self.connected = True
            
            # Send username to the server
            self.send_message({
                'type': 'username',
                'username': username
            })
            
            # Start a thread to receive messages
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except ConnectionRefusedError:
            print("Could not connect to the server. Is it running?")
            return False
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False
    
    def send_message(self, message):
        """Send a message to the server"""
        if not self.connected:
            print("Not connected to server!")
            return
            
        try:
            self.socket.sendall(json.dumps(message).encode('utf-8'))
        except:
            print("Error sending message. Disconnecting...")
            self.disconnect()
    
    def receive_messages(self):
        """Continuously receive and process messages from the server"""
        try:
            while self.connected:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                self.process_message(json.loads(data))
        except:
            if self.connected:
                print("Connection to server lost!")
                self.disconnect()
    
    def process_message(self, message):
        """Process received messages based on their type"""
        message_type = message.get('type', '')
        
        if message_type == 'welcome':
            print(message.get('message', ''))
            print(f"There are {message.get('player_count', 0)} players connected.")
            print("Type 'ready' when you're ready to play!")
            
        elif message_type == 'player_joined':
            print(message.get('message', ''))
            print(f"There are now {message.get('player_count', 0)} players connected.")
            
        elif message_type == 'player_left':
            print(message.get('message', ''))
            print(f"There are {message.get('player_count', 0)} players remaining.")
            
        elif message_type == 'waiting':
            print(message.get('message', ''))
            
        elif message_type == 'game_started':
            print("\n" + "="*50)
            print(message.get('message', ''))
            print("="*50)
            current_player = message.get('current_player', '')
            self.is_my_turn = (current_player == self.username)
            
            if self.is_my_turn:
                print("It's your turn! Enter a number between 1 and 100:")
            else:
                print(f"Waiting for {current_player} to make a guess...")
                
        elif message_type == 'next_turn':
            print(message.get('message', ''))
            current_player = message.get('current_player', '')
            self.is_my_turn = (current_player == self.username)
            
            if self.is_my_turn:
                print("It's your turn! Enter a number between 1 and 100:")
                
        elif message_type == 'guess_result':
            print(message.get('message', ''))
            
        elif message_type == 'error':
            print(f"Error: {message.get('message', '')}")
            
        elif message_type == 'game_won':
            print("\n" + "*"*50)
            print(message.get('message', ''))
            print("*"*50)
            print("The game will restart shortly. Type 'ready' when you're ready for the next round.")
            
        elif message_type == 'game_reset':
            print("\n" + "-"*50)
            print(message.get('message', ''))
            print("-"*50)
            
        elif message_type == 'chat':
            username = message.get('username', 'Unknown')
            chat_message = message.get('message', '')
            print(f"[CHAT] {username}: {chat_message}")
    
    def ready(self):
        """Send ready signal to the server"""
        self.send_message({'type': 'ready'})
        print("Waiting for other players to get ready...")
    
    def send_guess(self, guess):
        """Send a guess to the server"""
        if not self.is_my_turn:
            print("It's not your turn!")
            return
            
        try:
            guess_value = int(guess)
            self.send_message({
                'type': 'guess',
                'guess': guess_value
            })
        except ValueError:
            print("Please enter a valid number!")
    
    def send_chat(self, message):
        """Send a chat message to all players"""
        self.send_message({
            'type': 'chat',
            'message': message
        })
    
    def disconnect(self):
        """Disconnect from the server"""
        self.connected = False
        try:
            self.socket.close()
        except:
            pass
        print("Disconnected from server.")

# Command-line interface for the client
def run_client():
    client = None
    
    try:
        print("="*50)
        print("MULTIPLAYER NUMBER GUESSING GAME")
        print("="*50)
        print("\nEnter server details (press Enter for defaults):")
        
        host = input("Server hostname [localhost]: ").strip() or 'localhost'
        
        port_input = input("Server port [5555]: ").strip() or '5555'
        try:
            port = int(port_input)
        except ValueError:
            print("Invalid port number. Using default 5555.")
            port = 5555
        
        username = input("Enter your username: ").strip()
        while not username:
            username = input("Username cannot be empty. Please enter your username: ").strip()
        
        print(f"\nConnecting to {host}:{port} as {username}...")
        client = GameClient(host, port)
        
        if not client.connect(username):
            print("Failed to connect. Exiting...")
            return
        
        print("\nConnected to the server!")
        print("Type 'ready' to start the game, or 'help' for commands.")
        
        # Main input loop
        while client.connected:
            user_input = input().strip()
            
            if user_input.lower() == 'quit' or user_input.lower() == 'exit':
                client.disconnect()
                break
                
            elif user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("  ready    - Signal that you're ready to play")
                print("  chat <message> - Send a chat message to all players")
                print("  quit/exit - Disconnect and exit")
                print("  <number> - Make a guess when it's your turn")
                
            elif user_input.lower() == 'ready':
                client.ready()
                
            elif user_input.lower().startswith('chat '):
                chat_message = user_input[5:].strip()
                if chat_message:
                    client.send_chat(chat_message)
                    
            elif user_input.isdigit():
                client.send_guess(user_input)
                
            else:
                print("Unknown command. Type 'help' for available commands.")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if client and client.connected:
            client.disconnect()

if __name__ == "__main__":
    run_client()


# ----- HOW TO RUN THE GAME -----
# 1. Save the code into two separate files: server.py and client.py
# 2. Start the server by running: python server.py
# 3. Start clients (in separate terminals) by running: python client.py
# 4. Follow the instructions in the client to play the game
