'''

# TODO:

	* commands to add:
		- Time of animation
		- change/load entity (texture data)
		- repeat on/off
		- like id=<partial animation id>, list similarly named ids

	* actually display the animation both in
	edit mode and play mode

'''

# namespaces
import pygame
import content

# utilities
from sys import argv, getsizeof
from enum import IntEnum

# classes and constants
from pygame.locals import *

# time
PHYSICS_TIME_STEP = 1.0/100

# constants
MAXINPUTQUEUELEN = 10
ALLBONEANIMIDS = content.get_allboneanimids()

# colors
COLOR_LGRY = pygame.Color(125, 125, 125)
COLOR_DRED = pygame.Color(80, 0, 0)
COLOR_LRED = pygame.Color(250, 100, 100)
COLOR_LGRN = pygame.Color(100, 250, 100)
COLOR_LBLU = pygame.Color(100, 100, 250)
COLOR_GRY = pygame.Color(200, 200, 200)
COLOR_RED = pygame.Color('red')
COLOR_BLK = pygame.Color('black')

def sign(n):
	if (n < 0):
		return -1
	elif (n > 0):
		return 1
	else:
		return 0

class Rect:
	def __init__(self, pos, dim):
		self.x = pos[0]
		self.y = pos[1]
		self.width = dim[0]
		self.height = dim[1]

	def copy(self):
		result = Rect((self.x, self.y), (self.width, self.height))
		return result

	def print(self):
		print((self.x, self.y), (self.width, self.height))

	def get_dim(self):
		result = (self.width, self.height)
		return result

	def move(self, dp):
		self.x += dp[0]
		self.y += dp[1]
		return self

	def get_center(self):
		result = (self.x + self.width/2.0, self.y + self.height/2.0)
		return result

	def get_verts(self):
		topleft = (self.x, self.y)
		topright = (self.x+self.width, self.y)
		botleft = (self.x, self.y+self.height)
		botright = (self.x+self.width, self.y+self.height)

		return (topleft, topright, botleft, botright)

	def get_pyrect(self):
		result = pygame.Rect((int(self.x), int(self.y)), (int(self.width), int(self.height)))
		return result

	def contains_point(self, point):
		'''
		using strictly gt/lt on the left and top edges so that
		collision detection doesn't think it's colliding down
		when rubbing a wall on the left. 
		Easy fix and no discernable difference right now.
		'''
		result = (
			point[0] > self.x and
			point[0] < self.x+self.width and
			point[1] > self.y and
			point[1] < self.y+self.height
		)
		return result

#### TODO: ALL COMMANDS HERE ##########################################################
COMMANDS_DICT = {}

def command_help(kargs):
	commands = []
	commands.append(('[ command ]', '[ info ]'))

	for entry in content._EDIT_DATA['commands']:
		commands.append((entry['prompt'], entry['info']))

	maxplen = 1
	for line in commands:
		plen = len(line[0])
		if (plen > maxplen):
			maxplen = plen

	header = '~'*10 + ' Commands ' + '~'*10
	print(header)
	for lineindex in range(len(commands)):
		if ((lineindex+2)%3==0):
			print()
		prompt, info = commands[lineindex]
		numspaces = maxplen - len(prompt) + 3
		print(' %s'%prompt + ' '*numspaces + '\t' + '%s'%info)
	print('~'*len(header))
	print()
COMMANDS_DICT['help'] = command_help

def command_stateinfo(kargs):
	kargs['stateinfo'].print()
COMMANDS_DICT['state'] = command_stateinfo

def command_load(kargs):
	animid = kargs['animid']
	stateinfo = kargs['stateinfo']
	if (animid in ALLBONEANIMIDS):
		print('Loading "%s".' % animid)
		stateinfo.curr_animationid = animid
		stateinfo.curr_frame = 0
		stateinfo.curr_bone = content.get_bonesinanim(animid)[0]
	else:
		print('"%s" not recognized from list of animation ids.')
COMMANDS_DICT['load'] = command_load

def command_save():
	# save values here
	'''
	data[animation.name] = adata
	filename = './data/graphics/skellyanimationdata.json'
	os.remove(filename)
	with open(filename, 'w') as f:
		json.dump(data, f, indent=4)
	print('New animation saved.')
	'''

def command_addframe():
	pass

### TODO: ALL HOTKEYS HERE #######################################################

def hotkey_help():
	hotkeys = []
	hotkeys.append(('[ key ]', '[ info ]'))

	for entry in content._EDIT_DATA['hotkeys']:
		hotkeys.append((entry['key'], entry['info']))

	maxplen = 1
	for line in hotkeys:
		plen = len(line[0])
		if (plen > maxplen):
			maxplen = plen

	header = '~'*10 + ' Hotkeys ' + '~'*10
	print(header)
	for lineindex in range(len(hotkeys)):
		if ((lineindex+2)%3==0):
			print()
		prompt, info = hotkeys[lineindex]
		numspaces = maxplen - len(prompt) + 3
		print(' %s'%prompt + ' '*numspaces + '\t' + '%s'%info)

	command_help(None)

def hotkey_switchmode(stateinfo):
	if (stateinfo.editmode):
		print('Leaving edit mode, playing animation.')
	else:
		print('Returning to edit mode.')
	stateinfo.editmode = not stateinfo.editmode

def hotkey_command(stateinfo):
	done_with_prompt = False
	print('Command dialogue opened.')
	print('Enter "quit" to exit. Enter "help" for a list of commands.')
	while (not done_with_prompt):
		userinput = input('>> ')
		if (userinput == 'quit'):
			done_with_prompt = True
		else:
			splinput = userinput.split(' ')
			command = splinput[0]
			if (command in COMMANDS_DICT):
				kargs = {'stateinfo' : stateinfo}
				if (len(splinput) > 1):
					argslist = [item.split('=') for item in splinput[1:]]
					for arg in argslist:
						assert(arg != 'stateinfo')
						kargs[arg[0]] = arg[1]
				COMMANDS_DICT[command](kargs)
			else:
				print('Command not recognized. Enter "help" for a list of commands.')

class InputHandler:
	def __init__(self):
		pass

	def handle_input(self, inputdata, stateinfo):
		result = stateinfo.copy()

		movedir_prev = inputdata.get_var(InputDataIndex.MOVEDIR, 1)
		movedir = inputdata.get_var(InputDataIndex.MOVEDIR)

		# context sensitive move code
		if (stateinfo.editmode == True):
			pass

		# only count fresh inputs for these actions
		fresh_actions = [
			InputDataIndex.HELP,
			InputDataIndex.PLAY_EDIT_SWITCH,
			InputDataIndex.COMMAND
		]

		fresh_action_procs = {}
		for action in fresh_actions:
			proc = (
				inputdata.get_var(action) and 
				not inputdata.get_var(action, 1)
			)
			fresh_action_procs[action] = proc

		# map actions to functions here
		if (fresh_action_procs[InputDataIndex.HELP]):
			hotkey_help()
		elif (stateinfo.editmode == True): 
			# edit mode
			if (fresh_action_procs[InputDataIndex.PLAY_EDIT_SWITCH]):
				hotkey_switchmode(result)
			elif (fresh_action_procs[InputDataIndex.COMMAND]):
				hotkey_command(result)
		else: 
			# play mode
			if (fresh_action_procs[InputDataIndex.PLAY_EDIT_SWITCH]):
				hotkey_switchmode(result)

		return result


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

# TODO: remember to update button mapping in InputDataBuffer
class InputDataIndex(IntEnum):
	HELP = 0
	COMMAND = 1
	PLAY_EDIT_SWITCH = 2
	MOVEDIR = 3

MAXINPUTQUEUELEN = 5

class InputDataBuffer:
	def __init__(self):
		self.queuelength = 0

		self.vars = []

		# append in order of input data index enum
		for inputtype in InputDataIndex:
			self.vars.append([])

		self.button_mapping = {
			pygame.K_h : InputDataIndex.HELP,
			pygame.K_SPACE : InputDataIndex.PLAY_EDIT_SWITCH,
			pygame.K_BACKQUOTE : InputDataIndex.COMMAND
		}

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

			if (event.type == pygame.KEYDOWN):
				if event.key in self.button_mapping:
					self.set_var(self.button_mapping[event.key], True)

		# discrete thumbstick/keyboard directions
		if moveinputvecx > 0:
			slope = moveinputvecy/moveinputvecx
			if (slope < -2.41):
				self.set_var(InputDataIndex.MOVEDIR, InputMoveDir.DOWN)
			elif (slope > -2.41 and slope < -0.41):
				self.set_var(InputDataIndex.MOVEDIR, InputMoveDir.DOWN_RIGHT)
			elif (slope > -0.41 and slope < 0.41):
				self.set_var(InputDataIndex.MOVEDIR, InputMoveDir.RIGHT)
			elif (slope > 0.41 and slope < 2.41):
				self.set_var(InputDataIndex.MOVEDIR, InputMoveDir.UP_RIGHT)
			elif (slope > 2.41):
				self.set_var(InputDataIndex.MOVEDIR, InputMoveDir.UP)
		elif moveinputvecx < 0:
			slope = moveinputvecy/moveinputvecx
			if (slope < -2.41):
				self.set_var(InputDataIndex.MOVEDIR, InputMoveDir.UP)
			elif (slope > -2.41 and slope < -0.41):
				self.set_var(InputDataIndex.MOVEDIR, InputMoveDir.UP_LEFT)
			elif (slope > -0.41 and slope < 0.41):
				self.set_var(InputDataIndex.MOVEDIR, InputMoveDir.LEFT)
			elif (slope > 0.41 and slope < 2.41):
				self.set_var(InputDataIndex.MOVEDIR, InputMoveDir.DOWN_LEFT)
			elif (slope > 2.41):
				self.set_var(InputDataIndex.MOVEDIR, InputMoveDir.DOWN)
		else:
			if moveinputvecy > 0:
				self.set_var(InputDataIndex.MOVEDIR, InputMoveDir.DOWN)
			elif moveinputvecy < 0:
				self.set_var(InputDataIndex.MOVEDIR, InputMoveDir.UP)

	def set_var(self, var_idi, val):
		self.vars[var_idi][self.queuelength-1] = val
		return val

	def get_var(self, var_idi, queuei=0):
		if (self.queuelength-1-queuei < 0):
			return None
		result = self.vars[var_idi][self.queuelength-1-queuei]
		return result

class SpriteBatch:
	def draw_rect(image, rect, fliphorz=False):
		scale = rect.get_dim()
		image = pygame.transform.scale(image, scale)

		result = None

		if (fliphorz):
			image = pygame.transform.flip(image, True, False)
			result = (image, rect.get_pyrect())
		else:
			result = (image, rect.get_pyrect())

		return result

	def draw_boneframe(image, boneframe, scale=1.0, fliphorz=False):
		pos = boneframe.pos
		degrees = boneframe.rot

		# scale image to the rect (already zoomed)
		image = pygame.transform.scale(image, scale)

		# rotate image
		image = pygame.transform.rotate(image, degrees)

		# create rect from new scaled & rotated image
		rect = Rect(pos, image.get_size())

		result = None
		if (fliphorz):
			image = pygame.transform.flip(image, True, False)
			result = (image, rect.get_pyrect())
		else:
			result = (image, rect.get_pyrect())

		return result

	def draw_isrot(image, isrot, fliphorz=False):
		pos, scale, degrees = isrot

		# scale image to the rect (already zoomed)
		image = pygame.transform.scale(image, scale)

		# rotate image
		image = pygame.transform.rotate(image, degrees)

		# create rect from new scaled & rotated image
		rect = Rect(pos, image.get_size())

		result = None
		if (fliphorz):
			image = pygame.transform.flip(image, True, False)
			result = (image, rect.get_pyrect())
		else:
			result = (image, rect.get_pyrect())

		return result

class EditorState:
	def __init__(self):
		self.editmode = True
		self.curr_animationid = ''
		self.curr_frame = -1
		self.curr_bone = ''
		self.curr_entityid = ''
		self.animtime_ms = 1000

	def set(self, newinfo):
		result = None
		if (newinfo.curr_animationid != self.curr_animationid):
			result = content.get_animationdata(newinfo.curr_animationid)

		self.editmode = newinfo.editmode
		self.curr_animationid = newinfo.curr_animationid
		self.curr_frame = newinfo.curr_frame
		self.curr_bone = newinfo.curr_bone
		self.curr_entityid = newinfo.curr_entityid
		self.animtime_ms = newinfo.animtime_ms

		return result

	def print(self):
		header = '~'*6 + ' STATEINFO: ' + '~'*12
		print(header)

		print(' editmode:\t%s' % self.editmode)
		print(' anim id:\t%s' % self.curr_animationid)
		print(' frame:\t\t%d' % self.curr_frame)
		print(' bone:\t\t%s' % self.curr_bone)
		print(' entity:\t\t%s' % self.curr_entityid)
		print(' time:\t\t%d ms' % self.animtime_ms)
		print('~'*len(header))

	def copy(self):
		newinfo = EditorState()
		newinfo.set(self)
		return newinfo

def print_startmessage():
	print()
	print("Starting in editor mode.")
	hotkey_help()
	print()

def main():
	pygame.init()

	# screen stuff
	screendim = (800, 600)
	screen = pygame.display.set_mode(screendim)
	pygame.display.set_caption("animator")

	print_startmessage()

	# state info
	stateinfo = EditorState()
	done = False

	# load data
	bam = content.BoneAnimationManager(editor=True)

	# input stuff
	prev_input = []
	curr_input = [] # int list
	inputdata = InputDataBuffer()

	inputhandler = InputHandler()

	# load fonts
	font = pygame.font.Font('../data/fonts/ARI.ttf', 32)

	# editor stuff
	current_adata = None # this will be a deep copy dict into _WORKING_BA_DATA

	# timing stuff
	clock = pygame.time.Clock()
	t = 0.0
	accum = 0.0

	# fps display smoother
	current_fps = 0

	while not done:
		#frametime = clock.tick(60)
		frametime = clock.tick() # time passed in millisecondss
		accum += frametime/1000.0

		# display FPS
		current_fps = int(clock.get_fps()*0.9 + current_fps*0.1)
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
				elif (event.type == pygame.KEYDOWN or
					event.type == pygame.JOYBUTTONDOWN):
					curr_input.append(event)

			# remove values from curr_input on release of input
			for r_event in events:
				if (r_event.type == pygame.KEYUP):
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
			if (done):
				break

			inputdata.newinput(curr_input)

			inputresult = inputhandler.handle_input(inputdata, stateinfo)
			newanimationdata = stateinfo.set(inputresult)
			if (newanimationdata != None):
				current_adata = newanimationdata

		# start drawing
		screen.fill(COLOR_GRY)

		# draw sprites
		blitlist = []

		if (stateinfo.editmode):
			# draw frame
			#blitimg = SpriteBatch.draw_boneframe()
			#blitlist.append(blitimg)
			screen.blits(blitlist)
			blitlist.clear()
		else:
			# play animation
			pass

		# display fps
		screen.blit(fps_text, (1, 1))
		
		# display screen
		pygame.display.flip()

	pygame.quit()

if __name__=='__main__':
	main()