from connection import Connection
from dictprotocol import DictProtocol
from gui import Button, Label, ScoreTable


class State:
	
	def __init__(self, mahjong):
		self.mahjong = mahjong
		self.protocol = mahjong.protocol
		
	def tick(self):
		pass

	def enter_state(self):
		pass

	def leave_state(self):
		pass

	def tick(self):
		if self.protocol:
			message = self.protocol.read_message()
			while message:
				self.process_message(message)
				message = self.protocol.read_message()

	def process_message(self, message):
		self.mahjong.process_network_message(message)


class ConnectingState(State):

	def __init__(self, mahjong):
		State.__init__(self, mahjong)
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
		if name == "ROUND":
			self.init_round(message)
			return
		if name == "MOVE":
			actions = message["actions"].split()
			state = MyMoveState(self.mahjong, message["tile"], actions)
			self.mahjong.set_state(state)
			return
		if name == "OTHER_MOVE":
			state = OtherMoveState(self.mahjong, message["wind"])
			self.mahjong.set_state(state)
			return
		State.process_message(self, message)		

	def init_round(self, message):
		names = [ self.mahjong.get_username(), message["right"], message["across"], message["left"] ]
		self.mahjong.init_player_boxes(names)
		self.mahjong.table.set_new_hand(message["hand"].split())
		self.mahjong.table.add_dora(message["dora"])
		self.mahjong.my_wind = message["my_wind"]
		self.mahjong.round_wind = message["round_wind"]


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
		self.widgets = []


	def process_message(self, message):
		name = message["message"]
		
		if name == "DROPPED":
			self.mahjong.add_dropped_tile(message["wind"], message["tile"])
			actions = message["actions"].split()
			self.chi_choose = message["chi_choose"].split()
			if actions:
				self.add_buttons(actions, self.on_steal_action_click)
			return

		if name == "MOVE":
			actions = message["actions"].split()
			state = MyMoveState(self.mahjong, message["tile"], actions)
			self.mahjong.set_state(state)
			return
		if name == "OTHER_MOVE":
			state = OtherMoveState(self.mahjong, message["wind"])
			self.mahjong.set_state(state)
			return

		if name == "ROUND_END":
			state = ScoreState(self.mahjong, message)
			self.mahjong.set_state(state)
			return

		if name == "STOLEN_TILE":
			self.process_stolen_tile(message)
			return

		State.process_message(self, message)		

	def enter_state(self):
		pass

	def remove_widgets(self):
		for widget in self.widgets:
			self.mahjong.gui.remove_widget(widget)
		self.widgets = []

	def leave_state(self):
		self.remove_widgets()

	def add_buttons(self, button_labels, callback):
		px, py = 780,640
		button_labels.reverse()
		for label in button_labels:
			button = Button((px, py), (75,25), label, callback)
			py -= 27
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
				self.mahjong.table.remove_hand_tile(tile)
			self.mahjong.arrange_hand()
			self.mahjong.set_state(MyMoveState(self.mahjong, None, []))
		else:
			self.mahjong.set_state(OtherMoveState(self.mahjong, player))


class MyMoveState(RoundState):

	def __init__(self, mahjong, tile, actions):
		RoundState.__init__(self, mahjong)
		self.picked_tile_name = tile
		self.actions = actions
		self.picked_tile = None

	def enter_state(self):
		RoundState.enter_state(self)

		table = self.mahjong.table
		table.set_hand_callback(self.drop_hand_tile)		
		
		if self.picked_tile_name:
			tile = table.new_tile(self.picked_tile_name, table.picked_tile_position())
			tile.callback = self.drop_picked_tile
			self.picked_tile = tile

		self.mahjong.select_my_box()
		self.add_buttons(self.actions, self.on_action_click)

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
			self.picked_tile.callback = None
			table.add_to_hand(self.picked_tile)

		self.mahjong.arrange_hand()
		self.remove_widgets()

	def leave_state(self):
		RoundState.leave_state(self)
		self.mahjong.select_none()
		self.mahjong.table.set_hand_callback(None)		

	def on_action_click(self, button):
		self.remove_widgets()
		self.action_tsumo()

	def action_tsumo(self):
		self.protocol.send_message(message = "TSUMO")


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

class ScoreState(State):
	
	def __init__(self, mahjong, round_end_message):
		State.__init__(self, mahjong)
		self.message = round_end_message
		self.widgets = []
		
	def enter_state(self):
		State.enter_state(self)
		button = Button( (475,380), (120, 30), "Show score", self.show_score_clicked)
		shoutbox = self.mahjong.create_shoutbox(self.message["player"], self.message["wintype"] + "!")
		self.setup_widgets([ button, shoutbox ])

	def setup_widgets(self, widgets):
		self.widgets = widgets
		for widget in self.widgets:
			self.mahjong.gui.add_widget(widget)

	def remove_widgets(self):
		for widget in self.widgets:
			self.mahjong.gui.remove_widget(widget)

	def leave_state(self):
		State.leave_state(self)
		self.remove_widgets()

	def show_score_clicked(self, button):
		self.remove_widgets()
		score_items = self.message["score_items"].split(";")
		total_fans = self.message["total_fans"]
		payment = self.message["payment"]
		player_name = self.mahjong.get_player_name(self.message["player"])
		table = ScoreTable(score_items , total_fans, payment, player_name)
		button = Button( (400,560), (300, 25), "I am ready for next round", None)
		self.setup_widgets([table, button])


class TestState(State):

	def __init__(self, mahjong):
		State.__init__(self, mahjong)
		self.mahjong.table.set_new_hand(["DW", "DW", "C2","C3","C4", "WW", "WW", "WW", "B8", "B6", "B7"])
		self.mahjong.table.set_new_hand(["DW", "DW", "C2","C3","C4", "WW", "WW", "WW"])
		#self.mahjong.table.set_new_hand(["DW", "DW", ])

		for x in xrange(4):
			self.mahjong.table.add_open_set(x, [ "C2", "DR", "DR", "DR" ], [2,3])
			self.mahjong.table.add_open_set(x, [ "C2", "C1", "C2", "C3" ], [1])
			self.mahjong.table.add_open_set(x, [ "C2", "DR", "DR", "DR" ], [0])
			self.mahjong.table.add_open_set(x, [ "C2", "C1", "C2", "C3" ], [3])


		from table import all_tile_names
		for tile in all_tile_names[:18]:
			self.mahjong.table.new_tile_to_dropzone(0, tile)
			self.mahjong.table.new_tile_to_dropzone(1, tile)
			self.mahjong.table.new_tile_to_dropzone(2, tile)
			self.mahjong.table.new_tile_to_dropzone(3, tile)
		
		self.mahjong.init_player_boxes(["A","B", "C", "D"])
	def tick(self):
		pass
