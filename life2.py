import pygame
from cProfile import run as profile
from json import load
from random import choice, randint
from sys import argv
from typing import List

ignore = {
	'color',
	'default',
	'note',
	'weight',
}

settings = load(open('settings.json', 'r'))
if 1 < len(argv):
	rule = load(open(argv[1], 'r'))
else:
	rule = load(open('rules/'+settings['rule']+'.json', 'r'))

class Cell:
	def __init__(self, state: int):
		self.state = state
		self.rule = rule["rule"][self.state]
		self.state_changes = (v for k, v in self.rule.items() if k not in ignore)
	# special methods
	def __repr__(self):
		return "Cell(" + str(self.state) + ")"
	# methods
	def next_state(self, neighborhood): # neighborhood = List[Cell]
		for state_change in self.state_changes:
			# pattern, new_state
			if pattern:
				if all(cell.state == tgt for tgt, cell in zip(state_change["pattern"], neighborhood) if 0 <= tgt):
					return Cell(state_change["new_state"])
			# states, counts, new_state
			else:
				m = max(state_change["counts"])
				s = 0
				for c in neighborhood:
					if c.state in state_change["states"]:
						s += 1
					if m < s: # using this instead of list comprehension results in a ~8 ms savings per Grid.tick
						break
				else:
					if s in state_change["counts"]:
						return Cell(state_change["new_state"])
		return Cell(self.rule["default"])
	@staticmethod
	def random(): # -> Cell
		return Cell.weighted_random() if weighted else Cell(randint(0, types-1))
	@staticmethod
	def weighted_random(): # -> Cell
		deck = []
		for i in range(0, types):
			deck += [i] * rule["rule"][i]["weight"]
		return Cell(choice(deck))
# static vars
Cell.null = Cell(0)

class Grid:
	def __init__(self, width: int, height: int, loop: bool, data: List[List[Cell]]):
		self.width = width
		self.height = height
		self.loop = loop
		self.data = data
	@property
	def next_state(self):
		return [[c.next_state(self.neighborhood(x, y)) for x, c in enumerate(r)] for y, r in enumerate(self.data)]
	def getCellAt(self, x: int, y: int):
		if x < 0 or self.width <= x:
			if self.loop:
				x %= self.width
			else:
				return Cell.null
		if y < 0 or self.height <= y:
			if self.loop:
				y %= self.height
			else:
				return Cell.null
		return self.data[y][x]
	def neighborhood(self, x: int, y: int):
		# sort by likelihood of choosing
		if rule["neighborhood"] == "moore":
			return self.n_moore(x, y)
		if rule["neighborhood"] == "hex":
			return self.n_hex(x, y)
		if rule["neighborhood"] in {"vn", "von neumann"}:
			return self.n_vn(x, y)
		if rule["neighborhood"] == "elementary":
			return self.n_elementary(x, y)
		if rule["neighborhood"] == "moost":
			return self.n_moost(x, y)
		raise NotImplementedError()
	def n_elementary(self, x: int, y: int):
		# top three cells
		return [
			self.getCellAt(x-1, y-1),
			self.getCellAt(x, y-1),
			self.getCellAt(x+1, y-1),
		]
	def n_hex(self, x: int, y: int):
		"""
		XX
		XOX
		 XX
		"""
		return [
			self.getCellAt(x-1, y-1),
			self.getCellAt(x, y-1),
			self.getCellAt(x-1, y),
			self.getCellAt(x+1, y),
			self.getCellAt(x, y+1),
			self.getCellAt(x+1, y+1),
		]
	def n_moore(self, x: int, y: int):
		return [self.getCellAt(x+dx, y+dy) for dx in range(-1, 2) for dy in range(-1, 2) if not dx == 0 == dy]
	def n_moost(self, x: int, y: int):
		return [self.getCellAt(x+dx, y+dy) for dx in range(-2, 3) for dy in range(-2, 3) if not dx == 0 == dy]
	def n_vn(self, x: int, y: int):
		return [
			self.getCellAt(x, y-1), # up
			self.getCellAt(x-1, y), # left
			self.getCellAt(x+1, y), # right
			self.getCellAt(x, y+1), # down
		]
	def render(self):
		for i, row in enumerate(self.data):
			for j, cell in enumerate(row):
				color = cell.rule['color']
				if tuple(color) == screen.get_at((j*scale, i*scale))[:3]:
					continue
				rect = j*scale, i*scale, scale, scale
				pygame.draw.rect(screen, color, rect)
		refresh()
	def tick(self):
		self.data = self.next_state
	@staticmethod
	def random(width: int, height: int, loop: bool): # -> Grid
		return Grid(width, height, loop, [[Cell.random() for __ in range(width)] for _ in range(height)])

def controls():
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			pygame.display.quit()
			pygame.quit()
			exit()

# useful constants
width, height = settings['size']
scale = settings['scale']
name = rule['name']
types = len(rule['rule'])
pattern = "patterns" in rule["tags"]
weighted = "weighted" in rule["tags"]
debug = "debug" in argv

# pygame setup
pygame.init()
screen = pygame.display.set_mode((width*scale, height*scale))
pygame.display.set_caption(name)
refresh = pygame.display.flip

# make array
cell_map = Grid.random(width, height, settings['loop'])

# display
while 1:
	if debug:
		profile('cell_map.render()')
		profile('cell_map.tick()')
		input()
		break
	else:
		cell_map.render()
		cell_map.tick()
	controls()