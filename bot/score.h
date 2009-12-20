
#ifndef SCORE_H
#define SCORE_H

#include "tiles.h"

int score_of_hand(tile_id *tiles, int pair, TileSet **sets, int opened_sets);
int count_of_fan(tile_id *tile, int pair, TileSet **sets, int open_sets_count);


#endif 
