
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

