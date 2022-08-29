from __future__ import annotations

from collections import Counter
from typing import Union, Optional

from copy import deepcopy


from errors import NewNumberDiscoveredError, WrongNumberOfOptionsError, OutOfFieldError, BrokenAssumption, Solved


class SudokuTile:
    def __init__(self, number: Optional[int] = 0, options: Optional[set] = None, row: Optional[int] = None,
                 column: Optional[int] = None):
        self.number = number
        self.options: set = options or self.create_sudoku_tile_options()
        self.row = row
        self.column = column

    def __str__(self) -> str:
        # return f"{self.number or 'Options: ' + str(self.options)}"
        return f"SudokuTile({self.number})"

    def __repr__(self) -> str:
        # return f"{self.number or 'Options: ' + str(self.options)}"
        return f"SudokuTile({self.number})"

    def __eq__(self, other: SudokuTile) -> bool:
        return self.number == other.number

    def set_tile_values(self, new_number: Optional[int] = None, new_options: Optional[set] = None):
        if new_number:
            self.number = new_number
            self.options = {new_number, }
        if new_options:
            self.options = new_options

    def update_tile_values_by_sudoku(self, group_values: list[SudokuTile]):
        """
        :param group_values: list of tiles [row, column or big square]
        """
        if self.number:  # no need to update
            return
        discovered_numbers_in_group = {tile.number for tile in group_values}
        new_options = self.options.difference(discovered_numbers_in_group)
        if len(new_options) in range(2, 10):
            self.set_tile_values(new_options=new_options)
        elif len(new_options) == 1:
            self.set_tile_values(new_number=new_options.pop())
            raise NewNumberDiscoveredError
        else:
            raise WrongNumberOfOptionsError

    @staticmethod
    def create_sudoku_tile_options():
        return set(range(1, 10))


class SudokuField:
    def __init__(self, field: list[list[Union[SudokuTile, int]]], conversion_required=False):
        if conversion_required:
            self.field: list[list[SudokuTile]] = self.create_sudoku_field(field)
        else:
            self.field: list[list[SudokuTile]] = field

    def __str__(self):
        result = ""
        for r_i, row in enumerate(self.field):
            if r_i % 3 == 0:
                result += "-" * 19 + "\n"
            for t_i, tile in enumerate(row):
                if t_i % 3 == 0:
                    result += "|"
                else:
                    result += " "
                result += f"{tile.number}" if tile.number else " "
            result += "|" + "\n"
        return result

    @staticmethod
    def check_group_for_single_option(group_values: list[SudokuTile]):
        discovered_numbers = [n.number for n in group_values if n.number != 0]
        if discovered_numbers and max(Counter(discovered_numbers).values()) > 1:
            raise BrokenAssumption
        numbers_registry = {i: [] for i in range(1, 10)}
        for i, tile in enumerate(group_values):
            for number in tile.options:
                if not tile.number:
                    numbers_registry[number].append(i)
        for number, indexes in numbers_registry.items():
            if len(indexes) == 1:
                tile = group_values[indexes[0]]
                tile.set_tile_values(new_number=number)
                raise NewNumberDiscoveredError

    @staticmethod
    def create_sudoku_field(field: list[list[Union[SudokuTile, int]]]):
        return [[SudokuTile(field[row][column], row=row, column=column) for column in range(9)] for row in range(9)]

    @staticmethod
    def check_outside_the_field(value):
        if value not in range(9):
            raise OutOfFieldError

    @classmethod
    def get_sudoku_big_square_idx(cls, row, column):
        cls.check_outside_the_field(row)
        cls.check_outside_the_field(column)
        square_row_big_idx = row // 3
        square_column_big_idx = column // 3
        return square_row_big_idx * 3 + square_column_big_idx

    def get_tile(self, row: int, column: int) -> SudokuTile:
        self.check_outside_the_field(row)
        self.check_outside_the_field(column)
        return self.field[row][column]

    def get_row(self, row_idx: int):
        self.check_outside_the_field(row_idx)
        return self.field[row_idx]

    def get_column(self, column_idx: int):
        self.check_outside_the_field(column_idx)
        return [row[column_idx] for row in self.field]

    def get_square(self, square_idx: int):
        self.check_outside_the_field(square_idx)
        square_row_big_idx = square_idx // 3
        square_column_big_idx = square_idx % 3
        result = []
        for row in range(9):
            for column in range(9):
                if row // 3 == square_row_big_idx and column // 3 == square_column_big_idx:
                    result.append(self.field[row][column])
        return result


class SudokuSolver:
    def __init__(self, field: list[list[Union[SudokuTile, int]]], conversion_required=True):
        self.sudoku_field = SudokuField(field, conversion_required)

    @classmethod
    def error_handler(cls, error: Exception):
        print(error.__name__)

    def solve(self, sudoku_field: SudokuField, indent: str = ""):
        print(indent, end="")
        last_run = False
        while True:
            try:
                # check each tile
                tile_to_check = None
                for row_idx in range(9):
                    row_values = sudoku_field.get_row(row_idx)
                    for column_idx in range(9):
                        column_values = sudoku_field.get_column(column_idx)
                        tile = sudoku_field.get_tile(row_idx, column_idx)
                        if tile.number:
                            continue
                        tile_to_check = tile
                        square_idx = sudoku_field.get_sudoku_big_square_idx(row_idx, column_idx)
                        square_values = sudoku_field.get_square(square_idx)

                        # check big square
                        tile.update_tile_values_by_sudoku(square_values)

                        # check row
                        tile.update_tile_values_by_sudoku(row_values)

                        # check column
                        tile.update_tile_values_by_sudoku(column_values)

                for i in range(9):
                    # check each row for single option
                    row_values = sudoku_field.get_row(i)
                    sudoku_field.check_group_for_single_option(row_values)

                    # check each column for single option
                    column_values = sudoku_field.get_column(i)
                    sudoku_field.check_group_for_single_option(column_values)

                    # check each square
                    square_values = sudoku_field.get_square(i)
                    sudoku_field.check_group_for_single_option(square_values)

            # except new number found -> start over
            except NewNumberDiscoveredError:
                last_run = False
                continue
            except OutOfFieldError:
                print(OutOfFieldError)
                break

            # try new options
            if not last_run:
                last_run = True
                continue
            if tile_to_check:
                # print("No obvious number to check left. Need to extend logic or make assumptions")

                for row_idx in range(9):
                    for column_idx in range(9):
                        tile = sudoku_field.get_tile(row_idx, column_idx)
                        if tile.number:
                            continue
                        if len(tile.options) < len(tile_to_check.options):
                            if len(tile_to_check.options) == 1:
                                print("ALARM")
                            tile_to_check = tile

                # One of options should be valid
                for option in tile_to_check.options:
                    try:
                        new_sudoku_field = deepcopy(sudoku_field)
                        new_tile = new_sudoku_field.get_tile(tile_to_check.row, tile_to_check.column)
                        new_tile.set_tile_values(new_number=option)
                        print(
                            f"Assumption: row {new_tile.row}, column {new_tile.column}, value {option} (from {tile_to_check.options})")
                        self.solve(new_sudoku_field, indent+"\t")
                    except BrokenAssumption:

                        self.error_handler(BrokenAssumption)
                        continue
                    except WrongNumberOfOptionsError:
                        self.error_handler(WrongNumberOfOptionsError)
                        continue
            else:
                print("SOLVED")
                print(sudoku_field)
                raise Solved


            break


if __name__ == '__main__':
    demo_field = [[3, 0, 6, 5, 0, 8, 4, 0, 0],
                  [5, 2, 0, 0, 0, 0, 0, 0, 0],
                  [0, 8, 7, 0, 0, 0, 0, 3, 1],
                  [0, 0, 3, 0, 1, 0, 0, 8, 0],
                  [9, 0, 0, 8, 6, 3, 0, 0, 5],
                  [0, 5, 0, 0, 9, 0, 6, 0, 0],
                  [1, 3, 0, 0, 0, 0, 2, 5, 0],
                  [0, 0, 0, 0, 0, 0, 0, 7, 4],
                  [0, 0, 5, 2, 0, 6, 3, 0, 0]]
    sf = SudokuField(demo_field, conversion_required=True)
    print(sf.field)
    # print(sf.get_row(0))
