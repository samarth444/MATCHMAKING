import socket
import ssl

# Get user input for game configuration
tries = int(input("Tries: "))  # Number of tries allowed
max_number = int(input("Maximum number: "))  # Maximum number for guessing
role = input("Role: ")  # Role in the game (guesser or decider)

# Create a configuration string based on user input
config_string = f"{tries}-{max_number}-{role}"

# Create a TCP/IP socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Create an SSL context for TLS client authentication
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.check_hostname = False  # Disable hostname verification
context.verify_mode = ssl.CERT_NONE  # Disable certificate verification

# Wrap the socket with SSL/TLS encryption and connect to the server
client = context.wrap_socket(client, server_hostname="127.0.0.1")
client.connect(("127.0.0.1", 9999))

# Send the configuration string to the server
client.send(config_string.encode())

# Receive and print a message from the server
print(client.recv(1024).decode())

# Send user input (guess or number) to the server
client.send(input().encode())

# Game loop to receive and process messages from the server
while True:
    message = client.recv(1024).decode()
    print(message)
    # Check if the game has ended (e.g., tries exhausted, player lost, or invalid input)
    if "tries" in message or "lost" in message or "Invalid" in message:
        break
    # If the player is a guesser, send the guess to the server
    if role == "guesser":
        client.send(input().encode())
