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

from tile import Tile, Chi, Pon, Kan, all_tiles
from eval import count_of_tiles_yaku, compute_payment, hand_in_tenpai, compute_score, find_tiles_yaku, riichi_test
from eval import find_waiting_tiles, check_single_waiting
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

def kan(tile_name):
	kan =  Kan(Tile(tile_name))
	kan.closed = False
	return kan

def ckan(tile_name):
	kan =  Kan(Tile(tile_name))
	kan.closed = True
	return kan


test_hands = [
	([ "WW", "C4", "C4", "C4", "C4", "C2", "C3", "DR", "B9", "DR", "B8", "B7", "DR", "WW" ], [], 1), #0, Yaku-Pai
	([ "DR", "DR", "C1", "C1", "C4", "C2", "C3", "B8", "B9", "WN", "WN", "B7", "DR", "WN" ], [], 1), #1, Yaku-Pai
	([ "C1", "B1", "B9", "C2", "WW", "WW", "WN", "WS", "DR", "DG", "DW", "C5", "P7", "P9" ], [], 0), #2, Nothing
	([ "C1", "C1", "DW", "C1", "DW", "DW", "B1", "P2", "P2", "P2", "B1" ], [ kan("DR") ], 6), #3, 2x Yaku-Pai, San-anko, Toitoiho
	([ "C2", "C3", "C4", "B2", "B2", "B2", "P8", "P8", "P8", "P5", "P6", "P7", "C2", "C2" ], [], 1), #4, Tan-Yao
	([ "C2", "C3", "C4", "B3", "B3", "B4", "P8", "P8", "P8", "P5", "P6", "P7", "C9", "C9" ], [], 0), #5, Nothing
	([ "WW", "C1", "C1", "C1", "B9", "B8", "B7", "WW" ], [ pon("DR"), chi("C2")], 1), #6, Yaku-Pai
	([ "WW", "C1", "C1", "C1", "B9", "B8", "B7", "WW" ], [ ckan("DR"), chi("C3")], 1), #7, Yaku-Pai
	([ "WW", "C1", "C1", "C1", "B6", "B8", "B7", "WW" ], [ pon("DR"), pon("DG")], 2), #8, 2x Yaku-Pai
	([ "WW", "C1", "C1", "C1", "B6", "B8", "B7", "WW" ], [ ckan("DR"), ckan("DG")], 4), #9, 2x Yaku-Pai, San-anko
	([ "C2", "C3", "C4", "C2", "C3", "C4", "P8", "P8", "P8", "P5", "P6", "P7", "C9", "C9" ], [], 1), #10, Ipeikou
	([ "C2", "C3", "C4", "C2", "C3", "C4", "P8", "P8", "P8", "C9", "C9" ], [ chi("P5") ], 0), #11, Nothing
	([ "C6", "C7", "C8", "B6", "B7", "B8", "P6", "P7", "P8", "C9", "C9", "B1", "B1", "B1" ], [], 2), #12, Sanshoku doujun (closed)
	([ "C6", "C7", "C8", "B6", "B7", "B8", "P6", "P7", "P8", "C9", "C9" ], [ ckan("C8") ], 2), #13, Sanshoku doujun (closed)
	([ "B6", "B7", "B8", "P6", "P7", "P8", "C9", "C9" ], [ pon("B2"), chi("C6") ], 1 ), #14, Sanshoku doujun (opened)
	([ "B6", "B7", "B8", "P6", "P7", "P8", "C9", "C9" ], [ ckan("B2"), chi("C6") ], 1 ), #15, Sanshoku doujun (opened)
	([ "C6", "C7", "C8", "B6", "B7", "B8", "P6", "P7", "P8", "C2", "C2", "B6", "B8", "B7" ], [], 4), #16, Sanshoku doujun (closed), Ipeikou, Tan-Yao, Pinfu
	([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P1", "P1", "WN", "WN" ], [], 2), #17, Itsu (closed)
	([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "WN", "WN" ], [ ckan("P1") ], 2), #18, Itsu (closed)
	([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "WE", "WE" ], [ chi("P7") ], 1), #19, Itsu (opened)
	([ "C5", "P3", "P8", "C1", "C4", "P6", "DG", "B9", "WS", "B5", "B5", "P5", "B6", "C6"], [], 0), #20, Nothing
	([ "C5", "P3", "P8", "C1", "C4", "P6", "DG", "B9", "WS", "B6", "C6"], [ ckan("B5") ], 0), #21, Nothing
	([ "WN", "B9", "B6", "WN", "B4", "B8", "B5", "B7"], [chi("B1"), chi("P5")], 1), #22, Itsu (opened)
	([ "WW", "C9", "C8", "C7", "C1", "C2", "C3", "B1", "B1", "B1", "B1", "B2", "B3", "WW" ], [], 2), #23, Chanta
	([ "C6", "C9", "C8", "C7", "C1", "C2", "C3", "B1", "B1", "B1", "B1", "B2", "B3", "C6" ], [], 0), #24, Nothing 
	([ "DR", "C9", "C8", "C7", "C1", "C2", "C3", "B1", "B1", "B1", "B4", "B2", "B3", "DR" ], [], 0), #25, Nothing 
	([ "WW", "C9", "C8", "C7", "C1", "C2", "C3", "DR", "DR", "DR", "B1", "B2", "B3", "WW" ], [], 3), #26, Chanta, Yaku-pai
	([ "B9", "C9", "C8", "C7", "C1", "C2", "C3", "B1", "B1", "B1", "B1", "B2", "B3", "B9" ], [], 3), #27, Junchan
	([ "WW", "C1", "C2", "C3", "B7", "B8", "B9", "WW" ], [ pon("B9"), chi("P1") ], 1), #28, Chanta, (open)
	([ "B9", "C1", "C2", "C3", "B1", "B1", "B1", "B9" ], [ pon("P1"), chi("C7") ], 2), #29, Junchan
	([ "WN", "P2", "P3", "P1", "WN", "C3", "C2", "C1" ], [ pon("WE"), chi("C7") ], 1), #30, Chanta (open)
	([ "P2", "P2", "P2", "P2", "P3", "P4", "P9", "P9" ], [ pon("B2"), pon("C2") ], 2), #31, Sanshoku douko
	([ "WW", "C1", "C2", "C3", "B7", "B8", "B9", "WW" ], [ ckan("B9"), chi("P1") ], 1), #32, Chanta, (open)
	([ "B9", "C1", "C2", "C3", "B1", "B1", "B1", "B9" ], [ ckan("P1"), chi("C7") ], 2), #33, Junchan
	([ "WN", "P2", "P3", "P1", "WN", "C3", "C2", "C1" ], [ ckan("WE"), chi("C7") ], 1), #34, Chanta (open)
	([ "P2", "P2", "P2", "P2", "P3", "P4", "P9", "P9" ], [ ckan("B2"), ckan("C2") ], 4), #35, Sanshoku douko, San-anko
	([ "WN", "WN", "P9", "P9", "P9", "C9", "C9", "C9","C3","C4","C5", "B9","B9", "B9"], [], 4), #36, Sanshoku douko, San-anko
	([ "WS", "WS", "P9", "P9", "P9", "P9", "P1", "P1","DR","DR","B3", "B3","B4", "B4"], [], 0), #37, Nothing 
	([ "WS", "WS", "P1", "P1","DR","DR","B3", "B3","B4", "B4"], [ ckan("P9") ], 0), #38, Nothing 
	([ "DR", "DR", "P1", "P2", "P3","WE","WE","WE"], [ ckan("P9"), chi("P2") ], 2), #39, Honitsu 
	([ "WS", "WS", "P9", "P9", "P9", "P1", "P2", "P3","WE","WE","WE", "P3","P4", "P5"], [], 3), #40, Honitsu 
	([ "P2", "P2", "P1", "P2", "P3","P4","P5","P6"], [ ckan("P9"), chi("P6") ], 5), #41, Chinitsu 
	([ "B1", "B1", "P1", "P2", "P3","P4","P5","P6"], [ ckan("P9"), chi("P6") ], 0), #42, Nothing
	([ "P2", "P2", "P9", "P9", "P9", "P1", "P2", "P3","P8","P8","P8", "P3","P4", "P5"], [], 6), #43, Chinitsu 
	([ "P2", "P2", "P8", "P8", "P8", "P3", "P3", "P3", "P6","P7","P8", "P3","P4", "P5"], [], 7), #44, Chinitsu, tanyao
	([ "P1", "P1", "P1", "P2", "P3", "P9","P7","P8", "P9","P9", "P9"], [ ckan("DR") ], 6), #45, Honitsu, Chanta, Yaku-pai
	([ "WS", "WS", "P9","P7","P8", "P9","P9", "P9"], [ pon("P1"), ckan("DR") ], 4), #46, Honitsu, Chanta, Yaku-pai
	([ "WW", "C1", "C2", "C3", "WW" ], [ pon("B9"), pon("P1"), pon("C2") ], 0), #47, Nothing 
	([ "B2", "B2" ], [ pon("B9"), pon("P1"), ckan("C2"), ckan("B5") ], 2), #48, Toitoi 
	([ "B2", "B2" ], [ ckan("B8"), pon("P1"), ckan("C2"), ckan("B5") ], 4), #49, Toitoi, San-anko
	([ "P2", "P2", "P2", "P9", "P9" ], [ kan("B1"), ckan("B2"), ckan("C2") ], 6), #50, Sanshoku douko, San-anko, Toitoi
	([ "P4", "P4", "C6", "P3", "C5", "B7", "B6", "P1", "B8", "B8" ], [ ckan("WE") ], 0), #51, Nothing
	([ "C6", "C8", "B7", "B8", "B9", "P1", "P2", "P3", "C2", "C2", "B6", "B7", "B9" ], [], 0), #52, Nothing
	([ "C6", "C7", "C8", "B7", "B8", "B9", "P1", "P2", "P3", "DR", "DR", "B6", "B7", "B8" ], [], 0), #53, Nohthing
	([ "C6", "C7", "C8", "B7", "B8", "B9", "P1", "P2", "P3", "C2", "C2", "B6", "B7", "B8" ], [], 0), #54, Nothing
	([ "C6", "C7", "C8", "B7", "B8", "B9", "P2", "P3", "C2", "C2", "B3", "B4", "B5", "P1" ], [], 0), #55, Nothing
	([ "C6", "C7", "C8", "B7", "B8", "B9", "P1", "P2", "P3", "WW", "B6", "B7", "B8", "WW" ], [], 0), #56, Nothing
	([ "C6", "C7", "C8", "B2", "B3", "B4", "P1", "P2", "P3", "C2", "C2", "B7", "B8", "B9" ], [], 0), #57, Nothing
	([ "DR", "DR", "DR", "B3", "B4", "B2", "P2", "P2" ], [ ckan("DW"), pon("DG") ], 13), #58, dai-sangen
	([ "WE", "WE", "WE", "B3", "B4", "B2", "WN", "WN" ], [ ckan("WW"), pon("WS") ], 13), #59, shou-suushi
	([ "WE", "WE", "WE", "C9", "C9", "WN", "WN", "WN" ], [ ckan("WW"), pon("WS") ], 13), #60, dai-suushi
	([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "WN", "WN" ], [ kan("P1") ], 1), #61, Itsu (opened)
	([ "B1", "B1", "B1", "C2", "C2", "C2", "C9", "C9", "C9", "WW", "WW" ], [ ckan("DR") ], 13), #62, suu-ankou
	([ "C1", "C1", "C1", "C9", "C9", "C9", "B9", "B9", "B1", "B1", "B1" ], [ kan("P9") ], 13), #63, Chinroutou
	([ "DG", "DG", "B2", "B3", "B4", "B4", "B4", "B4", ], [ kan("B6"), pon("B8") ], 13), #64, ryuu-iisou
	([ "DG", "DG", "DG", "WE", "WE", "WN", "WN", "WN", ], [ kan("DR"), pon("WW") ], 13), #65, tsu-iisou
	([ "C1", "C1", "C1", "C5", "C6", "C7", "C8", "C9", "C9", "C9", "C3"], [ chi("C2") ], 0), #66, Nothing
	([ "B1", "B1", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B1"], [ pon("B9") ], 0), #67, Nothing 
	([ "P1", "P1", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P9", "P9", "B9"], [], 0), #68, Nohting


	# --------- Ignored by bot (because kan and pon are the same for bot)
	([ "B6", "B6" ], [ kan("B5"), kan("P3"), ckan("WE"), ckan("C9") ], 13), #63, suu-kantsu

	# -----Pinfu hands --------- Ignored by bot eval (bot don't see pinfu yet)
	([ "C6", "C7", "C8", "B6", "B7", "B8", "P6", "P7", "P8", "C2", "C2", "B6", "B7", "B8" ], [], 5), #X, Sanshoku doujun (closed), Ipeikou, Tan-Yao, Pinfu
	([ "C6", "C7", "C8", "B7", "B8", "B9", "P1", "P2", "P3", "C2", "C2", "B7", "B8", "B6" ], [], 1), #X, Pinfu
	([ "C6", "C7", "C8", "B7", "B8", "B9", "P1", "P2", "P3", "C2", "C2", "C3", "C4", "C5" ], [], 1), #X, Pinfu


	# -----Special hands --------- Ignored by bot eval
	([ "WE", "WE", "P9", "P9", "C9", "C9", "P1", "P1", "DR", "DR", "B3", "B3", "B4", "B4"], [], 2), #X, Chii toitsu
	([ "C3", "C3", "P8", "P8", "C7", "C7", "P5", "P5", "P6", "P6", "B3", "B3", "B4", "B4"], [], 3), #X, Chii toitsu, tanyao
	([ "WE", "WE", "P9", "P9", "P8", "P8", "P1", "P1", "DR", "DR", "P3", "P3", "P4", "P4"], [], 5), #X, Chii toitsu, honitsu
	([ "B1", "B1", "B8", "B8", "B7", "B7", "B5", "B5", "B6", "B6", "B3", "B3", "B4", "B4"], [], 8), #X, Chii toitsu, chinitsu
	([ "DR", "DR", "DG", "DG", "DW", "DW", "WE", "WE", "WW", "WW", "WN", "WN", "WS", "WS"], [], 13), #X, Tsu-iisou
	([ "C1", "C1", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C9", "C9", "C5"], [], 13), #X, Chuuren-pootoo
	([ "B1", "B1", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B9", "B9", "B1"], [], 13), #X, Chuuren-pootoo
	([ "P1", "P1", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P9", "P9", "P9"], [], 13), #X, Chuuren-pootoo
]


class EvalHandTestCase(TestCase):

	def test_yaku_count(self):
		for hand_id, h in enumerate(test_hands):
			hand, sets, r = h
			score = count_of_tiles_yaku(tiles(hand), sets, [], Tile("XX"), Tile("XX"), "Ron")
			yaku = find_tiles_yaku(tiles(hand), sets, [], Tile("XX"), Tile("XX"), "Ron")
			self.assert_(score == r, "Hand %i returned score %i %s hand=%s" % (hand_id, score, yaku, hand))

		hand = [ "WE", "C2", "C3", "C4", "WN", "WN", "WN", "DR", "B9", "DR", "B8", "B7", "WE", "WE" ]
		sets = []
		self.assertEquals(count_of_tiles_yaku(tiles(hand), sets, [], Tile("WE"), Tile("WN"), "Ron"), 2)
		self.assertEquals(count_of_tiles_yaku(tiles(hand), sets, [], Tile("WE"), Tile("WN"), "Tsumo"), 3)
		self.assertEquals(count_of_tiles_yaku(tiles(hand), sets, [], Tile("WE"), Tile("WE"), "Ron"), 2)
		self.assertEquals(count_of_tiles_yaku(tiles(hand), sets, [], Tile("WE"), Tile("WS"), "Ron"), 1)
		hand = [ "WE", "DW", "DW", "DW", "C4", "C2", "C3", "DR", "B9", "DR", "B8", "B7", "WE", "WE" ]
		self.assertEquals(count_of_tiles_yaku(tiles(hand), sets, [], Tile("WE"), Tile("WS"), "Ron"), 2)

		hand = [ "WN", "B9", "B6", "WN", "B4", "B8", "B5", "B7"]
		sets = [chi("B1"), chi("P5")]
		self.assertEquals(count_of_tiles_yaku(tiles(hand), sets, [], Tile("WE"), Tile("WW"), "Ron"), 1)
		self.assertEquals(count_of_tiles_yaku(tiles(hand), sets, [], Tile("WE"), Tile("WW"), "Tsumo"), 1)

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
		hands = (([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P1", "P1", "WN"], [], True, ["WN"]),
						([ "B3", "B3", "B2", "B2", "C9", "C9", "WW", "WW", "DR", "DR", "P1", "P1", "WN"], [], True, ["WN"]),
						([ "B3", "B3", "B2", "B2", "C9", "C9", "WW", "WW", "DR", "DR", "P1", "P7", "WN"], [], False, []),
						([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P3", "P1", "WN"], [], False, []),
						([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "WN", "WN"], [ pon("P1") ], True, ["B3","B6","B9"]),
						([ "P1", "P2", "P3", "DR", "DR", "DR", "B7", "B8", "WN", "WN"], [ pon("P1") ], True, ["B6", "B9"]),
						([ "P1", "P2", "P3", "DR", "DR", "DR", "B7", "B9", "WN", "WN"], [ pon("P1") ], True, ["B8"]))

		for h, sets, tenpai, w in hands:
			self.assertEquals(hand_in_tenpai(tiles(h), sets), tenpai)
			waiting = [ t.name for t in find_waiting_tiles(tiles(h), sets) ]
			waiting.sort()
			self.assertEquals(waiting, w)

	def test_riichi(self):
		hands = (([ "P5", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P1", "P1", "WN"], [], True),
					([ "B3", "B3", "B2", "B2", "C9", "C9", "WW", "WW", "DR", "DR", "P1", "P1", "WN", "WN"], [], True),
					([ "B3", "B3", "B2", "B2", "C9", "C9", "WW", "WW", "DR", "DR", "P1", "P7", "WN", "DR"], [], False),
					([ "P7", "P8", "P9", "P1", "P2", "P3", "WS", "WS", "B8", "B7", "P2", "C7", "C8", "DR"], [], False), 
					([ "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P3", "P1", "WN", "DG"], [], False),
					([ "P4", "P4", "P4", "C6", "C4", "C5", "B7", "B6", "B8", "B8", "DR" ], [ ckan("WE") ], True),	
					([ "P4", "P4", "C6", "P3", "C5", "B7", "B6", "P1", "DR", "B8", "DR" ], [ ckan("WE") ], False))
		for h, sets, riichi in hands:
			self.assertEquals(riichi_test(tiles(h), sets), riichi, [h,sets])

	def test_singlewait(self):
		hands = (([  "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P1", "P1", "WN", "WN"], [], True),
				([  "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P1", "WN", "WN", "WN"], [], False),
				([  "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P1", "P1", "P2", "P3"], [], False),
				([  "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P1", "P3", "P2", "P1"], [], True),
				([  "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P1", "C7", "C8", "C9"], [], True),
				([  "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P1", "C6", "C7", "C8"], [], False),
				([  "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "P1", "P1", "P3", "P1", "P2"], [], True))
		for h, sets, singlewait in hands:
			self.assertEquals(check_single_waiting(tiles(h), sets), singlewait)


	def test_score(self):
		hand = [ "WN", "B9", "B6", "WN", "B4", "B8", "B5", "B7"]
		sets = [chi("B1"), chi("P5")]
		payment, scores, minipoints = compute_score(tiles(hand), sets, "Ron", ([], [ Tile("B7") ]), [], Tile("WE"), Tile("WW"))
		self.assertEquals(payment, ('', 2000))
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
			action = e.get_string()
			self.assert_(action == "Discard")
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
			action = e.get_string()
			self.assert_(action == "Discard")
			tile = e.get_tile()
			self.assert_(tile in h)
		finally:
			e.shutdown()

	def test_bot_yaku_count(self):
		e = BotEngine()
		try:
			e.set_blocking()
			# Remove last 8 tests (Hand: seven pairs), bot "question_yaku" detect only "normal sets"
			# + 3 next hand because bot don't see pinfu yet
			# + 1 beacause bot see kan as pon
			for hand_id, h in enumerate(test_hands[:-12]): 
				hand, sets, r = h
				e.set_hand(tiles(hand))
				e.set_sets(sets)
				e.question_yaku()
				score = e.get_int() 
				self.assert_(score == r, "Hand %i returned score %i" % (hand_id, score))
		
		finally:
			e.shutdown()

	def test_bot_yaku_count2(self):
		e = BotEngine()
		try:
			e.set_blocking()
			hand = [ "WE", "C2", "C3", "C4", "DR", "B9", "DR", "B8", "B7", "WE", "WE" ]
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

	def test_nine_lanterns(self):
		e = BotEngine()
		try:
			e.set_blocking()
			h = tiles([ "C1", "C1", "C1", "C2", "C3", "C4", "B1", "C6", "C7", "C8", "C9", "C9", "B1", "B1" ])
			e.set_hand(h)
			e.set_turns(12)
			e.set_sets([])
			wall = 3 * all_tiles
			e.set_wall(wall)
			e.question_discard_tiles()
			tile_list = e.get_tiles()
			self.assertEquals(tile_list, [Tile("B1"), Tile("B1"), Tile("B1")])
		finally:
			e.shutdown()

	def test_seven_pairs(self):
		e = BotEngine()
		try:
			e.set_blocking()
			h = tiles([ "C1", "C1", "C2", "C2", "C3", "C3", "B2", "B2", "B4", "B4", "P3", "P4", "DR", "DR" ])
			e.set_hand(h)
			e.set_turns(3)
			e.set_sets([])
			wall = 3 * all_tiles
			wall.remove(Tile("P4"))
			wall.remove(Tile("B2"))
			wall.remove(Tile("C3"))
			wall.remove(Tile("C3"))
			e.set_wall(wall)
			e.question_discard_tiles()
			tile_list = e.get_tiles()
			self.assertEquals(tile_list, [Tile("P4")])
			h = tiles([ "C8", "C8", "C2", "C2", "C3", "C3", "B2", "B2", "B4", "B4", "P1", "P4", "B5", "B5" ])
			e.set_hand(h)
			e.question_discard_tiles()
			tile_list = e.get_tiles()
			self.assertEquals(tile_list, [Tile("P1")])

			wall = 3 * all_tiles
			wall.remove(Tile("WW"))
			wall.remove(Tile("WW"))
			wall.remove(Tile("C1"))
			e.set_turns(12)
			e.set_wall(wall)
			h = tiles([ "DR", "DR", "DW", "DW", "DG", "DG", "WE", "WE", "WW", "C9", "WN", "WN", "WS", "WS" ])
			e.set_hand(h)
			e.question_discard_tiles()
			tile_list = e.get_tiles()
			self.assertEquals(tile_list, [Tile("C9")])

		finally:
			e.shutdown()

	def test_kan(self):
		e = BotEngine()
		try:
			e.set_blocking()
			e.set_turns(3)
			e.set_sets([])
			wall = 3 * all_tiles
			e.set_wall(wall)
			h = tiles([ "C1", "C2", "C3", "P9", "P9", "P9", "P9", "B1", "B1", "B1", "P1", "P3", "DR", "DR" ])
			e.set_hand(h)
			e.question_discard()

			action = e.get_string()
			self.assert_(action == "Kan")
			tile = e.get_tile()
			self.assertEquals(tile, Tile("P9"))

			h = tiles([ "C1", "C2", "C3", "P9", "P9", "P9", "P9", "P7", "P8",  "P1", "P3", "DR", "DR", "C5" ])
			e.set_hand(h)
			e.question_discard()
			action = e.get_string()
			self.assert_(action == "Discard")
			tile = e.get_tile()
			self.assertEquals(tile, Tile("C5"))

		finally:
			e.shutdown()


if __name__ == '__main__':
    unittest.main()

