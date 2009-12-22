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


class Direction:
	def __init__(self, name, dir_id, vertical, dir_vector, angle):
		self.dir_id = dir_id
		self.vertical = vertical
		self.name = name
		self.dir_vector = dir_vector
		self.angle = angle

	def is_vertical(self):
		return self.vertical

	def is_horizontal(self):
		return not self.vertical

	def move_up(self, point, size):
		vx, vy = self.dir_vector
		return (point[0] + size * vx, point[1] + size * vy)

	def move_down(self, point, size):
		vx, vy = self.dir_vector
		return (point[0] - size * vx, point[1] - size * vy)

	def move_left(self, point, size):
		vx, vy = self.dir_vector
		return (point[0] + size * vy, point[1] - size * vx)

	def move_right(self, point, size):
		vx, vy = self.dir_vector
		return (point[0] - size * vy, point[1] + size * vx)


direction_up = Direction("up", 0, True, (0, -1), 0)
direction_down = Direction("down", 2, True, (0, 1), 180)
direction_left = Direction("left", 3, False, (-1, 0), 90)
direction_right = Direction("right", 1, False, (1, 0), 270)

direction_up.next = direction_right
direction_right.next = direction_down
direction_down.next = direction_left
direction_left.next = direction_up

for d in [ direction_up, direction_down, direction_left, direction_right ]:
	d.prev = d.next.next.next
