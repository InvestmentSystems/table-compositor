from collections import namedtuple
from itertools import product

import pandas as pd

import table_compositor.table_compositor as tbc
from ISLib import np_raise as np
from table_compositor.util import df_type_to_str
from table_compositor.xlsx_styles import (
    OpenPyxlStyleHelper,
    XlsxWriterStyleHelper,
)
from table_compositor.xlsx_writer import (
    OpenPyxlCompositor,
    XlsxWriterCompositor,
)

TestFixtures = namedtuple(
    "TestFixtures",
    (
        "name",
        "fixture_func",
        "grid",
        "nested",
        "orientation",
        "frame_library",
        "engine_and_callback_funcs_cls",
    ),
)


def get_scenarios():

    fixture_funcs = (get_simple_df_with_layout, get_multi_hierarchical_df_with_layouts)
    permutations = product(
        fixture_funcs,  # fixture function to get layout
        (True, False),  # grid arg for filter func
        (True, False),  # nested arg for filter func
        ("horizontal", "vertical"),  # horizontal or vertical orientation
        ("pandas", "static_frame"),
        (
            (OpenPyxlCompositor, XlsxCallBackFunc),
            (XlsxWriterCompositor, XlsxCallBackFuncXlsxWriter),
        ),
    )

    fixtures = []
    for p in permutations:
        fixture_name = "test_{}_grid_{}_nested_{}_orientation_{}_{}_{}".format(
            p[0].__name__, *p[1:-1], p[-1][0].__name__
        )
        fixture = TestFixtures(
            name=fixture_name,
            fixture_func=p[0],
            grid=p[1],
            nested=p[2],
            orientation=p[3],
            frame_library=p[4],
            engine_and_callback_funcs_cls=p[5],
        )
        fixtures.append(fixture)
    return fixtures


class XlsxCallBackFunc:
    def __init__(self, df):
        self.df = df

    def data_value_func(self, i, c):
        return self.df.loc[i, c]

    def data_style_func(self, i, c):
        number_format = '_($* #,##0_);_($* (#,##0);_($* "-"??_);_(@_)'
        if c == "b":
            return OpenPyxlStyleHelper.get_style(
                number_format=number_format,
                border=OpenPyxlStyleHelper.CustomBorders.thin_black_border,
            )

        if self.df.loc[i, c] >= 0.2 and c == "a":
            return OpenPyxlStyleHelper.get_style(
                bg_color="B8B8B8",
                border=OpenPyxlStyleHelper.CustomBorders.thin_black_border,
            )

        return OpenPyxlStyleHelper.get_style(
            border=OpenPyxlStyleHelper.CustomBorders.thin_black_border
        )

    def header_style_func(self, node):
        color = "FFFF00"
        if node.value == "a":
            color = "9BC2E6"
        if node.value == "b":
            color = "A9D08E"
        return OpenPyxlStyleHelper.get_style(
            bg_color=color, border=OpenPyxlStyleHelper.CustomBorders.thin_black_border
        )

    def header_value_func(self, node):
        if node.value == "c":
            return "Flag"
        return node.value

    def index_value_func(self, node):
        if node.key == ("a", 1):
            return "Aa"
        return node.value

    def index_style_func(self, node):
        color = "FFFF00"
        if node.value == "a":
            color = "9BC2E6"
        if node.value == "b":
            color = "A9D08E"
        return OpenPyxlStyleHelper.get_style(
            bg_color=color, border=OpenPyxlStyleHelper.CustomBorders.thin_black_border
        )

    def index_name_style_func(self, node):
        color = "9BC2E6"
        return OpenPyxlStyleHelper.get_style(
            bg_color=color, border=OpenPyxlStyleHelper.CustomBorders.thin_black_border
        )

    def index_name_value_func(self, value):
        return value


class XlsxCallBackFuncXlsxWriter:
    def __init__(self, df):
        self.df = df

    def data_value_func(self, i, c):
        return self.df.loc[i, c]

    def data_style_func(self, i, c):
        number_format = '_($* #,##0_);_($* (#,##0);_($* "-"??_);_(@_)'
        if c == "b":
            return XlsxWriterStyleHelper.get_style(number_format=number_format)

        if self.df.loc[i, c] >= 0.2 and c == "a":
            return XlsxWriterStyleHelper.get_style(bg_color="B8B8B8")

        return XlsxWriterStyleHelper.get_style()

    def header_style_func(self, node):
        color = "FFFF00"
        if node.value == "a":
            color = "9BC2E6"
        if node.value == "b":
            color = "A9D08E"
        return XlsxWriterStyleHelper.get_style(bg_color=color)

    def header_value_func(self, node):
        if node.value == "c":
            return "Flag"
        return node.value

    def index_value_func(self, node):
        if node.key == ("a", 1):
            return "Aa"
        return node.value

    def index_style_func(self, node):
        color = "FFFF00"
        if node.value == "a":
            color = "9BC2E6"
        if node.value == "b":
            color = "A9D08E"
        return XlsxWriterStyleHelper.get_style(bg_color=color)

    def index_name_style_func(self, node):
        color = "9BC2E6"
        return XlsxWriterStyleHelper.get_style(bg_color=color)

    def index_name_value_func(self, value):
        return value


class HtmlCallBackFunc:
    def __init__(self, df):
        self.df = df

    @staticmethod
    def _to_dollar_format(v):
        if not isinstance(v, (np.float, np.int)):
            return v
        r = "${:0,.0f}".format(v)
        return r

    def data_value_func(self, r, c):
        return df_type_to_str(self.df.loc[r, c])

    def data_style_func(self, r, c):
        if isinstance(self.df.loc[r, c], (np.int_, np.float, np.uint)):
            return dict(text_align="right", padding="10px")
        return dict(text_align="left", padding="10px")

    def header_value_func(self, node):
        return node.value

    def header_style_func(self, node):
        return dict(
            text_align="center",
            background_color="#4F81BD",
        )

    def index_value_func(self, node):
        return node.value

    def index_style_func(self, node):
        return dict(
            text_align="center",
            background_color="#4F81BD",
        )

    def index_name_style_func(self, node):
        return dict(text_align="left", padding="10px")

    def index_name_value_func(self, value):
        return value


def get_simple_df_with_layout(
    grid=False, nested=False, callback_func_cls=XlsxCallBackFunc, frame_library="pandas"
):

    data = dict(a=[0.1, 0.2, 0.3], b=[100, 200, -300], c=[True, False, True])
    df = pd.DataFrame(data=data, index=[100, 200, 300])
    df.index.name = "Sample_Index"

    if frame_library == "static_frame":
        import static_frame as sf

        df = sf.Frame.from_pandas(df)
        df.reindex(df.index.rename("Sample_Index"))

    call_back_func_inst = callback_func_cls(df)

    layout_model = tbc.build_presentation_model(
        df=df,
        data_value_func=call_back_func_inst.data_value_func,
        data_style_func=call_back_func_inst.data_style_func,
        header_value_func=call_back_func_inst.header_value_func,
        header_style_func=call_back_func_inst.header_style_func,
        index_value_func=call_back_func_inst.index_value_func,
        index_style_func=call_back_func_inst.index_style_func,
        index_name_func=call_back_func_inst.index_name_value_func,
        index_name_style_func=call_back_func_inst.index_name_style_func,
    )

    if isinstance(df, pd.DataFrame):
        inner_df = df.copy()
        inner_df.index = df.index.copy()
        inner_df.loc[400] = (1, 2, 3)
        # inner_df.index = [1, 2, 3]
        inner_df.index.name = "inner_df"
    else:
        # import ipdb; ipdb.set_trace()
        # inner_df = df.assign.loc[400](1,2,3)
        data = dict(
            a=[0.1, 0.2, 0.3, 1], b=[100, 200, -300, 2], c=[True, False, True, 3]
        )
        inner_df = sf.Frame.from_dict(
            mapping=data, index=sf.Index([100, 200, 300, 400], name="inner_df")
        )

    call_back_func_inst = callback_func_cls(inner_df)
    layout_model_inner = tbc.build_presentation_model(
        df=inner_df,
        data_value_func=call_back_func_inst.data_value_func,
        data_style_func=call_back_func_inst.data_style_func,
        header_value_func=call_back_func_inst.header_value_func,
        header_style_func=call_back_func_inst.header_style_func,
        index_value_func=call_back_func_inst.index_value_func,
        index_style_func=call_back_func_inst.index_style_func,
        index_name_func=call_back_func_inst.index_name_value_func,
        index_name_style_func=call_back_func_inst.index_name_style_func,
    )

    if nested:
        layout_model.data.values.loc[200, "b"] = layout_model_inner

    if grid:
        return [[layout_model, layout_model_inner], layout_model]

    return [layout_model]


def get_multi_hierarchical_df_with_layouts(
    grid=True, nested=False, callback_func_cls=XlsxCallBackFunc, frame_library="pandas"
):

    df = pd.DataFrame(
        data=dict(
            a=[0.1, 0.2, 0.3, 0.4], b=[100, 200, 300, 100], c=[True, False, True, False]
        )
    )
    df.index = pd.MultiIndex.from_tuples([("a", 1), ("a", 2), ("b", 1), ("b", 2)])
    df.columns = pd.MultiIndex.from_tuples([("a", 1), ("a", 2), ("b", 1)])
    df.index.name = "Sample_Index"

    if frame_library == "static_frame":
        import static_frame as sf

        df = sf.Frame.from_pandas(df)
        df = df.reindex(df.index.rename("Sample_Index"))

    call_back_func_inst = callback_func_cls(df)

    # excel calls begin here
    layout_model = tbc.build_presentation_model(
        df=df,
        data_value_func=call_back_func_inst.data_value_func,
        data_style_func=call_back_func_inst.data_style_func,
        header_value_func=call_back_func_inst.header_value_func,
        header_style_func=call_back_func_inst.header_style_func,
        index_value_func=call_back_func_inst.index_value_func,
        index_style_func=call_back_func_inst.index_style_func,
        index_name_func=call_back_func_inst.index_name_value_func,
        index_name_style_func=call_back_func_inst.index_name_style_func,
    )

    if isinstance(df, pd.DataFrame):
        inner_df = df.copy()
        inner_df.index = df.index.copy()
        inner_df.index.name = "inner_df"
    else:
        inner_df = df.reindex(df.index.rename("inner_df"))

    call_back_func_inst = callback_func_cls(inner_df)
    layout_model_inner = tbc.build_presentation_model(
        df=inner_df,
        data_value_func=call_back_func_inst.data_value_func,
        data_style_func=call_back_func_inst.data_style_func,
        header_value_func=call_back_func_inst.header_value_func,
        header_style_func=call_back_func_inst.header_style_func,
        index_value_func=call_back_func_inst.index_value_func,
        index_style_func=call_back_func_inst.index_style_func,
        index_name_func=call_back_func_inst.index_name_value_func,
        index_name_style_func=call_back_func_inst.index_name_style_func,
    )

    if nested:
        layout_model.data.values.loc[("a", 2), ("a", 1)] = layout_model_inner

    if grid:
        layout = [
            [layout_model_inner, layout_model, layout_model],
            [layout_model, layout_model_inner],
            [layout_model_inner],
        ]
    else:
        layout = [layout_model]

    return layout
