#ifndef TILES_H
#define TILES_H

#define TILE_DR 0
#define TILE_DG 1
#define TILE_DW 2
#define TILE_WE 3
#define TILE_WS 4
#define TILE_WW 5
#define TILE_WN 6
#define TILE_B1 7
#define TILE_B2 8
#define TILE_B3 9
#define TILE_B4 10
#define TILE_B5 11
#define TILE_B6 12
#define TILE_B7 13
#define TILE_B8 14
#define TILE_B9 15
#define TILE_P1 16
#define TILE_P2 17
#define TILE_P3 18
#define TILE_P4 19
#define TILE_P5 20
#define TILE_P6 21
#define TILE_P7 22
#define TILE_P8 23
#define TILE_P9 24
#define TILE_C1 25
#define TILE_C2 26
#define TILE_C3 27
#define TILE_C4 28
#define TILE_C5 29
#define TILE_C6 30
#define TILE_C7 31
#define TILE_C8 32
#define TILE_C9 33

#define TILES_COUNT 34

#define TILE_NONE 255

#define TILE_DRAGONS_FIRST TILE_DR
#define TILE_DRAGONS_LAST  TILE_DW

#define TILE_SUIT_FIRST TILE_B1

// TILES_COUNT (pons) + 7 * 3 (chis)
#define SETS_COUNT 55

#define CHI 0
#define PON 1

typedef char tile_id;

typedef struct TileSet TileSet;
struct TileSet { 
	int type;
	int tile;
};

extern char * tile_name[];

void zero_tiles(tile_id *tile);
void init_tiles(int *tiles, int count, tile_id *out);
int tile_from_name(char *name);
TileSet * all_tilesets();
int tiles_count(tile_id *tile);

void remove_set_from_tiles(tile_id *tiles, TileSet *set);
void add_set_to_tiles(tile_id *tiles, TileSet *set);

#endif 
