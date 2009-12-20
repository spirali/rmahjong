from tile import Pon, Chi
from tile import red_dragon, white_dragon, green_dragon
from copy import copy

def find_tiles_yaku(hand, open_sets):
	for pair, rest in detect_pairs(hand):
		sets = find_sets(rest, open_sets)
		if sets:
			return eval_sets(pair, sets)
	return []


def count_of_tiles_yaku(hand, open_sets):
	score = find_tiles_yaku(hand, open_sets)
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

	return round_to_base(points, 10)


def compute_score(hand, open_sets, wintype, doras, riichi, round_wind, player_wind):
	yaku = find_tiles_yaku(hand, open_sets)
	minipoints = compute_minipoints(hand, open_sets, wintype, round_wind, player_wind)
	fans = sum(map(lambda r: r[1], yaku))
	
	# TODO: Riichi
	# TODO: Doras
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


def eval_sets(pair, sets):
	result = []
	for name, fn in score_functions:
		score = fn(pair, sets)
		if score > 0:
			result.append((name, score))
	return result


def sum_over_sets(sets, fn):
	return reduce(lambda a, s: fn(s) + a, sets, 0)


def for_all_sets(sets, fn):
	for set in sets:
		if not fn(set):
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


score_functions = [ 
	("Yaku-Pai", score_yaku_pai),
	("Tan-Yao", score_tan_yao),
	("Ipeikou", score_ipeikou),
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

