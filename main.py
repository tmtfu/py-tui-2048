import math
import json
import curses 
import modules.grid as grid
from modules.utils import addstr_robust

# v1.0.3

class Game(object):
    
    def __init__(self: object) -> None:

        # Note: I put try/except statements after .addstr() because
        # when you resize to small, it will do raise an error
        
        self.stdscr = curses.initscr()

        try:
            self.stdscr.keypad(1)
            curses.noecho()
            curses.cbreak()
            curses.curs_set(0)
            curses.start_color()
            curses.use_default_colors()

            for i in range(curses.COLORS):
                curses.init_pair(i, i, -1);
            
            self.base = 2
            self.spawn_choices = tuple(self.base**i for i in range(1, 3))
            self.spawn_rates = (90, 10)
            self.winning_power = 11

            self.grid_size = (4, 4)
            self.grid_pos = (13, 4)
            self.cell_size = (6, 2)

            self.grid = grid.Grid(self.grid_size)
            
            self.score = 0

            # dead = 0
            # playing = 1
            # won the game (on select screen) = 2
            # endless mode = 3
            self.game_state = 1

            self.save_data = {'highscore': 0,
                              'tile_highscore': self.spawn_choices[0]}

            try:
                with open('save.json', 'r', encoding='UTF-8') as save_file:
                    self.save_data = json.load(save_file)
            except FileNotFoundError:
                self._save_save_data_to_file()

            with open('texts.json', 'r', encoding='UTF-8') as texts_file:
                self.texts = json.load(texts_file)
            
            types = {'win': list,
                     'empty_tile': str,
                     'score': str,
                     'highscore': str,
                     'tile_highscore': str,
                     'death': str,
                     'info': str,
                     'stats': str}

            # type checking for texts.json
            for key, value in self.texts.items():
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
            json.dump(self.save_data, save_file)

    def _draw_grid(self: object) -> None:

        for y, row in enumerate(self.grid.grid):
            for x, item in enumerate(row):
                item_str = str(item)
                try:
                    self.stdscr.addstr(self.grid_pos[1] + y * self.cell_size[1],
                                       self.grid_pos[0] + x * self.cell_size[0],

                                       # the * (self.cell_size[0] - 1) is to clear numbers 
                                       item_str + ' ' * (self.cell_size[0] - len(item_str))
                                       if item else self.texts['empty_tile'] + ' ' * 
                                         (self.cell_size[0] - len(self.texts['empty_tile'])),

                                       curses.color_pair(
                                           int(min(math.log(item, self.base), 7) if item else 0)))
                except curses.error:
                    pass

    def _handle_key_input(self: object,
                          key: str) -> None:

        original_grid = self.grid.grid

        if self.game_state == 1 or self.game_state == 3:
            if key in ('w', 'k', 'KEY_UP'):
                return_value = self.grid.up(1)
                self.grid.grid = return_value[0]
                self.score += return_value[1]
                if self.grid.grid != original_grid:
                    self.grid.spawn_new_numbers(1, self.spawn_choices, self.spawn_rates)

            elif key in ('s', 'j', 'KEY_DOWN'):
                return_value = self.grid.down(1)
                self.grid.grid = return_value[0]
                self.score += return_value[1]
                if self.grid.grid != original_grid:
                    self.grid.spawn_new_numbers(1, self.spawn_choices, self.spawn_rates)

            elif key in ('a', 'h', 'KEY_LEFT'):
                return_value = self.grid.left(1)
                self.grid.grid = return_value[0]
                self.score += return_value[1]
                if self.grid.grid != original_grid:
                    self.grid.spawn_new_numbers(1, self.spawn_choices, self.spawn_rates)

            elif key in ('d', 'l', 'KEY_RIGHT'):
                return_value = self.grid.right(1)
                self.grid.grid = return_value[0]
                self.score += return_value[1]
                if self.grid.grid != original_grid:
                    self.grid.spawn_new_numbers(1, self.spawn_choices, self.spawn_rates)
        
        elif self.game_state and key == 'c':
            self.game_state = 3

        if key == 'r':
            self._reset()

    def _reset(self: object) -> None:

        self.grid.reset()
        self.grid.spawn_new_numbers(2, (self.spawn_choices[0],))
        
        self.score = 0
        self.game_state = 1

    def _render_text(self: object) -> None:
        
        # The try and excepts are to prevent curses from raising an error when it tries to write outside of the terminal

        # score
        addstr_robust(self.stdscr, self.grid_pos[1] + 5,
                      self.grid_pos[0] + self.grid_size[0] * self.cell_size[0] + 5,
                      f'{self.texts['score']}{self.score}')

        # highscore
        addstr_robust(self.stdscr, self.grid_pos[1] + 3,
                      self.grid_pos[0] + self.grid_size[0] * self.cell_size[0] + 5,
                      f'{self.texts['highscore']}{self.save_data['highscore']}')

        # highest tile
        addstr_robust(self.stdscr, self.grid_pos[1] + 1,
                      self.grid_pos[0] + self.grid_size[0] * self.cell_size[0] + 5,
                      f'{self.texts['tile_highscore']}{self.save_data['tile_highscore']}')
        
        # info
        addstr_robust(self.stdscr, 1, self.grid_pos[0] + int((self.grid_size[0]
                      * self.cell_size[0] - len(self.texts['info'])) / 2) - 2,
                      self.texts['info'])

        # death
        if not self.game_state:
            addstr_robust(self.stdscr, self.grid_pos[1] + self.grid_size[1]
                          * self.cell_size[1] + 1, self.grid_pos[0] + int((self.grid_size[0]
                          * self.cell_size[0] - len(self.texts['death'])) / 2) - 1,
                          self.texts['death'])
        
        # win
        elif self.game_state == 2:
            for dex, string in enumerate(self.texts['win']):
                addstr_robust(self.stdscr, self.grid_pos[1] + self.grid_size[1]
                              * self.cell_size[1] + dex + 1, self.grid_pos[0] + int((self.grid_size[0]
                              * self.cell_size[0] - len(string)) / 2) - 2,
                              string)

    def run(self: object) -> None:

        running = 1
        
        try:

            self._reset()

            self._render_text()
            self._draw_grid()

            while running:
                key = self.stdscr.getkey()
                self._handle_key_input(key)

                if (self.grid.up() == self.grid.grid
                    and self.grid.down() == self.grid.grid
                    and self.grid.left() == self.grid.grid
                    and self.grid.right() == self.grid.grid):

                    self.game_state = 0 # dead
                # i use an if statement so that it won't become 1
                # if the condition is not satisfied; it will tay unchanged
                if self.score > self.save_data['highscore']:
                    self.save_data['highscore'] = self.score
                    self._save_save_data_to_file()

                for row in self.grid.grid:
                    for item in row:
                        if item > self.save_data['tile_highscore']:
                            self.save_data['tile_highscore'] = item
                            self._save_save_data_to_file()
                        # I add the == 1 so it doesn't overwrite the game_state if it is 3
                        if item >= self.base**self.winning_power and self.game_state == 1:
                            self.game_state = 2

                self.stdscr.erase()
                self._render_text()
                self._draw_grid()
                self.stdscr.refresh()

        except KeyboardInterrupt:
            pass

        finally:
            curses.endwin()

            print(f'{self.texts['stats']}',
                  f' - {self.texts['score']}{self.score}',
                  f' - {self.texts['highscore']}{self.save_data['highscore']}',
                  f' - {self.texts['tile_highscore']}{self.save_data['tile_highscore']}', sep='\n')


if __name__ == '__main__':
    Game().run()

