from sys import argv
from enum import IntEnum, unique
from battleforms import BATTLEFORM_DICT, BattleFormEnum

class GameState(IntEnum):
	mainmenu = 0
	battle_input = 1
	battle_resolve = 2

class BattleMenu(IntEnum):
	firstmenu = 0
	attackselect = 1
	targetselect = 2
	spiritselect_swap = 3
	spiritselect_faint = 4

class BattleMenuState():
	def __init__(self, name):
		self.name = name
		self.printlines = []
		self.args = {}

	def setarg(self, argname, argval):
		self.args[argname] = argval

	def print_state(self):
		for line in self.printlines:
			if ('$' in line):
				sline = line.split('$')
				for i in range(1, len(sline), 2):
					sline[i] = self.args[sline[i]]
				print(''.join(sline))
			else:
				print(line)

BATTLEMENUSTATES = {}

class Battle_Style(IntEnum):
	test = 0

class AttackMove:
	def __init__(self):
		self.form = 0
		self.effect = 0
		self.timingpair = (0, 0)

	def usemove(self, attacker, targets):
		self.effect.apply(attacker, targets)

def print_help():
	print('help:\topen this menu')
	print('quit:\texit the game')
	print('menu:\treturn to main menu')

def print_mainmenuoptions():
	print('enter "battle" to start the battle.')
	print('enter "menu" to return to this menu at any time.')
	print('YOUR TEAM:')
	print()
	print('ENEMY TEAM:')
	print()

def startbattle():
	pass

def main(*args):
	print('args: ', args)
	print('enter "help" for help')
	print()

	'''
	for key in BATTLEFORM_DICT:
		print(key.value, str(BATTLEFORM_DICT[key]))
	'''

	current_gs = GameState.mainmenu
	firstupdateings = False
	done = False

	# main menu vars?

	# battle vars
	battle_units = []
	active_unit = 0
	numofplayerunits = 1

	while (not done):
		player_input = input('>> ')
		if (player_input == 'help'):
			print_help()
		elif (player_input == 'quit'):
			done = True
			break
		elif (player_input == 'menu'):
			current_gs = GameState.mainmenu
			firstupdateings = True
			continue

		messages = [] # just strings? Message object?

		if (current_gs == GameState.mainmenu):
			if (firstupdateings):
				firstupdateings = False
				print_mainmenuoptions()

			if (player_input == 'battle'):
				current_gs = GameState.battle_input
				firstupdateings = True

		elif (current_gs == GameState.battle_input):
			if (firstupdateings):
				firstupdateings = False
				# print current spirit stats, your team and enemy team

			# just allow fight for now
			# pick a move
			# pick a target(s)
			# save the move and targets to the unit to be resolved
			active_unit += 1
			if (active_unit > numofplayerunits-1):
				current_gs = GameState.battle_resolve
				firstupdateings = True
				active_unit = 0 # reset for next battle_input phase
			
		elif (current_gs == GameState.battle_resolve):
			if (firstupdateings):
				firstupdateings = False

			# sort units by priority and speed
			# resolve their attacks:
			# battle_units[0].moves.get(movenum).usemove(battle_units[0], [targets])
			for unit in battle_units:
				pass

		# print messages here
		for mess in messages:
			print(mess)
			print()

if __name__=='__main__':
	main(argv[1:])