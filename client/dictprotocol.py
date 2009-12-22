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


class DictProtocol:

	def __init__(self, connection):
		self.connection = connection
		self.buffer = {}

	def close(self):
		self.connection.close()

	def send_message(self, **kw):
		self.send_dict(kw)		

	def send_dict(self, data):
		msg_list = [ "%s|%s\n" % key_value for key_value in data.items() ]
		msg_list.append("|\n")
		self.connection.send("".join(msg_list))
	
	def read_message(self):
		while True:
			line = self.connection.read_line()
			if line:
				if line == "|":
					buffer = self.buffer
					self.buffer = {}
					return buffer
				key, value = line.split("|", 1)
				self.buffer[key] = value
			else:
				return None
