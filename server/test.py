
import unittest
from unittest import TestCase

from tile import Tile
from eval import count_of_tiles_yaku


def tiles(strs):
	return map(Tile, strs)


class EvalHandTestCase(TestCase):

	def test_yaku_count(self):
		hands = [
			([ "WW", "C1", "C1", "C1", "C1", "C2", "C3", "DR", "B9", "DR", "B8", "B7", "DR", "WW" ], 1), #0, Yaku-Pai
			([ "DR", "DR", "C1", "C1", "C1", "C2", "C3", "B8", "B9", "WN", "WN", "B7", "DR", "WN" ], 1), #1, Yaku-Pai
			([ "C1", "B1", "B9", "C2", "WW", "WW", "WN", "WS", "DR", "DG", "DW", "C5", "P7", "P9" ], 0), #2, Nothing
			([ "DG", "DG", "DR", "DW", "DG", "DW", "DW", "DR", "B1", "B2", "B2", "B2", "B1", "DR" ], 3), #3, 3x Yaku-Pai
			([ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C2", "C2" ], 1), #4, Tan-Yao
			([ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C9", "C9" ], 0), #5, Nothing
		]

		for hand_id, h in enumerate(hands):
			hand, r = h
			score = count_of_tiles_yaku(tiles(hand))
			self.assert_(score == r, "Hand %i returned score %i" % (hand_id, score))
		self.assert_(all(map(lambda i: count_of_tiles_yaku(tiles(i[0])) == i[1], hands)))

if __name__ == '__main__':
    unittest.main()

