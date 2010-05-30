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
from gui import Button, Label, ScoreTable, PaymentTable, FinalTable
from table import winds
from copy import copy

def split_str(string, sep):
	return [ i for i in string.split(sep) if i != "" ]

class State:
	
	def __init__(self, mahjong):
		self.mahjong = mahjong
		self.protocol = mahjong.protocol
		self.widgets = []
		
	def tick(self):
		pass

	def enter_state(self):
		pass

	def leave_state(self):
		self.remove_widgets()

	def tick(self):
		if self.protocol:
			message = self.protocol.read_message()
			if message:
				self.process_message(message)

	def process_message(self, message):
		self.mahjong.process_network_message(message)

	def setup_widgets(self, widgets):
		self.remove_widgets()
		self.widgets = widgets
		for widget in self.widgets:
			self.mahjong.gui.add_widget(widget)

	def remove_widgets(self):
		for widget in self.widgets:
			self.mahjong.gui.remove_widget(widget)
		self.widgets = []


class RoundPreparingState(State):
	
	def process_message(self, message):
		name = message["message"]
		if name == "ROUND":
			self.mahjong.init_round(message)
			return
		if name == "MOVE":
			actions = split_str(message["actions"],";")
			state = MyMoveState(self.mahjong, message["tile"], actions)
			self.mahjong.set_state(state)
			return
		if name == "OTHER_MOVE":
			state = OtherMoveState(self.mahjong, message["wind"])
			self.mahjong.set_state(state)
			return
		State.process_message(self, message)		


class ConnectingState(RoundPreparingState):

	def __init__(self, mahjong):
		RoundPreparingState.__init__(self, mahjong)
		self.protocol = None

	def enter_state(self):
		self.label = Label( (350, 350), (350,45), "Connecting ... ")
		self.mahjong.gui.add_widget(self.label)
		self.button = None
		self.mahjong.draw_all()
		connection = Connection()
		self.button = Button( (475,420), (100, 30), "Cancel", lambda b: self.mahjong.quit())
		self.mahjong.gui.add_widget(self.button)
		if connection.connect("localhost", 4500):
			self.set_label("Intitializing ... ")
			self.protocol = DictProtocol(connection)
			self.mahjong.protocol = self.protocol
			self.protocol.send_message(message="LOGIN", 
				user_name = self.mahjong.get_username(), 
				version = self.mahjong.get_version_string())
		else:
			self.mahjong.set_state(ErrorState(self.mahjong, "Connection failed"))

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


class ErrorState(State):

	def __init__(self, mahjong, error_msg):
		State.__init__(self, mahjong)
		self.error_msg = error_msg

	def enter_state(self):
		self.label = Label( (350, 350), (350,45), self.error_msg, bg_color = (250, 20, 20, 90))
		self.mahjong.gui.add_widget(self.label)
		self.button = Button( (475,420), (100, 30), "Ok", lambda b: self.mahjong.quit())
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
			if actions:
				self.add_buttons(actions, self.on_steal_action_click)
			return

		if name == "MOVE":
			actions = split_str(message["actions"], ";")
			state = MyMoveState(self.mahjong, message["tile"], actions)
			self.mahjong.set_state(state)
			return

		if name == "OTHER_MOVE":
			state = OtherMoveState(self.mahjong, message["wind"])
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

		if name == "CLOSED_KAN":
			self.process_closed_kan(message)
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
		# TODO: Timed shout
		shoutbox = self.mahjong.create_shoutbox(player, action + "!")
		self.mahjong.gui.add_widget_with_timeout(shoutbox, 2500)
		self.mahjong.table.add_open_set(player_id, tiles, [])
		self.mahjong.table.steal_from_dropzone(self.mahjong.player_id_by_wind(from_player))
		
		if player_id == 0:
			tiles.remove(stolen_tile) # Tiles are now removed from hand, so we dont want remove stolen tile
			for tile in tiles:
				self.mahjong.table.remove_hand_tile_by_name(tile)
			self.mahjong.arrange_hand()
			self.mahjong.set_state(MyMoveState(self.mahjong, None, []))
		else:
			self.mahjong.set_state(OtherMoveState(self.mahjong, player))

	def process_closed_kan(self, message):
		self.mahjong.add_dora_indicator(message["dora_indicator"])
		tile_name = message["tile"]
		player = message["player"]
		player_id = self.mahjong.player_id_by_wind(player)
		shoutbox = self.mahjong.create_shoutbox(player, "Kan!")
		self.mahjong.gui.add_widget_with_timeout(shoutbox, 2500)
		self.mahjong.table.add_open_set(player_id, [tile_name] * 4, [])
		if player_id == 0:
			self.process_self_kan(message)

	def process_self_kan(self, message):
		raise Exception("Invalid state for self_kan")


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
		if button.label.startswith("Kan"):
			self.action_kan(button.label.split()[1])

	def action_tsumo(self):
		self.protocol.send_message(message = "TSUMO")

	def action_riichi(self):
		self.protocol.send_message(message = "RIICHI")

	def action_kan(self, tile):
		self.protocol.send_message(message = "CLOSED_KAN", tile = tile)

	def process_self_kan(self, message):
		tile_name = message["tile"]
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

	def __init__(self, mahjong, wind):
		RoundState.__init__(self, mahjong)
		self.wind = wind
		self.highlight_tiles = []

	def enter_state(self):
		RoundState.enter_state(self)
		self.mahjong.select_box(self.wind)

	def leave_state(self):
		RoundState.leave_state(self)
		self.mahjong.select_none()

	def on_steal_action_click(self, button):
		self.remove_widgets()
		action = button.label
		if action == "Pass":
			self.protocol.send_message(message = "READY")
		elif action == "Chi":
			if len(self.chi_choose) == 1:
				self.protocol.send_message(message="STEAL", action = "Chi", chi_choose = self.chi_choose[0])
			else:
				for tile_name in self.chi_choose:
					tile = self.mahjong.table.find_tile_in_hand(tile_name)
					self.highlight_tiles.append(tile)
					tile.highlight = True
					tile.callback = self.on_chi_choose_click
		else:
			self.protocol.send_message(message = "STEAL", action = action)

	def on_chi_choose_click(self, tile):
		self.protocol.send_message(message="STEAL", action = "Chi", chi_choose = tile.name)
		for tile in self.highlight_tiles:
			tile.highlight = False
			tile.callback = None


class ScoreState(RoundPreparingState):
	
	def __init__(self, mahjong, round_end_message):
		RoundPreparingState.__init__(self, mahjong)
		self.message = round_end_message

	def enter_state(self):
		State.enter_state(self)

		name = self.message["message"]
		if name == "ROUND_END":	
			button = Button( (475,380), (120, 30), "Show score", self.show_score_clicked)
			shoutbox = self.mahjong.create_shoutbox(self.message["player"], self.message["wintype"] + "!")
			self.setup_widgets([ button, shoutbox ])
			for tile_name in self.message["ura_dora_indicators"].split():
				self.mahjong.table.add_ura_dora_indicator(tile_name)
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
		table = ScoreTable(score_items , total, payment, player_name, looser_riichi)
		button = Button( (400,560), (300, 25), "Show payments", self.show_payments)
		self.setup_widgets([table, button])

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
		print self.message["end_of_game"]
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
		pass
		

class TestState(State):

	def __init__(self, mahjong):
		State.__init__(self, mahjong)
		#self.mahjong.table.set_new_hand(["DW", "DW", "C2","C3","C4", "WW", "WW", "WW", "B8", "B6", "B7"])
		self.mahjong.table.set_new_hand(["DW", "DW", "C1", "C2", "C3", "C4"])
		#self.mahjong.table.set_new_hand(["DW", "DW", "C2","C3","C4", "WW", "WW", "WW"])
		self.mahjong.my_wind = "WE"
		self.mahjong.set_round_wind("WS")
		#self.mahjong.table.set_new_hand(["DW", "DW", ])

		for x in xrange(4):
			self.mahjong.table.add_open_set(x, [ "DR", "DR", "DR", "DR" ], [])
			self.mahjong.table.add_open_set(x, [ "C1", "C2", "C3", "C4" ], [])
			self.mahjong.table.add_open_set(x, [ "B7", "B8", "B9", "B9" ], [])
	#		self.mahjong.table.add_open_set(x, [ "WN", "WE", "WS", "WW" ], [])

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

		self.mahjong.init_player_boxes(["A","B", "C", "D"], ["east", "south", "west", "north"], (1000, 2000, 25000, 30000))

		for w in winds:
			self.mahjong.set_riichi(w)

	def tick(self):
		pass

class TestTableState(State):

	def __init__(self, mahjong):
		State.__init__(self, mahjong)
		
		#table = ScoreTable(["ABC 100", "XYZ 200"], "8000", "2000/300", "Player_name", "2000")
		#table = PaymentTable([("ABC", 1000, 2000), ("CDE", 200000, -15000), ("EFG", 0, 123456), ("XYZ", 15000, 0)])
		table = FinalTable([("ABC", 1000), ("CDE", 200000), ("EFG", 0), ("XYZ", 15000)])
		mahjong.gui.add_widget(table)

	def tick(self):
		pass
