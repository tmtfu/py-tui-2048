import sys
import math
import json
import curses 
import grid


class Game(object):
    
    def __init__(self: object) -> None:

        # Note: I put try/except statements after .addstr() because
        # when you resize to small, it will do raise an error
        
        self.stdscr = curses.initscr()
        self.stdscr.keypad(1)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

        for i in range(curses.COLORS):
            curses.init_pair(i, i, -1);
        
        self.base = 2
        self.spawn_choices = (self.base, self.base**2)
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
                          'tile_highscore': 2}

        try:
            with open('save.json', 'r', encoding='UTF-8') as save_file:
                self.save_data = json.load(save_file)
        except FileNotFoundError:
            self.save_save_data_to_file()

        with open('texts.json', 'r', encoding='UTF-8') as texts_file:
            self.texts = json.load(texts_file)

    def save_save_data_to_file(self: object) -> None:
        'Saves the player\'s save data to the data/save/save.json file'

        with open('save.json', 'w', encoding='UTF-8') as save_file:
            json.dump(self.save_data, save_file)

    def draw_grid(self: object) -> None:

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

    def handle_key_input(self: object,
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
            self.reset()

    def reset(self: object) -> None:

        self.grid.reset()
        self.grid.spawn_new_numbers(2, (self.spawn_choices[0],))
        
        self.score = 0
        self.game_state = 1

    def render_text(self: object) -> None:
        
        # The try and excepts are to prevent curses from raising an error when it tries to write outside of the terminal
        try:
            self.stdscr.addstr(1, int(self.grid_pos[0] + (self.grid_size[0] * self.cell_size[0]
                               - len(self.texts['info'].splitlines()[0])) / 2) - 2,
                               self.texts['info'])
        except curses.error:
            pass

        # score
        try:
            self.stdscr.addstr(self.grid_pos[1] + 5, self.grid_pos[0]
                               + self.grid_size[0] * self.cell_size[0] + 5,
                               f'{self.texts['score']}{self.score}')
        except curses.error:
            pass
        
        # highscore
        try:
            self.stdscr.addstr(self.grid_pos[1] + 3, self.grid_pos[0]
                               + self.grid_size[0] * self.cell_size[0] + 5,
                               f'{self.texts['highscore']}{self.save_data['highscore']}')
        except curses.error:
            pass

        # highest tile
        try:
            self.stdscr.addstr(self.grid_pos[1] + 1, self.grid_pos[0]
                               + self.grid_size[0] * self.cell_size[0] + 5,
                               f'{self.texts['tile_highscore']}{self.save_data['tile_highscore']}')
        except curses.error:
            pass
        
        # death
        if not self.game_state:
            try:
                self.stdscr.addstr(self.grid_pos[1] + self.grid_size[1] * self.cell_size[1] + 1,
                                   int(self.grid_pos[0] + (self.grid_size[0] * self.cell_size[0]
                                        - len(self.texts['death'].splitlines()[0])) / 2) - 1,
                                   # splitlines()[0] to get the first line ^
                                   # the code for the x coord above centers the text below the grid
                                   self.texts['death'])
            except curses.error:
                pass

        elif self.game_state == 2:
            try:
                self.stdscr.addstr(self.grid_pos[1] + self.grid_size[1] * self.cell_size[1] + 1,
                                   int(self.grid_pos[0] + (self.grid_size[0] * self.cell_size[0]
                                        - len(self.texts['win'].splitlines()[0])) / 2) - 2,
                                   # splitlines()[0] to get the first line ^
                                   # the code for the x coord above centers the text below the grid
                                   self.texts['win'])
            except curses.error:
                pass

    def run(self: object) -> None:

        running = 1
        
        self.reset()
        self.render_text()

        self.draw_grid()
        
        try:
            while running:
                key = self.stdscr.getkey()
                self.handle_key_input(key)

                if (self.grid.up() == self.grid.grid
                    and self.grid.down() == self.grid.grid
                    and self.grid.left() == self.grid.grid
                    and self.grid.right() == self.grid.grid):

                    self.game_state = 0 # dead
                # i use an if statement so that it won't become 1
                # if the condition is not satisfied; it will tay unchanged

                if self.score > self.save_data['highscore']:
                    self.save_data['highscore'] = self.score
                    self.save_save_data_to_file()

                for row in self.grid.grid:
                    for item in row:
                        if item > self.save_data['tile_highscore']:
                            self.save_data['tile_highscore'] = item
                            self.save_save_data_to_file()
                        # I add the == 1 so it doesn't overwrite the game_state if it is 3
                        if item >= self.base**self.winning_power and self.game_state == 1:
                            self.game_state = 2

                self.stdscr.erase()
                self.render_text()
                self.draw_grid()
                self.stdscr.refresh()

        except KeyboardInterrupt:
            self.save_save_data_to_file()

            curses.endwin()

            print(f'{self.texts['stats']}',
                  f' - {self.texts['score']}{self.score}',
                  f' - {self.texts['highscore']}{self.save_data['highscore']}',
                  f' - {self.texts['tile_highscore']}{self.save_data['tile_highscore']}', sep='\n')


if __name__ == '__main__':
    Game().run()

