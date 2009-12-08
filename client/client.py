import pygame

from graphics import init_fonts
from table import Table
from gui import GuiManager, PlayerBox
from directions import direction_up, direction_down, direction_left, direction_right
from states import ConnectingState, TestState

winds = [ "WE", "WS", "WW", "WN" ]


class Mahjong:

	def __init__(self):
		self.table = Table()
		self.gui = GuiManager()
		self.player_boxes = []
		self.state = None
		self.quit_flag = False
		self.my_wind = None
		self.round_wind = None
		self.protocol = None

	def set_state(self, state):
		if self.state:
			self.state.leave_state()
		self.state = state
		if state:
			state.enter_state()

	def quit(self):
		self.quit_flag = True

	def process_events(self):
		for ev in pygame.event.get():
			if ev.type == pygame.QUIT:
				self.quit()
			if ev.type == pygame.MOUSEBUTTONDOWN:
				self.gui.button_down(ev.button, ev.pos)
				if ev.button == 1:
					self.table.on_left_button_down(ev.pos)
			if ev.type == pygame.MOUSEBUTTONUP:
				self.gui.button_up(ev.button, ev.pos)
		return True

	def draw_all(self):
		screen = pygame.display.get_surface()
		self.table.draw()
		self.gui.draw(screen)
		pygame.display.flip()


	def run(self):
		clock = pygame.time.Clock()
		while not self.quit_flag:
			self.process_events()
			self.draw_all()
			self.state.tick()
			self.gui.tick()
			clock.tick(10)

	def init_player_boxes(self, names):
		self.player_boxes = [
			PlayerBox((50, 700), names[0], 25000, direction_up, (0,-80)),
			PlayerBox((954, 300), names[1], 25000, direction_left, (-210, 0)), 
			PlayerBox((700, 0), names[2], 25000, direction_up, (0,80)),
			PlayerBox((0, 300), names[3], 25000, direction_right, (80,0)) ]
		for widget in self.player_boxes:
			self.gui.add_widget(widget)

	def select_none(self):
		for box in self.player_boxes:
			box.set_selection(False)

	def select_my_box(self):
		self.player_boxes[0].set_selection(True)

	def select_box(self, wind):
		self.player_boxes[self.player_id_by_wind(wind)].set_selection(True)

	def add_dropped_tile(self, wind, tile_name):
		self.table.new_tile_to_dropzone(self.player_id_by_wind(wind), tile_name)

	def player_id_by_wind(self, wind):
		my_id = winds.index(self.my_wind)
		for i in xrange(4):
			if winds[(my_id + i) % 4] == wind:
				return i

	def create_shoutbox(self, wind, text):
		return self.player_boxes[self.player_id_by_wind(wind)].create_shoutbox(text)

	def get_player_name(self, wind):
		return self.player_boxes[self.player_id_by_wind(wind)].player_name

	def set_protocol(self, protocol):
		self.protocol = protocol

	def get_username(self):
		import sys
		if len(sys.argv) >= 2:
			return sys.argv[1]
		else:
			return "Mahjong player"

	def get_version_string(self):
		return "0.0"

	def process_network_message(self, message):
		print "Unknown message: " + repr(message)

	def arrange_hand(self):
		self.table.arrange_hand()


def main_init():
	pygame.display.init()
	pygame.font.init()
	init_fonts()
	pygame.display.set_mode((1024,768), pygame.DOUBLEBUF, 32)
	pygame.display.set_caption("RMahjong")

main_init()
mahjong = Mahjong()
mahjong.set_state(ConnectingState(mahjong))
#mahjong.set_state(TestState(mahjong))
mahjong.run()
pygame.quit()
