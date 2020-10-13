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


import socket
import select
import string

class ConnectionClosed(Exception):
	pass


class Connection:
	def __init__(self, sock = None):
		if sock == None:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket = sock

	def connect(self, addr, port):
		return self.socket.connect_ex((addr, port)) == 0

	def bind_and_listen(self, port, reuse_addr = False):
		if reuse_addr:
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(('0.0.0.0', port))
		self.socket.listen(5)

	def is_read_ready(self):
		return len(select.select([self.socket], [], [], 0)[0]) > 0

	def wait_for_read(self, timeout = None):
		return len(select.select([self.socket], [], [], timeout)[0]) > 0

	def accept(self):
		if self.is_read_ready():
			return Connection(self.socket.accept()[0])
		else:
			return None

	def close(self):
		self.socket.close()

	def read_line(self):
		# TODO: Handle long lines
		try:
			if self.is_read_ready():
				buf = []
				while True:
					char = self.socket.recv(1).decode()
					if char == '\n':
						return "".join(buf)
					if char == '':
						raise ConnectionClosed()
					buf.append(char)
		except socket.error as e:
			raise ConnectionClosed()

	def send(self, string):
		try:
			self.socket.send(string.encode())
		except socket.error as e:
			raise ConnectionClosed()

	def get_peer_name(self):
		return self.socket.getpeername()[0]

	def get_peer_port(self):
		return self.socket.getpeername()[1]
