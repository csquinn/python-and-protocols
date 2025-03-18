import socket
import threading

HOST = "127.0.0.1"
PORT = 2299
p1_coords = [-1, -1]
p1_coords_spike = [-1, -1]
p1_xattack_button = False
p2_coords = [-1, -1]
p2_coords_spike = [-1, -1]
p2_xattack_button = False

# Store client connections and data
clients = []


def handle_client(conn, addr, client_id):
    global p1_coords, p1_coords_spike, p1_xattack_button, p2_coords, p2_coords_spike, p2_xattack_button
    print(f"[+] Client {client_id} connected from {addr}")

    # Receive data (adjust buffer size as needed)
    data = conn.recv(1024).decode()
    print(f"[Client {client_id}] Sent: {data}")

    if(data[0]== '1'):
        p1_coords[0] = int(data[1])
        p1_coords[1] = int(data[2])
        p1_coords_spike[0] = int(data[3])
        p1_coords_spike[1] = int(data[4])
        if(respones[5] == '1'):
            p1_xattack_button == True
        else:
            p1_xattack_button == False
    elif(data[0] == '2'):
        p2_coords[0] = int(data[1])
        p2_coords[1] = int(data[2])
        p2_coords_spike[0] = int(data[3])
        p2_coords_spike[1] = int(data[4])
        if(respones[5] == '1'):
            p2_xattack_button == True
        else:
            p2_xattack_button == False
            
    clients.append((conn, client_id), int(data[0]))

    # Wait until both clients have sent data
    while len(clients) < 2:
        print("waiting")
        pass  # Busy wait (could be improved with threading.Event)

    # Send data to both clients
    if(clients[1] == 2):
        if(p1_xattack_button == True):
            x_byte = 1
        else:
            x_byte = 0
        client_socket.sendall(b'1',p1_coords[0].to_bytes(1),p1_coords[1].to_bytes(1),p1_coords_spike[0].to_bytes(1),p1_coords_spike[1].to_bytes(1),x_byte.to_bytes(1))
    elif(clients[1] == 1):
        if(p2_xattack_button == True):
            x_byte = 1
        else:
            x_byte = 0
        client_socket.sendall(b'1',p2_coords[0].to_bytes(1),p2_coords[1].to_bytes(1),p2_coords_spike[0].to_bytes(1),p2_coords_spike[1].to_bytes(1),x_byte.to_bytes(1))
		
    print(f"[Client {client_id}] data Sent")

    conn.close()

def start_server():
    global server_socket
    server_socket.listen(2)  # Listen for up to 2 clients
    print(f"[*] Server listening on {HOST}:{PORT}")

    # Accept two clients
    for client_id in range(1, 3):
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr, client_id)).start()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
while True:
    start_server()
