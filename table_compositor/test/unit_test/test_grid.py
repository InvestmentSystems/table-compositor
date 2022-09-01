from pytest import mark
import typing as tp

import table_compositor.grid as glm


class PM(tp.NamedTuple):
    name: str
    i: int
    j: int
    max_rows: int
    max_cols: int

    def get_max_ht(self):
        return self.max_rows

    def get_max_width(self):
        return self.max_cols


class GridFixture(tp.NamedTuple):
    input: tp.List[PM]
    expected: tp.Tuple[tp.Tuple[int, int], ...]


def get_fixtures() -> tp.List[GridFixture]:
    # pmXY where X = # of rows, Y = # of cols
    pm22 = PM("22", 0, 0, 2, 2)
    pm42 = PM("42", 0, 0, 4, 2)
    pm32 = PM("32", 0, 0, 3, 2)
    pm24 = PM("24", 0, 0, 2, 4)

    # each fixture has input and expected co-ordinates, assuming 1 row padding
    return [
        (
            [pm22, pm22, pm22],
            ((0, 0), (3, 0), (6, 0)),
        ),
        (
            [pm42, [pm22, pm32]],
            ((0, 0), (5, 0), (5, 3)),
        ),
        (
            [pm42, [pm24, pm22]],
            ((0, 0), (5, 0), (5, 5)),
        ),
        (
            [[pm42, pm22], [pm22, pm42]],
            ((0, 0), (0, 3), (5, 0), (5, 3)),
        ),
        (
            [[pm22, [pm22, [pm24, [pm42, pm42], pm22]]], pm22],
            ((0, 0), (0, 3), (3, 3), (3, 8), (3, 11), (8, 8), (13, 0)),
        ),
    ]


@mark.parametrize("grid_fixture", get_fixtures())
def test_grid_layout_manager(grid_fixture: GridFixture) -> None:
    fixture, expected = grid_fixture

    shift_func = lambda pm, i, j: PM(
        pm.name, pm.i + i, pm.j + j, pm.max_rows, pm.max_cols
    )
    ht_func = lambda pm: pm.max_rows
    width_func = lambda pm: pm.max_cols

    grid = glm.GridLayoutManager.build_cells(fixture, vertical=True)
    shifted_grid = glm.GridLayoutManager.shift_grid(
        grid, 0, 0, shift_func, ht_func, width_func
    )

    # to get the dict of coords for testing
    f = lambda x, pm: {**x, **{(pm.i, pm.j): pm}}
    actual_dict = glm.GridLayoutManager.foldl(shifted_grid[1], f, dict())

    assert sorted(actual_dict) == sorted(expected)
