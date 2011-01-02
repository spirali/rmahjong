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


from connection import Connection
from dictprotocol import DictProtocol
from gui import Button, Label, ScoreTable, PaymentTable, FinalTable, Frame, HandWidget, GameSummary
from table import winds
from copy import copy
import subprocess
import logging
import os.path
import pygame


def split_str(string, sep):
	return [ i for i in string.split(sep) if i != "" ]

class StateBase:

	def __init__(self, mahjong):
		self.mahjong = mahjong
		self.protocol = mahjong.protocol
		self.widgets = []
		
	def enter_state(self):
		pass

	def leave_state(self):
		self.remove_widgets()

	def tick(self):
		pass

	def add_widget(self, widget):
		self.widgets.append(widget)
		self.mahjong.gui.add_widget(widget)

	def setup_widgets(self, widgets):
		self.remove_widgets()
		self.widgets = widgets
		for widget in self.widgets:
			self.mahjong.gui.add_widget(widget)

	def remove_widgets(self):
		for widget in self.widgets:
			self.mahjong.gui.remove_widget(widget)
		self.widgets = []

	def on_key_down(self, event):
		pass

	def show_error(self, message):
		self.mahjong.set_state(ErrorState(self.mahjong, message))

	

class State(StateBase):
	
	def __init__(self, mahjong):
		StateBase.__init__(self, mahjong)
		self.protocol = mahjong.protocol
		
	def tick(self):
		if self.protocol:
			message = self.protocol.read_message()
			if message:
				self.process_message(message)

	def process_message(self, message):
		self.mahjong.process_network_message(message)


class OfflineState(StateBase):
	pass


class RoundPreparingState(State):
	
	def process_message(self, message):
		name = message["message"]
		if name == "ROUND":
			self.mahjong.init_round(message)
			return
		if name == "MOVE":
			self.mahjong.table.remove_tile_from_wall()
			actions = split_str(message["actions"],";")
			state = MyMoveState(self.mahjong, message["tile"], actions)
			self.mahjong.set_state(state)
			return
		if name == "OTHER_MOVE":
			self.mahjong.table.remove_tile_from_wall()
			state = OtherMoveState(self.mahjong, message["wind"], True)
			self.mahjong.set_state(state)
			return
		State.process_message(self, message)		


class ConnectingState(RoundPreparingState):

	def __init__(self, mahjong, server_adress):
		RoundPreparingState.__init__(self, mahjong)
		self.protocol = None
		self.server_adress = server_adress

	def enter_state(self):
		self.label = Label( (350, 350), (350,45), "Connecting ... ")
		self.mahjong.gui.add_widget(self.label)
		self.button = None
		self.mahjong.draw_all()
		connection = Connection()
		self.button = Button( (475,420), (100, 30), "Cancel", lambda b: self.mahjong.open_main_menu())
		self.mahjong.gui.add_widget(self.button)
		if connection.connect(self.server_adress, 4500):
			self.set_label("Intitializing ... ")
			self.protocol = DictProtocol(connection)
			self.mahjong.protocol = self.protocol
			self.protocol.send_message(message="LOGIN", 
				user_name = self.mahjong.get_username(), 
				version = self.mahjong.get_version_string())
		else:
			self.show_error("Connection failed")

	def set_label(self, text):
		self.mahjong.gui.remove_widget(self.label)
		self.label = Label( (350, 350), (350,45), text)
		self.mahjong.gui.add_widget(self.label)

	def leave_state(self):
		self.mahjong.gui.remove_widget(self.label)
		if self.button:
			self.mahjong.gui.remove_widget(self.button)

	def process_message(self, message):
		name = message["message"]
		if name == "WELCOME":
			self.set_label("Waiting for other players ... ")
			return
		RoundPreparingState.process_message(self, message)


class StartServerState(OfflineState):

	def __init__(self, mahjong, number_of_players):
		OfflineState.__init__(self, mahjong)
		self.number_of_players = number_of_players

	def enter_state(self):
		label = Label( (350, 350), (350,45), "Starting server ... ")
		# button = Button( (475,420), (100, 30), "Cancel", lambda b: self.mahjong.open_main_menu())
		self.setup_widgets([label])
		self.mahjong.draw_all()
		
		process = None
		try:
			process = subprocess.Popen([ self.get_server_filename(), str(self.number_of_players) ], bufsize = 0, stdout = subprocess.PIPE)
			process_out = process.stdout
			# TODO: Nonblocking server start
			response = process_out.readline()
			if response != "Init done\n":
				self.show_error("Initialization of server failed")
				logging.error("Server response: " + response)
				process.terminate()
			else:
				self.mahjong.set_server_process(process)
				self.mahjong.set_state(ConnectingState(self.mahjong, "localhost"))
		except OSError, e:
			self.show_error("Server: " + str(e))
			if process:
				process.terminate()

	def get_server_filename(self):
		for f in [ "../server/run_server.sh", "../server/server.exe" ]:
			if os.path.isfile(f):
				return f

	def tick(self):
		pass


class ErrorState(State):

	def __init__(self, mahjong, error_msg):
		State.__init__(self, mahjong)
		self.error_msg = error_msg

	def enter_state(self):
		logging.error("ErrorState: " + self.error_msg)
		self.label = Label( (350, 350), (350,45), self.error_msg, bg_color = (250, 20, 20, 90))
		self.mahjong.gui.add_widget(self.label)
		self.button = Button( (475,420), (100, 30), "Ok", lambda b: self.mahjong.open_main_menu())
		self.mahjong.gui.add_widget(self.button)

	def leave_state(self):
		self.mahjong.gui.remove_widget(self.label)
		self.mahjong.gui.remove_widget(self.button)

	def tick(self):
		pass


class RoundState(State):

	def __init__(self, mahjong):
		State.__init__(self, mahjong)
		self.protocol = mahjong.protocol

	def process_message(self, message):
		name = message["message"]
		
		if name == "DROPPED":
			self.mahjong.add_dropped_tile(message["wind"], message["tile"])
			actions = split_str(message["actions"],";")
			self.chi_choose = split_str(message["chi_choose"], ";")

			if len(self.chi_choose) >= 2:
				actions.remove("Chi")
				self.chi_choose.sort()
				for choose in self.chi_choose:
					tile_num = int(choose[1]) # Get digit
					actions.append("Chi " + str(tile_num) + str(tile_num + 1) + str(tile_num+2)) 

			if actions:
				self.add_buttons(actions, self.on_steal_action_click)
			return

		if name == "MOVE":
			self.mahjong.table.remove_tile_from_wall()
			actions = split_str(message["actions"], ";")
			state = MyMoveState(self.mahjong, message["tile"], actions)
			self.mahjong.set_state(state)
			return

		if name == "OTHER_MOVE":
			self.mahjong.table.remove_tile_from_wall()
			state = OtherMoveState(self.mahjong, message["wind"], True)
			self.mahjong.set_state(state)
			return

		if name == "ROUND_END" or name == "DRAW":
			state = ScoreState(self.mahjong, message)
			self.mahjong.set_state(state)
			return

		if name == "RIICHI":
			self.mahjong.set_riichi(message["player"])
			shoutbox = self.mahjong.create_shoutbox(message["player"], "Riichi!")
			self.mahjong.gui.add_widget_with_timeout(shoutbox, 2500)
			return

		if name == "STOLEN_TILE":
			self.process_stolen_tile(message)
			return

		if name == "KAN":
			self.process_own_kan(message)
			return

		State.process_message(self, message)		

	def add_buttons(self, button_labels, callback):
		px, py = 290,730
		for label in button_labels:
			button = Button((px, py), (75,25), label, callback)
			px += 80
			self.mahjong.gui.add_widget(button)
			self.widgets.append(button)

	def process_stolen_tile(self, message):
		action = message["action"]
		tiles = message["tiles"].split()
		stolen_tile = message["stolen_tile"]
		player = message["player"]
		from_player = message["from_player"]
		player_id = self.mahjong.player_id_by_wind(player)
		from_player_id = self.mahjong.player_id_by_wind(from_player)
		# TODO: Timed shout
		shoutbox = self.mahjong.create_shoutbox(player, action + "!")
		self.mahjong.gui.add_widget_with_timeout(shoutbox, 2500)
		self.mahjong.table.add_open_set(player_id, tiles, from_player_id)
		self.mahjong.table.steal_from_dropzone(self.mahjong.player_id_by_wind(from_player))

		if action == "Kan":
			self.mahjong.table.remove_dead_wall_tile_for_kan()
			self.mahjong.add_dora_indicator(message["dora_indicator"])
		
		if player_id == 0:
			tiles.remove(stolen_tile) # Tiles are now removed from hand, so we dont want remove stolen tile
			for tile in tiles:
				self.mahjong.table.remove_hand_tile_by_name(tile)
			self.mahjong.arrange_hand()

			if action == "Kan":
				new_tile = message["new_tile"]
				actions = message["actions"].split(";")
			else:
				new_tile = None
				actions = []

			self.mahjong.set_state(MyMoveState(self.mahjong, new_tile, actions))
		else:
			self.mahjong.table.remove_tiles_from_other_hand(player_id, len(tiles) - 1)
			self.mahjong.set_state(OtherMoveState(self.mahjong, player, action == "Kan"))

	def process_own_kan(self, message):
		self.mahjong.table.remove_dead_wall_tile_for_kan()
		self.mahjong.add_dora_indicator(message["dora_indicator"])
		tile_name = message["tile"]
		player = message["player"]
		player_id = self.mahjong.player_id_by_wind(player)
		shoutbox = self.mahjong.create_shoutbox(player, "Kan!")
		self.mahjong.gui.add_widget_with_timeout(shoutbox, 2500)
		
		open_pon = self.mahjong.table.find_open_set_id(player_id, [tile_name] * 3)

		if open_pon is not None:
			self.mahjong.table.add_extra_kan_tile(player_id, open_pon, tile_name)		
		else:
			self.mahjong.table.add_open_set(player_id, [tile_name, "XX", "XX", tile_name], -1)

		if player_id == 0:
			self.process_self_kan(message, open_pon is not None)
		else:
			if open_pon is None:
				if self.picked_tile:
					self.mahjong.table.remove_tiles_from_other_hand(player_id, 3)			
					self.picked_tile.remove()
					self.picked_tile = None
				else:
					self.mahjong.table.remove_tiles_from_other_hand(player_id, 4)

	def process_self_kan(self, message, open_pon):
		raise Exception("Invalid state for self_kan")

	def on_key_down(self, event):
		State.on_key_down(self, event)
		if event.key == pygame.K_ESCAPE:
			if self.mahjong.light_state:
				self.mahjong.set_light_state(None)
			else:
				ingame_menu = IngameMenu(self.mahjong)
				self.mahjong.set_light_state(ingame_menu)


class MyMoveState(RoundState):

	def __init__(self, mahjong, tile, actions):
		RoundState.__init__(self, mahjong)
		self.picked_tile_name = tile
		self.actions = actions
		self.picked_tile = None

	def enter_state(self):
		RoundState.enter_state(self)

		table = self.mahjong.table

		if not self.mahjong.riichi:
			table.set_hand_callback(self.drop_hand_tile)		
		
		if self.picked_tile_name:
			self.new_picked_tile(self.picked_tile_name)

		self.mahjong.select_my_box()
		self.add_buttons(self.actions, self.on_action_click)

		if self.mahjong.riichi and not self.actions:
			self.drop_picked_tile(self.picked_tile)

	def new_picked_tile(self, tile_name):
		tile = self.mahjong.table.picked_tile(tile_name)
		tile.callback = self.drop_picked_tile
		self.picked_tile = tile

	def move_picked_tile_into_hand(self):
		self.picked_tile.callback = None
		self.mahjong.table.add_to_hand(self.picked_tile)

	def drop_picked_tile(self, tile):
		self.mahjong.table.set_hand_callback(None)		
		self.protocol.send_message(message = "DROP", tile = tile.name)
		tile.remove()
		self.remove_widgets()

	def drop_hand_tile(self, tile):
		table = self.mahjong.table
		table.set_hand_callback(None)		
		self.protocol.send_message(message = "DROP", tile = tile.name)
		tile.remove()
		if self.picked_tile:
			self.move_picked_tile_into_hand()
		self.mahjong.arrange_hand()
		self.remove_widgets()

	def leave_state(self):
		RoundState.leave_state(self)
		self.mahjong.select_none()
		self.mahjong.table.set_hand_callback(None)		

	def on_action_click(self, button):
		self.remove_widgets()
		if button.label == "Tsumo":
			self.action_tsumo()
		if button.label == "Riichi":
			self.action_riichi()
		if button.label.startswith("Kan "):
			self.action_kan(button.label.split()[1])

	def action_tsumo(self):
		self.protocol.send_message(message = "TSUMO")

	def action_riichi(self):
		self.protocol.send_message(message = "RIICHI")

	def action_kan(self, tile):
		self.protocol.send_message(message = "KAN", tile = tile)

	def process_self_kan(self, message, open_pon):
		tile_name = message["tile"]

		if not open_pon:
			self.mahjong.table.remove_hand_tile_by_name(tile_name)
			self.mahjong.table.remove_hand_tile_by_name(tile_name)
			self.mahjong.table.remove_hand_tile_by_name(tile_name)

		if self.picked_tile.name == tile_name:
			self.picked_tile.remove()
		else:
			self.mahjong.table.remove_hand_tile_by_name(tile_name)
			self.move_picked_tile_into_hand()

		self.new_picked_tile(message["new_tile"])
		self.mahjong.arrange_hand()
		actions = split_str(message["actions"],";")
		self.add_buttons(actions, self.on_action_click)


class OtherMoveState(RoundState):

	def __init__(self, mahjong, wind, pick_tile):
		RoundState.__init__(self, mahjong)
		self.wind = wind
		self.pick_tile = pick_tile
		self.picked_tile = None

	def enter_state(self):
		RoundState.enter_state(self)
		self.mahjong.select_box(self.wind)
		if self.pick_tile:
			player_id = self.mahjong.player_id_by_wind(self.wind)
			self.picked_tile = self.mahjong.table.picked_other_hand_tile(player_id)

	def leave_state(self):
		RoundState.leave_state(self)
		self.mahjong.select_none()

	def process_message(self, message):
		RoundState.process_message(self, message)
		if message["message"] == "DROPPED":
			if self.picked_tile:
				self.picked_tile.remove()
				self.picked_tile = None
			else:
				player_id = self.mahjong.player_id_by_wind(self.wind)
				self.mahjong.table.remove_tiles_from_other_hand(player_id, 1)

	def on_steal_action_click(self, button):
		self.remove_widgets()
		action = button.label
		if action == "Pass":
			self.protocol.send_message(message = "READY")
		elif action.startswith("Chi"):
			if len(self.chi_choose) == 1:
				self.protocol.send_message(message="STEAL", action = "Chi", chi_choose = self.chi_choose[0])
			else:
				tile_num = action[4]
				for tile_name in self.chi_choose:
					if tile_name[1] == tile_num:
						self.protocol.send_message(message="STEAL", action = "Chi", chi_choose = tile_name)
						break
		else:
			self.protocol.send_message(message = "STEAL", action = action)

class ScoreState(RoundPreparingState):
	
	def __init__(self, mahjong, round_end_message):
		RoundPreparingState.__init__(self, mahjong)
		self.message = round_end_message

	def enter_state(self):
		State.enter_state(self)

		name = self.message["message"]
		if name == "ROUND_END":	
			button = Button( (475,340), (120, 30), "Show score", self.show_score_clicked)
			shoutbox = self.mahjong.create_shoutbox(self.message["player"], self.message["wintype"] + "!")
			self.setup_widgets([ button, shoutbox ])
			#for tile_name in self.message["ura_dora_indicators"].split():
			#	self.mahjong.table.add_ura_dora_indicator(tile_name)
		else:
			# Draw
			if self.message["tenpai"]:
				players = [ self.mahjong.get_player_name(player) for player in self.message["tenpai"].split() ]
				text = "in tenpai: " + ",".join(players)
			else:
				text = "Nobody is tenpai"

			label = Label( (250, 350), (550,45), "Draw (" + text + ")")
			button = Button( (475,410), (120, 30), "Show score", self.show_payments)
			self.setup_widgets([ button, label ])

	def show_score_clicked(self, button):
		score_items = self.message["score_items"].split(";")
		total_fans = self.message["total_fans"]
		minipoints = self.message["minipoints"]
		payment = self.message["payment"]
		player_name = self.mahjong.get_player_name(self.message["player"])
		total = str(total_fans) + " (minipoints: " + str(minipoints) + ")"
		looser_riichi = self.message["looser_riichi"]
		winner_hand = self.message["winner_hand"].split()
		winner_sets = [ s.split() for s in self.message["winner_sets"].split(";") ]
		ura_dora_indicators = self.message["ura_dora_indicators"].split()

		table = ScoreTable(score_items , total, payment, player_name, looser_riichi)
		button = Button( (400,560), (300, 25), "Show payments", self.show_payments)
		hand = HandWidget((10,10), winner_hand, winner_sets , self.mahjong.table.tp)

		dora_indicators_names = [ tile.name for tile in self.mahjong.table.dora_indicators ]
		summary = GameSummary(self.mahjong.table.tp, dora_indicators_names, ura_dora_indicators, self.mahjong.get_round_wind())
		
		self.setup_widgets([table, button, hand, summary])

	def get_results(self):
		results = []
		for wind in winds:
			name = (self.mahjong.get_player_name(wind))
			score = (int(self.message[wind + "_score"]))
			payment = (int(self.message[wind + "_payment"]))
			results.append((name, score, payment))
		results.sort(key = lambda r: r[1], reverse = True)
		return results

	def show_payments(self, button):
		if self.message["end_of_game"] == "True":
			button = Button( (400,560), (300, 25), "Show final score", self.final_score)
		else:
			button = Button( (400,560), (300, 25), "I am ready for next round", self.send_ready)
		results = self.get_results()
		table = PaymentTable(results)
		self.setup_widgets([table, button])

	def send_ready(self, button):
		widgets = copy(self.widgets)
		widgets.remove(button)
		self.setup_widgets(widgets)
		self.protocol.send_message(message="READY")

	def final_score(self, button):
		results = self.get_results()
		results = map(lambda r: r[:2], results) # Remove payment
		state = FinalState(self.mahjong, results)
		self.mahjong.set_state(state)


class FinalState(State):
	
	def __init__(self, mahjong, results):
		State.__init__(self, mahjong)
		self.results = results

	def enter_state(self):
		State.enter_state(self)

		table = FinalTable(self.results)
		button = Button( (400,560), (300, 25), "Return to menu", self.return_to_menu_clicked)
		self.setup_widgets([table, button])

	def return_to_menu_clicked(self, button):
		self.mahjong.open_main_menu()


class LightState(StateBase):
	pass
	
	
class IngameMenu(LightState):

	def __init__(self, mahjong):
		LightState.__init__(self, mahjong)

	def enter_state(self):
		LightState.enter_state(self)
		frame = Frame((300, 300), (400, 180))
		button1 = Button((325, 320), (350, 35), "Return to game", self.on_return)
		button2 = Button((325, 380), (350, 35), "Toggle fullscreen", self.on_fullscreen)
		button3 = Button((325, 420), (350, 35), "Quit game", self.on_quit)
		self.setup_widgets([frame, button1, button2, button3])

	def on_quit(self, button):
		self.mahjong.open_main_menu()

	def on_fullscreen(self, button):
		self.mahjong.toggle_fullscreen()

	def on_return(self, button):
		self.mahjong.set_light_state(None)
		

class TestState(State):

	def __init__(self, mahjong):
		State.__init__(self, mahjong)
		self.mahjong.table.set_new_hand(["DW", "DW", "C2","C3","C4", "WW", "WW", "WW", "B8", "B6", "B7"])
		#self.mahjong.table.set_new_hand(["DW", "DW", "C1", "C2", "C3", "C4"])
		#self.mahjong.table.set_new_hand(["DW", "DW", "C2","C3","C4", "WW", "WW", "WW"])
		self.mahjong.my_wind = "WE"
		self.mahjong.set_round_wind("WS")
		self.mahjong.set_round_name("South 4")
		self.mahjong.set_prev_riichi_bets(11000)
		#self.mahjong.table.set_new_hand(["DW", "DW", ])

		self.mahjong.init_player_boxes(["A","B", "C", "D"], ["east", "south", "west", "north"], (1000, 2000, 25000, 30000))
		for w in winds:
			self.mahjong.set_riichi(w)

		for x in xrange(7):
			self.mahjong.table.new_other_hand_tile(1, x)
			self.mahjong.table.new_other_hand_tile(2, x)
			self.mahjong.table.new_other_hand_tile(3, x)


		for x in xrange(4):
			self.mahjong.table.add_open_set(x, [ "DR", "DR", "DR", "C4" ], 3)
			self.mahjong.table.add_open_set(x, [ "C1", "C2", "C3", "C4" ], 3)
			self.mahjong.table.add_open_set(x, [ "B7", "B8", "B9", "C4" ], 3)
			self.mahjong.table.add_open_set(x, [ "WN", "WE", "WS", "C4" ], 3)
	#		self.mahjong.table.add_extra_kan_tile(x, 0, "DR")
	#		self.mahjong.table.add_extra_kan_tile(x, 1, "DR")

		from table import all_tile_names
		for tile in all_tile_names[:13]:
			self.mahjong.table.new_tile_to_dropzone(0, tile)
			self.mahjong.table.new_tile_to_dropzone(1, tile)
			self.mahjong.table.new_tile_to_dropzone(2, tile)
			self.mahjong.table.new_tile_to_dropzone(3, tile)

		self.mahjong.table.steal_from_dropzone(0)
		self.mahjong.table.new_tile_to_dropzone(0, "DR")
		self.mahjong.table.steal_from_dropzone(0)
		self.mahjong.table.new_tile_to_dropzone(0, "DW")


		for tile in [ "C1","DR", "WW", "P5", "B3" ]:
			self.mahjong.table.add_dora_indicator(tile)

		for tile in [ "C2","DG", "WE", "P6", "B4" ]:
			self.mahjong.table.add_ura_dora_indicator(tile)


	def tick(self):
		pass

class TestTableState(State):

	def __init__(self, mahjong):
		State.__init__(self, mahjong)
		
		table = ScoreTable(["ABC 100", "XYZ 200"], "8000", "2000/300", "Player_name", "2000")
		gamesummary = GameSummary(self.mahjong.table.tp, ["DW", "C1", "C4", "B9", "WW", ], ["DW", "C1", "WW", "WE", "B1"],  "WE")
		#table = PaymentTable([("ABC", 1000, 2000), ("CDE", 200000, -15000), ("EFG", 0, 123456), ("XYZ", 15000, 0)])
		#table = FinalTable([("ABC", 1000), ("CDE", 200000), ("EFG", 0), ("XYZ", 15000)])
		hand = HandWidget((10,10), ["DR","C1","C2","DW", "DW", "B5", "B5", "WE", "WE", "WE", "DR", "P6", "P7", "B5"], [] , self.mahjong.table.tp)
	#	hand = HandWidget((10,10), ["DR","DR","C1","C2","C3", "B5", "B5", "B5", "WE", "WE", "WE"], [ ["WN", "WN", "WN"] ], self.mahjong.table.tp)
		#hand = HandWidget((10,10), ["DR","DR"], [ ["WN", "WN", "WN", "WE"], ["WN", "WN", "WN", "WE"], ["WN", "WN", "WN", "WE"], ["WN", "WN", "WN", "WE"] ], self.mahjong.table.tp)
		mahjong.gui.add_widget(table)
		mahjong.gui.add_widget(hand)
		mahjong.gui.add_widget(gamesummary)

	def tick(self):
		pass
