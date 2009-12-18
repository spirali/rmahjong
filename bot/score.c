
#include "score.h"

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

static int terminals_only(TileSet *set)
{
    switch(set->type) {
        case CHI:
            return (set->tile > TILE_B1 && set->tile < TILE_B7) ||
                   (set->tile > TILE_P1 && set->tile < TILE_P7) ||
                   (set->tile > TILE_C1 && set->tile < TILE_C7);
        case PON:
            return (set->tile > TILE_B1 && set->tile < TILE_B9) ||
                   (set->tile > TILE_P1 && set->tile < TILE_P9) ||
                   (set->tile > TILE_C1 && set->tile < TILE_C9);
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

static int count_of_fan(tile_id *tile, int pair, TileSet **sets)
{
    int fan = 0;
    int t;

	TileSet *chi[4], *pon[4];
	int chi_count = 0;
	int pon_count = 0;


    /* Yaku-pai */
    for (t = 0; t < 4; t++) {
        if (sets[t]->type == PON && sets[t]->tile >= TILE_DRAGONS_FIRST && sets[t]->tile <= TILE_DRAGONS_LAST)
            fan++;

		// General preprocess
		if (sets[t]->type == CHI) {
			chi[chi_count++] = sets[t];
		} else {
			pon[pon_count++] = sets[t];
		}
    }

    /* Tan-yao */
    for (t = 0; t < 4; t++) {
        if (!terminals_only(sets[t]))
            break;
    }
    if (t == 4) {
        fan++;
    }

	/* San shoku dokou */
	if (pon_count >= 3) {
		fan += score_san_shoku_dokou(pon[0]->tile, pon[1]->tile, pon[2]->tile);
		if (pon_count == 4) {
			fan += score_san_shoku_dokou(pon[3]->tile, pon[0]->tile, pon[1]->tile);
			fan += score_san_shoku_dokou(pon[3]->tile, pon[0]->tile, pon[2]->tile);
			fan += score_san_shoku_dokou(pon[3]->tile, pon[1]->tile, pon[2]->tile);
		}
	}
	return fan;
}

int score_of_hand(tile_id *tiles, int pair, TileSet **sets)
{
 	int fan = count_of_fan(tiles, pair, sets);   
	int t;
	int score = 80;
	for (t = 2; t < fan + 2; t++) {
		score *= 2;
	}
	return score;
	/*return (score - 1) / 100 + 1;*/
}
