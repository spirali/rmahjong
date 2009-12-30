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


from tile import Pon, Chi
from tile import red_dragon, white_dragon, green_dragon
from tile import bamboos, chars, pins, all_tiles
from copy import copy

def find_tiles_yaku(hand, open_sets, round_wind, player_wind):
	for pair, rest in detect_pairs(hand):
		sets = find_sets(rest, open_sets)
		if sets:
			return eval_sets(pair, sets, round_wind, player_wind)
	return []


def count_of_tiles_yaku(hand, open_sets, round_wind, player_wind):
	score = find_tiles_yaku(hand, open_sets, round_wind, player_wind)
	return sum(map(lambda r: r[1], score))


scoring_table = {
	20: [ None, 1400, 2600, 5200 ],
	25: [ None, 1600, 3200, 6400 ],
	30: [ 1000, 2000, 3900, 7700 ],
	40:	[ 1300, 2600, 5200, 8000 ],
	50: [ 1600, 3200, 6400, 8000 ],
	60: [ 2000, 3900, 7700, 8000 ],
	70: [ 2300, 4500, 8000, 8000 ],
	80: [ 2600, 5200, 8000, 8000 ],
	90: [ 2900, 5800, 8000, 8000 ],
	100:[ 3200, 6400, 8000, 8000 ]
}

limited_hands = {
	5: ("Mangan", 8000),
    6: ("Haneman", 12000),
    7: ("Haneman", 12000),
    8: ("Baiman", 16000),
    9: ("Baiman", 16000),
   10: ("Baiman", 16000),
   11: ("Sanbaiman", 24000),
   12: ("Sanbaiman",24000),
   13: ("Yakuman", 32000),
}


def round_to_base(num, base):
	if num % base == 0:
		return num
	else:
		return num - (num % base) + base


def compute_payment(fans, minipoints, wintype, player_wind):
	""" Returns: (name, x, y)
		x payment of looser (if Ron), payment of non-dealer (if Tsumo)
		y payment of dealer (if Tsumo)
	""" 
	if fans < 5:
		name, score = "", scoring_table[minipoints][fans - 1]
	else:
		name, score = limited_hands[fans]
	
	if wintype == "Ron":
		if player_wind.name == "WE":
			return (name, round_to_base(score / 2 * 3, 100))
		else:
			return (name, score)
	else:
		if player_wind.name == "WE":
			return (name, (round_to_base(score / 2, 100), 0))
		else:
			return (name, (round_to_base(score / 4, 100), round_to_base(score / 2, 100)))

def quick_pons_and_kans(hand):
	d = {}
	for tile in hand:
		d[tile] = hand.count(tile)
	pons = []
	kans = []
	for tile,i in d.items():
		if i == 3:
			pons.append(tile)
		if i == 4:
			kans.append(tile)
	return (pons, kans)

def points_sum(tiles, nontermial_points):
	s = 0
	for tile in tiles:		
		if tile.is_nonterminal():
			s += nontermial_points
		else:
			s += nontermial_points * 2
	return s

def compute_minipoints(hand, open_sets, wintype, round_wind, player_wind):
	if not open_sets and wintype == "Ron":
		points = 30
	else:
		points = 20

	pons, kans = quick_pons_and_kans(hand)
	points += points_sum(pons, 4)
	points += points_sum(kans, 16)
	points += points_sum([set.tile for set in open_sets if set.is_pon()], 2)
	points += points_sum([set.tile for set in open_sets if set.is_kan()], 4)

	for tile in [ red_dragon, white_dragon, green_dragon, round_wind, player_wind ]:
		if hand.count(tile) == 2:
			points += 2	

	if wintype == "Tsumo":
		points += 2

	# TODO: Waitings

	if points == 20:
		# In what case can 20 points happend??
		return 30

	return round_to_base(points, 10)


def compute_score(hand, open_sets, wintype, doras, riichi, round_wind, player_wind):
	yaku = find_tiles_yaku(hand, open_sets, round_wind, player_wind)

	dora_yaku = 0
	for dora in doras:
		dora_yaku += hand.count(dora)
		for set in open_sets:
			dora_yaku += set.count_of_tile(dora)
	
	if dora_yaku > 0:
		yaku.append(("Dora", dora_yaku))

	minipoints = compute_minipoints(hand, open_sets, wintype, round_wind, player_wind)
	fans = sum(map(lambda r: r[1], yaku))
	
	# TODO: Riichi
	# TODO: Red-fives

	return (compute_payment(fans, minipoints, wintype, player_wind), yaku, minipoints)
	

def detect_pairs(hand):
	result = []
	used = []
	for tile in hand:
		if tile not in used and hand.count(tile) >= 2:
			new_hand = copy(hand)
			new_hand.remove(tile)
			new_hand.remove(tile)
			new_hand.sort()
			result.append((tile, new_hand))
			used.append(tile)
	return result


def find_sets(hand, open_sets):
	""" Hand has to be sorted """
	founded = copy(open_sets)

	def check_triples(hand, level):			
			if level == 5:				
				return founded
			tile = hand[0]

			if hand.count(tile) >= 3:
				new_hand = copy(hand)
				new_hand.remove(tile)
				new_hand.remove(tile)
				new_hand.remove(tile)
				set = Pon(tile)
				founded.append(set)				
				r = check_triples(new_hand, level + 1)
				if r:
					return r
				founded.remove(set)
				
			if tile.is_suit() and tile.get_number() <= 7:
				tile2 = tile.next_tile()			
				tile3 = tile2.next_tile()
				if tile2 in hand and tile3 in hand:
					new_hand = copy(hand)
					new_hand.remove(tile)
					new_hand.remove(tile2)
					new_hand.remove(tile3)
					set = Chi(tile, tile2, tile3)
					founded.append(set)					
					r = check_triples(new_hand, level + 1)
					if r:
						return r;
					founded.remove(set)
			return None
	return check_triples(hand, 1 + len(open_sets))


def eval_sets(pair, sets, round_wind, player_wind):
	result = []
	for name, fn in score_functions:
		score = fn(pair, sets)
		if score > 0:
			result.append((name, score))

	yaku_pai_base = 0 
	for set in sets:
		if set.is_pon():
			if set.tile == round_wind:
				yaku_pai_base += 1
			if set.tile == player_wind:
				yaku_pai_base += 1

	if yaku_pai_base > 0:
		for name, yaku in result:
			if name == "Yaku-Pai":
				result.remove((name, yaku))
				result.append((name, yaku + yaku_pai_base))
				break
		else:
			result.append(("Yaku-Pai", yaku_pai_base))
	return result


def sum_over_sets(sets, fn):
	return reduce(lambda a, s: fn(s) + a, sets, 0)


def for_all_sets(sets, fn):
	for set in sets:
		if not fn(set):
			return False
	return True

def for_any_sets(sets, fn):
	for set in sets:
		if fn(set):
			return True
	return False

def is_sets_closed(sets):
	for set in sets:
		if not set.closed:
			return False
	return True

def score_yaku_pai(pair_tile, sets):
	def dragon_pon_or_kan(set):
		if set.all_tiles_is(red_dragon) or set.all_tiles_is(white_dragon) or set.all_tiles_is(green_dragon):
			return 1
		else:
			return 0
	return sum_over_sets(sets, dragon_pon_or_kan)


def score_tan_yao(pair_tile, sets):
	def set_is_nontermial(set):
		return set.all_tiles(lambda t: t.is_nonterminal())
	
	if pair_tile.is_nonterminal() and for_all_sets(sets, set_is_nontermial):
		return 1
	else:
		return 0

def score_ipeikou(pair_tile, sets):
	count = 0
	for i, set in enumerate(sets):
		if not set.closed:
			return 0
		if set.is_chi() and sets[i + 1:].count(set) == 1:
			count += 1
	return count

def score_sanshoku_doujun(pair_tile, sets):
	for set in sets:
		if set.is_chi() and set.is_bamboo() and sets.count(set.as_pins()) > 0 and sets.count(set.as_char()) > 0:
			if is_sets_closed(sets):
				return 2
			else:
				return 1
	return 0

def score_sanshoku_douko(pair_tile, sets):
	for set in sets:
		if set.is_pon_or_kan() and set.is_bamboo():
			pins = [ s for s in sets if s.is_pon_or_kan() and s.tile == set.tile.as_pins() ]
			chars = [ s for s in sets if s.is_pon_or_kan() and s.tile == set.tile.as_char() ]
			if pins and chars:
				return 2
	return 0


itsu_sets_bamboos = [ Chi(bamboos[0], bamboos[1], bamboos[2]), Chi(bamboos[3], bamboos[4], bamboos[5]), Chi(bamboos[6], bamboos[7], bamboos[8]) ]
itsu_sets_chars = [ Chi(chars[0], chars[1], chars[2]), Chi(chars[3], chars[4], chars[5]), Chi(chars[6], chars[7], chars[8]) ]
itsu_sets_pins = [ Chi(pins[0], pins[1], pins[2]), Chi(pins[3], pins[4], pins[5]), Chi(pins[6], pins[7], pins[8]) ]
		
def score_itsu(pair_tile, sets):
	if (sets.count(itsu_sets_bamboos[0]) > 0 and sets.count(itsu_sets_bamboos[1]) > 0 and sets.count(itsu_sets_bamboos[2])) or \
		(sets.count(itsu_sets_chars[0]) > 0 and sets.count(itsu_sets_chars[1]) > 0 and sets.count(itsu_sets_chars[2])) or \
		(sets.count(itsu_sets_pins[0]) > 0 and sets.count(itsu_sets_pins[1]) > 0 and sets.count(itsu_sets_pins[2])):
		if is_sets_closed(sets):
			return 2
		else:
			return 1

def score_chanta(pair_tile, sets):
	if pair_tile.is_nonterminal() or not for_any_sets(sets, lambda s: s.is_chi()):
		return 0	

	for set in sets:
		if not set.any_tiles(lambda t: t.is_honor() or t.is_terminal()):
			return 0

	if score_junchan(pair_tile, sets) > 0:
		return 0

	if is_sets_closed(sets):
		return 2
	else:
		return 1

def score_junchan(pair_tile, sets):
	if not pair_tile.is_terminal() or not for_any_sets(sets, lambda s: s.is_chi()):
		return 0	

	for set in sets:
		if not set.any_tiles(lambda t: t.is_terminal()):
			return 0
	if is_sets_closed(sets):
		return 3
	else:
		return 2


score_functions = [ 
	("Yaku-Pai", score_yaku_pai),
	("Tan-Yao", score_tan_yao),
	("Ipeikou", score_ipeikou),
	("Sanshoku doujun", score_sanshoku_doujun),
	("Itsu", score_itsu),
	("Chanta", score_chanta),
	("Junchan taiyai", score_junchan),
	("Sanshoku douko", score_sanshoku_douko),
]


def find_potential_chi(hand, tile):
	r = []
	if not tile.is_suit():
		return r
	n = tile.get_number()
	pt = tile.prev_tile()
	ppt = pt.prev_tile()
	nt = tile.next_tile()
	nnt = nt.next_tile()
	if n < 9 and n > 1 and pt in hand and nt in hand:
		r.append((Chi(pt, tile, nt), nt))
	if n < 8 and nt in hand and nnt in hand:
		r.append((Chi(tile, nt, nnt), nnt))
	if n > 2 and pt in hand and ppt in hand:
		r.append((Chi(ppt, pt, tile), ppt))
	return r

def hand_in_tenpai(hand, open_sets):

	# TODO: Special hands

	for tile in all_tiles:
		for pair, rest in detect_pairs(hand + [tile]):
			sets = find_sets(rest, open_sets)
			if sets:
				return True

	return False
