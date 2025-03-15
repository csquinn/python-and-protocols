import pygame
import random

#functions

#Function to render the grid
def drawGrid():
	pygame.draw.rect(screen, BLACK, (195, 95, 610, 610))
	for x in [200, 300, 400, 500, 600, 700]:
		for y in [100, 200, 300, 400, 500, 600]:
			pygame.draw.rect(screen, WHITE, (x+5, y+5, 90, 90))

#Helper function, draws hearts from pygame shapes
#total size is 50 x 50
def drawHeart(x, y):
	pygame.draw.polygon(screen, RED, ((x-25, y), (x+25, y), (x, y+25)))
	pygame.draw.circle(screen, RED, (x-12, y-9), 16)
	pygame.draw.circle(screen, RED, (x+13, y-9), 16)
#Function to render players and attacks
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

def gameLogic():
	#global variables
	global board, timer_value, gameNotes, last_pressed_move_p1, p1_coords, last_pressed_move_p2, p2_coords
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

	#Player 1 movement
	print(str(last_pressed_move_p1) + " " + str(last_pressed_move_p2))
	if(last_pressed_move_p1[1] != 0):
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
			elif(last_pressed_move_p1[1] == pygame.K_w and p1_coords[0] > 0):
				p1_coords[0] -=1
			elif(last_pressed_move_p1[1] == pygame.K_a and p1_coords[1] > 0):
				p1_coords[1] -=1
			elif(last_pressed_move_p1[1] == pygame.K_s and p1_coords[0] < 5):
				p1_coords[0] +=1
			elif(last_pressed_move_p1[1] == pygame.K_d and p1_coords[1] < 5):
				p1_coords[1] +=1
			#board[p1_coords[0]][p1_coords[1]] = 1
		except IndexError:
			print("Invalid move?")
	last_pressed_move_p1 = [0,0]

	#Player 2 movement
	if(last_pressed_move_p2[1] != 0):
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

	#Resolve positioning conflicts
	if(p1_coords[0] == p2_coords[0] and p1_coords[1] == p2_coords[1]):
		#print("p1 matches p2, " + str(p1_coords) + " " + str(p2_coords))
		#p1 moves into p2 while p2 stays in place
		if(p2_coords == p2_coords_old):
			#print("p2 new matches p2 old, " + str(p2_coords) + " " + str(p2_coords_old))
			p1_coords = p1_coords_old.copy()
		#p2 moves into p1 while p1 stays in place
		elif(p1_coords == p1_coords_old):
			p2_coords = p2_coords_old.copy()
		#p1 and p2 move into the same spot
		else:
			p1_coords == p1_coords_old.copy()
			p2_coords = p2_coords_old.copy()
		#Play boing sound effect and add game note to indicate conflict
		boing = pygame.mixer.Sound("boing.ogg")
		boing.play()
		gameNotes += "Both players went for the same space!"
		
	#Finalize Player position
	board[p1_coords[0]][p1_coords[1]] = 1 #Update player 1 location
	board[p2_coords[0]][p2_coords[1]] = 2 #Update player 2 location
#Main

#Initialize PyGame and audio
pygame.init()
pygame.mixer.init()

#Set up display
WIDTH, HEIGHT = 1000, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Couch Client")

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

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
gameUpdateTimer = 1500 #Get this value from user to see how long turns are
clock = pygame.time.Clock()
timer_value = gameUpdateTimer/1000
deltaTime = 0

#Custom Timer Event
#This should manage the logic every few seconds
TIMER_EVENT = pygame.USEREVENT + 1 #Custom event identifier
pygame.time.set_timer(TIMER_EVENT, gameUpdateTimer) #Trigger the timer event every 2 seconds

#General variables
 
last_pressed_move_p1= [0, 0]
p1_coords = [0, 0]
p1_health = 3

last_pressed_move_p2 = [0, 0]
p2_coords = [5, 5]
p2_health = 2

gameNotes=""

#Game Loop
running = True
while running:
#Update timer values
	deltaTime = clock.tick(120) / 1000
	timer_value -= deltaTime
	for event in pygame.event.get():

		if event.type == pygame.QUIT:
			running = False
		elif event.type == TIMER_EVENT: #Every 2 seconds, game action
			gameLogic()
			timer_value = gameUpdateTimer/1000
		elif event.type == pygame.KEYDOWN: #Get player movement
			if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
				last_pressed_move_p1.pop(0)
				last_pressed_move_p1.append(event.key)
			if event.key in [pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l]:
				last_pressed_move_p2.pop(0)
				last_pressed_move_p2.append(event.key)

	updateScreen() #Update graphics

pygame.quit()


