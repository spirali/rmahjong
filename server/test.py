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


import unittest
from unittest import TestCase

from tile import Tile, Chi, Pon, all_tiles
from eval import count_of_tiles_yaku, compute_payment, hand_in_tenpai, compute_score, find_tiles_yaku
from botengine import BotEngine


def tiles(strs):
	return map(Tile, strs)


def chi(tile_name):
	t = Tile(tile_name)
	chi = Chi(t, t.next_tile(), t.next_tile().next_tile())
	chi.closed = False
	return chi


def pon(tile_name):
	pon =  Pon(Tile(tile_name))
	pon.closed = False
	return pon


test_hands = [
	([ "WW", "C4", "C4", "C4", "C4", "C2", "C3", "DR", "B9", "DR", "B8", "B7", "DR", "WW" ], [], 1), #0, Yaku-Pai
	([ "DR", "DR", "C1", "C1", "C4", "C2", "C3", "B8", "B9", "WN", "WN", "B7", "DR", "WN" ], [], 1), #1, Yaku-Pai
	([ "C1", "B1", "B9", "C2", "WW", "WW", "WN", "WS", "DR", "DG", "DW", "C5", "P7", "P9" ], [], 0), #2, Nothing
	([ "DG", "DG", "DR", "DW", "DG", "DW", "DW", "DR", "B1", "B2", "B2", "B2", "B1", "DR" ], [], 3), #3, 3x Yaku-Pai
	([ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C2", "C2" ], [], 1), #4, Tan-Yao
	([ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C9", "C9" ], [], 0), #5, Nothing
	([ "WW", "C1", "C1", "C1", "B9", "B8", "B7", "WW" ], [ pon("DR"), chi("C2")], 1), #6, Yaku-Pai
	([ "WW", "C1", "C1", "C1", "B6", "B8", "B7", "WW" ], [ pon("DR"), pon("DG")], 2), #7, 2x Yaku-Pai
	([ "C2", "C3", "C4", "C2", "C3", "C4", "P8", "P8", "P8", "P5", "P6", "P7", "C9", "C9" ], [], 1), #8, Ipeikou
	([ "C2", "C3", "C4", "C2", "C3", "C4", "P8", "P8", "P8", "C9", "C9" ], [ chi("P5") ], 0), #9, Nothing
	([ "C6", "C7", "C8", "B6", "B7", "B8", "P6", "P7", "P8", "C9", "C9", "B1", "B1", "B1" ], [], 2), #10, Sanshoku doujun (closed)
	([ "B6", "B7", "B8", "P6", "P7", "P8", "C9", "C9" ], [ pon("B2"), chi("C6") ], 1 ), #11, Sanshoku doujun (opened)
	([ "C6", "C7", "C8", "B6", "B7", "B8", "P6", "P7", "P8", "C2", "C2", "B6", "B7", "B8" ], [], 4), #12, Sanshoku doujun (closed), Ipeikou, Tan-Yao
	([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P1", "P1", "WN", "WN" ], [], 2), #13, Itsu (closed)
	([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "WE", "WE" ], [ chi("P7") ], 1), #14, Itsu (opened)
	([ "C5", "P3", "P8", "C1", "C4", "P6", "DG", "B9", "WS", "B5", "B5", "P5", "B6", "C6"], [], 0), #15, Nothing
	([ "WN", "B9", "B6", "WN", "B4", "B8", "B5", "B7"], [chi("B1"), chi("P5")], 1), #16, Itsu (opened)
	([ "WW", "C9", "C8", "C7", "C1", "C2", "C3", "B1", "B1", "B1", "B1", "B2", "B3", "WW" ], [], 2), #17, Chanta
	([ "C6", "C9", "C8", "C7", "C1", "C2", "C3", "B1", "B1", "B1", "B1", "B2", "B3", "C6" ], [], 0), #18, Nothing 
	([ "DR", "C9", "C8", "C7", "C1", "C2", "C3", "B1", "B1", "B1", "B4", "B2", "B3", "DR" ], [], 0), #19, Nothing 
	([ "WW", "C9", "C8", "C7", "C1", "C2", "C3", "DR", "DR", "DR", "B1", "B2", "B3", "WW" ], [], 3), #20, Chanta, Yaku-pai
	([ "B9", "C9", "C8", "C7", "C1", "C2", "C3", "B1", "B1", "B1", "B1", "B2", "B3", "B9" ], [], 3), #21, Junchan
	([ "WW", "C1", "C2", "C3", "B7", "B8", "B9", "WW" ], [ pon("B9"), chi("P1") ], 1), #22, Chanta, (open)
	([ "B9", "C1", "C2", "C3", "B1", "B1", "B1", "B9" ], [ pon("P1"), chi("C7") ], 2), #23, Junchan
	([ "WN", "P2", "P3", "P1", "WN", "C3", "C2", "C1" ], [ pon("WE"), chi("C7") ], 1), #24, Chanta (open)
	([ "P2", "P2", "P2", "P2", "P3", "P4", "P9", "P9" ], [ pon("B2"), pon("C2") ], 2), #25, Sanshoku douko
	([ "WN", "WN", "P9", "P9", "P9", "C9", "C9", "C9","C3","C4","C5", "B9","B9", "B9"], [], 2), #26, Sanshoku douko
]


class EvalHandTestCase(TestCase):

	def test_yaku_count(self):
		for hand_id, h in enumerate(test_hands):
			hand, open_sets, r = h
			score = count_of_tiles_yaku(tiles(hand), open_sets, Tile("XX"), Tile("XX"))
			yaku = find_tiles_yaku(tiles(hand), open_sets, Tile("XX"), Tile("XX"))
			self.assert_(score == r, "Hand %i returned score %i %s" % (hand_id, score, yaku))

		hand = [ "WE", "C2", "C2", "C2", "WN", "WN", "WN", "DR", "B9", "DR", "B8", "B7", "WE", "WE" ]
		open_sets = []
		self.assertEquals(count_of_tiles_yaku(tiles(hand), open_sets, Tile("WE"), Tile("WN")), 2)
		self.assertEquals(count_of_tiles_yaku(tiles(hand), open_sets, Tile("WE"), Tile("WE")), 2)
		self.assertEquals(count_of_tiles_yaku(tiles(hand), open_sets, Tile("WE"), Tile("WS")), 1)
		hand = [ "WE", "DW", "DW", "DW", "C4", "C2", "C3", "DR", "B9", "DR", "B8", "B7", "WE", "WE" ]
		self.assertEquals(count_of_tiles_yaku(tiles(hand), open_sets, Tile("WE"), Tile("WS")), 2)

		hand = [ "WN", "B9", "B6", "WN", "B4", "B8", "B5", "B7"]
		open_sets = [chi("B1"), chi("P5")]
		self.assertEquals(count_of_tiles_yaku(tiles(hand), open_sets, Tile("WE"), Tile("WW")), 1)

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

	def test_tenpai(self):
		hands = (([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P1", "P1", "WN"], [], True),
						([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P3", "P1", "WN"], [], False),
						([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "WN"], [ pon("P1") ], True))
		for h, open_sets, tenpai in hands:
			hand = tiles(h)
			self.assertEquals(hand_in_tenpai(hand, open_sets), tenpai)

	def test_score(self):
		hand = [ "WN", "B9", "B6", "WN", "B4", "B8", "B5", "B7"]
		open_sets = [chi("B1"), chi("P5")]
		payment, scores, minipoints = compute_score(tiles(hand), open_sets, "Ron", [], False, Tile("WE"), Tile("WW"))
		self.assertEquals(minipoints, 30)

class BotEngineTestCase(TestCase):

	def test_discard(self):
		e = BotEngine()
		try:
			e.set_blocking()
			h = tiles([ "C1", "C2", "C3", "DR", "DR", "DR", "DG", "DG", "C9", "B1", "B2", "B3", "WN", "WN" ])
			e.set_turns(100)
			e.set_hand(h)
			e.set_sets([])
			e.set_wall(4 * all_tiles)
			e.question_discard()
			tile = e.get_tile()
			self.assert_(tile in h)
		finally:
			e.shutdown()

	def test_discard_with_open_sets(self):
		e = BotEngine()
		try:
			e.set_blocking()
			h = tiles([ "DG", "DG", "C9", "B1", "B2", "B3", "WN", "WN" ])
			e.set_turns(30)
			e.set_hand(h)
			e.set_sets([chi("C1"), pon("DR")])
			e.set_wall(4 * all_tiles)
			e.question_discard()
			tile = e.get_tile()
			self.assert_(tile in h)
		finally:
			e.shutdown()

	def test_bot_yaku_count(self):
		e = BotEngine()
		try:
			e.set_blocking()
			for hand_id, h in enumerate(test_hands):
				hand, open_sets, r = h
				e.set_hand(tiles(hand))
				e.set_sets(open_sets)
				e.question_yaku()
				score = e.get_int() 
				self.assert_(score == r, "Hand %i returned score %i" % (hand_id, score))
		
		finally:
			e.shutdown()

	def test_bot_yaku_count2(self):
		e = BotEngine()
		try:
			e.set_blocking()
			hand = [ "WE", "C1", "C1", "C1", "DR", "B9", "DR", "B8", "B7", "WE", "WE" ]
			e.set_hand(tiles(hand))
			e.set_sets([ pon("WN") ])

			e.set_round_wind(Tile("WE"))
			e.set_player_wind(Tile("WN"))
			e.question_yaku()
			self.assertEquals(e.get_int(), 2)

			e.set_round_wind(Tile("WE"))
			e.set_player_wind(Tile("WE"))
			e.question_yaku()
			self.assertEquals(e.get_int(), 2)

			e.set_round_wind(Tile("WE"))
			e.set_player_wind(Tile("WS"))
			e.question_yaku()
			self.assertEquals(e.get_int(), 1)

			e.set_sets([ pon("DW") ])
			e.set_round_wind(Tile("WE"))
			e.set_player_wind(Tile("WS"))
			e.question_yaku()
			self.assertEquals(e.get_int(), 2)

		finally:
			e.shutdown()


if __name__ == '__main__':
    unittest.main()

