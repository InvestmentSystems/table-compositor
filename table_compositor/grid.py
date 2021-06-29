from collections import namedtuple

from table_compositor.presentation_model import (
    PresentationLayoutManager,
    get_presentation_model_max_cols,
    get_presentation_model_max_rows,
    shift_presentation_model,
    to_row_col_dict,
)

Cell = namedtuple("Cell", ["vertical", "children"])


class GridLayoutManager:
    @staticmethod
    def build_cells(layout, vertical=True):
        children = []
        for i in layout:
            if isinstance(i, list):
                _inner_value = GridLayoutManager.build_cells(i, not vertical)
                children.append(Cell(children=_inner_value, vertical=vertical))
            else:
                children.append(Cell(children=i, vertical=vertical))
        return Cell(vertical=vertical, children=children)

    @staticmethod
    def traverse(cell, f):
        if not isinstance(cell.children, (Cell, list)):
            return Cell(vertical=cell.vertical, children=f(cell.children))

        if isinstance(cell.children, Cell):
            r = GridLayoutManager.traverse(cell.children, f)
            return Cell(vertical=cell.vertical, children=r)

        child_values = []
        if isinstance(cell.children, list):
            for child in cell.children:
                r = GridLayoutManager.traverse(child, f)
                child_values.append(r)
            return Cell(vertical=cell.vertical, children=child_values)

    @staticmethod
    def foldl(cell, f, accum):
        if not isinstance(cell.children, (Cell, list)):
            accum = f(accum, cell.children)
            return accum

        if isinstance(cell.children, Cell):
            return GridLayoutManager.foldl(cell.children, f, accum)

        if isinstance(cell.children, list):
            for child in cell.children:
                accum = GridLayoutManager.foldl(child, f, accum)
            return accum

    @staticmethod
    def shift_grid(
        cell, i, j, shifter_func, ht_func, width_func, h_shift_by=1, v_shift_by=1
    ):
        if not isinstance(cell.children, (list, Cell)):
            child = cell.children
            # shifting
            pm = shifter_func(child, i, j)
            new_c = Cell(vertical=cell.vertical, children=pm)
            offset = (ht_func(child) + v_shift_by, width_func(child) + h_shift_by)
            return (offset, new_c)

        if isinstance(cell.children, Cell):
            result = GridLayoutManager.shift_grid(
                cell.children,
                i,
                j,
                shifter_func,
                ht_func,
                width_func,
                h_shift_by,
                v_shift_by,
            )

            # print(('-----'))
            # print('result=', result)
            return result

        child_values = []
        row, col = i, j
        new_max_row, new_max_col = 0, 0
        for child in cell.children:
            (max_row, max_col), new_c = GridLayoutManager.shift_grid(
                child,
                row,
                col,
                shifter_func,
                ht_func,
                width_func,
                h_shift_by,
                v_shift_by,
            )

            child_values.append(new_c)
            if cell.vertical:
                row = row + max_row
                new_max_row = new_max_row + max_row
                new_max_col = max(new_max_col, max_col)
            else:
                col = col + max_col
                new_max_col = new_max_col + max_col
                new_max_row = max(new_max_row, max_row)

        # print('returning...', (new_max_row, new_max_col), child_values)
        # print('Done shift grid')
        return (
            (new_max_row, new_max_col),
            Cell(vertical=cell.vertical, children=child_values),
        )

    @staticmethod
    def get_row_col_dict(layout, orientation="vertical", h_shift_by=1, v_shift_by=1):
        """
        Transform the grid into a dict of {coord: value_and_style_attribute value}
        """

        grid = GridLayoutManager.compute_grid(layout, orientation)
        _, shifted_grid = GridLayoutManager.shift_grid(
            cell=grid,
            i=0,
            j=0,
            shifter_func=shift_presentation_model,
            ht_func=get_presentation_model_max_rows,
            width_func=get_presentation_model_max_cols,
            h_shift_by=h_shift_by,
            v_shift_by=v_shift_by,
        )

        f = lambda accum, pm: {**accum, **to_row_col_dict(pm)}
        return GridLayoutManager.foldl(shifted_grid, f, dict())

    @staticmethod
    def compute_grid(layout, orientation="vertical"):
        """
        Transform the grid into a dict of {coord: value_and_style_attribute value}
        """

        vertical = orientation.upper() == "VERTICAL"
        grid = GridLayoutManager.build_cells(layout, vertical)
        grid = GridLayoutManager.traverse(grid, PresentationLayoutManager.resolve_loc)
        return grid

    @staticmethod
    def get_non_shifted_row_col_dict(layout, orientation="vertical"):
        """
        Transform the grid into a dict of {coord: value_and_style_attribute value}
        """

        grid = GridLayoutManager.compute_grid(layout, orientation)
        return GridLayoutManager.traverse(grid, to_row_col_dict)
