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


from subprocess import PIPE, Popen
from threading import Thread, Lock
import queue
from tile import Tile, Pon, Chi

BOT_PATH = "../bot/bot"


class BotEngineException(Exception):
	pass

class BotEngineThread(Thread):

	def __init__(self, queue, process_out):
		Thread.__init__(self)
		self.daemon = True
		self.queue = queue
		self.process_out = process_out
		self.thread_quit = False

	def run(self):
		while not self.thread_quit:
			line = self.process_out.readline().decode()
			self.queue.put(line, True)

class BotEngine():

	def __init__(self):
		self.queue = queue.Queue(3)
		self.process = Popen([ BOT_PATH ], bufsize = 0, stdin = PIPE, stdout = PIPE)
		self.nonblocking = True
		self.process_out = self.process.stdout
		self.process_in = self.process.stdin
		self.thread = BotEngineThread(self.queue, self.process_out)
		self.thread.start()

	def shutdown(self):
		self.thread.thread_quit = True
		self.process.stdin.close()
		self.process.stdout.close()
		self.process.terminate()
		self.process.wait()
		#self._write("QUIT\n")
		#self.join()

	def get_tile(self, blocking = False):
		if self._is_next_line() or blocking:
			return Tile(self._read_line().strip())
		else:
			return None

	def get_string(self, blocking = False):
		if self._is_next_line() or blocking:
			return self._read_line().strip()
		else:
			return None

	def get_tiles(self, blocking = False):
		if self._is_next_line() or blocking:
			return [*map(Tile, (self._read_line().strip().split()))]
		else:
			return None

	def get_int(self, blocking = False):
		if self._is_next_line() or blocking:
			return int(self._read_line().strip())
		else:
			return None

	def get_set_or_pass(self):
		if self._is_next_line():
			line = self._read_line().strip()
			if "Pass" == line:
				return line
			tp, tile_name = line.split()
			tile = Tile(tile_name)
			if tp == "Chi":
				next_tile = tile.next_tile()
				return Chi(tile, next_tile, next_tile.next_tile())
			else:
				return Pon(tile)
		else:
			return None

	def set_blocking(self):
		self.nonblocking = False

	def set_hand(self, tiles):
		self._write("HAND\n")
		self._set_tiles(tiles)

	def set_turns(self, turns):
		self._write("TURNS\n%d\n" % turns)

	def set_wall(self, tiles):
		self._write("WALL\n")
		self._set_tiles(tiles)

	def set_doras(self, doras):
		self._write("DORAS\n")
		self._set_tiles(doras)

	def set_closed_kans(self, closed_kans):
		self._write("CLOSED_KANS\n")
		self._set_tiles([ kan.tile for kan in closed_kans ])

	def set_round_wind(self, tile):
		self._write("ROUND_WIND\n" + tile.name + "\n")

	def set_player_wind(self, tile):
		self._write("PLAYER_WIND\n" + tile.name + "\n")

	def set_open_sets(self, sets):
		self._write("OPEN_SETS\n")
		self._write_sets(sets)

	def set_sets(self, sets):
		self.set_open_sets( [ set for set in sets if not set.closed ] )
		self.set_closed_kans( [ set for set in sets if set.closed ] )

	def question_discard(self):
		self._write("DISCARD\n")

	def question_discard_and_target(self):
		self._write("DISCARD_AND_TARGET\n")

	def question_discard_tiles(self):
		self._write("DISCARD_TILES\n")

	def question_yaku(self):
		self._write("YAKU\n")

	def question_steal(self, tile, sets):
		self._write("STEAL\n")
		self._write(tile.name + "\n")
		self._write_sets(sets)

	def _write(self, string):
		self.process_in.write(string.encode())

	def _set_tiles(self, tiles):
		message = " ".join((tile.name for tile in tiles))
		self._write(message + "\n")

	def _write_sets(self, sets):
		for set in sets:
			self._write("%s %s " % (set.get_name(), set.get_representative_tile().name))
		self._write("\n")

	def _read_line(self):
		line = self.queue.get()
		if line[:5] == "Error":
			raise BotEngineException(line)
		return line

	def _is_next_line(self):
		return not self.queue.empty() or not self.nonblocking
