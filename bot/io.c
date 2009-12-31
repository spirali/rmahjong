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


#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "io.h"
#include "tiles.h"

#define LINE_LENGTH_LIMIT 4096

void dump_tiles(tile_id *tile)
{
	int t;
	printf("{");
	for (t = 0; t < TILES_COUNT; t++) {
		if (tile[t] > 0) {
			printf(" %s:%i,", tile_name[t], tile[t]);
		}
	}
	printf(" }\n");
}

void dump_set(FILE *fileout, TileSet *set)
{
	char *str;
	switch (set->type) {
		case CHI:
			str = "Chi"; break;
		case PON:
			str = "Pon"; break;
		default:
			str = "Error"; break;
	}
	fprintf(fileout, "%s %s\n", str, tile_name[set->tile]);
}

void print_tiles(FILE *fileout, tile_id *tile)
{
	int t;
	for (t = 0; t < TILES_COUNT; t++) {
		int s;
		for (s = 0; s < tile[t]; s++) {
			printf("%s ", tile_name[t]);
		}
	}
	printf("\n");
}

int read_tiles(FILE *file, tile_id *out)
{
	char line[LINE_LENGTH_LIMIT];
	char *s = fgets(line, LINE_LENGTH_LIMIT, file);
	if (s == NULL)
		return 0;

	zero_tiles(out);
	char *delim = "\n\t\r ";
	char *token = strtok(line, delim);
	while(token) {
		int tile = tile_from_name(token);
		if (tile == TILE_NONE) {
			return 0;
		}
		out[tile]++;
		token = strtok(NULL, delim);
	}
	return 1;
}

tile_id read_tile(FILE *file)
{
	char line[LINE_LENGTH_LIMIT];
	char *s = fgets(line, LINE_LENGTH_LIMIT, file);
	if (s == NULL)
		return TILE_NONE;

	char *delim = "\n\t\r ";
	char *token = strtok(line, delim);
	return tile_from_name(token);
}


tile_id * read_tiles_array(FILE *file)
{
	tile_id tiles[TILES_COUNT];
	if (read_tiles(file, tiles) == 0) {
		return NULL;
	}
	int count = 0;
	int t;
	for (t = 0; t < TILES_COUNT; t++) {
		count += tiles[t];
	}
	tile_id *array = malloc(sizeof(tile_id) * (count + 1));
	int i = 0;
	for (t = 0; t < TILES_COUNT; t++) {
		int s;
		for (s = 0; s < tiles[t]; t++) {
			array[i++] = t;
		}
	}
	array[i] = TILE_NONE;
	return array;
}


int read_sets(FILE *file, TileSet *set, int max, int *count)
{
	char line[LINE_LENGTH_LIMIT];
	char *s = fgets(line, LINE_LENGTH_LIMIT, file);
	if (s == NULL)
		return 0;

	char *delim = "\n\t\r ";
	char *token = strtok(line, delim);
	int c = 0;
	while(token && c < max) {
		int type;
		if (!strcmp("Chi", token)) {
			type = CHI;
		} else if (!strcmp("Pon", token)) {
			type = PON;
		} else {
			return 0;
		}

		token = strtok(NULL, delim);

		if (token == NULL) {
			return 0;
		}
		int tile = tile_from_name(token);
		if (tile == TILE_NONE) {
			return 0;
		}
		set[c].type = type;
		set[c].tile = tile;
		c++;
		token = strtok(NULL, delim);
	}
	*count = c;
	return 1;

}

int read_wall(FILE *file, tile_id *out)
{
	int t;
	for (t = 0; t < TILES_COUNT; t++) {
		int i;
		if (fscanf(file, "%i", &i) != 1) {
			return 0;
		}
		out[t] = i;
	}
	return fscanf(file, "\n") == 0;
}


