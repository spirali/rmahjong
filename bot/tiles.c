
#include "tiles.h"
#include <stdlib.h>
#include <string.h>

char *tile_name[TILES_COUNT] = { 
"DR",
"DG",
"DW",
"WE",
"WS",
"WW",
"WN",
"B1",
"B2",
"B3",
"B4",
"B5",
"B6",
"B7",
"B8",
"B9",
"P1",
"P2",
"P3",
"P4",
"P5",
"P6",
"P7",
"P8",
"P9",
"C1",
"C2",
"C3",
"C4",
"C5",
"C6",
"C7",
"C8",
"C9" };

void zero_tiles(tile_id *tile)
{
	memset(tile, 0, sizeof(tile_id) * TILES_COUNT);
}

int tile_from_name(char *name)
{
	int t;
	for (t = 0; t < TILES_COUNT; t++) {
		if (!strcmp(name, tile_name[t])) {
			return t;
		}
	}
	return TILE_NONE;
}

TileSet * all_tilesets()
{
	TileSet *sets = malloc(sizeof(TileSet) * SETS_COUNT);

	int t;
	for (t = 0; t < TILES_COUNT; t++) {
		sets[t].type = PON;
		sets[t].tile = t;
	}

	for (t = 0; t < 7; t++) {
		sets[TILES_COUNT + t * 3].type = CHI;
		sets[TILES_COUNT + t * 3].tile = TILE_B1 + t;
		sets[TILES_COUNT + t * 3 + 1].type = CHI;
		sets[TILES_COUNT + t * 3 + 1].tile = TILE_P1 + t;
		sets[TILES_COUNT + t * 3 + 2].type = CHI;
		sets[TILES_COUNT + t * 3 + 2].tile = TILE_C1 + t;
	}
	return sets;
}

int tiles_count(tile_id *tile)
{
	int t;
	int sum = 0;
	for (t = 0; t < TILES_COUNT; t++) {
		sum += tile[t];
	}
	return sum;
}



void init_tiles(int *tiles, int count, tile_id *out)
{
	zero_tiles(out);
	int t;
	for (t = 0; t < count; t++) {
		out[tiles[t]]++;
	} 
}


void add_set_to_tiles(tile_id *tiles, TileSet *set)
{
	switch(set->type) {
		case CHI:
			tiles[set->tile]++;
			tiles[set->tile + 1]++;
			tiles[set->tile + 2]++;
			return;
		case PON:
			tiles[set->tile]+=3;
			return;
	}
}

void remove_set_from_tiles(tile_id *tiles, TileSet *set)
{
	switch(set->type) {
		case CHI:
			tiles[set->tile]--;
			tiles[set->tile + 1]--;
			tiles[set->tile + 2]--;
			return;
		case PON:
			tiles[set->tile]-=3;
			return;
	}
}


