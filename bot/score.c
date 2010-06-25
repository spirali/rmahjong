/* Copyright (C) 2009 Stanislav Bohm 
 
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
 
  You should have received a copy of the GNU General Public License
  along with this program; see the file COPYING. If not, see 
  <http://www.gnu.org/licenses/>.
*/


#include <stdio.h>
#include "score.h"
#include "io.h"

int fan_to_score[14] = {
 1,          // 0
 1000,       // 1
 2000,       // 2
 3900,       // 3
 7700,       // 4
 8000,       // 5
 12000,      // 6
 12000,      // 7
 16000,      // 8
 16000,      // 9
 16000,      // 10
 24000,      // 11
 24000,      // 12
 32000,      // 13
};

static int suit_value(tile_id id)
{
	if (id >= TILE_C1) {
		return id -= TILE_C1;
	}
	if (id >= TILE_P1) {
		return id -= TILE_P1;
	}
	if (id >= TILE_B1) {
		return id -= TILE_B1;
	}
	return -1;
}

static int nonterminals_only(TileSet *set)
{
	switch(set->type) {
		case CHI:
			return (set->tile > TILE_B1 && set->tile < TILE_B7) ||
					(set->tile > TILE_P1 && set->tile < TILE_P7) ||
					(set->tile > TILE_C1 && set->tile < TILE_C7);
		case PON:
			return IS_NONTERMINAL(set->tile);
		default:
			return 0;
	}
}

static int terminals_any(TileSet *set)
{
	switch(set->type) {
		case CHI:
			return  set->tile == TILE_B1 || set->tile == TILE_B7 ||
				    set->tile == TILE_P1 || set->tile == TILE_P7 ||
					set->tile == TILE_C1 || set->tile == TILE_C7;
		case PON:
			return IS_TERMINAL(set->tile);
		default:
			return 0;
	}
}


static int score_san_shoku_dokou(int tile_1, int tile_2, int tile_3)
{
	int i1 = suit_value(tile_1);
	int i2 = suit_value(tile_2);
	int i3 = suit_value(tile_3);
	if (i1 != -1 && (i1 == i2) && (i2 == i3)) {
		if ((tile_1 != tile_2) && (tile_2 != tile_3) && (tile_1 != tile_3))
			return 2;
	}
	return 0;
}


/* !! Open sets has to be at the end of array of sets */
int count_of_fan(tile_id *tile, int pair, TileSet **sets, int open_sets_count, int round_wind, int player_wind)
{
	int fan = 0;
	int s, t;

	TileSet *chi[4], *pon[4];
	int chi_count = 0;
	int pon_count = 0;
	int dragons = 0;

	/* Yaku-pai */
	for (t = 0; t < 4; t++) {
		if (sets[t]->type == PON) {
			 if (sets[t]->tile >= TILE_DRAGONS_FIRST && sets[t]->tile <= TILE_DRAGONS_LAST) {
				dragons++;
				fan++;
			 } else {
				 if (sets[t]->tile == round_wind)
					fan++;
				 if (sets[t]->tile == player_wind)
					fan++;
			}
		}

		// General preprocess
		if (sets[t]->type == CHI) {
			chi[chi_count++] = sets[t];
		} else {
			pon[pon_count++] = sets[t];
		}
	}

	if (IS_GREEN(pair)) {
		for (t = 0; t < 4; t++) {
			if (sets[t]->type == PON) {
				if (!IS_GREEN(sets[t]->tile))
					break;
			} else {
				if (sets[t]->tile != TILE_B2) {
					break;
				}
			}
		}
		if (t == 4) {
			return 13; // ryuu-iisou
		}
	}

	/* Dai-sangen */
	if (dragons == 3) {
		return 13; 
	}

	/* Tan-yao */
	if (IS_NONTERMINAL(pair)) {
		for (t = 0; t < 4; t++) {
			if (!nonterminals_only(sets[t]))
				break;
		}
		if (t == 4) {
			fan++;
		}
	}

	/* San shoku dokou & San-anko & Toitoi */
	if (pon_count >= 3) {
		int closed_pons = 0;
		for (t = 0; t < 4 - open_sets_count; t++) { 
			// open sets are placed at the end of the array
			if (sets[t]->type == PON) {
				closed_pons++;
			}
		}
		if (closed_pons >= 3) {
			if (closed_pons == 4) {
				return 13; // suu-ankou
			}
			fan += 2; // San-anko
		}

		if (pon_count == 4) {
			if (IS_TERMINAL(pair) 
				&& IS_TERMINAL(pon[0]->tile) && IS_TERMINAL(pon[1]->tile) && IS_TERMINAL(pon[2]->tile) && IS_TERMINAL(pon[3]->tile)) {
				// chinroutou
				return 13;
			}
			if (IS_HONOR(pair)
				&& IS_HONOR(pon[0]->tile) && IS_HONOR(pon[1]->tile) && IS_HONOR(pon[2]->tile) && IS_HONOR(pon[3]->tile)) {
				return 13;
			}
		}

		fan += score_san_shoku_dokou(pon[0]->tile, pon[1]->tile, pon[2]->tile);
		if (pon_count == 4) {
			fan += 2; // Toitoi
			fan += score_san_shoku_dokou(pon[3]->tile, pon[0]->tile, pon[1]->tile);
			fan += score_san_shoku_dokou(pon[3]->tile, pon[0]->tile, pon[2]->tile);
			fan += score_san_shoku_dokou(pon[3]->tile, pon[1]->tile, pon[2]->tile);
		}

		int winds = 0;
		for (t = 0; t < pon_count; t++) {
			if (IS_WIND(pon[t]->tile)) {
				winds++;
			}
		}

		/* Shou suushi */
		if (winds == 3 && IS_WIND(pair)) {
			return 13;
		}

		/* Dai shuushi */
		if (winds == 4) {
			return 13;
		}

	}

	/* Ipeikou */
	if (open_sets_count == 0) {
		for (t = 0; t < chi_count - 1; t++) {
			int count = 0;
			for (s = t + 1; s < chi_count; s++) {
				if (chi[s]->tile == chi[t]->tile)
					count++;
			}
			if (count == 1)
				fan++;
		}
	}

	/* Chanta and Junchan */
	if (chi_count >= 1 && !IS_NONTERMINAL(pair)) {
		for (t = 0; t < 4; t++) {
			if (nonterminals_only(sets[t]))
				break;
		}
		if (t == 4) {
			for (t = 0; t < 4; t++) {
				if (!terminals_any(sets[t]))
					break;
			}
			if (t == 4 && !IS_HONOR(pair)) {
				fan += 2;
			} else {
				fan++;
			}
			if (!open_sets_count) {
				fan++;
			}
		}
	}

	/* Sanshoku doujun */
	if (chi_count >= 3) {
		for (t = 0; t < chi_count; t++) {
			if (chi[t]->tile >= TILE_B1 && chi[t]->tile <= TILE_B7) {
				int pchi = 0;
				int cchi = 0;
				int tile_num = chi[t]->tile - TILE_B1;
				for (s = 0; s < chi_count; s++) {
					if (chi[s]->tile == tile_num + TILE_P1)
						pchi = 1;
					if (chi[s]->tile == tile_num + TILE_C1)
						cchi = 1;
				}
				if (pchi && cchi) {
					if (open_sets_count) {
						fan++;
					} else {
						fan += 2;
					}
				}
				break;
			}
		}
		
		/* Itsu */
		int c1 = 0, c4 = 0, c7 = 0, p1 = 0, p4 = 0, p7 = 0, b1 = 0, b4 = 0, b7 = 0;
		
		for (t = 0; t < chi_count; t++) {
			switch(chi[t]->tile) {
				case TILE_C1: c1 = 1; continue;
				case TILE_C4: c4 = 1; continue;
				case TILE_C7: c7 = 1; continue;
				case TILE_P1: p1 = 1; continue;
				case TILE_P4: p4 = 1; continue;
				case TILE_P7: p7 = 1; continue;
				case TILE_B1: b1 = 1; continue;
				case TILE_B4: b4 = 1; continue;
				case TILE_B7: b7 = 1; continue;
				default: continue;
			}
		}
		if ((c1 && c4 && c7) || (p1 && p4 && p7) || (b1 && b4 && b7)) {
			if (open_sets_count) {
				fan++;
			} else {
				fan += 2;
			}
		}

	}

	/* Chinitsu & Honitsu */
	for (t = 0; t < 3; t++) {
		int start_tile = TILE_SUIT_FIRST + 9 * t;
		int end_tile = start_tile + 8;
		if ((pair < start_tile || pair > end_tile) && !IS_HONOR(pair))
			continue;
		for (s = 0; s < 4; s++) {
			if ((sets[s]->tile < start_tile || sets[s]->tile > end_tile) && !IS_HONOR(sets[s]->tile)) {
				break;	
			} 
		}
		if (s == 4) {
			for (s = 0; s < 4; s++) {
				if (IS_HONOR(sets[s]->tile)) {
					break;	
				}
			} 
			if (s == 4 && !IS_HONOR(pair)) { // Chinitsu
				if (open_sets_count) {
					fan += 5;
				} else {
					fan += 6;
				}
			} else {
				if (open_sets_count) { // Honitsu
					fan += 2;
				} else {
					fan += 3;
				}
			}
			break;
		}
	}
	return fan;
}

int score_of_hand(tile_id *tiles, int pair, TileSet **sets, int open_sets_count, int round_wind, int player_wind)
{
 	int fan = count_of_fan(tiles, pair, sets, open_sets_count, round_wind, player_wind);   

	if (fan == 0 && open_sets_count) {
		return 0;
	}

	if (fan > 13)
		fan = 13;

	return fan_to_score[fan];
}

int score_of_seven_pairs(tile_id *hand)
{

	int t;
	for (t = 0; t < TILES_COUNT; t++) {
		if (hand[t] > 0 && !IS_HONOR(t)) {
			break;
		}
	}

	// tsu-iisou
	if (t == TILES_COUNT) {
		return fan_to_score[13];
	}
	
	int fan = 2;
	for (t = 0; t < TILES_COUNT; t++) {
		if (hand[t] > 0 && !IS_NONTERMINAL(t)) {
			break;
		}
	}

	// Tanyao
	if (t == TILES_COUNT) {
		fan += 1;
	}

	return fan_to_score[fan];
}
