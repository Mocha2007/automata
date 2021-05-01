import pygame
from random import choice, randint
from json import load
from typing import List

ignore = {
	'color',
	'default',
	'note',
	'weight',
}

settings = load(open('settings.json', 'r'))
rule = load(open('rules/'+settings['rule']+'.json', 'r'))

class Cell:
	def __init__(self, state: int):
		self.state = state
	@property
	def default(self):
		return Cell(self.rule["default"])
	@property
	def rule(self):
		return rule["rule"][self.state]
	# special methods
	def __repr__(self):
		return "Cell(" + str(self.state) + ")"
	# methods
	def next_state(self, neighborhood): # neighborhood = List[Cell]
		for state_change in (v for k, v in self.rule.items() if k not in ignore):
			# pattern, new_state
			if pattern:
				if all(cell.state == tgt for tgt, cell in zip(state_change["pattern"], neighborhood) if 0 <= tgt):
					return Cell(state_change["new_state"])
			# states, counts, new_state
			else:
				count = sum(1 for c in neighborhood if c.state in state_change["states"])
				if count in state_change["counts"]:
					return Cell(state_change["new_state"])
		return self.default
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
		return [[cell.next_state(self.neighborhood(x, y)) for x, cell in enumerate(row)] for y, row in enumerate(self.data)]
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
		if rule["neighborhood"] == "moost":
			return self.n_moost(x, y)
		raise NotImplementedError()
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
		n = []
		for dy in range(-1, 2):
			for dx in range(-1, 2):
				if dx == 0 == dy:
					continue
				n.append(self.getCellAt(x+dx, y+dy))
		return n
	def n_moost(self, x: int, y: int):
		n = []
		for dy in range(-2, 3):
			for dx in range(-2, 3):
				if dx == 0 == dy:
					continue
				n.append(self.getCellAt(x+dx, y+dy))
		return n
	def n_vn(self, x: int, y: int):
		return [
			self.getCellAt(x, y-1),
			self.getCellAt(x-1, y),
			self.getCellAt(x+1, y),
			self.getCellAt(x, y+1),
		]
	def render(self):
		screen.fill((0, 0, 0))
		for i, row in enumerate(self.data):
			for j, cell in enumerate(row):
				color = cell.rule['color']
				if color == (0, 0, 0):
					continue
				rect = i*scale, j*scale, scale, scale
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

# pygame setup
pygame.init()
screen = pygame.display.set_mode((width*scale, height*scale))
pygame.display.set_caption(name)
refresh = pygame.display.flip

# make array
cell_map = Grid.random(width, height, settings['loop'])
i = 0

# display
while 1:
	print("tick", i)
	cell_map.render()
	cell_map.tick()
	controls()
	i += 1
