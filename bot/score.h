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


#ifndef SCORE_H
#define SCORE_H

#include "tiles.h"

int score_of_hand(tile_id *tiles, int pair, TileSet **sets, int opened_sets, int round_wind, int player_wind);
int count_of_fan(tile_id *tile, int pair, TileSet **sets, int open_sets_count, int round_wind, int player_wind);
int score_of_seven_pairs(tile_id *hand);


#endif 
