
import unittest
from unittest import TestCase

from tile import Tile, Chi, Pon
from eval import count_of_tiles_yaku, compute_payment


def tiles(strs):
	return map(Tile, strs)


def chi(tile_name):
	t = Tile(tile_name)
	return Chi(t, t.next_tile(), t.next_tile().next_tile())


def pon(tile_name):
	return Pon(Tile(tile_name))


class EvalHandTestCase(TestCase):

	def test_yaku_count(self):
		hands = [
			([ "WW", "C1", "C1", "C1", "C1", "C2", "C3", "DR", "B9", "DR", "B8", "B7", "DR", "WW" ], [], 1), #0, Yaku-Pai
			([ "DR", "DR", "C1", "C1", "C1", "C2", "C3", "B8", "B9", "WN", "WN", "B7", "DR", "WN" ], [], 1), #1, Yaku-Pai
			([ "C1", "B1", "B9", "C2", "WW", "WW", "WN", "WS", "DR", "DG", "DW", "C5", "P7", "P9" ], [], 0), #2, Nothing
			([ "DG", "DG", "DR", "DW", "DG", "DW", "DW", "DR", "B1", "B2", "B2", "B2", "B1", "DR" ], [], 3), #3, 3x Yaku-Pai
			([ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C2", "C2" ], [], 1), #4, Tan-Yao
			([ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C9", "C9" ], [], 0), #5, Nothing
			([ "WW", "C1", "C1", "C1", "B9", "B8", "B7", "WW" ], [ pon("DR"), chi("C1")], 1), #6, Yaku-Pai
			([ "WW", "C1", "C1", "C1", "B9", "B8", "B7", "WW" ], [ pon("DR"), pon("DG")], 2), #6, 2x Yaku-Pai
		]

		for hand_id, h in enumerate(hands):
			hand, open_sets, r = h
			score = count_of_tiles_yaku(tiles(hand), open_sets)
			self.assert_(score == r, "Hand %i returned score %i" % (hand_id, score))

	def test_basic_payment(self):
		self.assert_(compute_payment(2, 40, "Ron", Tile("WN")) == ("", 2600))
		self.assert_(compute_payment(2, 40, "Ron", Tile("WE")) == ("", 3900))
		self.assertEquals(compute_payment(2, 40, "Tsumo", Tile("WN")), ("", (700,1300)))
		self.assertEquals(compute_payment(2, 40, "Tsumo", Tile("WE")), ("", (1300, 0)))

		self.assert_(compute_payment(1, 40, "Ron", Tile("WN")) == ("", 1300))
		self.assert_(compute_payment(1, 40, "Ron", Tile("WE")) == ("", 2000))
		self.assertEquals(compute_payment(1, 40, "Tsumo", Tile("WN")), ("", (400, 700)))
		self.assertEquals(compute_payment(1, 40, "Tsumo", Tile("WE")), ("", (700, 0)))

		self.assertEquals(compute_payment(4, 20, "Tsumo", Tile("WN")), ("", (1300, 2600)))
		self.assertEquals(compute_payment(4, 20, "Tsumo", Tile("WE")), ("", (2600, 0)))

		self.assertEquals(compute_payment(3, 20, "Tsumo", Tile("WN")), ("", (700, 1300)))
		self.assertEquals(compute_payment(3, 20, "Tsumo", Tile("WE")), ("", (1300, 0)))

		self.assertEquals(compute_payment(5, 40, "Ron", Tile("WN")), ("Mangan", 8000))
		self.assertEquals(compute_payment(5, 40, "Ron", Tile("WE")), ("Mangan", 12000))
		self.assertEquals(compute_payment(5, 40, "Tsumo", Tile("WN")), ("Mangan", (2000, 4000)))
		self.assertEquals(compute_payment(5, 40, "Tsumo", Tile("WE")), ("Mangan", (4000, 0)))

		self.assertEquals(compute_payment(13, 40, "Ron", Tile("WN")), ("Yakuman", 32000))
		self.assertEquals(compute_payment(13, 40, "Ron", Tile("WE")), ("Yakuman", 48000))
		self.assertEquals(compute_payment(13, 40, "Tsumo", Tile("WN")), ("Yakuman", (8000, 16000)))
		self.assertEquals(compute_payment(13, 40, "Tsumo", Tile("WE")), ("Yakuman", (16000, 0)))


if __name__ == '__main__':
    unittest.main()

