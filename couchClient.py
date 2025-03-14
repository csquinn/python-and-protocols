import pygame
import random

#functions

#Function to render the grid
def drawGrid():
	pygame.draw.rect(screen, BLACK, (195, 95, 610, 610))
	for x in [200, 300, 400, 500, 600, 700]:
		for y in [100, 200, 300, 400, 500, 600]:
			pygame.draw.rect(screen, WHITE, (x+5, y+5, 90, 90))

#Function to render players and attacks
def drawActors():
	gridX = [200, 300, 400, 500, 600, 700]
	gridY = [100, 200, 300, 400, 500, 600]

	for y, outerList in enumerate(board):
		for x, element in enumerate(outerList):
			if element == 1:
				pygame.draw.circle(screen, BLUE, (gridX[x]+50, gridY[y]+50), 40)
			elif element == 2:
				pygame.draw.circle(screen, GREEN, (gridX[x]+50, gridY[y]+50), 40)
			elif element == 3:
				pygame.draw.polygon(screen, RED, ((gridX[x]+10, gridY[y]+90), (gridX[x]+90, gridY[y]+90), (gridX[x]+50, gridY[y]+10))) 
#Function to draw graphics to screen
def updateScreen():
	screen.fill(WHITE)

	#Render the grid
	drawGrid()

	#Render the actors
	drawActors()

	pygame.display.flip()

def gameLogic():
	#Reset board
	board = [[0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0], 
		[0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0]]

	#Player 1 movement
	if(last_pressed_move_p1 != None):
		try:
			if(last_pressed_move_p1 == pygame.K_w):
				p1_coords[1] -=1
			elif(last_pressed_move_p1 == pygame.K_d):
				p1_coord[0] +=1
		except:
			print("Invalid move?")
	board[p1_coord[0]][p1_coord[1]] = 1 #Update player 1 location
	last_pressed_move_p1 = None



#Main

#Initialize PyGame
pygame.init()

#Set up display
WIDTH, HEIGHT = 1000, 800
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
board = [[0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0],
	[0, 0, 0, 0, 0, 0]]

#Clock
clock = pygame.time.Clock()

#Custom Timer Event
#This should manage the logic every few seconds
TIMER_EVENT = pygame.USEREVENT + 1 #Custom event identifier
pygame.time.set_timer(TIMER_EVENT, 2000) #Trigger the timer event every 2 seconds

#General variables
last_pressed_move_p1 = None
p1_coords = [0, 0]
#Game Loop
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == TIMER_EVENT: #Every 2 seconds, game action
			gameLogic()
		elif event.type == pygame.KEYDOWN: #Get player movement
			if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
				last_pressed_move_p1 = event.key

	updateScreen() #Update graphics

pygame.quit()


