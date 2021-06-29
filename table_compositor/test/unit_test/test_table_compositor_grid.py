import unittest

import table_compositor.grid as glm


class PM:
    def __init__(self, name, i, j, max_rows, max_cols):
        self.name = name
        self.i = i
        self.j = j
        self.max_rows = max_rows
        self.max_cols = max_cols

    def get_max_ht(self):
        return self.max_rows

    def get_max_width(self):
        return self.max_cols

    def __repr__(self):
        return "PM(name={}, i={}, j={}, ht={} width={})".format(
            self.name, self.i, self.j, self.max_rows, self.max_cols
        )


class LayoutFixtures:
    @staticmethod
    def get_all_fixtures():

        # pmXY  where X = no of rows, Y = no of cols
        pm22 = PM("22", 0, 0, 2, 2)
        pm42 = PM("42", 0, 0, 4, 2)
        pm32 = PM("32", 0, 0, 3, 2)
        pm24 = PM("24", 0, 0, 2, 4)

        # each fixture has input and expected co-ordinates
        fixture0 = (
            [pm22, pm22, pm22],
            ((0, 0), (3, 0), (6, 0)),
        )  # assuming 1 row padding
        fixture1 = ([pm42, [pm22, pm32]], ((0, 0), (5, 0), (5, 3)))

        fixture2 = ([pm42, [pm24, pm22]], ((0, 0), (5, 0), (5, 5)))

        fixture3 = ([[pm42, pm22], [pm22, pm42]], ((0, 0), (0, 3), (5, 0), (5, 3)))

        fixture4 = (
            [[pm22, [pm22, [pm24, [pm42, pm42], pm22]]], pm22],
            ((0, 0), (0, 3), (3, 3), (3, 8), (3, 11), (8, 8), (13, 0)),
        )
        return (fixture0, fixture1, fixture2, fixture3, fixture4)


class TestGridLayoutManagerMeta(type):
    def __new__(cls, names, bases, attrs):
        def test_func_constructor(fixtures, is_vertical):
            def _func(self):
                fixture, expected = fixtures

                shift_func = lambda pm, i, j: PM(
                    pm.name, pm.i + i, pm.j + j, pm.max_rows, pm.max_cols
                )
                ht_func = lambda pm: pm.max_rows
                width_func = lambda pm: pm.max_cols

                grid = glm.GridLayoutManager.build_cells(fixture, vertical=is_vertical)
                shifted_grid = glm.GridLayoutManager.shift_grid(
                    grid, 0, 0, shift_func, ht_func, width_func
                )

                # to get the dict of coords for testing
                f = lambda x, pm: {**x, **{(pm.i, pm.j): pm}}
                z = glm.GridLayoutManager.foldl(shifted_grid[1], f, dict())
                self.compare(z, expected)

            return _func

        for i, fixtures in enumerate(LayoutFixtures.get_all_fixtures()):
            test_name = "test_{}".format(i)
            attrs[test_name] = test_func_constructor(fixtures, is_vertical=True)

        return type.__new__(cls, names, bases, attrs)


class TestUnit(unittest.TestCase, metaclass=TestGridLayoutManagerMeta):
    def compare(self, actual_dict, expected_dict):

        actual = sorted(actual_dict)
        expected = sorted(expected_dict)
        self.assertListEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
