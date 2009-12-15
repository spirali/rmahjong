
import time 

from states import LobbyState, ScoreState
from player import BotPlayer


class Server:

	def __init__(self, port):
		self.players = []
		self.players.append(BotPlayer(self))
		self.players.append(BotPlayer(self))
		self.players.append(BotPlayer(self))
		self.game = None
		self.round = None
		self.state = LobbyState(self, port)
		self.state.enter_state()

	def set_state(self, state):
		self.state.leave_state()
		self.state = state
		self.state.enter_state()

	def set_game(self, game):
		self.game = game

	def start_new_round(self):
		self.round = self.game.new_round()

	def add_player(self, player):
		self.players.append(player)

	def remove_player(self, player):
		self.players.remove(player)

	def player_leaved(self, player):
		self.state.player_leaved(player)
		self.remove_player(player)
	
	def player_tick(self):
		for player in self.players[:]:
			player.tick()

	def run(self):
		try:
			while True:
				self.state.tick()
				self.player_tick()
				time.sleep(0.07)
		finally:
			self.server_quit()

	def server_quit(self):
		for player in self.players:
			player.server_quit()

	def declare_win(self, player, wintype):
		self.set_state(ScoreState(self, player, wintype))

	def player_is_ready(self, player):
		self.state.player_is_ready(player)

	def player_try_steal_tile(self, player, action, chi_choose):
		self.state.player_try_steal_tile(player, action, chi_choose)

server = Server(4500)
server.run()
