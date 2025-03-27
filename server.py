import socket
import threading
import time
import copy

#Networking variables
HOST = "127.0.0.1"
PORT = 2299

#Game variables
p1_coords = [-1, -1]
p1_coords_spike = [-1, -1]
p1_xattack_button = False
p2_coords = [-1, -1]
p2_coords_spike = [-1, -1]
p2_xattack_button = False

#Function for interpreting packet that contains p1 position info, sent by p1 client
def getP1Info(data):
	global p1_coords, p1_coords_spike, p1_xattack_button
	if(data[0]== '1'):
		p1_coords[0] = int(data[1])
		p1_coords[1] = int(data[2])
		p1_coords_spike[0] = int(data[3])
		p1_coords_spike[1] = int(data[4])
		if(int(data[5]) == 1):
			p1_xattack_button = True
		else:
			p1_xattack_button = False
			
#Function for interpreting packet that contains p1 position info, sent by p2 client
def getP2Info(data):
	global p2_coords, p2_coords_spike, p2_xattack_button
	if(data[0]== '2'):
		p2_coords[0] = int(data[1])
		p2_coords[1] = int(data[2])
		p2_coords_spike[0] = int(data[3])
		p2_coords_spike[1] = int(data[4])
		if(int(data[5]) == 1):
			p2_xattack_button = True
		else:
			p2_xattack_button = False
		
#Create packet that has p1 location in it, sent to p2 client	
def craftP1PacketforP2():
	global p1_coords, p1_coords_spike, p1_xattack_button
	x_value = 0
	if(p1_xattack_button == True):
		x_value = 1
	returnPacket = ('1'+str(p1_coords[0])+str(p1_coords[1])+str(p1_coords_spike[0])+str(p1_coords_spike[1])+str(x_value))
	print(x_value)
	print(p1_xattack_button)
	print(returnPacket)
	return returnPacket
	
#Create packet that has p2 location in it, sent to p1 client	
def craftP2PacketforP1():
	global p2_coords, p2_coords_spike, p2_xattack_button
	x_value = 0
	if(p2_xattack_button == True):
		x_value = 1
	returnPacket = ('2'+str(p2_coords[0])+str(p2_coords[1])+str(p2_coords_spike[0])+str(p2_coords_spike[1])+str(x_value))
	return returnPacket
	
#Perform initial handshake with both players to get their connection info
def handshake():
	global server_socket, player1Client, player2Client
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind((HOST, PORT))
	
	server_socket.listen(2)  # Listen for up to 2 clients
	
	#Get client #1
	global conn1, addr1
	conn1, addr1 = server_socket.accept()
	sentPacket = conn1.recv(1000).decode()
	if sentPacket == '1':
		player1Client = conn1
	elif sentPacket == '2':
		player2Client = conn1
		
	#Get client #2
	global conn2, addr2
	conn2, addr2 = server_socket.accept()
	sentPacket = conn2.recv(1000).decode()
	if sentPacket == '1':
		player1Client = conn2
	elif sentPacket == '2':
		player2Client = conn2
		
	#Send go ahead signal
	player1Client.sendall(b'1')
	player2Client.sendall(b'1')
	
#Recieve, assign, and send all necessary info
def middleman():
	global server_socket, player1Client, p1_coords, p1_coords_spike, p1_xattack_button, player2Client, p2_coords, p2_coords_spike, p2_xattack_button
	
	p1SentPacket = player1Client.recv(1000).decode()
	
	getP1Info(p1SentPacket)
			
	p2SentPacket = player2Client.recv(1000).decode()
	
	getP2Info(p2SentPacket)
	
	player2Client.sendall(craftP1PacketforP2().encode())
	
	player1Client.sendall(craftP2PacketforP1().encode())
#Main
handshake()

while True:
	#try:
	middleman()
	#except:
	#	break
