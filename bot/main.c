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
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include "tools.h"
#include "eval.h"
#include "tiles.h"
#include "score.h"
#include "io.h"

void init() {
	srandom(time(0));
}

void process_commands(FILE *file, FILE *fileout, GameContext *gc)
{
	for(;;) {
		fflush(fileout);
		char line[4096];
		if (fgets(line, 4096, file) == NULL)
			break;

		if (line[0] == '#') {
			continue;
		}

		int l = strlen(line);
		while (line[l - 1]  == '\n' || line[l - 1] == '\r') { 
			l--;
			line[l] = 0;
		}

		// printf(">> %s\n", line);

		if (!strcmp(line, "QUIT")) {
			break;
		}
		
		if (!strcmp(line, "WALL")) {
			if (!read_tiles(file, gc->wall)) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			} else {
				gc->wall_size = tiles_count(gc->wall);
			}
			continue;
		}

		if (!strcmp(line, "HAND")) {
			if (!read_tiles(file, gc->hand)) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			}	
			continue;
		}

		if (!strcmp(line, "DISCARD")) {
			int tile = choose_drop_tile(gc);
			fprintf(fileout, "%s\n", tile_name[tile]);
			continue;
		}

		if (!strcmp(line, "DISCARD_TILES")) {
			tile_id tiles[TILES_COUNT];
			drop_candidates(gc, tiles);
			print_tiles(fileout, tiles);
			continue;
		}

		if (!strcmp(line, "TURNS")) {
			if (fscanf(file, "%i\n", &gc->turns) != 1) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			}
			continue;
		}

		if (!strcmp(line, "SETS")) {
			if (!read_sets(file, gc->open_sets, 4, &gc->open_sets_count)) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			}	
			continue;
		}

		if (!strcmp(line, "STEAL")) {
			int tile = read_tile(file);
			TileSet sets[5];
			int sets_count;
			if (!read_sets(file, sets, 5, &sets_count) || tile == TILE_NONE) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			} else {
				int choice = steal_chance(gc, sets, sets_count, tile);
				if (choice == -1) {
					fprintf(fileout, "Pass\n");
				} else {
					dump_set(fileout, &sets[choice]);
				}
			}
			continue;	
		}

		if (!strcmp(line, "YAKU")) {
			int yaku = compute_yaku_of_hand(gc->hand, gc->open_sets, gc->open_sets_count, gc->round_wind, gc->player_wind);
			fprintf(fileout, "%i\n", yaku);
			continue;
		}

		if (!strcmp(line, "DORAS")) {
			tile_id *array = read_tiles_array(file);
			if (array == NULL) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
				continue;
			}
			// TODO: Process DORA
			free(array);
			continue;
		}

		if (!strcmp(line, "ROUND_WIND")) {
			gc->round_wind = read_tile(file);
			if (gc->round_wind == TILE_NONE) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			}
			continue;
		}

		if (!strcmp(line, "PLAYER_WIND")) {
			gc->player_wind = read_tile(file);
			if (gc->player_wind == TILE_NONE) {
				fprintf(fileout, "Error: Invalid format (%s)\n", line);
			}
			continue;
		}

		fprintf(fileout, "Error: Unknown command (%s)\n", line);
	}
}

int main() {
	init();
	GameContext gc;
	init_gamecontext(&gc);
	process_commands(stdin, stdout, &gc);
	return 0;
}
