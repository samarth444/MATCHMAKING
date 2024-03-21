import socket
import threading
import ssl

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to a specific address and port
server.bind(("127.0.0.1", 9999))

# Listen for incoming connections
server.listen()

# List to keep track of connected clients
connected_clients = []


# Function to handle the matching and game logic between two clients
def handle_match(c1, c2):
    # Extracting configuration values from client data
    tries, max_num = c1[1].split("-")
    tries, max_num = int(tries), int(max_num)

    # Checking if c1 is the decider, if not, swap c1 and c2
    if c1[2] != "decider":
        c1, c2 = c2, c1

    c1_socket = c1[0]  # Socket for client 1
    c2_socket = c2[0]  # Socket for client 2

    # Checking if c2 socket is valid
    if not isinstance(c2_socket, socket.socket):
        print("Invalid socket for c2")
        c1_socket.send("Invalid socket for c2".encode())
        return

    # Sending instructions to clients
    c1_socket.send("Enter the number to be guessed: ".encode())
    number = int(c1_socket.recv(1024).decode())

    # Handling invalid number range
    if number > max_num:
        c1_socket.send("Invalid Range!".encode())
        c2_socket.send("Your partner messed up! Invalid range!".encode())
        c1_socket.close()
        c2_socket.close()
    else:
        guessed = False
        try_counter = 0
        c2_socket.send("Enter your guess: ".encode())

        # Main game loop
        while not guessed:
            try_counter += 1
            guess = int(c2_socket.recv(1024).decode())

            # Checking if the guess is correct
            if guess == number:
                c2_socket.send(f"Correct! It took you {try_counter} tries!".encode())
                c1_socket.send(f"Your partner guessed correctly after {try_counter} tries!".encode())
                c1_socket.close()
                c2_socket.close()
                guessed = True
            else:
                # Handling incorrect guesses
                if try_counter >= tries:
                    c2_socket.send(f"You lost! The number was {number}".encode())
                    c1_socket.send(f"Your partner lost! The number was {number}".encode())
                    c1_socket.close()
                    c2_socket.close()
                    break
                else:
                    if guess < number:
                        c2_socket.send(f"Your guess is too low. Try again: ".encode())
                        c1_socket.send(f"Your partner guessed {guess}".encode())
                    elif guess > number:
                        c2_socket.send(f"Your guess is too high. Try again: ".encode())
                        c1_socket.send(f"Your partner guessed {guess}".encode())


# Function to handle each client's connection and matchmaking
def handle_client(c):
    # Receive configuration and role information from the client
    config_string = c.recv(1024).decode()
    config = config_string[:config_string.rfind("-")]
    role = config_string[config_string.rfind("-") + 1:]
    found_match = False

    # Check for a match with an existing client
    for i in range(len(connected_clients)):
        if connected_clients[i][1] == config:
            if connected_clients[i][2] != role:
                c2 = connected_clients[i]
                print(f"MATCH between port {c.getpeername()[1]} and port {c2[0].getpeername()[1]}")
                # Start a new thread to handle the match
                threading.Thread(target=handle_match, args=((c, config, role), c2)).start()
                # Remove the matched client from the list
                del connected_clients[i]
                found_match = True
                break

    # If no match found, add the client to the list
    if not found_match:
        connected_clients.append((c, config, role))

    print("SSL connection established with client.")


# Main server loop to accept incoming connections
while True:
    # Accept a client connection
    client, addr = server.accept()
    hostname, port = addr
    print(f"Server has connected to {hostname} on port {port}")
    
    # Create an SSL context and wrap the client socket
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    client = context.wrap_socket(client, server_side=True)

    # Start a new thread to handle the client
    threading.Thread(target=handle_client, args=(client,)).start()
