# Copyright (C) 2009 Stanislav Bohm
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, see
# <http://www.gnu.org/licenses/>.


import pygame
import logging
import gettext

from graphics import init_fonts, init_opengl, enable2d, disable2d
from table import Table, winds
from gui import GuiManager, PlayerBox, TextWidget, ContainerWidget, TextureWidget
from directions import direction_up, direction_down, direction_left, direction_right
from states import ConnectingState, TestState, TestTableState
from menu import MainMenuState

class Mahjong:

	def __init__(self, config):
		self.config = config
		self.table = Table()
		self.gui = GuiManager(config)
		self.state = None
		self.light_state = None
		self.quit_flag = False
		self.protocol = None

		self.player_boxes = []
		self.my_wind = None
		self.round_wind = None
		self.riichi = False
		self.round_label = None
		self.prev_riichi_bets_label = None
		self.show_fps = False

		self.server_process = None

		self.username = _("Mahjong player")
		self.wind_names = [
			_("East"),
			_("South"),
			_("West"),
			_("North")
		]



	def reset_all(self):
		for box in self.player_boxes:
			self.gui.remove_widget(box)

		if self.round_label:
			self.gui.remove_widget(self.round_label)
			self.round_label = None

		if self.prev_riichi_bets_label:
			self.gui.remove_widget(self.prev_riichi_bets_label)
			self.prev_riichi_bets_label = None

		self.player_boxes = []
		self.table.reset_all()
		self.riichi = False

	def set_state(self, state):
		if self.state:
			self.state.leave_state()
		self.state = state
		if state:
			state.enter_state()

	def set_light_state(self, state):
		if self.light_state:
			self.light_state.leave_state()
		self.light_state = state
		if state:
			state.enter_state()

	def set_server_process(self, process):
		self.server_process = process

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
			if ev.type == pygame.KEYDOWN:
				self.state.on_key_down(ev)
			if ev.type == pygame.VIDEORESIZE:
				self.config.resize_window((ev.w, ev.h))
		return True

	def draw_all(self):
		screen = pygame.display.get_surface()
		self.table.draw()
		enable2d()
		self.gui.draw()
		disable2d()
		pygame.display.flip()

	def run(self):
		clock = pygame.time.Clock()
		time = pygame.time.get_ticks()
		frames = 0
		while not self.quit_flag:
			self.process_events()
			self.draw_all()
			self.state.tick()
			self.gui.tick()
			clock.tick(20)
			if self.show_fps:
				frames += 1
				t = pygame.time.get_ticks()
				if (t - time) >= 1000:
					print "FPS:",float(frames) / (t - time) * 1000
					time = t
					frames = 0


	def init_player_boxes(self, names, player_winds, score):
		self.player_boxes = [
			PlayerBox((50, 700), names[0], player_winds[0], int(score[0]), direction_up, (0,-80)),
			PlayerBox((954, 50), names[1], player_winds[1], int(score[1]), direction_left, (-210, 0)),
			PlayerBox((700, 0), names[2], player_winds[2], int(score[2]), direction_up, (0,80)),
			PlayerBox((0, 50), names[3], player_winds[3], int(score[3]), direction_right, (80,0)) ]
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

	def set_riichi(self, wind):
		player_id = self.player_id_by_wind(wind)
		self.player_boxes[player_id].score_delta(-1000)
		self.table.set_riichi(player_id)
		if player_id == 0:
			self.riichi = True

	def player_id_by_wind(self, wind):
		my_id = winds.index(self.my_wind)
		for i in xrange(4):
			if winds[(my_id + i) % 4] == wind:
				return i
		raise Exception("Unknown player: " + wind)

	def create_shoutbox(self, wind, text):
		return self.player_boxes[self.player_id_by_wind(wind)].create_shoutbox(text)

	def get_player_name(self, wind):
		return self.player_boxes[self.player_id_by_wind(wind)].player_name

	def set_protocol(self, protocol):
		self.protocol = protocol

	def set_username(self, name):
		self.username = name

	def get_username(self):
		return self.username

	def get_version_string(self):
		return "0.4"

	def process_network_message(self, message):
		print "Unknown message (%s): %s" % (self.state.__class__.__name__, repr(message))

	def arrange_hand(self):
		self.table.arrange_hand()

	def translate_round_name(self, round_name):
		server_wnames = [ "East", "South", "West", "North" ]
		name, number = round_name.split()
		return self.wind_names[server_wnames.index(name)] + " " + number

	def init_round(self, message):
		self.reset_all()

		# TODO: Random number from server
		import random
		self.table.break_wall(random.randint(1,6) + random.randint(1,6))

		self.my_wind = message["my_wind"]

		names = [ self.get_username(), message["right"], message["across"], message["left"] ]
		scores = [ message["my_score"], message["right_score"], message["across_score"], message["left_score"] ]
		wid = winds.index(self.my_wind)
		player_winds = [ self.wind_names[ (wid + t) % 4 ] for t in xrange(4) ]
		self.init_player_boxes(names, player_winds, scores)
		self.table.set_new_hand(message["hand"].split())
		self.add_dora_indicator(message["dora_indicator"])
		self.set_round_wind(message["round_wind"])
		self.set_round_name(self.translate_round_name(message["round_name"]))
		self.set_prev_riichi_bets(int(message["prev_riichi_bets"]))

	def add_dora_indicator(self, tile_name):
		self.table.add_dora_indicator(tile_name)

	def set_round_wind(self, wind):
		self.round_wind = wind

	def set_round_name(self, name):
		if self.round_label:
			self.gui.remove_widget(self.round_label)
		self.round_label = TextWidget((530,310), _("Round") + ": " + name, (175,175,175))
		self.gui.add_widget(self.round_label)

	def set_prev_riichi_bets(self, bets):
		if bets > 0:
			w1 = TextureWidget((520, 328), self.table.rstick_texture, 0.3, 0.3)
			w2 = TextWidget((500,330), str(bets / 1000) + "x", (175,175,175))
			self.prev_riichi_bets_label = ContainerWidget( [ w1, w2] )
			self.gui.add_widget(self.prev_riichi_bets_label)

	def get_round_wind(self):
		return self.round_wind

	def open_main_menu(self):
		self.set_light_state(None)
		self.reset_all()
		if self.server_process:
			self.server_process.terminate()
			self.server_process = None
		mahjong.set_state(MainMenuState(self))

	def toggle_fullscreen(self):
		self.config.toggle_fullscreen()
		self.config.video_init()

	def on_quit(self):
		if self.server_process:
			self.server_process.terminate()

multisamples = True

class Config:

	def __init__(self):
		self.window_size = (1024, 768)
		self.stored_window_size = self.window_size
		self.multisamples = True
		self.fullscreen = False

	def get_window_size(self):
		return self.window_size

	def preinit(self):
		info = pygame.display.Info()
		self.screen_resolution = (info.current_w, info.current_h)

	def video_init(self):
		if self.multisamples:
			pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS,1)
			pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES,4)
		else:
			pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS,0)
			pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES,0)

		flags = pygame.DOUBLEBUF | pygame.OPENGL

		if self.fullscreen:
			flags |= pygame.FULLSCREEN
		else:
			flags |= pygame.RESIZABLE
		pygame.display.set_mode(self.window_size, flags)
		pygame.display.set_caption("RMahjong")
		init_opengl(self.window_size[0], self.window_size[1])

	def resize_window(self, new_size):
		self.window_size = new_size
		self.video_init()

	def disable_multisamples(self):
		self.multisamples = False

	def toggle_fullscreen(self):
		self.fullscreen = not self.fullscreen
		if self.fullscreen:
			self.stored_window_size = self.window_size
			self.window_size = self.screen_resolution
		else:
			self.window_size = self.stored_window_size


def main_init(config):
	gettext.install('rmahjong', './data/locale', unicode=1)
	logging.basicConfig(filename = "client.log", format = "%(asctime)s - %(levelname)s - %(message)s", level = logging.DEBUG)
	pygame.display.init()
	pygame.font.init()
	config.preinit()
	try:
		config.video_init()
	except pygame.error, e:
		print "!! Display init failed: " + str(e)
		print "!! Openning fallback display without GL_MULTISAMPLEBUFFERS"
		config.disable_multisamples()
		config.video_init()
	init_fonts()
	pygame.key.set_repeat(100, 30)

config = Config()
main_init(config)
mahjong = Mahjong(config)
#mahjong.show_fps = True
try:
	mahjong.open_main_menu()
	#mahjong.set_state(ConnectingState(mahjong, "localhost"))
	#mahjong.set_state(TestState(mahjong))
	#mahjong.set_state(TestTableState(mahjong))
	mahjong.run()
finally:
	mahjong.on_quit()
	pygame.quit()
