import pygame
import random
import socket
import time

#functions for rendering

#Function to render the grid
def drawGrid():
	pygame.draw.rect(screen, BLACK, (195, 95, 610, 610))
	for x in [200, 300, 400, 500, 600, 700]:
		for y in [100, 200, 300, 400, 500, 600]:
			pygame.draw.rect(screen, WHITE, (x+5, y+5, 90, 90))

#Helper function, draws hearts from pygame shapes, x, y is center
def drawHeart(x, y):
	pygame.draw.polygon(screen, RED, ((x-25, y), (x+25, y), (x, y+25)))
	pygame.draw.circle(screen, RED, (x-12, y-9), 16)
	pygame.draw.circle(screen, RED, (x+13, y-9), 16)

#Helper function, draws x's fromm pygame shapes. p stands for which player the attack is by, x,y is top left of grid
def drawXattack(x, y, p):
	color = BLACK
	if p==1:
		color = BLACK
	elif p==2:
		color = GRAY
	
	pygame.draw.line(screen, color, (x+10, y+10), (x+90, y+90), 7)
	pygame.draw.line(screen, color, (x+10, y+90), (x+90, y+10), 7)
	
#Function to render players and attacks
#in board, 1 is p1, 2 is p2, 3 is spike, 4 is p1 xattack, 5 is p2 xattack, 6 is p1 hit by xattack, 7 is p2 hit by xattack
def drawActors():
	gridX = [200, 300, 400, 500, 600, 700]
	gridY = [100, 200, 300, 400, 500, 600]
	
	#Draw players and spikes
	for y, outerList in enumerate(board):
		for x, element in enumerate(outerList):
			if element == 1:
				pygame.draw.circle(screen, BLUE, (gridX[x]+50, gridY[y]+50), 40)
			elif element == 2:
				pygame.draw.circle(screen, GREEN, (gridX[x]+50, gridY[y]+50), 40)
			elif element == 3:
				pygame.draw.polygon(screen, RED, ((gridX[x]+10, gridY[y]+90), (gridX[x]+90, gridY[y]+90), (gridX[x]+50, gridY[y]+10)))
			elif element == 4:
				drawXattack(gridX[x], gridY[y], 1)
			elif element == 5:
				drawXattack(gridX[x], gridY[y], 2)
			elif element == 6:
				pygame.draw.circle(screen, BLUE, (gridX[x]+50, gridY[y]+50), 40)
				drawXattack(gridX[x], gridY[y], 2)
			elif element == 7:
				pygame.draw.circle(screen, GREEN, (gridX[x]+50, gridY[y]+50), 40)
				drawXattack(gridX[x], gridY[y], 1)
				
				
	
#Function to render HUD elements
def drawHUD():
	global time_value, gameNotes
	font = pygame.font.Font(None, 50)
	fontSmall = pygame.font.Font(None, 25)
	
	#timer
	if(timer_value <= 1.0):
		timer_text = font.render(f"{timer_value:.2f}", True, RED)
	else:
		timer_text = font.render(f"{timer_value:.2f}", True, BLACK)
	screen.blit(timer_text, (465, 50))

	#gameNotes
	#pygame render doesn't natively support newlines
	lines = gameNotes.split("\n")
	for i, line in enumerate(lines):
		gameNotesText = font.render(line, True, BLACK)
		screen.blit(gameNotesText, (50, 725 + i*50))

	#Player 1 hearts
	screen.blit(fontSmall.render("Player 1 Health:", True, BLACK), (25, 40))
	for i in range(1, p1_health+1):
		drawHeart(150 + i*60, 50)

	#Player 2 hearts
	screen.blit(fontSmall.render("Player 2 Health:", True, BLACK), (675, 40))
	for i in range(1, p2_health+1):
		drawHeart(775 + i*60, 40)
#Function to draw graphics to screen
def updateScreen():
	screen.fill(WHITE)

	#Render the grid
	drawGrid()

	#Render the actors
	drawActors()

	#Render the HUD
	drawHUD()

	pygame.display.flip()


###############################################################################################################################################################

#Functions for network transmission

def sendGamePacket():
	global serverIP, serverPort, p1_coords, p1_coords_spike, p1_xattack_button, p2_coords, p2_coords_spike, p2_xattack_button, playerNumber
	
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	client_socket.connect((serverIP, serverPort))
	print("connected!")
	
	#Send data
	if(playerNumber == 1):
		#time.sleep(.005) #waiting to reduce a collision? Not sure
		if(p1_xattack_button == True):
			x_byte = 1
		else:
			x_byte = 0
		data = ('1'+str(p1_coords[0])+str(p1_coords[1])+str(p1_coords_spike[0])+str(p1_coords_spike[1])+str(x_byte))
		print("attempting send?"+ data)
		client_socket.sendall(data.encode())
	elif(playerNumber == 2):
		#time.sleep(.01)
		if(p2_xattack_button == True):
			x_byte = 1
		else:
			x_byte = 0
		data = ('2'+str(p2_coords[0])+str(p2_coords[1])+str(p2_coords_spike[0])+str(p2_coords_spike[1])+str(x_byte))
		print("attempting send?"+ data)
		client_socket.sendall(data.encode())
		
	#Get packet of other player's movement
	response = client_socket.recv(1024).decode()
	print("received! "+ response)
	response = str(response)
	if(response[0]== '1'):
		p1_coords[0] = int(response[1])
		p1_coords[1] = int(response[2])
		p1_coords_spike[0] = int(response[3])
		p1_coords_spike[1] = int(response[4])
		if(response[5] == '1'):
			p1_xattack_button == True
		else:
			p1_xattack_button == False
	elif(response[0] == '2'):
		p2_coords[0] = int(response[1])
		p2_coords[1] = int(response[2])
		p2_coords_spike[0] = int(response[3])
		p2_coords_spike[1] = int(response[4])
		if(response[5] == '1'):
			p2_xattack_button == True
		else:
			p2_xattack_button == False

	client_socket.close()
###############################################################################################################################################################

#Functions for game logic

#Handle p1 movements
def p1_movement():
	global p1_coords, last_pressed_move_p1
	try:
			#diagonal line movement
		if(pygame.K_w in last_pressed_move_p1 and pygame.K_a in last_pressed_move_p1 and p1_coords[0] > 0 and p1_coords[1] > 0):
			p1_coords[0] -=1
			p1_coords[1] -=1
		elif(pygame.K_w in last_pressed_move_p1 and pygame.K_d in last_pressed_move_p1 and p1_coords[0] > 0 and p1_coords[1] < 5):
			p1_coords[0] -=1
			p1_coords[1] +=1
		elif(pygame.K_s in last_pressed_move_p1 and pygame.K_a in last_pressed_move_p1 and p1_coords[0] < 5 and p1_coords[1] > 0):
			p1_coords[0] +=1
			p1_coords[1] -=1
		elif(pygame.K_s in last_pressed_move_p1 and pygame.K_d in last_pressed_move_p1 and p1_coords[0] < 5 and p1_coords[1] < 5):
			p1_coords[0] +=1
			p1_coords[1] +=1

			#straight line movement
		elif(last_pressed_move_p1[1 ] == pygame.K_w and p1_coords[0] > 0):
			p1_coords[0] -=1
		elif(last_pressed_move_p1[1] == pygame.K_a and p1_coords[1] > 0):
			p1_coords[1] -=1
		elif(last_pressed_move_p1[1] == pygame.K_s and p1_coords[0] < 5):
			p1_coords[0] +=1
		elif(last_pressed_move_p1[1] == pygame.K_d and p1_coords[1] < 5):
			p1_coords[1] +=1
	except IndexError:
		print("Invalid move?")
	last_pressed_move_p1 = [0,0]

#handles placement of spikes for player 1
def p1_spikes():
	global p1_coords_spike, p1_coords, last_pressed_move_p1
	p1_coords_spike = p1_coords.copy() #spike gets the same position as player and then follows movement logic, reusing code efficiently
	try:
			#diagonal line movement
		if(pygame.K_w in last_pressed_move_p1 and pygame.K_a in last_pressed_move_p1 and p1_coords_spike[0] > 0 and p1_coords_spike[1] > 0):
			p1_coords_spike[0] -=1
			p1_coords_spike[1] -=1
		elif(pygame.K_w in last_pressed_move_p1 and pygame.K_d in last_pressed_move_p1 and p1_coords_spike[0] > 0 and p1_coords_spike[1] < 5):
			p1_coords_spike[0] -=1
			p1_coords_spike[1] +=1
		elif(pygame.K_s in last_pressed_move_p1 and pygame.K_a in last_pressed_move_p1 and p1_coords_spike[0] < 5 and p1_coords_spike[1] > 0):
			p1_coords_spike[0] +=1
			p1_coords_spike[1] -=1
		elif(pygame.K_s in last_pressed_move_p1 and pygame.K_d in last_pressed_move_p1 and p1_coords_spike[0] < 5 and p1_coords_spike[1] < 5):
			p1_coords_spike[0] +=1
			p1_coords_spike[1] +=1

			#straight line movement
		elif(last_pressed_move_p1[1] == pygame.K_w and p1_coords_spike[0] > 0):
			p1_coords_spike[0] -=1
		elif(last_pressed_move_p1[1] == pygame.K_a and p1_coords_spike[1] > 0):
			p1_coords_spike[1] -=1
		elif(last_pressed_move_p1[1] == pygame.K_s and p1_coords_spike[0] < 5):
			p1_coords_spike[0] +=1
		elif(last_pressed_move_p1[1] == pygame.K_d and p1_coords_spike[1] < 5):
			p1_coords_spike[1] +=1
	except IndexError:
		print("Invalid spike?")
	last_pressed_move_p1 = [0,0]
	

#Function for p2 movements
def p2_movement():
	global p2_coords, last_pressed_move_p2
	try:
                        #diagonal line movement
		if(pygame.K_i in last_pressed_move_p2 and pygame.K_j in last_pressed_move_p2 and p2_coords[0] > 0 and p2_coords[1] > 0):
			p2_coords[0] -=1
			p2_coords[1] -=1
		elif(pygame.K_i in last_pressed_move_p2 and pygame.K_l in last_pressed_move_p2 and p2_coords[0] > 0 and p2_coords[1] < 5):
			p2_coords[0] -=1
			p2_coords[1] +=1
		elif(pygame.K_k in last_pressed_move_p2 and pygame.K_j in last_pressed_move_p2 and p2_coords[0] < 5 and p2_coords[1] > 0):
			p2_coords[0] +=1
			p2_coords[1] -=1
		elif(pygame.K_k in last_pressed_move_p2 and pygame.K_l in last_pressed_move_p2 and p2_coords[0] < 5 and p2_coords[1] < 5):
			p2_coords[0] +=1
			p2_coords[1] +=1
			
                        #straight line movement
		elif(last_pressed_move_p2[1] == pygame.K_i and p2_coords[0] > 0):
			p2_coords[0] -=1
		elif(last_pressed_move_p2[1] == pygame.K_j and p2_coords[1] > 0):
			p2_coords[1] -=1
		elif(last_pressed_move_p2[1] == pygame.K_k and p2_coords[0] < 5):
			p2_coords[0] +=1
		elif(last_pressed_move_p2[1] == pygame.K_l and p2_coords[1] < 5):
			p2_coords[1] +=1
                       
	except IndexError:
		print("Invalid move?")
	last_pressed_move_p2 = [0,0]
	
#handles placement of spikes for player 2
def p2_spikes():
	global p2_coords_spike, p2_coords, last_pressed_move_p2
	p2_coords_spike = p2_coords.copy() #spike gets the same position as player and then follows movement logic, reusing code efficiently
	try:
                        #diagonal line movement
		if(pygame.K_i in last_pressed_move_p2 and pygame.K_j in last_pressed_move_p2 and p2_coords_spike[0] > 0 and p2_coords_spike[1] > 0):
			p2_coords_spike[0] -=1
			p2_coords_spike[1] -=1
		elif(pygame.K_i in last_pressed_move_p2 and pygame.K_l in last_pressed_move_p2 and p2_coords_spike[0] > 0 and p2_coords_spike[1] < 5):
			p2_coords_spike[0] -=1
			p2_coords_spike[1] +=1
		elif(pygame.K_k in last_pressed_move_p2 and pygame.K_j in last_pressed_move_p2 and p2_coords_spike[0] < 5 and p2_coords_spike[1] > 0):
			p2_coords_spike[0] +=1
			p2_coords_spike[1] -=1
		elif(pygame.K_k in last_pressed_move_p2 and pygame.K_l in last_pressed_move_p2 and p2_coords_spike[0] < 5 and p2_coords_spike[1] < 5):
			p2_coords_spike[0] +=1
			p2_coords_spike[1] +=1
			
                        #straight line movement
		elif(last_pressed_move_p2[1] == pygame.K_i and p2_coords_spike[0] > 0):
			p2_coords_spike[0] -=1
		elif(last_pressed_move_p2[1] == pygame.K_j and p2_coords_spike[1] > 0):
			p2_coords_spike[1] -=1
		elif(last_pressed_move_p2[1] == pygame.K_k and p2_coords_spike[0] < 5):
			p2_coords_spike[0] +=1
		elif(last_pressed_move_p2[1] == pygame.K_l and p2_coords_spike[1] < 5):
			p2_coords_spike[1] +=1
                       
	except IndexError:
		print("Invalid spike?")
	last_pressed_move_p2 = [0,0]
	
#Function handles conflicts when two players enter the same spot. Parameters are original coordinates before move was attempted
def movement_conflict_resolution(p1_coords_old, p2_coords_old):
	global p1_coords, p2_coords, gameNotes
	
	#p1 moves into p2 while p2 stays in place
	if(p2_coords == p2_coords_old):
		p1_coords = p1_coords_old.copy()
	#p2 moves into p1 while p1 stays in place
	elif(p1_coords == p1_coords_old):
		p2_coords = p2_coords_old.copy()
	#p1 and p2 move into the same spot
	else:
		p1_coords = p1_coords_old.copy()
		p2_coords = p2_coords_old.copy()
	#Play boing sound effect and add game note to indicate conflict
	boing = pygame.mixer.Sound("boing.ogg")
	boing_channel.play(boing)
	gameNotes += "Both players went for the same space!\n"

	
def xAttack():
	global board, p1_health, p1_coords, p1_xattack_button, p1_coords_spike, p2_health, p2_coords, p2_xattack_button, p2_coords_spike, gameNotes
	
	#Player 1 attack
	if(p1_xattack_button == True):
		#Check in a t pattern
		if(p1_coords[0] > 0):
			#if p1 is in line of fire
			if(board[p1_coords[0]-1][p1_coords[1]] == 2):
				board[p1_coords[0]-1][p1_coords[1]] = 7
				p2_health -=1
				
			#if spike is in line of fire
			elif(board[p1_coords[0]-1][p1_coords[1]] == 3):
				board[p1_coords[0]-1][p1_coords[1]] = 3
			#if nothing is in line of fire
			else:
				board[p1_coords[0]-1][p1_coords[1]] = 4
		if(p1_coords[1] > 0):
			if(board[p1_coords[0]][p1_coords[1]-1] == 2):
				board[p1_coords[0]][p1_coords[1]-1] = 7
				p2_health -=1
				
				
			elif(board[p1_coords[0]][p1_coords[1]-1] == 3):
				board[p1_coords[0]][p1_coords[1]-1] = 3
			else:
				board[p1_coords[0]][p1_coords[1]-1] = 4
		if(p1_coords[0] < 5):
			if(board[p1_coords[0]+1][p1_coords[1]] == 2):
				board[p1_coords[0]+1][p1_coords[1]] = 7
				p2_health -=1
				
				
			elif(board[p1_coords[0]+1][p1_coords[1]] == 3):
				board[p1_coords[0]+1][p1_coords[1]] = 3
			else:
				board[p1_coords[0]+1][p1_coords[1]] = 4
		if(p1_coords[1] < 5):
			if(board[p1_coords[0]][p1_coords[1]+1] == 2):
				board[p1_coords[0]][p1_coords[1]+1] = 7
				p2_health -=1
				
				
			elif(board[p1_coords[0]][p1_coords[1]+1] == 3):
				board[p1_coords[0]][p1_coords[1]+1] = 3
			else:
				board[p1_coords[0]][p1_coords[1]+1] = 4
	#Player 2 attack
	if(p2_xattack_button == True):
		#Check in a x pattern
		if(p2_coords[0] > 0 and p2_coords[1] > 0): #upleft
			if(board[p2_coords[0]-1][p2_coords[1]-1] == 1):
				board[p2_coords[0]-1][p2_coords[1]-1] = 6
				p1_health -=1
				
				
			elif(board[p2_coords[0]-1][p2_coords[1]-1] == 3):
				board[p2_coords[0]-1][p2_coords[1]-1] = 3
			else:
				board[p2_coords[0]-1][p2_coords[1]-1] = 5
				
		if(p2_coords[0] > 0 and p2_coords[1] < 5): #upright
			if(board[p2_coords[0]-1][p2_coords[1]+1] == 1):
				board[p2_coords[0]-1][p2_coords[1]+1] = 6
				p1_health -=1
				
				
			elif(board[p2_coords[0]-1][p2_coords[1]+1] == 3):
				board[p2_coords[0]-1][p2_coords[1]+1] = 3
			else:
				board[p2_coords[0]-1][p2_coords[1]+1] = 5
				
		if(p2_coords[0] < 5 and p2_coords[1] > 0): #downleft
			if(board[p2_coords[0]+1][p2_coords[1]-1] == 1):
				board[p2_coords[0]+1][p2_coords[1]-1] = 6
				p1_health -=1
				
				
			elif(board[p2_coords[0]+1][p2_coords[1]-1] == 3):
				board[p2_coords[0]+1][p2_coords[1]-1] = 3
			else:
				board[p2_coords[0]+1][p2_coords[1]-1] = 5
				
		if(p2_coords[0] < 5 and p2_coords[1] < 5): #downright
			if(board[p2_coords[0]+1][p2_coords[1]+1] == 1):
				board[p2_coords[0]+1][p2_coords[1]+1] = 6
				p1_health -=1
				
				
			elif(board[p2_coords[0]+1][p2_coords[1]+1] == 3):
				board[p2_coords[0]+1][p2_coords[1]+1] = 3
			else:
				board[p2_coords[0]+1][p2_coords[1]+1] = 5
	
	
	
def resolveSpikes():
	global p1_health, p2_health, p1_coords, p2_coords, p1_coords_spike, p2_coords_spike, gameNotes
	
	#p1 steps on a spike
	if((p1_coords == p1_coords_spike) or (p1_coords == p2_coords_spike)):
		#remove correct spike
		if(p1_coords == p1_coords_spike and p1_coords == p2_coords_spike): #logic for both spikes being in same place
			p1_coords_spike=[7,7]
			p2_coords_spike=[7,7]
		elif(p1_coords == p1_coords_spike):
			p1_coords_spike=[7,7]
		elif(p1_coords == p2_coords_spike):
			p2_coords_spike=[7,7]
		#take damage
		p1_health -=1
		
		
	#p2 steps on a spike
	if((p2_coords == p1_coords_spike) or (p2_coords == p2_coords_spike)):
		#remove correct spike
		if(p2_coords == p1_coords_spike and p2_coords == p2_coords_spike): #logic for both spikes being in same place
			p1_coords_spike=[7,7]
			p2_coords_spike=[7,7]
		elif(p2_coords == p1_coords_spike):
			p1_coords_spike=[7,7]
		elif(p2_coords == p2_coords_spike):
			p2_coords_spike=[7,7]
		#take damage
		p2_health -=1
		
	#play oof
	
		
def gameLogic():
	#global variables
	global board, timer_value, pauseTime, gameNotes, last_pressed_move_p1, p1_coords, p1_spike_button, p1_coords_spike, p1_xattack_button, last_pressed_move_p2, p2_coords, p2_spike_button, p2_coords_spike, p2_xattack_button, playerNumber
	
	#Pause clock
	pauseTime = True
	#Reset audio
	boing_channel.stop()
	oof_channel.stop()
	ding_channel.stop()
	
	#Reset board and timer
	board = [[0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0], 
		[0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0]]

	timer_value = gameUpdateTimer/1000
	gameNotes = ""
	#Create variables for old positions, used for when players try to go into same spot
	#Here is where I learned that python lists can be referenced by multiple variables. This is an unoptimal way to make a copy instead of .copy
	p1_coords_old = [p1_coords[0], p1_coords[1]]
	p2_coords_old = [p2_coords[0], p2_coords[1]]

	if(playerNumber == 1): #calculate position locally
		#Player 1 movement
		if(last_pressed_move_p1[1] != 0 and p1_spike_button == False and p1_xattack_button == False):
			p1_movement()

		#Player 1 Spikes
		if(p1_spike_button == True and last_pressed_move_p1[1] != 0 and p1_xattack_button == False):
			p1_spikes()
			p1_spike_button = False
		
	if(playerNumber == 2):	#calculate position locally
		#Player 2 movement
		if(last_pressed_move_p2[1] != 0 and p2_spike_button == False and p2_xattack_button == False):
			p2_movement()

		#Player 2 Spikes
		if(p2_spike_button == True and last_pressed_move_p2[1] != 0 and p2_xattack_button == False):
			p2_spikes()
			p2_spike_button = False
	
	#Get online player's information
	sendGamePacket()
	
	
	#Resolve positioning conflicts
	if(p1_coords[0] == p2_coords[0] and p1_coords[1] == p2_coords[1]):
		movement_conflict_resolution(p1_coords_old, p2_coords_old)
		
	#Resolve spike damage
	if((p1_coords == p1_coords_spike)or(p1_coords == p2_coords_spike)or(p2_coords == p1_coords_spike)or(p2_coords == p2_coords_spike)):
		resolveSpikes()
		
	#Finalize Player position
	board[p1_coords[0]][p1_coords[1]] = 1 #Update player 1 location
	board[p2_coords[0]][p2_coords[1]] = 2 #Update player 2 location
	
	#Finalize Spike position
	if(p1_coords_spike != [7,7]):
		board[p1_coords_spike[0]][p1_coords_spike[1]] = 3
	if(p2_coords_spike != [7,7]):
		board[p2_coords_spike[0]][p2_coords_spike[1]] = 3
	
	#xAttacks
	if(p1_xattack_button == True or p2_xattack_button == True):
		xAttack()
		last_pressed_move_p1 = [0,0]
		p1_xattack_button = False
		last_pressed_move_p2 = [0,0]
		p2_xattack_button = False
	
	#One final check to make sure everything is reset
	last_pressed_move_p1 = [0,0]
	p1_spike_button = False
	p1_xattack_button = False
	last_pressed_move_p2 = [0,0]
	p2_spike_button = False
	p2_xattack_button = False
	
	#Reset timer
	pauseTime = False
	timer_value = gameUpdateTimer/1000
	pygame.time.set_timer(TIMER_EVENT, 0)
	pygame.time.set_timer(TIMER_EVENT, 2000)

#############################################################################################################################################

#Main

#Get necessary data
print("Welcome to my unnamed game!")
serverIP = input("Please enter the IP of the server you wish to connect to (default is 127.0.0.1): ") or "127.0.0.1"
serverPort =  input("Please enter the port of the server you wish to connect to (default is 2299): ") or 2299
playerNumber = int(input("Please enter your player number (1 or 2): "))
playerNumber = int(playerNumber)
gameUpdateTimer = int(input("Enter the value for gameUpdateTimer (must be the same for both players, default is 5000): ") or 5000)

#Some sort of logic here to wait until both players are connected and ready

#Initialize PyGame
pygame.init()

#Audio
pygame.mixer.init()
boing_channel = pygame.mixer.Channel(0)
oof_channel = pygame.mixer.Channel(1)
ding_channel = pygame.mixer.Channel(2)

#Set up display
WIDTH, HEIGHT = 1000, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Local Client")

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

#Game Board
#Board is a grid that's a 6x6 2D list. Each value in the list is an int
#0 means unoccupied, 1 means player 1, 2 means player 2, 3 means attack

board = [[1, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 2]]

#Clock
clock = pygame.time.Clock()
timer_value = gameUpdateTimer/1000
deltaTime = 0
pauseTime = False

#Custom Timer Event
#This should manage the logic every few seconds
TIMER_EVENT = pygame.USEREVENT + 1 #Custom event identifier
pygame.time.set_timer(TIMER_EVENT, gameUpdateTimer) #Trigger the timer event every x seconds

#General variables
 
#P1 variables
last_pressed_move_p1= [0, 0] #movement buttons pressed, handled every TIMER_EVENT
p1_spike_button = False #tracks if spike button is pressed
p1_coords = [0, 0] #current position on grid
p1_health = 3 #current health
p1_coords_spike = [7,7] #current spikes position, 7,7 means not placed
p1_xattack_button = False #tracks if xAttack button is pressed

#p2 variables
last_pressed_move_p2 = [0, 0]
p2_spike_button = False
p2_coords = [5, 5]
p2_health = 3
p2_coords_spike = [7,7]
p2_xattack_button = False

gameNotes=""

#Game Loop
running = True
while running:
#Update timer values
	if(pauseTime == False):
		deltaTime = clock.tick(120) / 1000
		timer_value -= deltaTime
#check health
	if(p1_health <= 0 or p2_health <= 0):
		running = False
	
#get updates from pygame
	for event in pygame.event.get():

		if event.type == pygame.QUIT:
			running = False
			pygame.quit()
		elif event.type == TIMER_EVENT: #Every 2 seconds, game action
			gameLogic()
			timer_value = gameUpdateTimer/1000
			pygame.time.set_timer(TIMER_EVENT, gameUpdateTimer)
		elif event.type == pygame.KEYDOWN and playerNumber == 1: #Get player 1 movement and actions
			if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
				last_pressed_move_p1.pop(0)
				last_pressed_move_p1.append(event.key)
			if event.key == pygame.K_q:
				p1_spike_button = not p1_spike_button
			if event.key == pygame.K_e:
				p1_xattack_button = not p1_xattack_button
		elif event.type == pygame.KEYDOWN and playerNumber == 2: #Get player 2 movement and actions
			if event.key in [pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l]:
				last_pressed_move_p2.pop(0)
				last_pressed_move_p2.append(event.key)
			if event.key == pygame.K_u:
				p2_spike_button = not p2_spike_button
			if event.key == pygame.K_o:
				p2_xattack_button = not p2_xattack_button

	updateScreen() #Update graphics

#print winner
exit=True
winnerText=""
if(p1_health > p2_health):
	winnerText="Player 1 Wins!"
elif(p2_health > p1_health):
	winnerText="Player 2 Wins!"
else:
	winnerText="uh"

screen.fill(WHITE)
font = pygame.font.Font(None, 50)
screen.blit(font.render(winnerText, True, BLACK), (HEIGHT //2, WIDTH // 2))
screen.blit(font.render("Press any key to exit.", True, BLACK), (HEIGHT //2, WIDTH // 2 - 75))
pygame.display.flip()

while exit:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			exit = False
			
pygame.quit()


