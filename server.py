import socket
import threading
import time
import copy

HOST = "127.0.0.1"
PORT = 2299
p1_coords = [-1, -1]
p1_coords_spike = [-1, -1]
p1_xattack_button = False
p2_coords = [-1, -1]
p2_coords_spike = [-1, -1]
p2_xattack_button = False

cont1 = False
cont2 = False
updated_p1 = False
updated_p2 = False

# Store client connections and data
clients = []


def handle_client(conn, addr):
    global p1_coords, p1_coords_spike, p1_xattack_button, p2_coords, p2_coords_spike, p2_xattack_button, clients, cont1, cont2, updated_p1, updated_p2
    client_id = -1
    print(f"[+] Client connected from {addr}")

    # Receive data
    data = conn.recv(1500).decode()
    data = str(data)
    print(f"[Client {addr}] Sent: {data}")
    print(data[0])
    if(data[0]== '1'):
        client_id = 0
        p1_coords[0] = int(data[1])
        p1_coords[1] = int(data[2])
        p1_coords_spike[0] = int(data[3])
        p1_coords_spike[1] = int(data[4])
        if(data[5] == '1'):
            p1_xattack_button == True
        else:
            p1_xattack_button == False
        clients.append(((conn, client_id), int(data[0])))
        updated_p1 = True
    elif(data[0] == '2'):
        client_id = 1
        p2_coords[0] = int(data[1])
        p2_coords[1] = int(data[2])
        p2_coords_spike[0] = int(data[3])
        p2_coords_spike[1] = int(data[4])
        if(data[5] == '1'):
            p2_xattack_button == True
        else:
            p2_xattack_button == False
        clients.append(((conn, client_id), int(data[0])))
        updated_p2 = True
            
    

    # Wait until both clients have sent data
    while len(clients) < 2 or updated_p1 == False or updated_p2 == False:
        time.sleep(.005) #This is in the top 5 worst things I've ever done
    time.sleep(.01)
    # Send data to both clients
    listInUse = False
    while listInUse == True:
    	time.sleep(.005)
    time.sleep(.01)
    listInUse = True
    print("This is client_id: " + str(client_id))
    if(clients[client_id][1] == 2):
        
        if(p1_xattack_button == True):
            x_byte = 1
        else:
            x_byte = 0
        returnPacket = ('1'+str(p1_coords[0])+str(p1_coords[1])+str(p1_coords_spike[0])+str(p1_coords_spike[1])+str(x_byte))
        print(returnPacket)
        conn.sendall(returnPacket.encode())
        cont1 = True
        listInUse = False
    elif(clients[client_id][1] == 1):
        
        if(p2_xattack_button == True):
            x_byte = 1
        else:
            x_byte = 0
        returnPacket = ('2'+str(p2_coords[0])+str(p2_coords[1])+str(p2_coords_spike[0])+str(p2_coords_spike[1])+str(x_byte))
        print(returnPacket)
        conn.sendall(returnPacket.encode())
        cont2 = True
        listInUse = False
		
    print(f"[Client {client_id}] data Sent")
    
    while cont1 == False or cont2 == False:
        conn.close()

def start_server():
    global server_socket, clients, cont1, cont2
    server_socket.listen(2)  # Listen for up to 2 clients
    print(f"[*] Server listening on {HOST}:{PORT}")

    # Accept two clients
    
    conn1, addr1 = server_socket.accept()
    threading.Thread(target=handle_client, args=(conn1, addr1)).start()
    
    conn2, addr2 = server_socket.accept()
    threading.Thread(target=handle_client, args=(conn2, addr2)).start()
    
    #wait clause
    while cont1 == False or cont2 == False:
        time.sleep(.005)
    cont1 = False
    cont2 = False
    updated_p1 = False
    updated_p2 = False
    clients = []
    
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
while True:
    start_server()
