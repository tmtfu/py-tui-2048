import math
import json
import curses 
import modules.grid as grid
from modules.utils import addstr_robust

# v2.0.1

class Game(object):
    
    def __init__(self: object) -> None:

        # Note: I put try/except statements after .addstr() because
        # when you resize to small, it will do raise an error
        
        self._stdscr = curses.initscr()

        try:
            self._stdscr.keypad(1)
            curses.noecho()
            curses.cbreak()
            curses.curs_set(0)
            curses.start_color()
            curses.use_default_colors()

            for i in range(curses.COLORS):
                curses.init_pair(i, i, -1);
            
            self._base = 2
            self._spawn_choices = tuple(self._base**i for i in range(1, 3))
            self._spawn_rates = (90, 10)
            self._winning_power = 11

            self._grid_size = (4, 4)
            self._grid_pos = (13, 4)
            self._cell_size = (8, 3)

            self._grid = grid.Grid(self._grid_size)
            
            self._score = 0

            # dead = 0
            # playing = 1
            # won the game (on select screen) = 2
            # endless mode = 3
            self._game_state = 1

            self._save_data = {'highscore': 0,
                               'tile_highscore': self._spawn_choices[0]}

            try:
                with open('save.json', 'r', encoding='UTF-8') as save_file:
                    self._save_data = json.load(save_file)
            except FileNotFoundError:
                self._save_save_data_to_file()

            with open('texts.json', 'r', encoding='UTF-8') as texts_file:
                self._texts = json.load(texts_file)
            
            types = {'win': list,
                     'empty_tile': str,
                     'score': str,
                     'highscore': str,
                     'tile_highscore': str,
                     'death': str,
                     'info': str,
                     'stats': str}

            # type checking for texts.json
            for key, value in self._texts.items():
                value_type = type(value)
                if value_type != types[key]:
                    if types[key] == list:
                        raise ValueError(f'value for "{key}" in text.json should be a list of str lines, not {types[key]}')
                    else:
                        raise ValueError(f'value for "{key}" in text.json should be of type {types[key]}, not {value_type}')

        finally:
            curses.endwin()

    def _save_save_data_to_file(self: object) -> None:
        'Saves the player\'s save data to the data/save/save.json file'

        with open('save.json', 'w', encoding='UTF-8') as save_file:
            json.dump(self._save_data, save_file)

    def _draw_grid(self: object) -> None:

        for y, row in enumerate(self._grid.grid):
            for x, item in enumerate(row):
                item_str = str(item)
                try:
                    self._stdscr.addstr(self._grid_pos[1] + y * self._cell_size[1],
                                       self._grid_pos[0] + x * self._cell_size[0],

                                       # the * (self._cell_size[0] - 1) is to clear numbers 
                                       item_str + ' ' * (self._cell_size[0] - len(item_str))
                                       if item else self._texts['empty_tile'] + ' ' * 
                                         (self._cell_size[0] - len(self._texts['empty_tile'])),

                                       curses.color_pair(
                                           int(min(math.log(item, self._base), 7) if item else 0)))
                except curses.error:
                    pass

    def _handle_key_input(self: object,
                          key: str) -> None:

        original_grid = self._grid.grid

        if self._game_state == 1 or self.game_state == 3:
            if key in ('w', 'k', 'KEY_UP'):
                return_value = self._grid.up(1)
                self._grid.grid = return_value[0]
                self._score += return_value[1]
                if self._grid.grid != original_grid:
                    self._grid.spawn_new_numbers(1, self._spawn_choices, self._spawn_rates)

            elif key in ('s', 'j', 'KEY_DOWN'):
                return_value = self._grid.down(1)
                self._grid.grid = return_value[0]
                self._score += return_value[1]
                if self._grid.grid != original_grid:
                    self._grid.spawn_new_numbers(1, self._spawn_choices, self._spawn_rates)

            elif key in ('a', 'h', 'KEY_LEFT'):
                return_value = self._grid.left(1)
                self._grid.grid = return_value[0]
                self._score += return_value[1]
                if self._grid.grid != original_grid:
                    self._grid.spawn_new_numbers(1, self._spawn_choices, self._spawn_rates)

            elif key in ('d', 'l', 'KEY_RIGHT'):
                return_value = self._grid.right(1)
                self._grid.grid = return_value[0]
                self._score += return_value[1]
                if self._grid.grid != original_grid:
                    self._grid.spawn_new_numbers(1, self._spawn_choices, self._spawn_rates)
        
        elif self._game_state and key == 'c':
            self._game_state = 3

        if key == 'r':
            self._reset()

    def _reset(self: object) -> None:

        self._grid.reset()
        self._grid.spawn_new_numbers(2, (self._spawn_choices[0],))
        
        self._score = 0
        self._game_state = 1

    def _render_text(self: object) -> None:
        
        # The try and excepts are to prevent curses from raising an error when it tries to write outside of the terminal

        # score
        addstr_robust(self._stdscr, self._grid_pos[1] + self._cell_size[1] * 3 - 1,
                      self._grid_pos[0] + self._grid_size[0] * self._cell_size[0] + 5,
                      f'{self._texts['score']}{self._score}')

        # highscore
        addstr_robust(self._stdscr, self._grid_pos[1] + self._cell_size[1] * 2 - 1,
                      self._grid_pos[0] + self._grid_size[0] * self._cell_size[0] + 5,
                      f'{self._texts['highscore']}{self._save_data['highscore']}')

        # highest tile
        addstr_robust(self._stdscr, self._grid_pos[1] + self._cell_size[1] - 1,
                      self._grid_pos[0] + self._grid_size[0] * self._cell_size[0] + 5,
                      f'{self._texts['tile_highscore']}{self._save_data['tile_highscore']}')
        
        # info
        addstr_robust(self._stdscr, 1, self._grid_pos[0] + math.ceil((((self._grid_size[0] - 1)
                        * self._cell_size[0] + len(self._texts['empty_tile'])) - len(self._texts['info'])) / 2),
                      self._texts['info'])

        # death
        if not self._game_state:
            addstr_robust(self._stdscr, self._grid_pos[1] + self._grid_size[1] * self._cell_size[1] + 1,
                          self._grid_pos[0] + math.ceil((((self._grid_size[0] - 1) * self._cell_size[0]
                          + len(self._texts['empty_tile'])) - len(self._texts['death'])) / 2),
                          self._texts['death'])

        # the centering is around the first dot and last dot
        
        # win
        elif self._game_state == 2:
            for dex, string in enumerate(self._texts['win']):
                addstr_robust(self._stdscr, self._grid_pos[1] + self._grid_size[1] * self._cell_size[1] + dex + 1,
                              self._grid_pos[0] + math.ceil((((self._grid_size[0] - 1) * self._cell_size[0]
                                + len(self._texts['empty_tile'])) - len(string)) / 2),
                              string)

    def run(self: object) -> None:

        running = 1
        
        try:

            self._reset()

            self._render_text()
            self._draw_grid()

            while running:
                key = self._stdscr.getkey()
                self._handle_key_input(key)

                if (self._grid.up() == self._grid.grid
                    and self._grid.down() == self._grid.grid
                    and self._grid.left() == self._grid.grid
                    and self._grid.right() == self._grid.grid):

                    self._game_state = 0 # dead
                # i use an if statement so that it won't become 1
                # if the condition is not satisfied; it will tay unchanged
                if self._score > self._save_data['highscore']:
                    self._save_data['highscore'] = self._score
                    self._save_save_data_to_file()

                for row in self._grid.grid:
                    for item in row:
                        if item > self._save_data['tile_highscore']:
                            self._save_data['tile_highscore'] = item
                            self._save_save_data_to_file()
                        # I add the == 1 so it doesn't overwrite the game_state if it is 3
                        if item >= self._base**self._winning_power and self._game_state == 1:
                            self._game_state = 2

                self._stdscr.erase()
                self._render_text()
                self._draw_grid()
                self._stdscr.refresh()

        except KeyboardInterrupt:
            pass

        finally:
            curses.endwin()

            print(f'{self._texts['stats']}',
                  f' - {self._texts['score']}{self._score}',
                  f' - {self._texts['highscore']}{self._save_data['highscore']}',
                  f' - {self._texts['tile_highscore']}{self._save_data['tile_highscore']}', sep='\n')


if __name__ == '__main__':
    Game().run()

