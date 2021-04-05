from sys import argv
from enum import IntEnum
import pygame
from pygame.locals import *

# time
PHYSICS_TIME_STEP = 1.0/100

# colors
COLOR_RED = pygame.Color('red')
COLOR_BLK = pygame.Color('black')
COLOR_GRY = pygame.Color(200, 200, 200)

class GameState(IntEnum):
	play = 0
	pause = 1

def handle_input(inputdata):
	# get current stuff
	movedir = inputdata.get_var(InputDataIndex.STICK)
	a_button = inputdata.get_var(InputDataIndex.A)
	b_button = inputdata.get_var(InputDataIndex.B)

class BasePlayer:
	def __init__(self):
		pass

class Player_Menu(BasePlayer):
	pass
	# just collection of menu state info -- different for battle/world?

# there will be two of these, since two player characters.
class Player_World(BasePlayer):
	pass

# will it be helpful to have two of these? Not sure
class Player_Battle(BasePlayer):
	def __init__(self):
		self.states = []

	def reset(self):
		pass

class BaseInputHandler:
	def __init__(self):
		pass
	def handle_input(player, inputdata):
		pass

class InputHandler_Menu(BaseInputHandler):
	def handle_input(self, player, inputdata):
		movedir = inputdata.get_var(InputDataIndex.STICK)
		confirm = inputdata.get_var(InputDataIndex.A)
		back = inputdata.get_var(InputDataIndex.B)

class InputHandler_World(BaseInputHandler):
	def handle_input(self, player, inputdata):
		movedir_prev = inputdata.get_var(InputDataIndex.STICK, 1)
		movedir = inputdata.get_var(InputDataIndex.STICK)
		# do something to handle diagonal inputs

		activate = inputdata.get_var(InputDataIndex.A)
		cancel = inputdata.get_var(InputDataIndex.B)

class InputHandler_Battle(BaseInputHandler):
	def handle_input(self, player, inputdata):
		movedir_prev = inputdata.get_var(InputDataIndex.STICK, 1)
		movedir = inputdata.get_var(InputDataIndex.STICK)
		# directions must be performed from neutral to do anything
		if (movedir >= 6 and movedir <= 8 and 
			(movedir_prev == InputMoveDir.NONE or movedir_prev == None)):
			movedir = InputMoveDir.DOWN
		elif (movedir >= 2 and movedir <= 4 and 
			(movedir_prev == InputMoveDir.NONE or movedir_prev == None)):
			movedir = InputMoveDir.UP
		else:
			movedir = InputMoveDir.NONE

		counter = inputdata.get_var(InputDataIndex.A)
		switch = inputdata.get_var(InputDataIndex.B)
		light_atk = inputdata.get_var(InputDataIndex.RT)
		heavy_atk = inputdata.get_var(InputDataIndex.LT)

		# handle state changes on player(s)


class InputMoveDir(IntEnum):
	NONE = 0
	RIGHT = 1
	UP_RIGHT = 2
	UP = 3
	UP_LEFT = 4
	LEFT = 5
	DOWN_LEFT = 6
	DOWN = 7
	DOWN_RIGHT = 8

class InputDataIndex(IntEnum):
	STICK = 0
	RT = 1
	LT = 2
	A = 3
	B = 4
	START = 5

MAXINPUTQUEUELEN = 5

class InputDataBuffer:
	def __init__(self):
		self.queuelength = 0

		self.vars = []

		# append in order of input data index enum
		for inputtype in InputDataIndex:
			self.vars.append([])

	''' 
	~ joystick event info ~
	JOYAXISMOTION     joy, axis, value
	JOYBALLMOTION     joy, ball, rel
	JOYHATMOTION      joy, hat, value
	JOYBUTTONUP       joy, button
	JOYBUTTONDOWN     joy, button
	'''

	def newinput(self, curr_input):
		if (self.queuelength == MAXINPUTQUEUELEN):
			for varlist in self.vars:
				varlist.pop(0)
		else:
			self.queuelength += 1

		# put in default values
		for varlist in self.vars:
			varlist.append(0)

		# movement
		moveinputvecx, moveinputvecy = (0, 0)

		# check out current input events
		for event in curr_input:
			# keyboard directions
			if (event.type == pygame.KEYDOWN):
				if event.key == pygame.K_LEFT:
					moveinputvecx += -1
				if event.key == pygame.K_RIGHT:
					moveinputvecx += 1
				if event.key == pygame.K_DOWN:
					moveinputvecy += 1
				if event.key == pygame.K_UP:
					moveinputvecy += -1

			# joystick directions
			if (event.type == pygame.JOYAXISMOTION):
				pass
			if (event.type == pygame.JOYHATMOTION):
				if event.hat == 0:
					# haven't checked whether y-value is good on this
					moveinputvecx, moveinputvecy = event.value

			if (event.type == pygame.KEYDOWN):
				# jumping
				if event.key == pygame.K_SPACE:
					self.set_var(InputDataIndex.A, True)

				# attacking
				if event.key == pygame.K_f:
					self.set_var(InputDataIndex.RT, True)
				if event.key == pygame.K_d:
					self.set_var(InputDataIndex.LT, True)

			# more joystick actions
			if (event.type == pygame.JOYBUTTONDOWN):
				# jumping
				if event.button == 0:
					self.set_var(InputDataIndex.A, True)

				# attacking
				if event.button == 1:
					self.set_var(InputDataIndex.RT, True)
				if event.button == 2:
					self.set_var(InputDataIndex.LT, True)

		# discrete thumbstick/keyboard directions
		if moveinputvecx > 0:
			slope = moveinputvecy/moveinputvecx
			if (slope < -2.41):
				self.set_var(InputDataIndex.STICK, InputMoveDir.DOWN)
			elif (slope > -2.41 and slope < -0.41):
				self.set_var(InputDataIndex.STICK, InputMoveDir.DOWN_RIGHT)
			elif (slope > -0.41 and slope < 0.41):
				self.set_var(InputDataIndex.STICK, InputMoveDir.RIGHT)
			elif (slope > 0.41 and slope < 2.41):
				self.set_var(InputDataIndex.STICK, InputMoveDir.UP_RIGHT)
			elif (slope > 2.41):
				self.set_var(InputDataIndex.STICK, InputMoveDir.UP)
		elif moveinputvecx < 0:
			slope = moveinputvecy/moveinputvecx
			if (slope < -2.41):
				self.set_var(InputDataIndex.STICK, InputMoveDir.UP)
			elif (slope > -2.41 and slope < -0.41):
				self.set_var(InputDataIndex.STICK, InputMoveDir.UP_LEFT)
			elif (slope > -0.41 and slope < 0.41):
				self.set_var(InputDataIndex.STICK, InputMoveDir.LEFT)
			elif (slope > 0.41 and slope < 2.41):
				self.set_var(InputDataIndex.STICK, InputMoveDir.DOWN_LEFT)
			elif (slope > 2.41):
				self.set_var(InputDataIndex.STICK, InputMoveDir.DOWN)
		else:
			if moveinputvecy > 0:
				self.set_var(InputDataIndex.STICK, InputMoveDir.DOWN)
			elif moveinputvecy < 0:
				self.set_var(InputDataIndex.STICK, InputMoveDir.UP)

	def set_var(self, var_idi, val):
		self.vars[var_idi][self.queuelength-1] = val
		return val

	def get_var(self, var_idi, queuei=0):
		if (self.queuelength-1-queuei < 0):
			return None
		result = self.vars[var_idi][self.queuelength-1-queuei]
		return result

def main(*args):
	pygame.init()

	# Set the width and height of the screen (width, height).
	screendim = (1024, 720) #use this value when move to C++
	flags = DOUBLEBUF
	window = pygame.display.set_mode(screendim, flags)
	window.set_alpha(None)
	pygame.display.set_caption("sekimon")

	# load fonts
	fontdir = '../data/fonts/ARI.ttf' #'./data/fonts/ARI.ttf'
	font = pygame.font.Font(fontdir, 32)

	done = False
	clock = pygame.time.Clock()

	# input stuff
	prev_input = []
	curr_input = [] # int list
	inputdata = InputDataBuffer()

	inputhandlers = [InputHandler_Menu(), InputHandler_World(), InputHandler_Battle()]
	curr_inputhandler = inputhandlers[2]

	num_joysticks = pygame.joystick.get_count()
	joystick = None
	# TODO: if-statement isn't working very well
	'''
	if num_joysticks > 0:
		joystick = pygame.joystick.Joystick(0) # 0 -> player 1
		joystick.init()	
	'''

	'''
	Probably going to be setting up some memory constructs around here
	'''

	#camera = Camera(geometry.get_tile2pos(*geometry.spawn), screendim)
	'''
	screen = window.subsurface(
		pygame.Rect(
			self.screenoffset,
			(self.width, self.height)
		)
	)
	'''
	screen = window # temporary while no camera code

	# timing stuff
	t = 0.0
	accum = 0.0

	# fps display smoother
	current_fps = 0

	while not done:
		frametime = clock.tick() # time passed in millisecondss
		accum += frametime/1000.0

		# display FPS
		current_fps = int(clock.get_fps()*0.6 + current_fps*0.4)
		#current_fps = int(clock.get_fps())
		fps_text = font.render(str(current_fps), 0, COLOR_RED)

		# poll input and update physics 100 times a second
		while (accum >= PHYSICS_TIME_STEP):
			accum -= PHYSICS_TIME_STEP
			t += PHYSICS_TIME_STEP

			# poll input, put in curr_input and prev_input
			events = pygame.event.get()

			# add values to curr_input on input
			for event in events:
				if event.type == pygame.QUIT:
					done = True
				elif (event.type == pygame.JOYBUTTONDOWN or
					event.type == pygame.KEYDOWN):
					curr_input.append(event)

				# if new axis/hat, then remove previous (if any) from curr_input
				elif (event.type == pygame.JOYAXISMOTION or
					event.type == pygame.JOYHATMOTION):
					for cev in curr_input:
						if (event.type == cev.type):
							curr_input.remove(cev)
					if (event.value != (0, 0)):
						curr_input.append(event)

			# remove values from curr_input on release of input
			for r_event in events:
				if (r_event.type == pygame.JOYBUTTONUP):
					for event in curr_input:
						if (event.type == pygame.JOYBUTTONDOWN and
							event.button == r_event.button):
							curr_input.remove(event)
							break
				elif (r_event.type == pygame.KEYUP):
					for event in curr_input:
						if (event.type == pygame.KEYDOWN and 
							event.key == r_event.key):
							curr_input.remove(event)
							break

			# skip update and quit if directed
			for event in curr_input:
				if (event.type == pygame.KEYDOWN and
					event.key == pygame.K_ESCAPE):
					done = True
				elif (event.type == pygame.JOYBUTTONDOWN and
					event.button == 6):
					done = True
			if (done):
				break

			inputdata.newinput(curr_input)
			curr_inputhandler.handle_input(1, inputdata)

			'''
			# update player state/forces by reading inputdata structure
			player_handleinput(player, inputdata)

			# physics and logic updates
			player_update(player.player)

			update_physicsbodies(worldstate.entities, worldstate.numentities, geometry)

			camera.update_pos(player.physics)
			'''

		# handle AI less often than physics?
		#megabrain.update()

		# start drawing
		screen.fill(COLOR_GRY)

		# get camera maptile range
		'''
		camerabounds = camera.get_maptilebounds(geometry)
		camera_minx = max(camerabounds.x-1, 0)
		camera_miny = max(camerabounds.y-1, 0)
		camera_maxx = min(camerabounds.x + camerabounds.width, geometry.width)
		camera_maxy = min(camerabounds.y + camerabounds.height, geometry.height)
		'''

		# draw sprites
		blitlist = []

		# draw background

		# draw middle ground sprites
		'''
		for j in range(camera_miny, camera_maxy):
			for i in range(camera_minx, camera_maxx):
				si = geometry.get_mgspriteindex(i, j)
				if (si >= 0):
					rect = Rect(
						geometry.get_tile2pos(i, j, offset=False), 
						(TILE_WIDTH*2, TILE_WIDTH*2)
					)
					rect = camera.get_screenrect(rect)
					blitlist.append(spritebatch.draw(si, rect))
		screen.blits(blitlist)
		blitlist.clear()
		'''

		# draw geometry sprites
		'''
		for j in range(camera_miny, camera_maxy):
			for i in range(camera_minx, camera_maxx):
				si = geometry.get_geospriteindex(i, j)
				if (si >= 0):
					rect = Rect(
						geometry.get_tile2pos(i, j, offset=False), 
						(TILE_WIDTH*2, TILE_WIDTH*2)
					)
					rect = camera.get_screenrect(rect)
					blitlist.append(spritebatch.draw(si, rect))
		screen.blits(blitlist)
		blitlist.clear()
		'''

		# draw player
		'''
		playerblit = player.draw(spritebatch, camera)
		screen.blit(*playerblit)
		'''

		screen.blit(fps_text, (1, 1))
		
		pygame.display.flip()

	pygame.quit()

if __name__=='__main__':
	main(argv[1:])