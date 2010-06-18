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

import collections 
from tile import Pon, Chi
from tile import red_dragon, white_dragon, green_dragon
from tile import bamboos, chars, pins, all_tiles, honors
from copy import copy

def is_hand_open(sets):
	for set in sets:
		if not set.closed:
			return True
	return False

def find_tiles_yaku(hand, sets, specials, round_wind, player_wind):
	last_tile = hand[-1]
	if not sets and all((hand.count(tile) == 2 for tile in hand)):
		return score_special_chii_toitsu(hand) + specials

	for pair, rest in detect_pairs(hand):
		founded_sets = find_sets(rest, sets)
		if founded_sets:
			return eval_sets(pair, founded_sets, round_wind, player_wind, last_tile) + specials
	return []


def count_of_tiles_yaku(hand, sets, specials, round_wind, player_wind):
	score = find_tiles_yaku(hand, sets, specials, round_wind, player_wind)
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

def compute_minipoints(hand, sets, wintype, round_wind, player_wind, last_tile):
	if not is_hand_open(sets) and wintype == "Ron":
		points = 30
	else:
		points = 20

	pons, kans = quick_pons_and_kans(hand)
	points += points_sum(pons, 4)
	points += points_sum(kans, 16)
	points += points_sum([set.tile for set in sets if set.is_pon()], 2)
	points += points_sum([set.tile for set in sets if set.is_kan() and set.closed ], 8)
	points += points_sum([set.tile for set in sets if set.is_kan() and not set.closed ], 16)

	for tile in [ red_dragon, white_dragon, green_dragon, round_wind, player_wind ]:
		if hand.count(tile) == 2:
			points += 2	

	if wintype == "Tsumo":
		points += 2

	hh = copy(hand)
	hh.remove(last_tile)
	if is_single_waiting(hh, sets):
		points += 2

	if points == 20:
		# In what case can 20 points happend??
		return 30

	return round_to_base(points, 10)


def compute_doras(hand, sets, doras, score_name):
	dora_yaku = 0
	for dora in doras:
		dora_yaku += hand.count(dora)
		for set in sets:
			dora_yaku += set.count_of_tile(dora)
	
	if dora_yaku > 0:
		return [ (score_name, dora_yaku) ]
	else:
		return []


def compute_score(hand, sets, wintype, doras_and_ura_doras, specials, round_wind, player_wind):
	last_tile = hand[-1]
	yaku = find_tiles_yaku(hand, sets, specials, round_wind, player_wind)

	doras, ura_doras = doras_and_ura_doras
	yaku += compute_doras(hand, sets, doras, "Dora")
	yaku += compute_doras(hand, sets, ura_doras, "Ura dora")

	if wintype == "Tsumo":
		yaku.append(("Tsumo", 1))

	if ("Pinfu",1) in yaku:
		minipoints = 30 if wintype == "Ron" else 20	
	else:
		minipoints = compute_minipoints(hand, sets, wintype, round_wind, player_wind, last_tile)
	fans = min(sum(map(lambda r: r[1], yaku)), 13)

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


def find_sets(hand, sets):
	""" Hand has to be sorted """
	founded = copy(sets)

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
	return check_triples(hand, 1 + len(sets))

def check_pinfu(pair, sets, round_wind, player_wind, last_tile):
	if for_any_sets(sets, lambda s: not s.closed or not s.is_chi()):
		return False

	if pair in [ red_dragon, white_dragon, green_dragon, round_wind, player_wind ]:
		return False

	# Kan don't need to be tested because all sets are chi
	hand = [ pair, pair ]
	for s in sets :
		hand += s.tiles()
	hand.remove(last_tile)

	return not is_single_waiting(hand, [])


def eval_sets(pair, sets, round_wind, player_wind, last_tile):
	result = []
	for name, fn in score_functions:
		score = fn(pair, sets)
		if score > 0:
			result.append((name, score))

	if check_pinfu(pair, sets, round_wind, player_wind, last_tile):
		result.append(("Pinfu", 1))

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
	return not is_hand_open(sets)

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


def score_honitsu(pair_tile, sets):
	if score_chinitsu(pair_tile, sets) > 0:
		return 0

	for suits in [ pins, chars, bamboos ]:
		if pair_tile not in suits and pair_tile not in honors:
			continue
		for set in sets:
			tile = set.get_representative_tile()
			if tile not in suits and tile not in honors:
				break
		else:
			if is_sets_closed(sets):
				return 3
			else:
				return 2
	return 0


def score_chinitsu(pair_tile, sets):
	if not pair_tile.is_suit():
		return 0
	
	for set in sets:
		if not set.all_tiles(lambda t: pair_tile.is_same_type(t)):
			return 0

	if is_sets_closed(sets):
		return 6
	else:
		return 5


def score_sananko(pair_tile, sets):
	s = [ set for set in sets if set.closed and set.is_pon_or_kan() ]
	if len(s) >= 3:
		return 2
	return 0


def score_toitoiho(pair_tile, sets):
	if for_all_sets(sets, lambda s: s.is_pon_or_kan()):
		return 2
	return 0


def score_special_chii_toitsu(hand):
	yaku = [ ("Chii toitsu", 2) ]
	if all((tile.is_nonterminal() for tile in hand)):
		yaku.append(("Tan-Yao", 1))

	for suits in [ pins, chars, bamboos ]:
		if all((tile in suits for tile in hand)):
			yaku.append(("Chinitsu", 6))
			break
		if all((tile in suits or tile in honors for tile in hand)):
			yaku.append(("Honitsu", 3))
			break

	return yaku


score_functions = [ 
	("Yaku-Pai", score_yaku_pai),
	("Tan-Yao", score_tan_yao),
	("Ipeikou", score_ipeikou),
	("Sanshoku doujun", score_sanshoku_doujun),
	("Itsu", score_itsu),
	("Chanta", score_chanta),
	("Junchan taiyai", score_junchan),
	("Sanshoku douko", score_sanshoku_douko),
	("Honitsu", score_honitsu),
	("Chinitsu", score_chinitsu),
	("San-anko", score_sananko),
	("Toitoiho", score_toitoiho),
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
		r.append((Chi(pt, tile, nt), pt))
	if n < 8 and nt in hand and nnt in hand:
		r.append((Chi(tile, nt, nnt), tile))
	if n > 2 and pt in hand and ppt in hand:
		r.append((Chi(ppt, pt, tile), ppt))
	return r

def tile_counts(hand):
	d = collections.defaultdict(set)
	for tile in hand:
		d[hand.count(tile)].add(tile)
	return d

def riichi_test(hand, sets):
	if any([ not s.closed for s in sets ]):
		return False

	for tile in set(hand):
		h = copy(hand)
		h.remove(tile)
		if hand_in_tenpai(h, sets):
			return True
	return False

def hand_in_tenpai(hand, sets):
	""" Check if hand is in tenpai. Function work with 13 tiles hand """
	# TODO: Special hands

	return len(find_waiting_tiles(hand, sets)) > 0

def find_waiting_tiles(hand, sets):
	""" Returns tiles that forming hand. Function work with 13 tiles hand """

	if not sets:
		# Seven pairs
		counts = tile_counts(hand)
		if len(counts[1]) == 1 and len(counts[2]) == 6:
			return counts[1]

	tiles = []
	for tile in all_tiles:
		for pair, rest in detect_pairs(hand + [tile]):
			if find_sets(rest, sets):
				tiles.append(tile)
		
	return tiles

def is_single_waiting(hand, sets):
	# FIXME: This is NOT correct way how to detect single waiting!
	return len(find_waiting_tiles(hand,sets)) == 1
