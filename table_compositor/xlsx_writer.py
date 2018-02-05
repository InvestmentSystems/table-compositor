import logging
import functools
import collections
from itertools import chain

from openpyxl import Workbook

from .grid import GridLayoutManager
from .util import df_type_to_str

logger = logging.getLogger()

# handle switch from openpyxl 2.3 to 2.4
try:
    from openpyxl.cell import get_column_letter
except ImportError:
    from openpyxl.utils.cell import get_column_letter

class XLSXWriter:
    @staticmethod
    @functools.lru_cache(maxsize=None)
    def _get_column_letter(col):
        return get_column_letter(col)

    @staticmethod
    def new_workbook():
        '''
        Helper function to create an empty workbook.
        '''
        wb = Workbook()
        wb.remove_sheet(wb.active)
        return wb

    @staticmethod
    def add_sheet(wb: Workbook, sheet_name: str):
        '''
        Given a wb and sheet_name, create a new sheet in the workbook
        and make this sheet the active sheet.
        '''
        ws = wb.create_sheet(title=sheet_name[:31]) # max allowed title size
        return ws

    @staticmethod
    def to_xlsx(layout, output_fp, orientation='vertical', **kwargs):
        '''
        Take a layout which contains a list of presentation models builts using the build_presentation_model function.

        Args:
            layout: An nested list of presentation_models, examples: [presentation_model] or [presentation_model1, presentation_mode2] etc
            output_fp: the xlsx file name
            orientation: if vertical, the top level presentation model elements are rendered vertically, and for every nested level the orientation is flipped.
                         if horizontal, then the behavior is inverse
            kwargs:
                column-width: default=20, the default column width of all columns in the worksheet. Individual column width cannot be set currently
        '''
        row_col_dict = GridLayoutManager.get_row_col_dict(
            layout, orientation=orientation)
        wb = Workbook()
        ws = wb.active
        XLSXWriter._to_xlsx_worksheet(row_col_dict, ws, **kwargs)
        wb.save(output_fp)

    @staticmethod
    def to_xlsx_worksheet(layout, ws, orientation='vertical', **kwargs):
        '''
        Take a layout which contains a list of presentation models builts using the build_presentation_model function. This method is useful to control where the file is created and to add more attributes to the worksheet before it is being saved. Updates the ws argument in place.

        Args:
            layout: An nested list of presentation_models, examples: [presentation_model] or [presentation_model1, presentation_mode2] etc
            ws: openpyxl Worksheet is which the presentation model will be rendered.
            orientation: if vertical, the top level presentation model elements are rendered vertically, and for every nested level the orientation is flipped.
                         if horizontal, then the behavior is inverse
            kwargs:
                    column-width: default=20, the default column width of all columns in the worksheet. Individual column width cannot be set currently
                    post_process_ws_func: a function that will be called back with the worksheet, for final processing. For example, if special
                    formatting needs to be performed at the column level (freezing columns, hiding columns. etc.)
        '''

        row_col_dict = GridLayoutManager.get_row_col_dict(
            layout, orientation=orientation)
        #print('Got row col dict')
        XLSXWriter._to_xlsx_worksheet(row_col_dict, ws, **kwargs)

    range_string = '{}{}:{}{}'

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def _get_range_string(offsets):
        r1, c1, r2, c2 = offsets

        range_string = XLSXWriter.range_string.format(
                XLSXWriter._get_column_letter(c1),
                r1,
                XLSXWriter._get_column_letter(c2),
                r2)
        return range_string

    @staticmethod
    def _to_xlsx_worksheet(row_col_dict, ws, **kwargs):
        '''
        Args:
            ws: worksheet to use for rendering
        '''
        kwargs = kwargs or {}
        column_width = kwargs.get('column_width', 20)
        call_back_fn = kwargs.get('post_process_ws_func')
        logger.debug('Start creating xlsx cells')
        for offsets, (value, style, _) in row_col_dict.items():
            offsets = tuple(i + 1 for i in offsets) #bump needed for openpyxl
            cell = ws.cell(column=offsets[1],
                        row=offsets[0],
                        value=df_type_to_str(value))
            if offsets[0] != offsets[2]  or offsets[1] != offsets[3]:
                ws.merge_cells(
                    start_row=offsets[0],
                    start_column=offsets[1],
                    end_row=offsets[2],
                    end_column=offsets[3])

            rows = ws[XLSXWriter._get_range_string(offsets)]
            # we do this since some formatting (fill, border) for merged cells
            # still need set for each individual cell.
            # we assume setting the same formatting (eg. border)
            # for each cell in merged range will mask the values
            # such that it feels like the merged cell is being
            # formatted as one cell. For example the left border
            # is derived from leftmost cell and right border is
            # derived from right most cell, even though same border
            # attributes are set for each cell in the merged range.
            for cell in chain(*rows):
                for attr, style_value in style.user_style.items():
                    try:
                        setattr(cell, attr, style_value)
                    except AttributeError:
                        # we do not set the attr
                        pass
        # we loop around all columns so that we do this
        # column level work only once for each column
        for offsets in row_col_dict:
            col_letter = XLSXWriter._get_column_letter(offsets[1] + 1)
            ws.column_dimensions[col_letter].width = column_width
        #print("Before callback function")
        if call_back_fn:
            call_back_fn(ws)
        logger.debug('Returning after creating worksheet')
