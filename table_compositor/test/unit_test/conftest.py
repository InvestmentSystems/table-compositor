import typing as tp
import warnings
from dbm.ndbm import library
from itertools import product

import pandas as pd

import table_compositor.table_compositor as tbc
from table_compositor.presentation_model import PresentationModel
from table_compositor.xlsx_styles import (
    OpenPyxlStyleHelper,
    XlsxWriterStyleHelper,
)
from table_compositor.xlsx_writer import (
    OpenPyxlCompositor,
    XlsxWriterCompositor,
    _XLSXCompositor,
)

LayoutT = tp.Union[PresentationModel, tp.List[PresentationModel]]


@tp.runtime_checkable
class CallBackFuncInterface(tp.Protocol):
    df: pd.DataFrame

    def data_value_func(self, i, c):
        pass

    def data_style_func(self, i, c):
        pass

    def header_style_func(self, node):
        pass

    def header_value_func(self, node):
        pass

    def index_value_func(self, node):
        pass

    def index_style_func(self, node):
        pass

    def index_name_style_func(self, node):
        pass

    def index_name_value_func(self, value):
        pass


class XlsxCallBackFunc(CallBackFuncInterface):
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


class XlsxCallBackFuncXlsxWriter(CallBackFuncInterface):
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


def get_simple_df_with_layout(
    *,
    grid: bool = False,
    nested: bool = False,
    callback_func_cls: tp.Type[CallBackFuncInterface] = XlsxCallBackFunc,
    frame_library: str = "pandas",
) -> tp.List[PresentationModel]:

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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            layout_model.data.values.loc[200, "b"] = layout_model_inner

    if grid:
        return [[layout_model, layout_model_inner], layout_model]

    return [layout_model]


def get_multi_hierarchical_df_with_layouts(
    *,
    grid=True,
    nested=False,
    callback_func_cls: tp.Type[CallBackFuncInterface] = XlsxCallBackFunc,
    frame_library: str = "pandas",
) -> PresentationModel:

    df = pd.DataFrame(
        data=dict(
            a=[0.1, 0.2, 0.3, 0.4],
            b=[100, 200, 300, 100],
            c=[True, False, True, False],
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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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


class FixtureFunc(tp.Protocol):
    def __call__(
        self,
        *,
        grid=True,
        nested=False,
        callback_func_cls: tp.Type[CallBackFuncInterface] = XlsxCallBackFunc,
        frame_library: str = "pandas",
    ) -> LayoutT:
        pass


class Fixture(tp.NamedTuple):
    name: str
    fixture_func: FixtureFunc
    grid: bool
    nested: bool
    orientation: str
    frame_library: str
    engine: tp.Type[_XLSXCompositor]
    callback_func_cls: tp.Type[CallBackFuncInterface]


def get_scenarios() -> tp.List[Fixture]:

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
    for (
        func,
        grid,
        nested,
        orientation,
        frame_library,
        (engine, callback_func_cls),
    ) in permutations:
        fixture_name = f"test_{func.__name__}_grid_{grid}_nested_{nested}_orientation_{orientation}_{frame_library}_{engine.__name__}"

        fixture = Fixture(
            name=fixture_name,
            fixture_func=func,
            grid=grid,
            nested=nested,
            orientation=orientation,
            frame_library=frame_library,
            engine=engine,
            callback_func_cls=callback_func_cls,
        )
        fixtures.append(fixture)

    return fixtures
