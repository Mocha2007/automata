import pygame
from random import choice
from json import load
#from time import time

ignore = {
	'color',
	'default',
	'note',
	'weight',
}

settings = load(open('settings.json', 'r'))
rule = load(open('rules/'+settings['rule']+'.json', 'r'))


def r_state() -> int:
	if 'weighted' in rule['tags']:
		array = []
		for i, state in enumerate(rule['rule']):
			array += [i]*state['weight']
		return choice(array)
	return choice(range(len(rule['rule'])))


def make_row() -> list:
	return [r_state() for _ in range(width)]


def make_map() -> list:
	return [make_row() for _ in range(height)]


def clone_map(m: list) -> list:
	return [list(row) for row in m]


def coord_exists(coord: (int, int)) -> bool:
	x, y = coord
	return (0 <= x < width) and (0 <= y < height)


def moore(m: list, coord: (int, int)) -> list:
	neighbors = []
	min_y, max_y = max(0, coord[1]-1), min(height, coord[1]+2)
	# above row
	if 0 < coord[0]:
		neighbors += m[coord[0]-1][min_y:max_y]
	# middle row
	neighbors += m[coord[0]][min_y:max_y:2]
	# below row
	if coord[0]+1 < width:
		neighbors += m[coord[0]+1][min_y:max_y]
	return neighbors


def moore_loop(m: list, coord: (int, int)) -> list:
	neighbors = [
		# UL
		m[coord[0]-1][coord[1]-1],
		# U
		m[coord[0]-1][coord[1]],
		# UR
		m[coord[0]-1][coord[1]+1] if coord[1]+1 < len(m[0]) else m[coord[0]-1][0],
		# L
		m[coord[0]][coord[1]-1],
		# R
		m[coord[0]][coord[1]+1] if coord[1]+1 < len(m[0]) else m[coord[0]][0],
		# DL
		m[coord[0]+1][coord[1]-1] if coord[0]+1 < len(m) else m[0][coord[1]-1],
		# D
		m[coord[0]+1][coord[1]] if coord[0]+1 < len(m) else m[0][coord[1]]
	]
	# DR
	# can we go right?
	if coord[1]+1 < len(m[0]):
		# can we go down?
		if coord[0]+1 < len(m):
			dr = m[coord[0]+1][coord[1]+1]
		else:
			dr = m[0][coord[1]+1]
	else:
		# can we go down?
		if coord[0]+1 < len(m):
			dr = m[coord[0]+1][0]
		else:
			dr = m[0][0]
	return neighbors + [dr]


def von_neumann_loop(m: list, coord: (int, int)) -> list:
	neighbors = [
		# U
		m[coord[0]-1][coord[1]],
		# L
		m[coord[0]][coord[1]-1],
		# R
		m[coord[0]][coord[1]+1] if coord[1]+1 < len(m[0]) else m[coord[0]][0],
		# D
		m[coord[0]+1][coord[1]] if coord[0]+1 < len(m) else m[0][coord[1]]
	]
	return neighbors


def count_states(array: list, states: set) -> int:
	return sum(1 for item in array if item in states)


def check_pattern(array: list, pattern: list) -> bool: # negatives represent wildcards
	return False not in [(array[i] == item) for i, item in enumerate(pattern) if 0 <= item]


def time_step(m: list) -> list:
	#TIME_DEBUG = time()
	new_m = clone_map(m)
	for i, row in enumerate(m):
		for j, cell in enumerate(row):
			this_rule_dict = rule['rule'][cell]
			if rule['neighborhood'] == 'moore':
				neighborhood = moore_loop(m, (i, j)) if settings['loop'] else moore(m, (i, j))
			elif rule['neighborhood'] == 'von neumann':
				neighborhood = von_neumann_loop(m, (i, j)) if settings['loop'] else von_neumann(m, (i, j))
			next = this_rule_dict['default']
			# check each rule for satisfaction
			for name, data in this_rule_dict.items():
				if name in ignore:
					continue
				if 'patterns' in rule['tags']:
					if check_pattern(neighborhood, data['pattern']):
						next = data['new_state']
						break
				elif count_states(neighborhood, data['states']) in data['counts']:
					next = data['new_state']
					break
			new_m[i][j] = next
	#print(int(1000*(time() - TIME_DEBUG)))
	return new_m


def show_map(m: list):
	screen.fill((0, 0, 0))
	for i, row in enumerate(m):
		for j, cell in enumerate(row):
			# screen.set_at((i, j), state_map[cell])
			if rule['rule'][cell]['color'] == (0, 0, 0):
				continue
			rect = i*scale, j*scale, scale, scale
			pygame.draw.rect(screen, rule['rule'][cell]['color'], rect)
	refresh()


def controls():
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			pygame.display.quit()
			pygame.quit()
			exit()


width, height = settings['size']
scale = settings['scale']
name = rule['name']

# pygame setup
pygame.init()
screen = pygame.display.set_mode((width*scale, height*scale))
pygame.display.set_caption(name)
refresh = pygame.display.flip

# make array
cell_map = make_map()

# display
while 1:
	show_map(cell_map)
	cell_map = time_step(cell_map)
	controls()
