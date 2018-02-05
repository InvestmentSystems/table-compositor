from itertools import groupby
from .grid import GridLayoutManager
from .grid import Cell
from .presentation_model import StyleWrapper
from .presentation_model import ValueAndStyleAttributes

class HTMLWriter:

    @staticmethod
    def _wrap_table_element(element, attrs, value):
        _attrs = ' '.join("{}='{}'".format(k, v) for k, v in sorted(attrs.items()))
        _attrs = _attrs.strip(" ")
        _attrs = ' ' + _attrs if _attrs else ''
        s = '<{elem}{elem_attr}>{v}</{elem}>\n'.format(
            elem=element, elem_attr=_attrs, v=value)
        return s

    @staticmethod
    def style_to_str(style):
        '''
        convert td_style to str in inline css format.
        '''
        if isinstance(style, StyleWrapper):
            style = style.user_style._asdict()
        if hasattr(style, '_asdict'):  #for named tuples
            style = style._asdict()
        if isinstance(style, str):
            return style
        d = {k.replace('_', '-'):v for k, v in style.items()}
        d = ";".join("{}:{}".format(k, v) for k, v in sorted(d.items()) if v)
        return d

    @staticmethod
    def _to_html(row_col_dict, **kwargs):
        '''
        Args:
            row_col_dict: dict with (0, 0, 0, 0) : (Value, Style)
        '''
        def wrap_tr(offsets):
            s = []
            nesting_level = row_col_dict[offsets[0]].nesting_level
            for offset in offsets:
                row_span = offset.end_row - offset.start_row + 1
                col_span = offset.end_col - offset.start_col + 1
                value = row_col_dict[offset].value
                style = row_col_dict[offset].style_wrapper.user_style
                style = HTMLWriter.style_to_str(style)

                td_attr = dict(
                    rowspan=row_span,
                    colspan=col_span, style=style)
                if nesting_level > row_col_dict[offset].nesting_level:
                    # we have encountered a nested table
                    inner_html = HTMLWriter._to_html(value)
                else:
                    inner_html = value
                td = HTMLWriter._wrap_table_element('td', td_attr, inner_html)
                s.extend(td)
            tr = HTMLWriter._wrap_table_element('tr', {}, ''.join(s))
            return tr

        trs = []
        for _, offsets in groupby(sorted(row_col_dict), key=lambda x: (x[0])):
            trs.append(wrap_tr(list(offsets)))

        table_attrs = kwargs or dict()
        return HTMLWriter._wrap_table_element(
            'table',
            table_attrs,
            ''.join(trs))

    @staticmethod
    def _to_html_from_grid(grid, **kwargs):
        '''
        Built the HTML table by nested cell in each grid in its own table
        '''

        new_grid = GridLayoutManager.apply_func_to_grid(grid,
            lambda i, c, row_col_dict: HTMLWriter._to_html(row_col_dict, **kwargs))

        html = ['<table>']
        for i, values in enumerate(new_grid):
            html.append('<tr>')
            for j, value in enumerate(values):
                if not value:
                    html.append('<td></td>')
                else:
                    html.append('<td>')
                    html.append(value)
                    html.append('</td>')
            html.append('</tr>')
        html.append('</table>')

        return "".join(html)

    @staticmethod
    def _grid_to_html(cell, **kwargs):
        if isinstance(cell.children, dict):
            html = HTMLWriter._to_html(cell.children, **kwargs)
            return html

        if isinstance(cell.children, Cell):
            return HTMLWriter._grid_to_html(cell.children, **kwargs)

        tables = []
        if isinstance(cell.children, list):
            for c in cell.children:
                tables.append(HTMLWriter._grid_to_html(c, **kwargs))

            if len(tables) == 1:
                return tables[0]
            html = ''
            for table in tables:
                if cell.vertical:
                    html += '<tr style="vertical-align:top;"><td style="vertical-align:top;">' + table + "</td></tr>"
                else:
                    html += '<td style="vertical-align:top">' + table + '</td>'
            return '<table>' + html + '</table>'


    @staticmethod
    def to_html(layout, orientation='vertical', **kwargs):
        '''
        Take a layout which contains a list of presentation models builts using the build_presentation_model function.

        Args:
            layout: An nested list of presentation_models, examples: [presentation_model] or [presentation_model1, presentation_mode2]. Not all nested layouts work very well in HTML, currently
            orientation: if vertical, the top level presentation model elements are rendered vertically, and for every nested level the orientation is flipped.
                         if horizontal, then the behavior is inverse
            kwargs:
                    all key-value pairs available in kwargs are directly set as value of the style attribute of `table` tag. example dict(backgroud-color='#FF88FF'), is used as <table style='background-color:#FF88FF'>..</table>

        Returns:
             Return a HTML formatted string. The outermost tag of the returned string is the `<table>`
        '''
        if not isinstance(layout, list):
            layout = [layout]

        #grid = GridLayoutManager.compute_grid(layout, orientation)
        grid = GridLayoutManager.get_non_shifted_row_col_dict(
            layout, orientation)
        return HTMLWriter._grid_to_html(grid, **kwargs)
