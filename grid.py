import copy
import curses
import random

class Grid(object):

    def __init__(self: object,
                 size: tuple):
        
        self._size = size
        self._grid = self._create_grid(size)

    @property
    def grid(self: object) -> list[list[int]]:

        return self._grid

    @grid.setter
    def grid(self: object,
             value: list[list[int]]) -> None:

        if type(value) != list:
            raise ValueError('grid needs to be [list row[int number], list row[int number]...].')
        for row in value:
            if type(row) != list:
                raise ValueError('grid needs to be [list row[int number], list row[int number]...].')

            # this catches size difference and row length difference
            # if size was different, it would catch (obvious)
            # if length was different from other rows, then at least one row is not the correct row length

            if (len(value), len(row)) != self._size:
                raise ValueError('new grid needs to be the same size as was last set ' +
                                 'and the length of all rows should be the same.')
            for item in row:
                if type(item) != int:
                    raise ValueError('grid needs to be [list row[int number], list row[int number]...].')

            self._grid = value
    
    @property
    def size(self: object) -> tuple[int]:

        return size

    @size.setter
    def size(self: object,
             value: tuple[int]) -> None:

        if type(value) != tuple or len(value) != 2:
            raise ValueError('size needs to be tuple[int length, int height].')
        for item in value:
            if type(item) != int:
                raise ValueError('size needs to be tuple[int length, int height].')
            elif item <= 0:
                raise ValueError('size needs to be at least tuple[1, 1].')

        if value[0] >= self._size[0]:
            for row in self._grid:
                for x in range(self._size[0], value[0]):
                    row.append(0)
        else:
            for row in self._grid:
                print(row)
                for x in range(self._size[0] - 1, value[0] - 1, -1):
                    del row[x]

        if value[1] >= self._size[1]:
            for y in range(self._size[1], value[1]):
                self._grid.append([0] * value[0])
        else:
            for y in range(self._size[0] - 1, value[1] - 1, -1):
                del self._grid[y]
                
        self._size = value

    def _create_grid(self: object,
                     size: tuple) -> None:

        grid = []
        for i in range(size[1]):
            grid.append([0] * size[0])
        
        return grid

    def reset(self: object) -> None:
        self.grid = self._create_grid(self._size)

    def spawn_new_numbers(self: object, 
                          count: int,
                          choices: list or tuple[int],
                          weights: list or tuple[float] or None=None) -> None:

        available_spaces = []

        for y in range(self._size[1]):
            for x in range(self._size[0]):
                if not self._grid[y][x]:
                    available_spaces.append((x, y))
                    
        for i in range(min(count, len(available_spaces),
                           self._size[0] * self._size[1])):
            dex = random.randrange(0, len(available_spaces))
            random_pos = available_spaces[dex]
            del available_spaces[dex]

            self._grid[random_pos[1]][random_pos[0]] = random.choices(choices, weights, k=1)[0]

    def up(self: object,
           return_score: int=0) -> list or tuple:

        grid = self._grid

        grid_size = self._size
        return_grid = copy.deepcopy(grid)

        score = 0

        # a grid containing the combined status of each value
        # what I mean is that, if the number at a position is 1
        # the tile at that position on the real grid was combined during this iteration
        # tiles should only combine with tiles not combined during this iteration
        combined_statuses = self._create_grid(grid_size)

        for x in range(grid_size[0]):
            for y in range(1, grid_size[1]):
                unchanged_value = return_grid[y][x]
                current_y = y
                # repeatedly checks if there is available space above
                # moves the number if there is
                while current_y > 0 and not return_grid[current_y - 1][x]:
                    return_grid[current_y - 1][x] = unchanged_value 
                    return_grid[current_y][x] = 0
                    current_y -= 1
                # checks for combining numbers
                if (current_y > 0 and not combined_statuses[y][current_y - 1]
                    and unchanged_value == return_grid[current_y - 1][x]):

                    return_grid[current_y - 1][x] = unchanged_value * 2
                    combined_statuses[current_y - 1][x] = 1
                    return_grid[current_y][x] = 0
                    score += unchanged_value * 2

        return (return_grid, score) if return_score else return_grid
        
    def down(self: object,
             return_score: int=0) -> list or tuple:

        grid = self._grid

        grid_size = self._size
        return_grid =  copy.deepcopy(grid)

        score = 0

        # a grid containing the combined status of each value
        # what I mean is that, if the number at a position is 1
        # the tile at that position on the real grid was combined during this iteration
        # tiles should only combine with tiles not combined during this iteration
        combined_statuses = self._create_grid(grid_size)

        for x in range(grid_size[0]):
            for y in range(grid_size[1] - 2, -1, -1):
                unchanged_value = return_grid[y][x]
                current_y = y
                # repeatedly checks if there is available space below
                # moves the number if there is
                while current_y < grid_size[1] - 1 and not return_grid[current_y + 1][x]:
                    return_grid[current_y + 1][x] = unchanged_value
                    return_grid[current_y][x] = 0
                    current_y += 1
                # checks for combining numbers

                if (current_y < grid_size[1] - 1 and not combined_statuses[y][current_y + 1]
                    and unchanged_value == return_grid[current_y + 1][x]):

                    return_grid[current_y + 1][x] = unchanged_value * 2
                    combined_statuses[current_y + 1][x] = 1
                    return_grid[current_y][x] = 0
                    score += unchanged_value * 2

        return (return_grid, score) if return_score else return_grid

    def left(self: object,
             return_score: int=0) -> list or tuple:

        grid = self._grid

        grid_size = self._size
        return_grid = copy.deepcopy(grid)
        
        score = 0

        # a grid containing the combined status of each value
        # what I mean is that, if the number at a position is 1
        # the tile at that position on the real grid was combined during this iteration
        # tiles should only combine with tiles not combined during this iteration
        combined_statuses = self._create_grid(grid_size)

        for y in range(grid_size[1]):
            for x in range(1, grid_size[0]):
                unchanged_value = return_grid[y][x]
                current_x = x
                # repeatedly checks if there is available space above
                # moves the number if there is
                while current_x > 0 and not return_grid[y][current_x - 1]:
                    return_grid[y][current_x - 1] = unchanged_value 
                    return_grid[y][current_x] = 0
                    current_x -= 1
                # checks for combining numbers
                if (current_x > 0 and not combined_statuses[y][current_x - 1] 
                    and unchanged_value == return_grid[y][current_x - 1]):

                    return_grid[y][current_x - 1] = unchanged_value * 2
                    combined_statuses[y][current_x - 1] = 1
                    return_grid[y][current_x] = 0
                    score += unchanged_value * 2

        return (return_grid, score) if return_score else return_grid

    def right(self: object,
              return_score: int=0) -> list or tuple:

        grid = self._grid

        grid_size = self._size 
        return_grid = copy.deepcopy(grid)

        score = 0

        # a grid containing the combined status of each value
        # what I mean is that, if the number at a position is 1
        # the tile at that position on the real grid was combined during this iteration
        # tiles should only combine with tiles not combined during this iteration
        combined_statuses = self._create_grid(grid_size)

        for y in range(grid_size[1]):
            for x in range(grid_size[0] - 2, -1, -1):
                unchanged_value = return_grid[y][x]
                current_x = x
                # repeatedly checks if there is available space below
                # moves the number if there is
                while current_x < grid_size[0] - 1 and not return_grid[y][current_x + 1]:
                    return_grid[y][current_x + 1] = unchanged_value
                    return_grid[y][current_x] = 0
                    current_x += 1

                # checks for combining numbers
                if (current_x < grid_size[0] - 1 and not combined_statuses[y][current_x + 1]
                    and unchanged_value == return_grid[y][current_x + 1]):

                    return_grid[y][current_x + 1] = unchanged_value * 2
                    combined_statuses[y][current_x + 1] = 1
                    return_grid[y][current_x] = 0
                    score += unchanged_value * 2

        return (return_grid, score) if return_score else return_grid

        

