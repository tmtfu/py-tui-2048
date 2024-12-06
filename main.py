import sys
import math
import json
import curses 
import grid


class Game(object):
    
    def __init__(self: object,
                 stdscr: curses.window) -> None:

        # Note: I put try/except statements after .addstr() because
        # when you resize to small, it will do raise an error

        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        self.stdscr = stdscr

        for i in range(curses.COLORS):
            curses.init_pair(i, i, -1);
        
        self.base = 2
        self.spawn_choices = (self.base, self.base**2)
        self.spawn_rates = (90, 10)

        self.grid_size = (4, 4)
        self.grid_pos = (13, 4)
        self.cell_size = (6, 2)

        self.grid = grid.Grid(self.grid_size)
        
        self.score = 0

        self.dead = 0

        self.save_data = {'highscore': 0,
                          'tile_highscore': 2}

        try:
            with open('save.json', 'r', encoding='UTF-8') as save_file:
                self.save_data = json.load(save_file)
        except FileNotFoundError:
            self.save_save_data_to_file()

        # texts
        with open('text.json', 'r', encoding='UTF-8') as save_file:
            self.texts = json.load(save_file)

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
                                  if item else self.texts['empty_tile'] + ' '
                                  * (self.cell_size[0] - len(self.texts['empty_tile'])),

                                  curses.color_pair(
                                      int(min(math.log(item, self.base), 7) if item else 0)))
                except curses.error:
                    pass


    def handle_key_input(self: object,
                         key_code: int) -> None:

        original_grid = self.grid.grid

        name = curses.keyname(key_code)

        if not self.dead and str(name) in ("b'w'", "b'k'", "b'KEY_UP'"):
            return_value = self.grid.up(1)
            self.grid.grid = return_value[0]
            self.score += return_value[1]
            if self.grid.grid != original_grid:
                self.grid.spawn_new_numbers(1, self.spawn_choices, self.spawn_rates)

        elif not self.dead and str(name) in ("b's'", "b'j'", "b'KEY_DOWN'"):
            return_value = self.grid.down(1)
            self.grid.grid = return_value[0]
            self.score += return_value[1]
            if self.grid.grid != original_grid:
                self.grid.spawn_new_numbers(1, self.spawn_choices, self.spawn_rates)

        elif not self.dead and str(name) in ("b'a'", "b'h'", "b'KEY_LEFT'"):
            return_value = self.grid.left(1)
            self.grid.grid = return_value[0]
            self.score += return_value[1]
            if self.grid.grid != original_grid:
                self.grid.spawn_new_numbers(1, self.spawn_choices, self.spawn_rates)

        elif not self.dead and str(name) in ("b'd'", "b'l'", "b'KEY_RIGHT'"):
            return_value = self.grid.right(1)
            self.grid.grid = return_value[0]
            self.score += return_value[1]
            if self.grid.grid != original_grid:
                self.grid.spawn_new_numbers(1, self.spawn_choices, self.spawn_rates)

        if str(name) == "b'r'":
            self.reset()

    def reset(self: object) -> None:

        self.grid.reset()
        self.grid.spawn_new_numbers(2, (self.spawn_choices[0],))
        
        self.score = 0
        self.dead = 0

    def render_text(self: object) -> None:

        try:
            self.stdscr.addstr(1, 2, self.texts['info'])
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
        self.dead = (self.grid.up() == self.grid.grid
                     and self.grid.down() == self.grid.grid
                     and self.grid.left() == self.grid.grid
                     and self.grid.right() == self.grid.grid)
        if self.dead:
            try:
                self.stdscr.addstr(self.grid_pos[1] + self.grid_size[1] 
                                   * self.cell_size[1] + 1, self.grid_pos[0] + 6,
                                   self.texts['death'])
            except curses.error:
                pass

    def run(self: object) -> None:

        running = 1
        
        self.reset()
        self.render_text()
        
        self.draw_grid()
        
        try:
            while running:
                key = self.stdscr.getch()
                self.handle_key_input(key)
                if self.score > self.save_data['highscore']:
                    self.save_data['highscore'] = self.score
                    self.save_save_data_to_file()
                for row in self.grid.grid:
                    for item in row:
                        if item > self.save_data['tile_highscore']:
                            self.save_data['tile_highscore'] = item
                            self.save_save_data_to_file()
                self.stdscr.erase()
                self.render_text()
                self.draw_grid()
                self.stdscr.refresh()

        except KeyboardInterrupt:
            self.save_save_data_to_file()
            curses.endwin()
            print(f'{self.texts['stats']}\n'
                  f' - {self.texts['score']}{self.score}\n' \
                  f' - {self.texts['highscore']}{self.save_data['highscore']}\n' \
                  f' - {self.texts['tile_highscore']}{self.save_data['tile_highscore']}')
            sys.exit()


def main(stdscr):
    Game(stdscr).run()

if __name__ == '__main__':
    curses.wrapper(main)

