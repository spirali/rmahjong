from tile import Pon, Chi
from tile import red_dragon, white_dragon, green_dragon
from copy import copy

def find_tiles_yaku(hand):
	for pair, rest in detect_pairs(hand):
		sets = find_sets(rest)
		if sets:
			return eval_sets(pair, sets)
	return []


def count_of_tiles_yaku(hand):
	score = find_tiles_yaku(hand)
	return sum(map(lambda r: r[1], score))


def compute_payment(fans, minipoints):
	pass


def compute_score(hand, doras, riichi, round_wind, player_wind):
	yaku = find_tiles_yaku(hand)
	return yaku
	

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


def find_sets(hand):
	""" Hand has to be sorted """
	founded = []
	result = []

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
	return check_triples(hand, 1)


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
	def dragon_pon_or_kon(set):
		if set.all_tiles_is(red_dragon) or set.all_tiles_is(white_dragon) or set.all_tiles_is(green_dragon):
			return 1
		else:
			return 0
	return sum_over_sets(sets, dragon_pon_or_kon)


def score_tan_yao(pair_tile, sets):
	def set_is_nontermial(set):
		return set.all_tiles(lambda t: t.is_nonterminal())
	
	if pair_tile.is_nonterminal() and for_all_sets(sets, set_is_nontermial):
		return 1
	else:
		return 0


score_functions = [ 
	("Yaku-Pai", score_yaku_pai),
	("Tan-Yao", score_tan_yao),
]
