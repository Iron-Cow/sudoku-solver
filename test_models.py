import pytest

from errors import OutOfFieldError
from models import SudokuField, SudokuTile

TEST_FIELD = [
    [3, 0, 6, 5, 0, 8, 4, 0, 0],
    [5, 2, 0, 0, 0, 0, 0, 0, 0],
    [0, 8, 7, 0, 0, 0, 0, 3, 1],
    [0, 0, 3, 0, 1, 0, 0, 8, 0],
    [9, 0, 0, 8, 6, 3, 0, 0, 5],
    [0, 5, 0, 0, 9, 0, 6, 0, 0],
    [1, 3, 0, 0, 0, 0, 2, 5, 0],
    [0, 0, 0, 0, 0, 0, 0, 7, 4],
    [0, 0, 5, 2, 0, 6, 3, 0, 0],
]

# Formatting alias
ST = SudokuTile


@pytest.fixture()
def sudoku_field() -> SudokuField:
    return SudokuField(TEST_FIELD, conversion_required=True)


def test_sudoku_field_creation(sudoku_field):
    new_sudoku_field = [
        [ST(3), ST(0), ST(6), ST(5), ST(0), ST(8), ST(4), ST(0), ST(0)],
        [ST(5), ST(2), ST(0), ST(0), ST(0), ST(0), ST(0), ST(0), ST(0)],
        [ST(0), ST(8), ST(7), ST(0), ST(0), ST(0), ST(0), ST(3), ST(1)],
        [ST(0), ST(0), ST(3), ST(0), ST(1), ST(0), ST(0), ST(8), ST(0)],
        [ST(9), ST(0), ST(0), ST(8), ST(6), ST(3), ST(0), ST(0), ST(5)],
        [ST(0), ST(5), ST(0), ST(0), ST(9), ST(0), ST(6), ST(0), ST(0)],
        [ST(1), ST(3), ST(0), ST(0), ST(0), ST(0), ST(2), ST(5), ST(0)],
        [ST(0), ST(0), ST(0), ST(0), ST(0), ST(0), ST(0), ST(7), ST(4)],
        [ST(0), ST(0), ST(5), ST(2), ST(0), ST(6), ST(3), ST(0), ST(0)]
    ]
    assert new_sudoku_field == sudoku_field.field


def test_get_row(sudoku_field):
    assert sudoku_field.get_row(4) == [ST(9), ST(0), ST(0), ST(8), ST(6), ST(3), ST(0), ST(0), ST(5)]


def test_get_column(sudoku_field):
    assert sudoku_field.get_column(7) == [ST(0), ST(0), ST(3), ST(8), ST(0), ST(0), ST(5), ST(7), ST(0)]


def test_get_square(sudoku_field):
    assert sudoku_field.get_square(5) == [ST(0), ST(8), ST(0), ST(0), ST(0), ST(5), ST(6), ST(0), ST(0)]


@pytest.mark.parametrize(
    "row, column, result, should_error",
    [
        (1, 7, 2, False),
        (8, 7, 8, False),
        (8, 1, 6, False),
        (0, 0, 0, False),
        (0, 9, 0, True),
        (11, 4, 0, True),
        (11, 99, 0, True),
        (-1, 0, 0, True),
        (-10, 9, 0, True),
    ],
)
def test_get_sudoku_big_square_idx(row, column, result, should_error):
    if should_error:
        with pytest.raises(OutOfFieldError):
            assert SudokuField.get_sudoku_big_square_idx(row, column)
    else:
        assert SudokuField.get_sudoku_big_square_idx(row, column) == result

